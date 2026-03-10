import asyncio
from textual.screen import Screen
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static, RichLog, Input
from textual.containers import Vertical, Center, Middle
from spin import SpinScreen
import socket
import subprocess

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

class SurveyScreen(Screen):

    BINDINGS = [("escape", "close_log", "Close Terminal Log")]

    CSS = """
    DoodleScreen {
    layers: menu background;
    }
    
    #bg-terminal {
        layer: background;
        width: 50%;
        height: 25%;
        background-tint: #536B78;
        color: #E887B7;
        padding: 0 1;
        border: round #FF1D8D;
        scrollbar-visibility: hidden;
    }

    #overlay-container {
        layer: menu;
        position: absolute;  /* THIS IS THE SECRET SAUCE */
        width: 100%;
        height: 100%;

    }

    #options-container {
        layer: options;
        width: 50%;
        height: 25%;
        padding: 0 1;
        border: round #FF1D8D;
        scrollbar-visibility: hidden;
        content-align: right middle;
    }
    """


    def compose(self) -> ComposeResult:
        # 1. Yield the background log first (assigned to the background layer via CSS)
        
        # 2. Yield your centered menu (assigned to the menu layer via CSS)
        with Center(id="overlay-container"):
            with Middle():
                
                main_container = Vertical(id="main-container")
                main_container.border_subtitle = "surveyOS"

                with main_container:
                    yield Static("◆ radio survey ◆", id="header-text")
                    yield Static("─" * 54)
                    yield Label("test dat radio!", id="status-box-doodle")
                    yield ListView(
                        ListItem(Label("> start digi survey"), id="digisurvey"),
                        ListItem(Label("> start doodle survey"), id="doodlesurvey"),
                        ListItem(Label("> dont worry about this one"), id="donut"),
                        ListItem(Label("> back"), id="back"),
                        id="list-view"
                    )
                    yield Label("READY_STAT: AWAITING INPUT", id="status-box")



    
    def on_list_view_selected(self, event: ListView.Selected) -> None:

        

        choice = event.item.id
        if choice == "back":
            self.app.pop_screen()

        elif choice == "digisurvey":
            self.query_one("#status-box", Label).update(f"EXECUTING: SURVEY...")

            # Trigger options menu for name
            if not self.query("#options-container"):
                # Create the options container with a text box and a list
                options_menu = Vertical(
                    Label("◆ Digi Survey ◆", id="options-header"),
                    Label("Select an option:"),
                    ListView(
                        ListItem(Label("> start survey"), id="startdigi"),
                        ListItem(Label("> stop survey"), id="stopdigi"),
                        ListItem(Label("> close"), id="close"),
                        id="sub-options-list"
                    ),
                    id="options-container"
                )
                
                # Mount it to the screen
                self.mount(options_menu)

                options_menu.focus()

        elif choice == "doodlesurvey":
            self.query_one("#status-box", Label).update("EXECUTING: SURVEY...")

            # Trigger options menu for name
            if not self.query("#options-container"):
                # Create the options container with a text box and a list
                options_menu = Vertical(
                    Label("◆ Doodle Survey ◆", id="options-header"),
                    Label("Select an option:"),
                    ListView(
                        ListItem(Label("> start survey"), id="startdoodle"),
                        ListItem(Label("> stop survey"), id="stopdoodle"),
                        ListItem(Label("> close"), id="close"),
                        id="sub-options-list"
                    ),
                    id="options-container"
                )
                
                # Mount it to the screen
                self.mount(options_menu)

            self.query_one("#sub-options-list").focus()

        elif choice == "startdigi":
            # Edit the config json!
            with self.app.suspend():
                subprocess.call(['vim', '/agility/radio_testing/digi_client/digi_receiver_profile.json'])

            self.send_message("startdigi")

        elif choice == "stopdigi":
            self.send_message("stopdigi")

        elif choice == "startdoodle":
            # Edit the config json!
            with self.app.suspend():
                subprocess.call(['vim', '/agility/radio_testing/doodle_labs_client/doodle_labs_receiver_profile.json'])

            self.send_message("startdoodle")

        elif choice == "stopdoodle":
            self.send_message("stopdoodle")

        elif choice == "close":
            self.action_close_log("#options-container")



        elif choice == "donut":
            self.app.push_screen(SpinScreen())
        else:
            self.query_one("#status-box", Label).update(f"EXECUTING: {choice.upper()}...")





    def send_message(self, message: str) -> None:
        
        self.query_one("#status-box", Label).update(f"Sending {message}")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(message.encode('utf-8'))

                data = s.recv(1024)
                print(f"Server says: {data.decode("utf-8")}")
                self.notify(data.decode("utf-8"))
        
        except ConnectionRefusedError:
            print("Could not connect to server, is it on??")
            self.notify({data.decode("utf-8")})


    
    def action_close_log(self, close_widget: str) -> None:
        """Fired when the user presses the Escape key."""
        # Look for the log widget
        log_nodes = self.query(close_widget)
        
        # If it exists, remove it from the screen and give the menu focus back
        if log_nodes:
            log_nodes.first().remove()
            self.query_one("#list-view", ListView).focus()




   
