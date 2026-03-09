from textual.screen import Screen
from textual.widgets import Static, Digits
from textual.containers import Center, Middle, Vertical
from textual.app import ComposeResult, App
import asyncio



background_color = "#191c21"
text_color = "#71c2b4"
header_color = "#8ebb97"
highlight_color = "#CEE5F2"


class SplashScreen(Screen):
    """A 'Booting' screen with a retro terminal feel."""
    
    CSS = f"""

    Screen {{
        background: {background_color};
    }}

    #main-container{{
        border: none;
        text-align: center;
    }}
    
    #header-text {{
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        color: {header_color};
    }}
    """

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical(id = "main-container"):
                    yield Static("radiOS")
        
         
    def on_mount(self) -> None:
        self.set_timer(5, self.app.pop_screen)
        
