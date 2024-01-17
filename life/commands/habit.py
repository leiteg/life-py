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

from typing import Annotated, Optional

from rich import box
from rich.table import Table
from typer import Argument, Context, Option, Typer

from life.app import App
from life.notion.filters import Checkbox
from life.util import iterfzf

# ==============================================================================
# GLOBAL
# ==============================================================================

cli = Typer()

# ==============================================================================
# DAILY
# ==============================================================================


@cli.command("show")
def habit_show(
    ctx: Context,
    days: Annotated[int, Option("--days", "-d")] = 0,
):
    """
    Show habits for an offset of DAYS from today.
    """
    app: App = ctx.obj

    with app.working():
        daily = app.db.daily.delta(days=days)

        if daily is None:
            app.error("No daily page found for this day.").exit(0)

        when = daily.date().start()
        assert when is not None

        table = Table(box=box.HORIZONTALS)
        table.add_column(when.strftime("%Y/%m/%d"))
        table.add_column("")

        habits = sorted(daily.checkboxes().keys())

        for habit in habits:
            check = daily.checkbox(habit).value()
            check = "[green]✔" if check else "[red]✘"
            table.add_row(habit, f"{check}")

    app.console.print(table)


@cli.command("mark")
def habit_mark(
    ctx: Context,
    name: Annotated[Optional[str], Argument()] = None,
    check: Annotated[bool, Option("--check/--uncheck", "-c/-C")] = True,
):
    """
    Mark a habit NAME as completed for today.
    """
    app: App = ctx.obj

    with app.working():
        today = app.db.daily.today()
        habits = today.checkboxes()

    if name is None:
        choice = iterfzf(habits.keys(), prompt="> Select habit: ")
        if choice is None:
            app.log.error("No habit selected.")
            raise SystemExit(1)
        assert isinstance(choice, str)
        name = choice

    with app.working():
        app.db.daily.update(
            page_id=today.id,
            properties=[
                Checkbox(name).assign(checked=check),
            ],
        )

    app.success()
