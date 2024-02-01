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

import functools
from datetime import date, datetime
from enum import Enum
from typing import Annotated, Optional

from rich import box
from rich.prompt import Confirm, FloatPrompt, Prompt
from rich.table import Table
from typer import Context, Option, Typer

from life.app import App
from life.notion.filters import Date, Number, Relation, Title, UniqueID
from life.notion.schema import Page
from life.util import dictfzf

# ==============================================================================
# GLOBAL
# ==============================================================================

cli = Typer()

# ==============================================================================
# HELPERS
# ==============================================================================


@functools.cache
def _acc_color(page: Page) -> str:
    select = page.select("Type").value()
    color = "default"
    if select is not None:
        match select.name:
            case "Credit":
                color = "green"
            case "Debit":
                color = "red"
    return color


@functools.cache
def _acc_name(page: Page) -> str:
    alias = page.text("Alias").plain_text()
    if len(alias) == 0:
        return page.name()
    return alias


# ==============================================================================
# TYPES
# ==============================================================================


class Period(str, Enum):
    week = "week"
    month = "month"
    year = "year"
    future = "future"
    all = "all"


# ==============================================================================
# TRANSACTIONS
# ==============================================================================


@cli.command("view")
def transaction_view(ctx: Context, period: Period = Period.month):
    """
    View a summary of transactions on the terminal.
    """
    app: App = ctx.obj

    filter = None
    match period:
        case Period.week:
            filter = Date().this_week()
        case Period.month:
            filter = Date().this_month()
        case Period.year:
            filter = Date().this_week()
        case Period.future:
            filter = Date().after(date.today())

    sort = [Date().sort("ascending"), UniqueID().sort("ascending")]

    with app.working("Fetching transactions"):
        transactions = app.db.transactions.query(filter, sort).by_id()

    if len(transactions) == 0:
        app.error("No transactions in the selected period.").exit(0)

    with app.working("Fetching accounts"):
        accounts = app.db.accounts.query().by_id()

    table = Table("Day", "Name", "Value", "Source", "Destination", box=box.HORIZONTALS)

    for _, trn in transactions.items():
        # Retrieve properties
        name = trn.name()
        when = trn.date().start()
        cash = trn.number("Value").value()
        src = trn.relation("Source").value()
        dst = trn.relation("Destination").value()

        assert len(src) == 1
        assert len(dst) == 1

        src = accounts[src.pop().id]
        dst = accounts[dst.pop().id]

        # Format properties
        src_color = _acc_color(src)
        dst_color = _acc_color(dst)
        src_name = _acc_name(src)
        dst_name = _acc_name(dst)

        title = f"[i]{name}[/i]"
        if when is not None:
            when = f"[dim]{when.strftime('%b %d')}[/dim]"
        else:
            when = ""
        cash = f"R$ {cash:10.2f}"
        src_name = f"[{src_color}]{src_name}[/]"
        dst_name = f"[{dst_color}]{dst_name}[/]"

        table.add_row(when, title, cash, src_name, dst_name)

    with app.console.pager(styles=True):
        app.console.print(table)


@cli.command("add")
def transaction_add(
    ctx: Context,
    name: Annotated[Optional[str], Option("--name", "-n")] = None,
    value: Annotated[Optional[float], Option("--value", "-v")] = None,
    when: Annotated[Optional[datetime], Option("--date", "-d")] = None,
    source: Annotated[Optional[str], Option("--src", "-s")] = None,
    destination: Annotated[Optional[str], Option("--dst", "-t")] = None,
    confirm: Annotated[bool, Option("--confirm/--no-confirm")] = True,
):
    """
    Add a new transaction.
    """
    app: App = ctx.obj

    with app.working("Fetching accounts"):
        accounts = app.db.accounts.query().by_name()

    if name is None:
        name = Prompt.ask("> Name of the transaction")

    if value is None:
        value = FloatPrompt.ask("> Value of the transaction")

    if source is None:
        src_page = dictfzf(accounts, prompt="> Select source account: ")
        if src_page is None:
            app.error("No source account selected").exit(1)
    else:
        raise NotImplementedError()

    if destination is None:
        dst_page = dictfzf(accounts, prompt="> Select source account: ")
        if dst_page is None:
            app.error("No destination account selected").exit(1)
    else:
        raise NotImplementedError()

    if when is None:
        when = datetime.today()

    if confirm and not Confirm.ask("> Create transaction?", default=False):
        app.error("Aborted!").exit(0)

    with app.working("Creating transaction"):
        app.db.transactions.create(
            properties=[
                Title().assign(name),
                Number("Value").assign(value),
                Relation("Source").assign(src_page.id),
                Relation("Destination").assign(dst_page.id),
                Date().assign(when),
            ]
        )

    app.success()
