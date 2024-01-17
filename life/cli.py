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

from typing import Annotated

from typer import Context, Option, Typer

from life.app import App
from life.commands import account, area, habit, note, session, task, todo, transaction

# ==============================================================================
# GLOBALS
# ==============================================================================

cli = Typer()

cli.add_typer(habit.cli, name="habit", help="Manage habits.")
cli.add_typer(session.cli, name="session", help="Manage sessions.")
cli.add_typer(task.cli, name="task", help="Manage tasks.")
cli.add_typer(note.cli, name="note", help="Manage notes.")
cli.add_typer(area.cli, name="area", help="Manage areas.")
cli.add_typer(account.cli, name="account", help="Manage accounts.")
cli.add_typer(transaction.cli, name="transaction", help="Manage transactions.")
cli.add_typer(todo.cli, name="todo", help="Manage to-do items.")

# ==============================================================================
# MAIN CALLBACK
# ==============================================================================


@cli.callback()
def main_callback(
    ctx: Context,
    verbose: Annotated[int, Option("--verbose", "-v", count=True)] = 0,
):
    """
    Life, Notion dashboard integration from the command-line!
    """
    ctx.obj = App(verbosity=verbose)


# ==============================================================================
# MAIN
# ==============================================================================


def main():
    cli()


if __name__ == "__main__":
    main()
