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

from datetime import datetime, timezone
from typing import Annotated

from rich.prompt import Confirm, Prompt
from rich.tree import Tree
from typer import Argument, Context, Typer, launch

from life.app import App
from life.notion.filters import Relation, Status, Title
from life.util import dictfzf

# ==============================================================================
# GLOBAL
# ==============================================================================

cli = Typer()

# ==============================================================================
# SESSIONS
# ==============================================================================


@cli.command("start")
def session_start(
    ctx: Context,
    name: Annotated[list[str], Argument()],
    confirm: bool = True,
):
    """
    Start a new session.
    """
    app: App = ctx.obj

    with app.working("Fetching sessions"):
        sessions = app.db.sessions.in_progress()

    if len(sessions) > 0:
        if not Confirm.ask("There is a session in-progress, continue?"):
            raise SystemExit(0)

    if name is None:
        title = Prompt.ask("> Session name", default="Work session")
    else:
        title = " ".join(name)

    with app.working("Fetching dailies"):
        today = app.db.daily.today()

    with app.working("Fetching tasks"):
        tasks = app.db.tasks.not_done()

    task = dictfzf(tasks, prompt="> Select the task: ")

    properties = [
        Title().assign(title),
        Status().assign("In progress"),
        Relation("Daily").assign(today.id),
    ]

    if task is not None:
        properties += [
            Relation("Task").assign(task.id),
        ]

    if confirm and not Confirm.ask("Create session?", default=False):
        app.error("Aborted.").exit(0)

    with app.working("Creating session"):
        session = app.db.sessions.create(
            properties=properties,
        )

    if task is not None and task.status().not_started():
        app.db.tasks.update(
            page_id=task.id, properties=[Status().assign("In progress")]
        )

    if task is not None:
        launch(task.get_url())
    else:
        launch(session.get_url())

    app.success()


@cli.command("end")
def session_end(ctx: Context):
    """
    End the current session.
    """
    app: App = ctx.obj

    with app.working("Fetching sessions"):
        sessions = app.db.sessions.in_progress()

    if len(sessions) == 0:
        app.success("No sessions in-progress.").exit(0)

    session = None
    if len(sessions) > 1:
        session = dictfzf(sessions, prompt="> Select the session: ")
        if session is None:
            app.error("No session selected.").exit(1)
    else:
        session = next(iter(sessions.values()))

    with app.working("Updating session"):
        session = app.db.sessions.update(
            page_id=session.id, properties=[Status().assign("Done")]
        )

    title = session.title().plain_text()
    duration = session.formula("Duration").as_number()
    total = app.db.daily.today().formula("Time Working").as_number()

    tree = Tree("[green]:heavy_check_mark:[/] DONE!")
    duration_hours = ""
    if duration is not None and duration > 60:
        duration_hours = f" ({duration//60} hours {duration%60} minutes)"
    tree.add(f"Session {title!r} took {duration} minutes{duration_hours}.")
    tree.add(f"You have worked {total} hours so far today.")

    app.console.print(tree)


@cli.command("info")
def session_info(ctx: Context):
    """
    Get info about the current session.
    """
    app: App = ctx.obj

    with app.working("Fetching sessions"):
        sessions = app.db.sessions.today()

    tree = Tree("[i]Today[/]")
    now = datetime.now(timezone.utc)
    total = 0

    for title, session in sessions.items():
        start = session.date("Start").start()
        assert isinstance(start, datetime)

        if session.status().name() == "In progress":
            icon = "[blue]:play_button:[/]"
            duration = (now - start).seconds / 60.0
        else:
            icon = "[green]:heavy_check_mark:[/]"
            duration = session.formula("Duration").as_number()

        assert duration is not None
        total += duration
        hours = duration // 60
        minutes = duration % 60
        tree.add(
            f"{icon} [i]{title}[/] / [dim]{hours:.0f} hours {minutes:.0f} minutes[/]"
        )

    hours = total // 60
    minutes = total % 60

    tree.label = f"[i]Today[/] / [dim]{hours:.0f} hours {minutes:.0f} minutes[/]"
    app.console.print(tree)
