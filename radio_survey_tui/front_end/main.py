from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static
from textual.containers import Vertical, Center, Middle
from doodle_labs_config import DoodleScreen
from digi_config import DigiScreen
from radio_testing import SurveyScreen
from textual.events import ScreenResume
import subprocess
import atexit



background_color = "#191c21"
text_color = "#71c2b4"
header_color = "#8ebb97"
highlight_color = "#CEE5F2"

class RadiOSApp(App):
    # This CSS creates the 'Boutique CLI' look
    CSS = f"""
    Screen {{
        background: {background_color};
    }}

    #main-container {{
        width: 60;
        height: 20;
        border: round #789192;
        padding: 1 2;
        background: {background_color};
        border-subtitle-align: right;
    }}

    #header-text {{
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        color: {header_color};
        transition: color 1s in_out_sine;
    }}

    ListView {{
        background: {background_color};
        border: none;
        height: auto;
        margin: 1 0;
    }}

    ListItem {{
        background: {background_color};
        color: {text_color};
        padding: 0 1;
    }}

    /* The "Selection" look: White text on black with a prefix */
    ListItem.--highlight {{
        background: #000000;
        color: {text_color};
        text-style: bold;
    }}

    /* The 'lighter' state of the breathing effect */
    #header-text.--breathe {{
        color: #FFFFFF; /* Replace this with whatever lighter hex color you prefer */
    }}
    
    """
    
    AUTO_FOCUS = "#list-view"

    async def on_mount(self) -> None:
       # Every 1.0 seconds, trigger the toggle_breathing method
        # self.push_screen(SplashScreen())
  

        self.set_interval(3.0, self.toggle_breathing)

        self.notify("This app is a work in progress. Just exit, or explore if you really want im not the boss of you", 
                title="WIP", 
                severity="information")




    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                main_container = Vertical(id="main-container")
                main_container.border_subtitle = "radiOS"
                with main_container:
                    yield Static("◆ radiOS ◆", id="header-text")
                    yield Static("─" * 54) # Simple ASCII divider
                    
                    yield ListView(
                        ListItem(Label("> digi radio "), id="godigi"),
                        ListItem(Label("> doodle labs radio"), id="godoodle"),
                        ListItem(Label("> survey radios"), id="surveytime"),
                        ListItem(Label("> exit"), id="exit"),
                        id="list-view"
                    )
                    yield Label("READY_STAT: AWAITING INPUT", id="status-box")


    def on_list_view_selected(self, event: ListView.Selected) -> None:
        choice = event.item.id
        if choice == "exit":
            self.exit()
        elif choice == "godoodle":
            self.push_screen(DoodleScreen())
        elif choice == "godigi":
            self.push_screen(DigiScreen())
        elif choice == "surveytime":
            self.push_screen(SurveyScreen())
        else:
            self.query_one("#status-box", Label).update(f"EXECUTING: {choice.upper()}...")


    def toggle_breathing(self) -> None:
        # Find the header and toggle the class on/off
        header = self.query_one("#header-text")
        header.toggle_class("--breathe")


if __name__ == "__main__":

    RadiOSApp().run()
