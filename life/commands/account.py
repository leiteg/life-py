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

from typer import Context, Option, Typer, launch

from life.app import App
from life.notion.filters import Checkbox, Select
from life.util import dictfzf

# ==============================================================================
# GLOBAL
# ==============================================================================

cli = Typer()

# ==============================================================================
# ACCOUNTS
# ==============================================================================


@cli.command("open")
def account_open(ctx: Context, all: Annotated[bool, Option("--all", "-a")] = False):
    """
    Open an account on the browser.
    """
    app: App = ctx.obj

    filter = Checkbox("Hidden").unchecked()
    if not all:
        filter &= Select("Type").equals("Credit")

    with app.working("Fetching accounts"):
        accounts = app.db.accounts.query(filter).by_name()

    account = dictfzf(accounts, prompt="> Select the account: ")
    if account is None:
        app.error("No account selected.").exit(1)

    launch(account.get_url())


@cli.command("view")
def account_view(
    ctx: Context,
    all: Annotated[bool, Option("--all", "-a")] = False
):  # fmt: skip
    """
    View a summary of accounts on the terminal.
    """
    raise NotImplementedError()
