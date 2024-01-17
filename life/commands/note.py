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

import webbrowser
from typing import Annotated, Optional

from click import edit
from typer import Context, Option, Typer

from life.app import App
from life.notion.filters import Relation, Select, Title
from life.notion.schema import BlockBuilder as bb
from life.util import dictfzf, iterfzf

# ==============================================================================
# GLOBAL
# ==============================================================================

cli = Typer()

# ==============================================================================
# NOTES
# ==============================================================================


@cli.command("open")
def note_open(
    ctx: Context,
    kind: Annotated[Optional[str], Option("--type", "-t")] = None,
):
    """
    Open a note on the browser.
    """
    app: App = ctx.obj

    filter = None
    if kind is not None:
        filter = Select("Type").equals(kind)

    with app.working():
        notes = app.db.notes.query(filter).by_name()

    note = dictfzf(notes, prompt="> Select the note: ")

    if note is None:
        app.error("No note selected.").exit(1)

    webbrowser.open(note.get_url())
    app.success()


@cli.command("new")
def note_new(
    ctx: Context,
    quick: Annotated[bool, Option("--quick", "-q")] = False,
):
    """
    Create a new note.
    """
    app: App = ctx.obj
    contents = edit("Untitled Note")

    if contents is None or contents == "":
        app.error("Empty note.").exit(1)

    contents = contents.strip().split("\n\n")
    contents = [paragraph.strip().replace("\n", " ") for paragraph in contents]

    title = contents[0]
    body = contents[1:]

    # Quick notes have empty area and "Quick" type
    if quick:
        app.db.notes.create(
            properties=[
                Title().assign(title),
                Select("Type").assign("Quick"),
            ],
            children=[bb.paragraph(text) for text in body],
            icon=bb.external_file("https://www.notion.so/icons/clipping_gray.svg"),
        )
        app.success().exit(0)

    # Select the Area
    areas = app.db.areas.all()
    area = dictfzf(areas, prompt="> Select the area: ")
    if area is None:
        app.error("No area selected.").exit(1)

    # Select the type
    kinds = app.db.notes.schema().select("Type").options()
    kind = iterfzf([k.name for k in kinds], prompt="> Select the type: ")
    if kind is None:
        app.error("No type selected.").exit(1)

    # Create note
    with app.working():
        app.db.notes.create(
            properties=[
                Title().assign(title),
                Relation("Area").assign(area.id),
                Select("Type").assign(kind),
            ]
        )

    app.success()
