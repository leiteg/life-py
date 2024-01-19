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


from typer import Context, Typer

from life.app import App
from life.notion.schema import BlockBuilder as bb

# ==============================================================================
# GLOBALS
# ==============================================================================

cli = Typer()

# ==============================================================================
# TODO
# ==============================================================================


@cli.command("today")
def todo_today(ctx: Context, what: list[str]):
    """
    Create a new to-do item in today's column in Work dashboard.
    """
    app: App = ctx.obj

    with app.working("Adding to-do item"):
        app.block.today.after(children=[bb.todo(" ".join(what))])

    app.success()


@cli.command("tomorrow")
def todo_tomorrow(ctx: Context, what: list[str]):
    """
    Create a new to-do item in tomorrow's column Work dashboard.
    """
    app: App = ctx.obj

    with app.working("Adding to-do item"):
        app.block.tomorrow.after(children=[bb.todo(" ".join(what))])

    app.success()


@cli.command("later")
def todo_later(ctx: Context, what: list[str]):
    """
    Create a new to-do item in later column in Work dashboard.
    """
    app: App = ctx.obj

    with app.working("Adding to-do item"):
        app.block.later.after(children=[bb.todo(" ".join(what))])

    app.success()
