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

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import IO, NoReturn

import tomllib
from pydantic import UUID4, BaseModel, TypeAdapter
from rich import print
from rich.console import Console
from rich.status import Status

from life.endpoints import (
    AccountsEndpoint,
    AreasEndpoint,
    DailyEndpoint,
    NotesEndpoint,
    ResourcesEndpoint,
    SessionsEndpoint,
    TasksEndpoint,
    TransactionsEndpoint,
)
from life.notion import Client
from life.notion.endpoints import BlockEndpoint, DatabaseEndpoint

# ==============================================================================
# CONSTANTS
# ==============================================================================

DEFAULT_CONFIG_PATH = "~/.config/life/life.toml"

# ==============================================================================
# CONFIG
# ==============================================================================


class ApiConfig(BaseModel):
    secret: str


class DatabaseConfig(BaseModel):
    daily: UUID4
    areas: UUID4
    tasks: UUID4
    sessions: UUID4
    notes: UUID4
    accounts: UUID4
    transactions: UUID4
    plantarium: UUID4
    garden: UUID4
    resources: UUID4


class BlockConfig(BaseModel):
    today: UUID4
    tomorrow: UUID4
    later: UUID4


class IconConfig(BaseModel):
    daily: str | None = None
    areas: str | None = None
    tasks: str | None = None
    sessions: str | None = None
    notes: str | None = None
    accounts: str | None = None
    transactions: str | None = None
    plantarium: str | None = None
    garden: str | None = None
    resources: str | None = None


class Config(BaseModel):
    api: ApiConfig
    databases: DatabaseConfig
    blocks: BlockConfig
    default_icons: IconConfig

    @staticmethod
    def parse_toml(f: IO[bytes]) -> Config:
        return TypeAdapter(Config).validate_python(tomllib.load(f))


# ==============================================================================
# APP
# ==============================================================================


@dataclass
class DatabaseEndpoints:
    daily: DailyEndpoint
    areas: AreasEndpoint
    tasks: TasksEndpoint
    sessions: SessionsEndpoint
    notes: NotesEndpoint
    accounts: AccountsEndpoint
    transactions: TransactionsEndpoint
    plantarium: DatabaseEndpoint
    garden: DatabaseEndpoint
    resources: ResourcesEndpoint

    def __init__(self, client: Client, config: DatabaseConfig, icons: IconConfig):
        self.daily = DailyEndpoint(
            client=client, id=str(config.daily), default_icon=icons.daily
        )
        self.areas = AreasEndpoint(
            client=client, id=str(config.areas), default_icon=icons.areas
        )
        self.tasks = TasksEndpoint(
            client=client, id=str(config.tasks), default_icon=icons.tasks
        )
        self.sessions = SessionsEndpoint(
            client=client, id=str(config.sessions), default_icon=icons.sessions
        )
        self.notes = NotesEndpoint(
            client=client, id=str(config.notes), default_icon=icons.notes
        )
        self.accounts = AccountsEndpoint(
            client=client, id=str(config.accounts), default_icon=icons.accounts
        )
        self.transactions = TransactionsEndpoint(
            client=client, id=str(config.transactions), default_icon=icons.transactions
        )


@dataclass
class BlockEndpoints:
    today: BlockEndpoint
    tomorrow: BlockEndpoint
    later: BlockEndpoint

    def __init__(self, client: Client, config: BlockConfig):
        self.today = BlockEndpoint(client=client, id=str(config.today))
        self.tomorrow = BlockEndpoint(client=client, id=str(config.tomorrow))
        self.later = BlockEndpoint(client=client, id=str(config.later))


@dataclass
class App:
    config: Config
    client: Client
    console: Console
    db: DatabaseEndpoints
    block: BlockEndpoints
    log: logging.Logger
    verbosity: int = 0

    def __init__(
        self, *, verbosity: int, config_path: str = DEFAULT_CONFIG_PATH
    ) -> None:
        self.verbosity = verbosity

        path = Path(config_path).expanduser()

        if not path.is_file():
            raise ValueError(f"Could not find config file under '{config_path}'")

        with path.open(mode="rb") as f:
            config = Config.parse_toml(f)

        self.config = config
        self.client = Client(auth=self.config.api.secret)
        self.console = Console()
        self.db = DatabaseEndpoints(
            self.client, self.config.databases, self.config.default_icons
        )
        self.block = BlockEndpoints(self.client, self.config.blocks)
        self.log = logging.getLogger("app")

        self.log.info("Application initialized!")

    def exit(self, code: int = 0) -> NoReturn:
        raise SystemExit(code)

    def error(self, message: str) -> App:
        print(f" [red]✘[/] {message}")
        return self

    def success(self, message: str = "DONE!") -> App:
        print(f" [green]:heavy_check_mark:[/] {message}")
        return self

    def working(self, message: str = "Working", **kwargs) -> Status:
        return self.console.status(message, **kwargs)
