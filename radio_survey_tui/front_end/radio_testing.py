import asyncio
from textual import work
from textual.screen import Screen
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static, RichLog, Input
from textual.containers import Vertical, Center, Middle
import json
from spin import SpinScreen
from datetime import datetime
import subprocess
import psutil


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
                    Label("◆ Configure Survey ◆", id="options-header"),
                    Label("Survey Name:"),
                    Input(placeholder="Type name here...", id="survey-name-input"),
                    Label("Select an option:"),
                    ListView(
                        ListItem(Label("> Edit "), id="opt1"),
                        ListItem(Label("> Option 2"), id="opt2"),
                        ListItem(Label("> Option 3"), id="opt3"),
                        id="sub-options-list"
                    ),
                    id="options-container"
                )
                
                # Mount it to the screen
                self.mount(options_menu)
                
                # Give focus to the text box so the user can start typing immediately
                options_menu.query_one("#survey-name-input", Input).focus()
                
                # IMPORTANT: We need to return early here!
                # If we don't, the code will continue downward and immediately run 
                # the survey script before the user has a chance to type their name.
                return 

            # Trigger the background worker
            # [Your existing terminal_log mounting and run_survey_script logic goes here...]
            # Trigger the background worker
            if not self.query("#bg-terminal"):
                # Create the widget (notice we leave can_focus alone this time)
                terminal_log = RichLog(id="bg-terminal", highlight=True, markup=True, auto_scroll=True)
                
                # Mount it to the screen
                self.mount(terminal_log)
                
                # Force focus onto the log so the user can scroll it immediately
                terminal_log.focus()
            
            # Edit the config json!
            self.edit_log_profile("/agility/radio_testing/digi_client/digi_receiver_profile.json")

            # Fire the background worker!
            # self.run_survey_script("/agility/radio_testing/digi_client/run_digi_receiver_docker.sh", "/agility/radio_testing/digi_client") # Replace with your actual shell script!
            self.run_survey_script("test_script.sh", ".")
        elif choice == "doodlesurvey":
            self.query_one("#status-box", Label).update(f"EXECUTING: SURVEY...")
            # Trigger the background worker
            if not self.query("#bg-terminal"):
                # Create the widget (notice we leave can_focus alone this time)
                terminal_log = RichLog(id="bg-terminal", highlight=True, markup=True, auto_scroll=True)
                
                # Mount it to the screen
                self.mount(terminal_log)
                
                # Force focus onto the log so the user can scroll it immediately
                terminal_log.focus()
            
            # Edit the config json!
            self.edit_log_profile("/agility/radio_testing/doodle_labs_client/doodle_labs_receiver_profile.json")

            # Fire the background worker!
            self.run_survey_script("/agility/radio_testing/doodle_labs_client/run_doodle_labs_receiver_docker.sh", "/agility/radio_testing/doodle_labs_client") # Replace with your actual shell script!


        elif choice == "donut":
            self.app.push_screen(SpinScreen())
        else:
            self.query_one("#status-box", Label).update(f"EXECUTING: {choice.upper()}...")





    @work(exclusive=True)
    async def run_survey_script(self, command: str, radio_directory: str) -> None:
        """Runs the script in the background and pipes output to the background RichLog."""
        log_widget = self.query_one("#bg-terminal", RichLog)
        status_box = self.query_one("#status-box", Label)
        
        log_widget.write(f"[bold cyan]SYSTEM:[/bold cyan] Initializing command: {command}\n")
        

        with open("tui_cache/cache.pid", 'r') as f:
            pid = f.read()

        if not psutil.pid_exists(pid):
            # Start the shell process
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=radio_directory
            )
            

            
            with open("tui_cache/cache.pid", 'w') as f:
                f.write()
                


        try:
            # Stream the output line-by-line into the background layer
            if process.stdout:
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break
                    log_widget.write(line.decode().rstrip())

            await process.wait()
            
            log_widget.write(f"\n[bold green]SYSTEM:[/bold green] Process complete. Exit code: {process.returncode}")
            self.action_close_log("#bg-terminal")
            status_box.update("READY_STAT: SURVEY COMPLETE")

        except asyncio.CancelledError:
            # THIS IS THE MAGIC: If the app closes, kill the shell process!
            process.terminate()
            log_widget.write("\n[bold red]SYSTEM:[/bold red] Process forcefully terminated.")
            status_box.update("READY_STAT: SURVEY ABORTED")
            raise  # Re-raise the error so Textual can finish shutting down cleanly

    def action_close_log(self, close_widget: str) -> None:
        """Fired when the user presses the Escape key."""
        # Look for the log widget
        log_nodes = self.query(close_widget)
        
        # If it exists, remove it from the screen and give the menu focus back
        if log_nodes:
            log_nodes.first().remove()
            self.query_one("#list-view", ListView).focus()




    def edit_log_profile(self, filepath: str) -> None:
        current_time = datetime.now().strftime("%Y-%m-%d_%H_%M")

        current_time = current_time + ".log"

        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            print(f"Error: Could not find {filepath}")
            return
        except json.JSONDecodeError:
            print(f"Error: {filepath} is not a valid JSON file.")
            return

        # 3. Update the specific key-value pair
        # (If "name" doesn't exist yet, this will create it!)
        data["log_file"] = current_time

        # 4. Open the file in write mode and save the updated dictionary
        # Using indent=4 keeps the JSON file nicely formatted and readable
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)

