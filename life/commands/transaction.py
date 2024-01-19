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

from datetime import date
from enum import Enum

from rich import box
from rich.table import Table
from typer import Context, Typer

from life.app import App
from life.notion.filters import Date

# ==============================================================================
# GLOBAL
# ==============================================================================

cli = Typer()

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

    with app.working("Fetching transactions"):
        transactions = app.db.transactions.query(filter).by_id()

    if len(transactions) == 0:
        app.error("No transactions in the selected period.").exit(0)

    with app.working("Fetching accounts"):
        accounts = app.db.accounts.query().by_id()

    table = Table("Date", "Name", "Value", "Source", "Destination", box=box.HORIZONTALS)

    for _, trn in transactions.items():
        name = trn.name()
        when = trn.date().start()
        cash = trn.number("Value").value()
        src = trn.relation("Source").value()
        dst = trn.relation("Destination").value()
        assert when is not None
        when = when.strftime("%Y-%m-%d")
        cash = f"R$ {cash:10.2f}"
        src = accounts[src[0].id].name()
        dst = accounts[dst[0].id].name()
        table.add_row(when, name, cash, src, dst)

    app.console.print(table)


@cli.command("add")
def transaction_add(
    ctx: Context,
):  # fmt: skip
    """
    Add a new transaction.
    """
    raise NotImplementedError()
