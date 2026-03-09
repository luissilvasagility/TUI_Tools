from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical, Center, Middle
import math

# ==========================================
# 1. ADD THE DONUT WIDGET
# ==========================================
class SpinningDonut(Static):
    """A custom widget that renders a spinning 3D ASCII donut."""
    
    def on_mount(self) -> None:
        self.A = 0.0
        self.B = 0.0
        # Re-render the donut 20 times a second
        self.set_interval(0.05, self.render_donut)

    def render_donut(self) -> None:
        b = [' '] * 1760
        z = [0.0] * 1760
        self.A += 0.04
        self.B += 0.02
        
        for j in range(0, 628, 7):
            for i in range(0, 628, 2):
                c = math.sin(i / 100)
                d = math.cos(j / 100)
                e = math.sin(self.A)
                f = math.sin(j / 100)
                g = math.cos(self.A)
                h = d + 2
                D = 1 / (c * h * e + f * g + 5)
                l = math.cos(i / 100)
                m = math.cos(self.B)
                n = math.sin(self.B)
                t = c * h * g - f * e
                
                x = int(40 + 30 * D * (l * h * m - t * n))
                y = int(12 + 15 * D * (l * h * n + t * m))
                o = int(x + 80 * y)
                N = int(8 * ((f * e - c * d * g) * m - c * d * e - f * g - l * d * n))
                
                if 0 <= y < 22 and 0 <= x < 80 and D > z[o]:
                    z[o] = D
                    b[o] = ".,-~:;=!*#$@"[N if N > 0 else 0]

        frame = "\n".join("".join(b[k:k+80]) for k in range(0, 1760, 80))
        self.update(frame)


# ==========================================
# 2. UPDATE YOUR SCREEN
# ==========================================
class SpinScreen(Screen):
    BINDINGS = [("escape", "close_log", "Close Terminal Log")]

    CSS = """
    DoodleScreen {
        layers: menu background;
    }
    
    /* IMPORTANT: The donut needs to be exactly 80x22 or the text wraps and breaks the illusion! */
    SpinningDonut {
        width: 80;
        height: 22;
        content-align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        # Yield your centered menu
        with Center():
            with Middle():
                # Replace 'pass' with the new widget
                yield SpinningDonut()

    def on_mount(self):
        self.notify("Why is this here?", title="ACHIEVEMENT GET!")
