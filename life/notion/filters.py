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

from datetime import date, datetime, timedelta
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, RootModel, model_serializer

# ==============================================================================
# PROPERTIES
# ==============================================================================


class Property(BaseModel):
    name: str
    kind: str

    def _assign(self, value: Value) -> Assign:
        return Assign(property=self, value=value)

    def _matches(self, operator: Operator) -> Filter:
        return Condition(property=self, operator=operator)

    def sort(self, direction: Literal["ascending", "descending"]) -> Sort:
        return Sort(property=self.name, direction=direction)

    def __contains__(self, other: Any) -> Filter:
        return self._matches(Contains(value=other))

    def equals(self, other: Any) -> Filter:
        return self._matches(Equals(value=other))

    def not_equal(self, other: Any) -> Filter:
        return self._matches(NotEquals(value=other))

    def contains(self, item: Any) -> Filter:
        return self._matches(Contains(value=item))

    def not_contains(self, item: Any) -> Filter:
        return self._matches(NotContains(value=item))

    def empty(self) -> Filter:
        return self._matches(Empty())

    def not_empty(self) -> Filter:
        return self._matches(NotEmpty())


class Checkbox(Property):
    def __init__(self, name) -> None:
        super().__init__(name=name, kind="checkbox")

    def assign(self, checked: bool) -> Assign:
        return self._assign(Plain(value=checked))

    def checked(self) -> Filter:
        return self._matches(Equals(value=True))

    def unchecked(self) -> Filter:
        return self._matches(Equals(value=False))


class CreatedBy(Property):
    pass  # TODO


class CreatedTime(Property):
    pass  # TODO


class Date(Property):
    def __init__(self, name="Date") -> None:
        super().__init__(name=name, kind="date")

    def assign(
        self, start: str | date | datetime, end: str | date | datetime | None = None
    ) -> Assign:
        return self._assign(DateValue(start=start, end=end))

    def __gt__(self, date: str | date | datetime) -> Filter:
        return self._matches(After(date=date))

    def __ge__(self, date: str | date | datetime) -> Filter:
        return self._matches(OnOrAfter(date=date))

    def __lt__(self, date: str | date | datetime) -> Filter:
        return self._matches(Before(date=date))

    def __le__(self, date: str | date | datetime) -> Filter:
        return self._matches(OnOrBefore(date=date))

    def after(self, date: str | date | datetime) -> Filter:
        return self.__gt__(date)

    def on_or_after(self, date: str | date | datetime) -> Filter:
        return self.__ge__(date)

    def before(self, date: str | date | datetime) -> Filter:
        return self.__lt__(date)

    def on_or_before(self, date: str | date | datetime) -> Filter:
        return self.__le__(date)

    def next_month(self) -> Filter:
        return self._matches(NextMonth())

    def next_week(self) -> Filter:
        return self._matches(NextWeek())

    def next_year(self) -> Filter:
        return self._matches(NextYear())

    def past_month(self) -> Filter:
        return self._matches(PastMonth())

    def past_week(self) -> Filter:
        return self._matches(PastWeek())

    def past_year(self) -> Filter:
        return self._matches(PastYear())

    def this_week(self) -> Filter:
        return self._matches(ThisWeek())

    def today(self) -> Filter:
        return self._matches(Equals(value=date.today()))

    def delta(self, **kwargs) -> Filter:
        return self._matches(Equals(value=date.today() + timedelta(**kwargs)))


class Email(Property):
    pass  # TODO


class Files(Property):
    pass  # TODO


class Formula(Property):
    pass  # TODO


class LastEditedBy(Property):
    pass  # TODO


class LastEditedTime(Property):
    pass  # TODO


class MultiSelect(Property):
    def __init__(self, name) -> None:
        super().__init__(name=name, kind="multi_select")

    def assign(self, names: list[str]) -> Assign:
        return self._assign(NamesValue(value=names))


class Number(Property):
    def __init__(self, name) -> None:
        super().__init__(name=name, kind="number")

    def assign(self, number: int | float) -> Assign:
        return self._assign(Plain(value=number))

    def __lt__(self, other: int | float) -> Filter:
        return self._matches(LessThan(value=other))

    def __le__(self, other: int | float) -> Filter:
        return self._matches(LessThanOrEqual(value=other))

    def __gt__(self, other: int | float) -> Filter:
        return self._matches(GreaterThan(value=other))

    def __ge__(self, other: int | float) -> Filter:
        return self._matches(GreaterThanOrEqual(value=other))


class People(Property):
    pass  # TODO


class PhoneNumber(Property):
    pass  # TODO


class Relation(Property):
    def __init__(self, name) -> None:
        super().__init__(name=name, kind="relation")

    def assign(self, value: str | UUID | list[str | UUID]) -> Assign:
        return self._assign(RelationValue(value=value))


class Rollup(Property):
    pass  # TODO


class RichText(Property):
    def __init__(self, name) -> None:
        super().__init__(name=name, kind="rich_text")

    def assign(self, title: str | Mention | list[str | Mention]) -> Assign:
        if not isinstance(title, list):
            title = [title]
        values = []
        for fragment in title:
            if isinstance(fragment, str):
                values.append(Text(value=fragment))
            else:
                values.append(fragment)
        return self._assign(RichTextValue(value=values))


class Select(Property):
    def __init__(self, name) -> None:
        super().__init__(name=name, kind="select")

    def assign(self, name: str) -> Assign:
        return self._assign(NameValue(value=name))


class Status(Property):
    def __init__(self, name="Status") -> None:
        super().__init__(name=name, kind="status")

    def assign(self, name: str) -> Assign:
        return self._assign(NameValue(value=name))

    def state(self, name: str) -> Filter:
        return self.equals(name)  # type: ignore

    def not_started(self) -> Filter:
        return self.state("Not started")

    def in_progress(self) -> Filter:
        return self.state("In progress")

    def paused(self) -> Filter:
        return self.state("Paused")

    def done(self) -> Filter:
        return self.state("Done")

    def abandoned(self) -> Filter:
        return self.state("Abandoned")


class Title(Property):
    def __init__(self, name="Name") -> None:
        super().__init__(name=name, kind="title")

    def assign(self, title: str | Mention | list[str | Mention]) -> Assign:
        if not isinstance(title, list):
            title = [title]
        values = []
        for fragment in title:
            if isinstance(fragment, str):
                values.append(Text(value=fragment))
            else:
                values.append(fragment)
        return self._assign(TitleValue(value=values))


class URL(Property):
    pass  # TODO


class UniqueID(Property):
    def __init__(self, name) -> None:
        super().__init__(name=name, kind="unique_id")


class Verification(Property):
    pass  # TODO


# ==============================================================================
# OPERATORS
# ==============================================================================


class Operator(BaseModel):
    pass


class Equals(Operator):
    value: str | int | bool | date | datetime

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"equals": self.value}


class NotEquals(Operator):
    value: str | int | bool

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"does_not_equal": self.value}


class Contains(Operator):
    value: str

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"contains": self.value}


class NotContains(Operator):
    value: str

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"does_not_contains": self.value}


class Empty(Operator):
    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"is_empty": True}


class NotEmpty(Operator):
    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"is_not_empty": True}


class DateOperator(Operator):
    pass


class After(DateOperator):
    date: str | date | datetime

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"after": self.date}


class OnOrAfter(DateOperator):
    date: str | date | datetime

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"on_or_after": self.date}


class Before(DateOperator):
    date: str | date | datetime

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"before": self.date}


class OnOrBefore(DateOperator):
    date: str | date | datetime

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"on_or_before": self.date}


class NextMonth(DateOperator):
    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"next_month": {}}


class NextWeek(DateOperator):
    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"next_week": {}}


class NextYear(DateOperator):
    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"next_year": {}}


class PastMonth(DateOperator):
    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"past_month": {}}


class PastWeek(DateOperator):
    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"past_week": {}}


class PastYear(DateOperator):
    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"past_year": {}}


class ThisWeek(DateOperator):
    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"this_week": {}}


class LessThan(Operator):
    value: int | float

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"less_than": self.value}


class LessThanOrEqual(Operator):
    value: int | float

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"less_than_or_equal_to": self.value}


class GreaterThan(Operator):
    value: int | float

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"greater_than": self.value}


class GreaterThanOrEqual(Operator):
    value: int | float

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"greater_than_or_equal_to": self.value}


# ==============================================================================
# FILTERS
# ==============================================================================


class Filter(BaseModel):
    def __and__(self, other: Filter) -> Filter:
        lhs = [self]
        if isinstance(self, And):
            lhs = self.children
        rhs = [other]
        if isinstance(other, And):
            rhs = other.children
        return And(children=[*lhs, *rhs])

    def __or__(self, other: Filter) -> Filter:
        lhs = [self]
        if isinstance(self, Or):
            lhs = self.children
        rhs = [other]
        if isinstance(other, Or):
            rhs = other.children
        return Or(children=[*lhs, *rhs])


class EmptyFilter(Filter):
    pass


class CustomFilter(Filter):
    filter: dict[str, Any]

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return self.filter


class Condition(Filter):
    property: Property
    operator: Operator

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {
            "property": self.property.name,
            self.property.kind: self.operator,
        }


class And(Filter):
    children: list[Filter]

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"and": self.children}


class Or(Filter):
    children: list[Filter]

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"or": self.children}


# ==============================================================================
# SORTS
# ==============================================================================


class Sort(BaseModel):
    property: str
    direction: Literal["ascending", "descending"]


SortList = RootModel[list[Sort]]


# ==============================================================================
# ASSIGNS
# ==============================================================================


class Assign(BaseModel):
    property: Property
    value: Value

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {self.property.name: {self.property.kind: self.value}}


class AssignList(RootModel[list[Assign]]):
    root: list[Assign]

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        data = {}
        for assign in self.root:
            data = {**data, **assign.serialize()}
        return data


# ==============================================================================
# VALUES
# ==============================================================================


class Value(BaseModel):
    pass


class Plain(Value):
    value: Any

    @model_serializer
    def serialize(self) -> Any:
        return self.value


class Text(Value):
    value: str

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"text": {"content": self.value}}


class MentionDate(Value):
    start: date | datetime
    end: date | datetime | None = None

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"mention": {"date": {"start": self.start, "end": self.end}}}


class MentionPage(Value):
    id: str | UUID

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"mention": {"page": {"id": self.id}}}


class MentionDatabase(Value):
    id: str | UUID

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"mention": {"database": {"id": self.id}}}


class MentionUser(Value):
    id: str | UUID

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"mention": {"user": {"id": self.id}}}


class MentionLinkPreview(Value):
    url: str

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"mention": {"link_preview": {"url": self.url}}}


Mention = MentionDate | MentionPage | MentionDatabase | MentionUser | MentionLinkPreview


class RichTextValue(Value):
    value: list[Mention | Text]

    @model_serializer
    def serialize(self) -> list[dict[str, Any]]:
        return [v.serialize() for v in self.value]


class TitleValue(Value):
    value: list[Mention | Text]

    @model_serializer
    def serialize(self) -> list[dict[str, Any]]:
        return [v.serialize() for v in self.value]


class NameValue(Value):
    value: str

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"name": self.value}


class NamesValue(Value):
    value: list[str]

    @model_serializer
    def serialize(self) -> list[dict[str, Any]]:
        return [{"name": name} for name in self.value]


class DateValue(Value):
    start: str | date | datetime
    end: str | date | datetime | None

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {
            "start": self.start,
            "end": self.end,
        }


class RelationValue(Value):
    value: str | UUID | list[str | UUID]

    @model_serializer
    def serialize(self) -> list[dict[str, Any]]:
        value = self.value
        if not isinstance(value, list):
            value = [value]
        value = [str(v) if isinstance(v, UUID) else v for v in value]
        return [{"id": id} for id in value]


# ==============================================================================
# FUNCTIONS
# ==============================================================================


def all(*args: Filter) -> Filter:
    return And(children=list(args))


def any(*args: Filter) -> Filter:
    return Or(children=list(args))
