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


from typer import Context, Typer, launch

from life.app import App
from life.notion.filters import Files, Select
from life.util import dictfzf

# ==============================================================================
# GLOBALS
# ==============================================================================

cli = Typer()

# ==============================================================================
# RESOURCES
# ==============================================================================


@cli.command("open")
def resource_open(ctx: Context):
    """
    Open a resource from the Resources database.
    """
    app: App = ctx.obj

    filter = Select("Type").equals("Textbook") & Files("Attachments").not_empty()
    with app.working("Fetching resources"):
        results = app.db.resources.query(filter).by_name()

    resource = dictfzf(results, prompt="> Select the resource: ")
    if resource is None:
        app.error("No resource selected").exit(1)

    file = resource.files("Attachments").get(0)
    launch(file.get_url())
