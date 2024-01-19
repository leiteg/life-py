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
from uuid import UUID

from pydantic import TypeAdapter
from rich.pretty import pretty_repr

from . import Client
from .filters import Assign, AssignList, Filter, Sort, SortList
from .schema import (
    Block,
    Cover,
    Database,
    Icon,
    InnerBlock,
    InnerBlockList,
    Page,
    QueryResult,
)
from .schema import (
    BlockBuilder as bb,
)

# ==============================================================================
# GLOBALS
# ==============================================================================

log = logging.getLogger("endpoints")

# ==============================================================================
# CLASSES
# ==============================================================================


@dataclass
class Endpoint:
    client: Client
    id: str

    def __init__(self, client: Client, id: str | UUID):
        self.client = client
        self.id = id if isinstance(id, str) else str(id)


@dataclass
class BlockEndpoint(Endpoint):
    def __init__(self, client: Client, id: str | UUID):
        super().__init__(client, id)

    def get(self) -> Block:
        res = self.client.blocks.retrieve(block_id=self.id)
        return TypeAdapter(Block).validate_python(res)

    def after(self, children: list[InnerBlock]) -> QueryResult[Block]:
        parent_id = self.get().parent.id()
        assert parent_id is not None

        res = self.client.blocks.children.append(
            block_id=str(parent_id),
            after=str(self.id),
            children=InnerBlockList(root=children).model_dump(mode="json"),
        )

        return QueryResult[Block].parse(res)


@dataclass
class DatabaseEndpoint(Endpoint):
    default_icon: str | None = None

    def __init__(self, client: Client, id: str | UUID):
        super().__init__(client, id)

    def query(
        self, filter: Filter | None = None, sorts: list[Sort] | None = None
    ) -> QueryResult[Page]:
        request = {}

        if filter is not None:
            request["filter"] = filter.model_dump(mode="json")

        if sorts is not None:
            request["sorts"] = SortList(sorts).model_dump(mode="json")

        log.debug(f"[QUERY @ {self.id}] REQUEST:")
        log.debug(f"{pretty_repr(request)}")

        response = self.client.databases.query(database_id=self.id, **request)

        log.debug(f"[QUERY @ {self.id}] RESPONSE:")
        log.debug(f"{pretty_repr(response)}")

        return QueryResult.parse(response)

    def schema(self) -> Database:
        return Database.parse(self.client.databases.retrieve(self.id))

    def create(
        self,
        properties: Assign | list[Assign],
        children: list[InnerBlock] | None = None,
        icon: Icon | None = None,
        cover: Cover | None = None,
    ) -> Page:
        if children is None:
            children = []

        if not isinstance(properties, list):
            properties = [properties]

        properties = AssignList(root=properties).model_dump(mode="json")
        children = InnerBlockList(root=children).model_dump(mode="json")

        request = {
            "parent": {"database_id": self.id},
            "properties": properties,
            "children": children,
        }

        if icon is not None:
            request["icon"] = icon.model_dump(mode="json")
        elif self.default_icon is not None:
            request["icon"] = bb.external_file(self.default_icon).model_dump(
                mode="json"
            )

        if cover is not None:
            request["cover"] = cover.model_dump(mode="json")

        log.debug(f"[CREATE @ {self.id}] REQUEST:")
        log.debug(f"{pretty_repr(request)}")

        response = self.client.pages.create(**request)

        log.debug(f"[CREATE @ {self.id}] RESPONSE:")
        log.debug(f"{pretty_repr(response)}")

        return Page.parse(response)

    def update(
        self,
        page_id: str | UUID,
        properties: Assign | list[Assign],
    ) -> Page:
        if isinstance(page_id, UUID):
            page_id = str(page_id)

        if not isinstance(properties, list):
            properties = [properties]

        properties = AssignList(root=properties).model_dump(mode="json")

        log.debug(f"[UPDATE @ {self.id}] PROPERTIES:")
        log.debug(f"{pretty_repr(properties)}")

        response = self.client.pages.update(
            page_id=page_id,
            properties=properties,
        )

        log.debug(f"[UPDATE @ {self.id}] RESPONSE:")
        log.debug(f"{pretty_repr(response)}")

        return Page.parse(response)
