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

import logging
from dataclasses import dataclass
from datetime import date

from life.notion.endpoints import DatabaseEndpoint
from life.notion.filters import Date, Status, Title
from life.notion.schema import BlockBuilder as bb
from life.notion.schema import Page

# ==============================================================================
# GLOBALS
# ==============================================================================

log = logging.getLogger()

# ==============================================================================
# CLASSES
# ==============================================================================


@dataclass
class DailyEndpoint(DatabaseEndpoint):
    def today(self) -> Page:
        """Get or create today's daily page."""
        query = self.query(Date().today())

        if query.count() > 1:
            log.error("Found more than one daily page for today.")

        if query.count() >= 1:
            return query.first()

        return self.create(
            icon=bb.external_file(
                "https://www.notion.so/icons/partly-cloudy-day_gray.svg"
            ),
            properties=[
                Title().assign("Today"),
                Date().assign(date.today()),
            ],
        )

    def delta(self, **kwargs) -> Page | None:
        query = self.query(Date().delta(**kwargs))

        if query.count() == 0:
            return None

        if query.count() > 1:
            log.error("Found more than one daily page.")

        if query.count() >= 1:
            return query.first()


@dataclass
class TasksEndpoint(DatabaseEndpoint):
    def all(self) -> dict[str, Page]:
        return self.query().by_name()

    def not_done(self) -> dict[str, Page]:
        return self.query(Status().in_progress() | Status().not_started()).by_name()


@dataclass
class SessionsEndpoint(DatabaseEndpoint):
    def today(self) -> dict[str, Page]:
        return self.query(
            filter=Date("Start").today(), sorts=[Date("Start").sort("ascending")]
        ).by_name()

    def in_progress(self) -> dict[str, Page]:
        return self.query(Status().in_progress()).by_name()


@dataclass
class AreasEndpoint(DatabaseEndpoint):
    def all(self) -> dict[str, Page]:
        return self.query().by_name()


@dataclass
class AccountsEndpoint(DatabaseEndpoint):
    pass


@dataclass
class TransactionsEndpoint(DatabaseEndpoint):
    pass


@dataclass
class NotesEndpoint(DatabaseEndpoint):
    def all(self) -> dict[str, Page]:
        return self.query().by_name()


@dataclass
class ResourcesEndpoint(DatabaseEndpoint):
    pass
