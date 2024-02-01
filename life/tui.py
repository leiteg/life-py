# Copyright 2024 Gustavo Leite
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from textual.app import App as TextualApp
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import (
    Checkbox,
    Footer,
    Header,
    Static,
    TabbedContent,
    TabPane,
)

from life.app import App

# ==============================================================================
# CUSTOM WIDGETS
# ==============================================================================


class Title(Static):
    pass


class Sidebar(Widget):
    def compose(self) -> ComposeResult:
        yield Title("LifeApp")


# ==============================================================================
# APP
# ==============================================================================


class LifeTUI(TextualApp[None]):
    CSS_PATH = "life.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit", False),
        Binding("ctrl+b", "toggle_sidebar", "Sidebar", False),
    ]

    life_app: App

    def __init__(self, app: App) -> None:
        super().__init__()
        self.life_app = app

    def compose(self) -> ComposeResult:
        yield Header()
        yield Sidebar(classes="-hidden")
        with TabbedContent():
            yield TabPane("Habits", id="habits")
            yield TabPane("Sessions", id="sessions")
        yield Footer()

    def on_mount(self) -> None:
        ctn_habits = self.query_one("#habits")
        ctn_sessions = self.query_one("#sessions")
        today = self.life_app.db.daily.today()
        sessions = self.life_app.db.sessions.today()

        for name, checkbox in today.checkboxes().items():
            ctn_habits.mount(Checkbox(name, checkbox.value(), disabled=True))
        for name, _ in sessions.items():
            ctn_sessions.mount(Static(name))

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one(Sidebar)
        self.set_focus(None)
        if sidebar.has_class("-hidden"):
            sidebar.remove_class("-hidden")
        else:
            if sidebar.query("*:focus"):
                self.screen.set_focus(None)
            sidebar.add_class("-hidden")


# ==============================================================================
# MAIN
# ==============================================================================


def main() -> None:
    return LifeTUI(App(verbosity=0)).run()


if __name__ == "__main__":
    main()
