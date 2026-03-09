import asyncio
from textual import work
from textual.screen import Screen
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static, RichLog
from textual.containers import Vertical, Center, Middle
import subprocess





class DigiScreen(Screen):

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
        padding: 2 2;
        border: round #FF1D8D;
        scrollbar-visibility: hidden;
        text-wrap: wrap;
    }

    #main-container {
        border-title-align: left;
    }


    #overlay-container {
        layer: menu;
        position: absolute;  /* THIS IS THE SECRET SAUCE */
        width: 100%;
        height: 100%;
    }    
    """

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                main_container = Vertical(id="main-container")
                main_container.border_title = "digiOS"

                with main_container:
                    yield Static("◆ digi config menu ◆", id="header-text")
                    yield Static("─" * 54)
                    yield Label("the one that works...", id="status-box-digi")
                    yield ListView(
                        ListItem(Label("> view digi JSON configuration"), id="viewdigiconf"),
                        ListItem(Label("> digi radio configuration"), id="digiconf"),
                        ListItem(Label("> back"), id="back"),
                        id="list-view"
                    )
                    yield Label("READY_STAT: AWAITING INPUT", id="status-box")


    def on_list_view_selected(self, event: ListView.Selected) -> None:
        choice = event.item.id
        if choice == "back":
            self.app.pop_screen()
        elif choice == "viewdigiconf":
            with self.app.suspend():
                subprocess.call(['vim', '/agility/digi_radio_configuration_and_setup/digi_config_profile.json'])
        elif choice == "digiconf":
            self.query_one("#status-box", Label).update(f"EXECUTING: CONFIG...")
            # Trigger the background worker
            if not self.query("#bg-terminal"):
                # Create the widget (notice we leave can_focus alone this time)
                terminal_log = RichLog(id="bg-terminal", highlight=True, markup=True, auto_scroll=True)
                
                # Mount it to the screen
                self.mount(terminal_log)
                
                # Force focus onto the log so the user can scroll it immediately
                terminal_log.focus()
                
            # Fire the background worker!
            self.run_survey_script("/agility/digi_configuration_and_setup/configure_radio.sh") # Replace with your actual shell script!

        else:
            self.query_one("#status-box", Label).update(f"EXECUTING: {choice.upper()}...")


    @work(exclusive=True)
    async def run_survey_script(self, command: str) -> None:
        """Runs the script in the background and pipes output to the background RichLog."""
        log_widget = self.query_one("#bg-terminal", RichLog)
        status_box = self.query_one("#status-box", Label)
        
        log_widget.write(f"[bold cyan]SYSTEM:[/bold cyan] Initializing command: {command}\n")
        
        # Start the shell process
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )

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
            self.action_close_log()
            status_box.update("READY_STAT: SURVEY COMPLETE")

        except asyncio.CancelledError:
            # THIS IS THE MAGIC: If the app closes, kill the shell process!
            process.terminate()
            log_widget.write("\n[bold red]SYSTEM:[/bold red] Process forcefully terminated.")
            status_box.update("READY_STAT: SURVEY ABORTED")
            raise  # Re-raise the error so Textual can finish shutting down cleanly

    def action_close_log(self) -> None:
        """Fired when the user presses the Escape key."""
        # Look for the log widget
        log_nodes = self.query("#bg-terminal")
        
        # If it exists, remove it from the screen and give the menu focus back
        if log_nodes:
            log_nodes.first().remove()
            self.query_one("#list-view", ListView).focus()
    
