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

from datetime import date, datetime
from typing import Annotated, Any, Callable, Generic, Literal, TypeVar, Union
from uuid import UUID

from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    RootModel,
    TypeAdapter,
    model_serializer,
)

# ==============================================================================
# ENUMS
# ==============================================================================

ForegroundColor = Literal[
    "blue",
    "brown",
    "default",
    "gray",
    "green",
    "green",
    "orange",
    "pink",
    "purple",
    "red",
    "yellow",
]

BackgroundColor = Literal[
    "blue_background",
    "brown_background",
    "gray_background",
    "green_background",
    "orange_background",
    "pink_background",
    "purple_background",
    "red_background",
    "yellow_background",
]

Color = ForegroundColor | BackgroundColor

RollupFunction = Literal[
    "average",
    "checked",
    "count_per_group",
    "count",
    "count_values",
    "date_range",
    "earliest_date",
    "empty",
    "latest_date",
    "max",
    "median",
    "min",
    "not_empty",
    "percent_checked",
    "percent_empty",
    "percent_not_empty",
    "percent_per_group",
    "percent_unchecked",
    "range",
    "unchecked",
    "unique",
    "show_original",
    "show_unique",
    "sum",
]

NumberFormat = Literal[
    "argentine_peso",
    "baht",
    "australian_dollar",
    "canadian_dollar",
    "chilean_peso",
    "colombian_peso",
    "danish_krone",
    "dirham",
    "dollar",
    "euro",
    "forint",
    "franc",
    "hong_kong_dollar",
    "koruna",
    "krona",
    "leu",
    "lira",
    "mexican_peso",
    "new_taiwan_dollar",
    "new_zealand_dollar",
    "norwegian_krone",
    "number",
    "number_with_commas",
    "percent",
    "philippine_peso",
    "pound",
    "peruvian_sol",
    "rand",
    "real",
    "ringgit",
    "riyal",
    "ruble",
    "rupee",
    "rupiah",
    "shekel",
    "singapore_dollar",
    "uruguayan_peso",
    "yen,",
    "yuan",
    "won",
    "zloty",
]

# ==============================================================================
# OBJECTS
# ==============================================================================

# BASIC ------------------------------------------------------------------------


class EmptyObject(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IdentifierObject(BaseModel):
    id: UUID4


class NumberObject(BaseModel):
    number: int | float


class InternalLinkObject(BaseModel):
    url: HttpUrl
    expiry_time: datetime


class ExternalLinkObject(BaseModel):
    url: HttpUrl


class DateObject(BaseModel):
    start: date | datetime
    end: date | datetime | None
    time_zone: Any | None = Field(repr=False)


class SelectObject(BaseModel):
    color: ForegroundColor
    id: str
    name: str


class UniqueIDObject(BaseModel):
    number: int
    prefix: str | None


class VerificationObject(BaseModel):
    state: str
    verified_by: PartialUser | None
    date: DateObject


# FILE -------------------------------------------------------------------------


class ExternalUnnamedFile(BaseModel):
    type: Literal["external"] = Field(default="external", repr=False)
    external: ExternalLinkObject


class InternalUnnamedFile(BaseModel):
    type: Literal["file"] = Field(default="file", repr=False)
    file: InternalLinkObject


UnnamedFile = Annotated[
    Union[ExternalUnnamedFile, InternalUnnamedFile],
    Field(discriminator="type"),
]


class ExternalCaptionedFile(BaseModel):
    type: Literal["external"] = Field(default="external", repr=False)
    external: ExternalLinkObject
    caption: RichText


class InternalCaptionedFile(BaseModel):
    type: Literal["file"] = Field(default="file", repr=False)
    file: InternalLinkObject
    caption: RichText


CaptionedFile = Annotated[
    Union[ExternalCaptionedFile, InternalCaptionedFile],
    Field(discriminator="type"),
]


# RICH TEXT --------------------------------------------------------------------


class AnnotationsObject(BaseModel):
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: Color


class TextObject(BaseModel):
    content: str
    link: ExternalLinkObject | None


class SimpleTextFragmentObject(BaseModel):
    type: Literal["simple_text"] = Field(default="simple_text", repr=False)
    text: TextObject

    @model_serializer
    def serializer(self) -> dict[str, Any]:
        return {"text": self.text}


class TextFragmentObject(BaseModel):
    type: Literal["text"] = Field(repr=False)
    text: TextObject
    annotations: AnnotationsObject | None = Field(repr=False)
    plain_text: str | None
    href: HttpUrl | None = Field(repr=False)


class MentionDatabaseObject(BaseModel):
    type: Literal["database"] = Field(repr=False)
    database: IdentifierObject


class MentionDateObject(BaseModel):
    type: Literal["date"] = Field(repr=False)
    date: DateObject


class MentionLinkPreviewObject(BaseModel):
    type: Literal["link_preview"] = Field(repr=False)
    link: ExternalLinkObject


class MentionPageObject(BaseModel):
    type: Literal["page"] = Field(repr=False)
    page: IdentifierObject


class MentionTemplateObject(BaseModel):
    type: Literal["template_mention"] = Field(repr=False)
    template_mention: Any  # TODO


class MentionUserObject(BaseModel):
    type: Literal["user"] = Field(repr=False)
    user: PartialUser


MentionObject = Annotated[
    Union[
        MentionDatabaseObject,
        MentionDateObject,
        MentionLinkPreviewObject,
        MentionPageObject,
        MentionTemplateObject,
        MentionUserObject,
    ],
    Field(discriminator="type"),
]


class MentionFragmentObject(BaseModel):
    type: Literal["mention"] = Field(repr=False)
    mention: MentionObject
    annotations: AnnotationsObject = Field(repr=False)
    plain_text: str
    href: HttpUrl | None = Field(repr=False)


class EquationFragmentObject(BaseModel):
    type: Literal["equation"] = Field(repr=False)
    equation: Equation
    annotations: AnnotationsObject = Field(repr=False)
    plain_text: str
    href: HttpUrl | None = Field(repr=False)


RichTextFragment = Annotated[
    Union[
        SimpleTextFragmentObject,
        TextFragmentObject,
        MentionFragmentObject,
        EquationFragmentObject,
    ],
    Field(discriminator="type"),
]


class RichText(RootModel[list[RichTextFragment]]):
    pass


# PARENTS ----------------------------------------------------------------------


class DatabaseParent(BaseModel):
    type: Literal["database_id"] = Field(repr=False)
    database_id: UUID4


class PageParent(BaseModel):
    type: Literal["page_id"] = Field(repr=False)
    page_id: UUID4


class WorkspaceParent(BaseModel):
    type: Literal["workspace"] = Field(repr=False)
    workspace: bool


class BlockParent(BaseModel):
    type: Literal["block_id"] = Field(repr=False)
    block_id: UUID4


_Parent = Annotated[
    Union[DatabaseParent, PageParent, BlockParent, WorkspaceParent],
    Field(discriminator="type"),
]


class Parent(RootModel[_Parent]):
    root: _Parent

    def id(self) -> UUID | None:
        if isinstance(self.root, DatabaseParent):
            return self.root.database_id
        if isinstance(self.root, PageParent):
            return self.root.page_id
        if isinstance(self.root, BlockParent):
            return self.root.block_id
        return None


# EMOJI ------------------------------------------------------------------------


class Emoji(BaseModel):
    type: Literal["emoji"] = Field(default="emoji", repr=False)
    emoji: str


# ICON -------------------------------------------------------------------------

Icon = (
    Annotated[
        Union[UnnamedFile, Emoji],
        Field(discriminator="type"),
    ]
    | None
)

# COVER ------------------------------------------------------------------------

Cover = UnnamedFile | None

# PROPERTY VALUE SPECIFIC ------------------------------------------------------


class BooleanFormulaObject(BaseModel):
    type: Literal["boolean"] = Field(repr=False)
    boolean: bool | None


class NumberFormulaObject(BaseModel):
    type: Literal["number"] = Field(repr=False)
    number: int | float | None


class StringFormulaObject(BaseModel):
    type: Literal["string"] = Field(repr=False)
    string: str | None


class DateFormulaObject(BaseModel):
    type: Literal["date"] = Field(repr=False)
    date: date | datetime | None


FormulaObject = Annotated[
    BooleanFormulaObject
    | NumberFormulaObject
    | StringFormulaObject
    | DateFormulaObject,
    Field(discriminator="type"),
]

# TODO: This union is not complete.
RollupObject = Annotated[
    DateFormulaObject | NumberFormulaObject, Field(discriminator="type")
]


# DATABASE SPECIFIC ------------------------------------------------------------


class SelectDatabaseObject(BaseModel):
    options: list[SelectObject]


class RelationDatabaseObject(BaseModel):
    type: str = Field(repr=False)
    database_id: str


class RollupDatabaseObject(BaseModel):
    function: RollupFunction
    relation_property_id: str
    relation_property_name: str
    rollup_property_id: str
    rollup_property_name: str


class NumberDatabaseObject(BaseModel):
    format: NumberFormat


class FormulaDatabaseObject(BaseModel):
    expression: str


# ==============================================================================
# USERS
# ==============================================================================


class PartialUser(BaseModel):
    object: Literal["user"] = Field(repr=False)
    id: str


class BaseUserModel(BaseModel):
    object: Literal["user"] = Field(repr=False)
    id: UUID4
    name: str | None
    avatar_url: HttpUrl | None


class PersonUser(BaseUserModel):
    type: Literal["person"] = Field(repr=False)
    person: dict[str, Any]


class BotUser(BaseUserModel):
    type: Literal["bot"] = Field(repr=False)
    bot: dict[str, Any]


User = Annotated[PersonUser | BotUser, Field(discriminator="type")]

# ==============================================================================
# BLOCKS
# ==============================================================================


class BaseBlockModel(BaseModel):
    object: Literal["block"] = Field(repr=False)
    id: UUID4
    parent: Parent
    created_time: datetime
    last_edited_time: datetime
    created_by: PartialUser
    last_edited_by: PartialUser
    has_children: bool
    archived: bool


# BOOKMARK ---------------------------------------------------------------------


class Bookmark(BaseModel):
    type: Literal["bookmark"] = Field(default="bookmark", exclude=True)
    caption: RichText
    url: HttpUrl


class BookmarkBlock(BaseBlockModel):
    type: Literal["bookmark"] = Field(repr=False)
    bookmark: Bookmark


# BREADCRUMB -------------------------------------------------------------------


class Breadcrumb(EmptyObject):
    type: Literal["breadcrumb"] = Field(default="breadcrumb", exclude=True)


class BreadcrumbBlock(BaseBlockModel):
    type: Literal["breadcrumb"] = Field(repr=False)
    breadcrumb: Breadcrumb


# BULLET -----------------------------------------------------------------------


class BulletItem(BaseModel):
    type: Literal["bulleted_list_item"] = Field(
        default="bulleted_list_item", exclude=True
    )
    rich_text: RichText
    color: Color
    children: InnerBlockList | None = None


class BulletItemBlock(BaseBlockModel):
    type: Literal["bulleted_list_item"] = Field(repr=False)
    bulleted_list_item: BulletItem


# CALLOUT ----------------------------------------------------------------------


class Callout(BaseModel):
    type: Literal["callout"] = Field(default="callout", exclude=True)
    rich_text: RichText
    color: Color
    icon: Icon
    children: InnerBlockList | None = None


class CalloutBlock(BaseBlockModel):
    type: Literal["callout"] = Field(repr=False)
    callout: Callout


# CHILD DATABASE ---------------------------------------------------------------


class ChildDatabase(BaseModel):
    title: str


class ChildDatabaseBlock(BaseBlockModel):
    type: Literal["child_database"] = Field(repr=False)
    child_database: ChildDatabase


# CHILD PAGE -------------------------------------------------------------------


class ChildPage(BaseModel):
    title: str


class ChildPageBlock(BaseBlockModel):
    type: Literal["child_page"] = Field(repr=False)
    child_page: ChildPage


# CODE -------------------------------------------------------------------------


class Code(BaseModel):
    type: Literal["code"] = Field(default="code", exclude=True)
    caption: RichText
    rich_text: RichText
    language: str


class CodeBlock(BaseBlockModel):
    type: Literal["code"] = Field(repr=False)
    code: Code


# COLUMN -----------------------------------------------------------------------


class Column(EmptyObject):
    type: Literal["column"] = Field(default="column", exclude=True)
    children: InnerBlockList | None = None


class ColumnBlock(BaseBlockModel):
    type: Literal["column"] = Field(repr=False)
    column: Column


# COLUMN LIST ------------------------------------------------------------------


class ColumnList(EmptyObject):
    type: Literal["column_list"] = Field(default="column_list", exclude=True)
    children: InnerBlockList | None = None


class ColumnListBlock(BaseBlockModel):
    type: Literal["column_list"] = Field(repr=False)
    column_list: ColumnList


# DIVIDER ----------------------------------------------------------------------


class Divider(EmptyObject):
    type: Literal["divider"] = Field(default="divider", exclude=True)


class DividerBlock(BaseBlockModel):
    type: Literal["divider"] = Field(repr=False)
    divider: Divider


# EMBED ------------------------------------------------------------------------


class Embed(BaseModel):
    type: Literal["embed"] = Field(default="embed", exclude=True)
    url: HttpUrl


class EmbedBlock(BaseBlockModel):
    type: Literal["embed"] = Field(repr=False)
    embed: Embed


# EQUATION ---------------------------------------------------------------------


class Equation(BaseModel):
    type: Literal["equation"] = Field(default="equation", exclude=True)
    expression: str


class EquationBlock(BaseBlockModel):
    type: Literal["equation"] = Field(repr=False)
    equation: Equation


# FILE -------------------------------------------------------------------------


class InternalNamedFile(BaseModel):
    type: Literal["file"] = Field(default="file", repr=False)
    name: str | None = None
    caption: RichText
    file: InternalLinkObject


class ExternalNamedFile(BaseModel):
    type: Literal["external"] = Field(default="external", repr=False)
    name: str | None = None
    caption: RichText
    external: ExternalLinkObject


NamedFile = Annotated[
    Union[ExternalNamedFile, InternalNamedFile],
    Field(discriminator="type"),
]


class File(BaseModel):
    type: Literal["file"] = Field(default="file", repr=False)
    file: NamedFile


class FileBlock(BaseBlockModel):
    type: Literal["file"] = Field(repr=False)
    file: NamedFile


# HEADING 1 --------------------------------------------------------------------


class Heading1(BaseModel):
    type: Literal["heading_1"] = Field(default="heading_1", exclude=True)
    rich_text: RichText
    color: Color
    is_toggleable: bool


class Heading1Block(BaseBlockModel):
    type: Literal["heading_1"] = Field(repr=False)
    heading_1: Heading1


# HEADING 2 --------------------------------------------------------------------


class Heading2(BaseModel):
    type: Literal["heading_2"] = Field(default="heading_2", exclude=True)
    rich_text: RichText
    color: Color
    is_toggleable: bool


class Heading2Block(BaseBlockModel):
    type: Literal["heading_2"] = Field(repr=False)
    heading_2: Heading2


# HEADING 3 -------------------------------------------------------------------


class Heading3(BaseModel):
    type: Literal["heading_3"] = Field(default="heading_3", exclude=True)
    rich_text: RichText
    color: Color
    is_toggleable: bool


class Heading3Block(BaseBlockModel):
    type: Literal["heading_3"] = Field(repr=False)
    heading_3: Heading3


# IMAGE ------------------------------------------------------------------------


class Image(BaseModel):
    type: Literal["image"] = Field(default="image", repr=False)
    image: CaptionedFile


class ImageBlock(BaseBlockModel):
    type: Literal["image"] = Field(repr=False)
    image: NamedFile


# LINK PREVIEW -----------------------------------------------------------------


class LinkPreviewBlock(BaseBlockModel):
    type: Literal["link_preview"] = Field(repr=False)
    link_preview: ExternalLinkObject


# NUMBERED ---------------------------------------------------------------------


class NumberedItem(BaseModel):
    type: Literal["numbered_list_item"] = Field(
        default="numbered_list_item", exclude=True
    )
    rich_text: RichText
    color: Color
    children: InnerBlockList | None = None


class NumberedItemBlock(BaseBlockModel):
    type: Literal["numbered_list_item"] = Field(repr=False)
    numbered_list_item: NumberedItem


# PARAGRAPH --------------------------------------------------------------------


class Paragraph(BaseModel):
    type: Literal["paragraph"] = Field(default="paragraph", exclude=True)
    rich_text: RichText
    color: Color
    children: InnerBlockList | None = None


class ParagraphBlock(BaseBlockModel):
    type: Literal["paragraph"] = Field(repr=False)
    paragraph: Paragraph


# PDF --------------------------------------------------------------------------


class Pdf(BaseModel):
    type: Literal["pdf"] = Field(default="pdf", exclude=True)
    pdf: CaptionedFile


class PdfBlock(BaseBlockModel):
    type: Literal["pdf"] = Field(repr=False)
    pdf: NamedFile


# QUOTE ------------------------------------------------------------------------


class Quote(BaseModel):
    type: Literal["quote"] = Field(default="quote", exclude=True)
    rich_text: RichText
    color: Color
    children: InnerBlockList | None = None


class QuoteBlock(BaseBlockModel):
    type: Literal["quote"] = Field(repr=False)
    quote: Quote


# SYNCED BLOCK -----------------------------------------------------------------


class Synced(BaseModel):
    type: Literal["synced_block"] = Field(default="synced_block", exclude=True)
    synced_from: None
    children: InnerBlockList | None = None


class SyncedBlock(BaseBlockModel):
    type: Literal["synced_block"] = Field(repr=False)
    synced_block: Synced


# TABLE ------------------------------------------------------------------------


class Table(BaseModel):
    type: Literal["table"] = Field(default="table", exclude=True)
    table_width: int
    has_column_header: bool
    has_row_header: bool
    children: InnerBlockList | None = None


class TableBlock(BaseBlockModel):
    type: Literal["table"] = Field(repr=False)
    table: Table


# TABLE ROW --------------------------------------------------------------------


class TableRow(BaseModel):
    type: Literal["table_row"] = Field(default="table_row", exclude=True)
    cells: list[RichText]


class TableRowBlock(BaseBlockModel):
    type: Literal["table_row"] = Field(repr=False)
    table_row: TableRow


# TABLE OF CONTENTS (TOC) ------------------------------------------------------


class Toc(BaseModel):
    type: Literal["table_of_contents"] = Field(
        default="table_of_contents", exclude=True
    )
    color: Color


class TocBlock(BaseBlockModel):
    type: Literal["table_of_contents"] = Field(repr=False)
    table_of_contents: Toc


# TO-DO ITEM -------------------------------------------------------------------


class TodoItem(BaseModel):
    type: Literal["to_do"] = Field(default="to_do", exclude=True)
    rich_text: RichText
    color: Color
    checked: bool | None
    children: InnerBlockList | None = None


class TodoItemBlock(BaseBlockModel):
    type: Literal["to_do"] = Field(repr=False)
    to_do: TodoItem


# TOGGLE -----------------------------------------------------------------------


class Toggle(BaseModel):
    type: Literal["toggle"] = Field(default="toggle", exclude=True)
    rich_text: RichText
    color: Color
    children: InnerBlockList | None = None


class ToggleBlock(BaseBlockModel):
    type: Literal["toggle"] = Field(repr=False)
    toggle: Toggle


# VIDEO ------------------------------------------------------------------------


class Video(BaseModel):
    type: Literal["video"] = Field(default="video", exclude=True)
    video: CaptionedFile


class VideoBlock(BaseBlockModel):
    type: Literal["video"] = Field(repr=False)
    video: NamedFile


# BLOCK ------------------------------------------------------------------------


Block = Annotated[
    Union[
        BookmarkBlock,
        BreadcrumbBlock,
        BulletItemBlock,
        CalloutBlock,
        ChildDatabaseBlock,
        ChildPageBlock,
        CodeBlock,
        ColumnBlock,
        ColumnListBlock,
        DividerBlock,
        EmbedBlock,
        EquationBlock,
        FileBlock,
        Heading1Block,
        Heading2Block,
        Heading3Block,
        ImageBlock,
        LinkPreviewBlock,
        NumberedItemBlock,
        ParagraphBlock,
        PdfBlock,
        QuoteBlock,
        SyncedBlock,
        TableBlock,
        TableRowBlock,
        TocBlock,
        TodoItemBlock,
        ToggleBlock,
        VideoBlock,
    ],
    Field(discriminator="type"),
]


class BlockList(RootModel[list[Block]]):
    pass


InnerBlock = Annotated[
    Union[
        Bookmark,
        Breadcrumb,
        BulletItem,
        Callout,
        # `ChildDatabase` not applicable
        # `ChildPage` not applicable
        Code,
        Column,
        ColumnList,
        Divider,
        Embed,
        Equation,
        File,
        Heading1,
        Heading2,
        Heading3,
        Image,
        # `LinkPreview` not applicable
        NumberedItem,
        Paragraph,
        Pdf,
        Quote,
        Synced,
        Table,
        TableRow,
        Toc,
        TodoItem,
        Toggle,
        Video,
    ],
    Field(discriminator="type"),
]


class InnerBlockList(RootModel[list[InnerBlock]]):
    root: list[InnerBlock]

    @model_serializer
    def serialize(self) -> list[Any]:
        return [
            {inner_block.type: inner_block}
            if not isinstance(inner_block, File | Image | Video | Pdf)
            else inner_block
            for inner_block in self.root
        ]


# ==============================================================================
# PAGE PROPERTIES
# ==============================================================================


class CheckboxValue(BaseModel):
    type: Literal["checkbox"] = Field(repr=False)
    id: str = Field(repr=False)
    checkbox: bool

    def value(self) -> bool:
        return self.checkbox


class CreatedByValue(BaseModel):
    type: Literal["created_by"] = Field(repr=False)
    id: str = Field(repr=False)
    created_by: PartialUser

    def value(self) -> PartialUser:
        return self.created_by


class CreatedTimeValue(BaseModel):
    type: Literal["created_time"] = Field(repr=False)
    id: str = Field(repr=False)
    created_time: datetime

    def value(self) -> datetime:
        return self.created_time


class DateValue(BaseModel):
    type: Literal["date"] = Field(repr=False)
    id: str = Field(repr=False)
    date: DateObject | None

    def value(self) -> DateObject | None:
        return self.date

    def start(self) -> date | datetime | None:
        if self.date:
            return self.date.start
        return None

    def end(self) -> date | datetime | None:
        if self.date:
            return self.date.end
        return None


class EmailValue(BaseModel):
    type: Literal["email"] = Field(repr=False)
    id: str = Field(repr=False)
    email: EmailStr | None

    def value(self) -> EmailStr | None:
        return self.email


class FilesValue(BaseModel):
    type: Literal["files"] = Field(repr=False)
    id: str = Field(repr=False)
    files: list[UnnamedFile]

    def value(self) -> list[UnnamedFile]:
        return self.files


class FormulaValue(BaseModel):
    type: Literal["formula"] = Field(repr=False)
    id: str = Field(repr=False)
    formula: FormulaObject

    def value(self) -> FormulaObject:
        return self.formula

    def as_boolean(self) -> bool | None:
        assert isinstance(self.formula, BooleanFormulaObject)
        return self.formula.boolean

    def as_number(self) -> int | float | None:
        assert isinstance(self.formula, NumberFormulaObject)
        return self.formula.number

    def as_string(self) -> str | None:
        assert isinstance(self.formula, StringFormulaObject)
        return self.formula.string

    def as_date(self) -> date | datetime | None:
        assert isinstance(self.formula, DateFormulaObject)
        return self.formula.date


class LastEditedByValue(BaseModel):
    type: Literal["last_edited_by"] = Field(repr=False)
    id: str = Field(repr=False)
    last_edited_by: PartialUser

    def value(self) -> PartialUser:
        return self.last_edited_by


class LastEditedTimeValue(BaseModel):
    type: Literal["last_edited_time"] = Field(repr=False)
    id: str = Field(repr=False)
    last_edited_time: datetime

    def value(self) -> datetime:
        return self.last_edited_time


class MultiSelectValue(BaseModel):
    type: Literal["multi_select"] = Field(repr=False)
    id: str = Field(repr=False)
    multi_select: list[SelectObject]

    def value(self) -> list[SelectObject]:
        return self.multi_select


class NumberValue(BaseModel):
    type: Literal["number"] = Field(repr=False)
    id: str = Field(repr=False)
    number: int | float | None

    def value(self) -> int | float | None:
        return self.number


class PeopleValue(BaseModel):
    type: Literal["people"] = Field(repr=False)
    id: str = Field(repr=False)
    people: list[PartialUser]

    def value(self) -> list[PartialUser]:
        return self.people


class PhoneNumberValue(BaseModel):
    type: Literal["phone_number"] = Field(repr=False)
    id: str = Field(repr=False)
    phone_number: str | None

    def value(self) -> str | None:
        return self.phone_number


class RelationValue(BaseModel):
    type: Literal["relation"] = Field(repr=False)
    id: str = Field(repr=False)
    has_more: bool
    relation: list[IdentifierObject]

    def value(self) -> list[IdentifierObject]:
        return self.relation


class RichTextValue(BaseModel):
    type: Literal["rich_text"] = Field(repr=False)
    id: str = Field(repr=False)
    rich_text: RichText

    def value(self) -> RichText:
        return self.rich_text

    def plain_text(self) -> str:
        return "".join(fragment.plain_text for fragment in self.rich_text)


class RollupValue(BaseModel):
    type: Literal["rollup"] = Field(repr=False)
    id: str = Field(repr=False)
    rollup: RollupObject

    def value(self) -> RollupObject:
        return self.rollup

    def as_number(self) -> int | float | None:
        assert isinstance(self.rollup, NumberFormulaObject)
        return self.rollup.number

    def as_date(self) -> date | datetime | None:
        assert isinstance(self.rollup, DateFormulaObject)
        return self.rollup.date


class SelectValue(BaseModel):
    type: Literal["select"] = Field(repr=False)
    id: str = Field(repr=False)
    select: SelectObject | None

    def value(self) -> SelectObject | None:
        return self.select


class StatusValue(BaseModel):
    type: Literal["status"] = Field(repr=False)
    id: str = Field(repr=False)
    status: SelectObject

    def value(self) -> SelectObject:
        return self.status

    def name(self) -> str:
        return self.status.name

    def not_started(self) -> bool:
        return self.status.name == "Not started"

    def in_progress(self) -> bool:
        return self.status.name == "In progress"

    def done(self) -> bool:
        return self.status.name == "Done"


class TitleValue(BaseModel):
    type: Literal["title"] = Field(repr=False)
    id: str = Field(repr=False)
    title: RichText

    def value(self) -> RichText:
        return self.title

    def plain_text(self) -> str:
        return "".join(text_obj.plain_text for text_obj in self.title.root)


class URLValue(BaseModel):
    type: Literal["url"] = Field(repr=False)
    id: str = Field(repr=False)
    url: HttpUrl | None

    def value(self) -> HttpUrl | None:
        return self.url


class UniqueIDValue(BaseModel):
    type: Literal["unique_id"] = Field(repr=False)
    id: str = Field(repr=False)
    unique_id: UniqueIDObject

    def value(self) -> UniqueIDObject:
        return self.unique_id

    def number(self) -> int:
        return self.unique_id.number

    def prefix(self) -> str | None:
        return self.unique_id.prefix


class VerificationValue(BaseModel):
    type: Literal["verification"] = Field(repr=False)
    id: str = Field(repr=False)
    verification: VerificationObject

    def value(self) -> VerificationObject:
        return self.verification


PropertyValue = Annotated[
    Union[
        CheckboxValue,
        CreatedByValue,
        CreatedTimeValue,
        DateValue,
        EmailValue,
        FilesValue,
        FormulaValue,
        LastEditedByValue,
        LastEditedTimeValue,
        MultiSelectValue,
        NumberValue,
        PeopleValue,
        PhoneNumberValue,
        RelationValue,
        RichTextValue,
        RollupValue,
        SelectValue,
        StatusValue,
        TitleValue,
        URLValue,
        UniqueIDValue,
        VerificationValue,
    ],
    Field(discriminator="type"),
]

# ==============================================================================
# PAGES
# ==============================================================================


class Page(BaseModel):
    object: Literal["page"] = Field(repr=False)
    id: UUID4
    created_time: datetime = Field(repr=False)
    last_edited_time: datetime = Field(repr=False)
    created_by: PartialUser = Field(repr=False)
    last_edited_by: PartialUser = Field(repr=False)
    cover: Cover
    icon: Icon
    parent: Parent
    archived: bool = Field(repr=False)
    properties: dict[str, PropertyValue]
    url: HttpUrl
    public_url: HttpUrl | None = Field(repr=False)

    @staticmethod
    def parse(obj) -> Page:
        return TypeAdapter(Page).validate_python(obj)

    def name(self) -> str:
        return self.title().plain_text()

    def checkbox(self, property_name: str) -> CheckboxValue:
        property = self.properties[property_name]
        assert isinstance(property, CheckboxValue)
        return property

    def checkboxes(self) -> dict[str, CheckboxValue]:
        props = {}
        for name, prop in self.properties.items():
            if isinstance(prop, CheckboxValue):
                props[name] = prop
        return props

    def created_by_prop(self, property_name: str = "Created by") -> CreatedByValue:
        property = self.properties[property_name]
        assert isinstance(property, CreatedByValue)
        return property

    def created_time_prop(
        self, property_name: str = "Created time"
    ) -> CreatedTimeValue:
        property = self.properties[property_name]
        assert isinstance(property, CreatedTimeValue)
        return property

    def date(self, property_name: str = "Date") -> DateValue:
        property = self.properties[property_name]
        assert isinstance(property, DateValue)
        return property

    def email(self, property_name: str = "Email") -> EmailValue:
        property = self.properties[property_name]
        assert isinstance(property, EmailValue)
        return property

    def files(self, property_name: str = "Files & Media") -> FilesValue:
        property = self.properties[property_name]
        assert isinstance(property, FilesValue)
        return property

    def formula(self, property_name: str) -> FormulaValue:
        property = self.properties[property_name]
        assert isinstance(property, FormulaValue)
        return property

    def last_edited_by_prop(
        self, property_name: str = "Last edited by"
    ) -> LastEditedByValue:
        property = self.properties[property_name]
        assert isinstance(property, LastEditedByValue)
        return property

    def last_edited_time_prop(
        self, property_name: str = "Last edited time"
    ) -> LastEditedTimeValue:
        property = self.properties[property_name]
        assert isinstance(property, LastEditedTimeValue)
        return property

    def multi_select(self, property_name: str) -> MultiSelectValue:
        property = self.properties[property_name]
        assert isinstance(property, MultiSelectValue)
        return property

    def number(self, property_name: str) -> NumberValue:
        property = self.properties[property_name]
        assert isinstance(property, NumberValue)
        return property

    def people(self, property_name: str = "Person") -> PeopleValue:
        property = self.properties[property_name]
        assert isinstance(property, PeopleValue)
        return property

    def phone_number(self, property_name: str = "Phone") -> PhoneNumberValue:
        property = self.properties[property_name]
        assert isinstance(property, PhoneNumberValue)
        return property

    def relation(self, property_name: str) -> RelationValue:
        property = self.properties[property_name]
        assert isinstance(property, RelationValue)
        return property

    def text(self, property_name: str) -> RichTextValue:
        property = self.properties[property_name]
        assert isinstance(property, RichTextValue)
        return property

    def rollup(self, property_name: str) -> RollupValue:
        property = self.properties[property_name]
        assert isinstance(property, RollupValue)
        return property

    def select(self, property_name: str) -> SelectValue:
        property = self.properties[property_name]
        assert isinstance(property, SelectValue)
        return property

    def status(self, property_name: str = "Status") -> StatusValue:
        property = self.properties[property_name]
        assert isinstance(property, StatusValue)
        return property

    def title(self, property_name: str = "Name") -> TitleValue:
        property = self.properties[property_name]
        assert isinstance(property, TitleValue)
        return property

    def url_prop(self, property_name: str = "URL") -> URLValue:
        property = self.properties[property_name]
        assert isinstance(property, URLValue)
        return property

    def unique_id(self, property_name: str = "ID") -> UniqueIDValue:
        property = self.properties[property_name]
        assert isinstance(property, UniqueIDValue)
        return property

    def verification(self, property_name: str = "Verification") -> VerificationValue:
        property = self.properties[property_name]
        assert isinstance(property, VerificationValue)
        return property

    def get_url(self) -> str:
        return str(self.url)


# ==============================================================================
# DATABASE PROPERTIES
# ==============================================================================


class CheckboxDatabaseProperty(BaseModel):
    type: Literal["checkbox"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    checkbox: EmptyObject


class CreatedByDatabaseProperty(BaseModel):
    type: Literal["created_by"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    created_by: EmptyObject


class CreatedTimeDatabaseProperty(BaseModel):
    type: Literal["created_time"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    created_time: EmptyObject


class DateDatabaseProperty(BaseModel):
    type: Literal["date"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    date: EmptyObject


class EmailDatabaseProperty(BaseModel):
    type: Literal["email"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    email: EmptyObject


class FilesDatabaseProperty(BaseModel):
    type: Literal["files"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    files: EmptyObject


class FormulaDatabaseProperty(BaseModel):
    type: Literal["formula"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    formula: FormulaDatabaseObject

    def expression(self) -> str:
        return self.formula.expression


class LastEditedByDatabaseProperty(BaseModel):
    type: Literal["last_edited_by"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    last_edited_by: EmptyObject


class LastEditedTimeDatabaseProperty(BaseModel):
    type: Literal["last_edited_time"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    last_edited_time: EmptyObject


class MultiSelectDatabaseProperty(BaseModel):
    type: Literal["multi_select"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    multi_select: SelectDatabaseObject

    def options(self) -> list[SelectObject]:
        return self.multi_select.options


class NumberDatabaseProperty(BaseModel):
    type: Literal["number"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    number: NumberDatabaseObject

    def format(self) -> str:
        return self.number.format


class PeopleDatabaseProperty(BaseModel):
    type: Literal["people"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    people: EmptyObject


class PhoneNumberDatabaseProperty(BaseModel):
    type: Literal["phone_number"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    phone_number: EmptyObject


class RelationDatabaseProperty(BaseModel):
    type: Literal["relation"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    relation: RelationDatabaseObject

    def database_id(self) -> str:
        return self.relation.database_id


class RichTextDatabaseProperty(BaseModel):
    type: Literal["rich_text"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    rich_text: EmptyObject


class RollupDatabaseProperty(BaseModel):
    type: Literal["rollup"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    rollup: RollupDatabaseObject

    def value(self) -> RollupDatabaseObject:
        return self.rollup


class SelectDatabaseProperty(BaseModel):
    type: Literal["select"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    select: SelectDatabaseObject

    def options(self) -> list[SelectObject]:
        return self.select.options


class StatusDatabaseProperty(BaseModel):
    type: Literal["status"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    status: SelectDatabaseObject

    def options(self) -> list[SelectObject]:
        return self.status.options


class TitleDatabaseProperty(BaseModel):
    type: Literal["title"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    title: EmptyObject


class URLDatabaseProperty(BaseModel):
    type: Literal["url"] = Field(repr=False)
    id: str = Field(repr=False)
    name: str
    url: EmptyObject


DatabaseProperty = Annotated[
    Union[
        CheckboxDatabaseProperty,
        CreatedByDatabaseProperty,
        CreatedTimeDatabaseProperty,
        DateDatabaseProperty,
        EmailDatabaseProperty,
        FilesDatabaseProperty,
        FormulaDatabaseProperty,
        LastEditedByDatabaseProperty,
        LastEditedTimeDatabaseProperty,
        MultiSelectDatabaseProperty,
        NumberDatabaseProperty,
        PeopleDatabaseProperty,
        PhoneNumberDatabaseProperty,
        RelationDatabaseProperty,
        RichTextDatabaseProperty,
        RollupDatabaseProperty,
        SelectDatabaseProperty,
        StatusDatabaseProperty,
        TitleDatabaseProperty,
        URLDatabaseProperty,
    ],
    Field(discriminator="type"),
]


# ==============================================================================
# DATABASES
# ==============================================================================


class Database(BaseModel):
    object: Literal["database"] = Field(repr=False)
    id: UUID4
    created_time: datetime
    created_by: PartialUser
    last_edited_time: datetime
    last_edited_by: PartialUser
    title: RichText
    description: RichText
    icon: Icon
    cover: Cover
    properties: dict[str, DatabaseProperty]
    parent: Parent
    url: HttpUrl
    archived: bool
    is_inline: bool
    public_url: HttpUrl | None

    @staticmethod
    def parse(obj) -> Database:
        return TypeAdapter(Database).validate_python(obj)

    def checkbox(self, property_name: str) -> CheckboxDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, CheckboxDatabaseProperty)
        return property

    def created_by_prop(
        self, property_name: str = "Created by"
    ) -> CreatedByDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, CreatedByDatabaseProperty)
        return property

    def created_time_prop(
        self, property_name: str = "Created time"
    ) -> CreatedTimeDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, CreatedTimeDatabaseProperty)
        return property

    def date(self, property_name: str = "Date") -> DateDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, DateDatabaseProperty)
        return property

    def email(self, property_name: str = "Email") -> EmailDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, EmailDatabaseProperty)
        return property

    def files(self, property_name: str = "Files & Media") -> FilesDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, FilesDatabaseProperty)
        return property

    def formula(self, property_name: str) -> FormulaDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, FormulaDatabaseProperty)
        return property

    def last_edited_by_prop(
        self, property_name: str = "Last edited by"
    ) -> LastEditedByDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, LastEditedByDatabaseProperty)
        return property

    def last_edited_time_prop(
        self, property_name: str = "Last edited time"
    ) -> LastEditedTimeDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, LastEditedTimeDatabaseProperty)
        return property

    def multi_select(self, property_name: str) -> MultiSelectDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, MultiSelectDatabaseProperty)
        return property

    def number(self, property_name: str) -> NumberDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, NumberDatabaseProperty)
        return property

    def people(self, property_name: str = "Person") -> PeopleDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, PeopleDatabaseProperty)
        return property

    def phone_number(self, property_name: str = "Phone") -> PhoneNumberDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, PhoneNumberDatabaseProperty)
        return property

    def relation(self, property_name: str) -> RelationDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, RelationDatabaseProperty)
        return property

    def text(self, property_name: str) -> RichTextDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, RichTextDatabaseProperty)
        return property

    def rollup(self, property_name: str) -> RollupDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, RollupDatabaseProperty)
        return property

    def select(self, property_name: str) -> SelectDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, SelectDatabaseProperty)
        return property

    def status(self, property_name: str = "Status") -> StatusDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, StatusDatabaseProperty)
        return property

    def title_prop(self, property_name: str = "Name") -> TitleDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, TitleDatabaseProperty)
        return property

    def url_prop(self, property_name: str = "URL") -> URLDatabaseProperty:
        property = self.properties[property_name]
        assert isinstance(property, URLDatabaseProperty)
        return property


# ==============================================================================
# QUERIES
# ==============================================================================

Result = TypeVar("Result", Page, Block, User)
T = TypeVar("T")


class QueryResult(BaseModel, Generic[Result]):
    object: Literal["list"] = Field(repr=False)
    type: str = Field(repr=False)
    results: list[Result]
    next_cursor: str | None = Field(repr=False)
    has_more: bool = Field(repr=False)
    request_id: str = Field(repr=False)

    @staticmethod
    def parse(obj) -> QueryResult:
        return TypeAdapter(QueryResult).validate_python(obj)

    def count(self) -> int:
        return len(self.results)

    def __len__(self) -> int:
        return self.count()

    def __getitem__(self, idx: int) -> Result:
        return self.results[idx]

    def map(self, f: Callable[[Result], T]) -> dict[UUID4, T]:
        return {result.id: f(result) for result in self.results}

    def inverse_map(self, f: Callable[[Result], T]) -> dict[T, Result]:
        return {f(result): result for result in self.results}

    def by_id(self) -> dict[UUID, Result]:
        return self.inverse_map(lambda x: x.id)

    def by_name(self) -> dict[str, Result]:
        return self.inverse_map(lambda x: x.title().plain_text())  # type: ignore

    def first(self) -> Result:
        assert len(self.results) >= 1
        return self.results[0]


# ==============================================================================
# HELPERS
# ==============================================================================


def _richify(text: str | RichText | None) -> RichText:
    if isinstance(text, RichText):
        return text
    return RichText(
        root=[
            SimpleTextFragmentObject(
                type="simple_text",
                text=TextObject(content=text, link=None),
            )
        ]
        if text is not None
        else []
    )


def _url(url: str) -> ExternalLinkObject:
    return ExternalLinkObject(url=HttpUrl(url=url))


def _children(blocks: list[InnerBlock] | None) -> InnerBlockList:
    return InnerBlockList(root=blocks if blocks is not None else [])


def _default_icon() -> Icon:
    return BlockBuilder.emoji("❤️")


# ==============================================================================
# BLOCK BUILDER
# ==============================================================================

_Text = str | RichText


class BlockBuilder:
    @staticmethod
    def rich(*args: str) -> RichText:
        return RichText(
            root=[
                SimpleTextFragmentObject(text=TextObject(content=arg, link=None))
                for arg in args
            ]
        )

    @staticmethod
    def bookmark(url: str, *, caption: _Text | None = None) -> Bookmark:
        """
        Create a bookmark block.
        """
        return Bookmark(url=HttpUrl(url=url), caption=_richify(caption))

    @staticmethod
    def breadcrumb() -> Breadcrumb:
        """
        Create a breadcrumb block.
        """
        return Breadcrumb()

    @staticmethod
    def bullet(
        text: _Text,
        *,
        color: Color = "default",
        children: list[InnerBlock] | None = None,
    ) -> BulletItem:
        """
        Create a bulleted list item block.
        """
        return BulletItem(
            rich_text=_richify(text), color=color, children=_children(children)
        )

    @staticmethod
    def callout(
        text: _Text,
        *,
        color: Color = "default",
        icon: Icon | None = None,
        children: list[InnerBlock] | None = None,
    ) -> Callout:
        """
        Create a callout block.
        """
        if icon is None:
            icon = _default_icon()
        return Callout(
            rich_text=_richify(text),
            color=color,
            icon=icon,
            children=_children(children),
        )

    @staticmethod
    def code(text: _Text, *, language: str, caption: _Text | None = None) -> Code:
        return Code(
            rich_text=_richify(text),
            caption=_richify(caption),
            language=language,
        )

    @staticmethod
    def column(*, children: list[InnerBlock]) -> Column:
        """
        Create a column.
        """
        return Column(children=_children(children))

    @staticmethod
    def column_list(*, children: list[Column]) -> ColumnList:
        """
        Create a column list.
        """
        return ColumnList(children=_children(children))  # type: ignore

    @staticmethod
    def divider() -> Divider:
        """
        Create a divider.
        """
        return Divider()

    @staticmethod
    def embed(url: str) -> Embed:
        """
        Create an embedded block.
        """
        return Embed(url=HttpUrl(url=url))

    @staticmethod
    def equation(expression: str) -> Equation:
        """
        Create an equation block.
        """
        return Equation(expression=expression)

    @staticmethod
    def file(name: str, *, url: str, caption: _Text | None = None) -> File:
        """
        Create an external file block.
        """
        return File(
            file=ExternalNamedFile(
                name=name,
                external=ExternalLinkObject(url=HttpUrl(url=url)),
                caption=_richify(caption),
            )
        )

    @staticmethod
    def h1(
        text: _Text, *, color: Color = "default", toggleable: bool = False
    ) -> Heading1:
        """
        Create a heading 1 block.
        """
        return Heading1(
            rich_text=_richify(text),
            color=color,
            is_toggleable=toggleable,
        )

    @staticmethod
    def h2(
        text: _Text, *, color: Color = "default", toggleable: bool = False
    ) -> Heading2:
        """
        Create a heading 2 block.
        """
        return Heading2(
            rich_text=_richify(text),
            color=color,
            is_toggleable=toggleable,
        )

    @staticmethod
    def h3(
        text: _Text, *, color: Color = "default", toggleable: bool = False
    ) -> Heading3:
        """
        Create a heading 3 block.
        """
        return Heading3(
            rich_text=_richify(text),
            color=color,
            is_toggleable=toggleable,
        )

    @staticmethod
    def image(url: str, *, caption: _Text | None = None) -> Image:
        """
        Create an embedded image block.
        """
        return Image(
            image=ExternalCaptionedFile(external=_url(url), caption=_richify(caption))
        )

    @staticmethod
    def numbered(
        text: _Text,
        *,
        color: Color = "default",
        children: list[InnerBlock] | None = None,
    ) -> NumberedItem:
        """
        Create a numbered list item block.
        """
        return NumberedItem(
            rich_text=_richify(text), color=color, children=_children(children)
        )

    @staticmethod
    def paragraph(
        text: _Text,
        *,
        color: Color = "default",
        children: list[InnerBlock] | None = None,
    ) -> Paragraph:
        """
        Create a paragraph block.
        """
        return Paragraph(
            rich_text=_richify(text), color=color, children=_children(children)
        )

    @staticmethod
    def pdf(url: str, *, caption: _Text | None = None) -> Pdf:
        """
        Create an embedded PDF block.
        """
        return Pdf(
            pdf=ExternalCaptionedFile(external=_url(url), caption=_richify(caption))
        )

    @staticmethod
    def quote(
        text: _Text,
        *,
        color: Color = "default",
        children: list[InnerBlock] | None = None,
    ) -> Quote:
        """
        Create a quotation block.
        """
        return Quote(
            rich_text=_richify(text), color=color, children=_children(children)
        )

    @staticmethod
    def synced(*, children: list[InnerBlock]) -> Synced:
        """
        Create a synced block.
        """
        return Synced(synced_from=None, children=_children(children))

    @staticmethod
    def table(
        width: int,
        *,
        column_header: bool = False,
        row_header: bool = False,
        children: list[TableRow],
    ) -> Table:
        """
        Create a table block.
        """
        return Table(
            table_width=width,
            has_column_header=column_header,
            has_row_header=row_header,
            children=_children(children),  # type: ignore
        )

    @staticmethod
    def table_row(cells: list[_Text]) -> TableRow:
        """
        Create a table row.
        """
        return TableRow(cells=[_richify(text) for text in cells])

    @staticmethod
    def toc() -> Toc:
        """
        Create a table of contents block.
        """
        return Toc(color="default")

    @staticmethod
    def todo(
        text: _Text,
        *,
        color: Color = "default",
        children: list[InnerBlock] | None = None,
    ) -> TodoItem:
        """
        Create a todo list item block.
        """
        return TodoItem(
            rich_text=_richify(text),
            color=color,
            checked=False,
            children=_children(children),
        )

    @staticmethod
    def toggle(
        text: _Text,
        *,
        color: Color = "default",
        children: list[InnerBlock] | None = None,
    ) -> Toggle:
        """
        Create a toggle block.
        """
        return Toggle(
            rich_text=_richify(text), color=color, children=_children(children)
        )

    @staticmethod
    def video(url: str, *, caption: _Text | None = None) -> Video:
        """
        Create an embedded video block.
        """
        return Video(
            video=ExternalCaptionedFile(external=_url(url), caption=_richify(caption))
        )

    @staticmethod
    def external_file(url: str) -> ExternalUnnamedFile:
        """
        Create an external file object.
        """
        return ExternalUnnamedFile(external=ExternalLinkObject(url=HttpUrl(url=url)))

    @staticmethod
    def emoji(emoji: str) -> Emoji:
        """
        Create an icon object.
        """
        return Emoji(emoji=emoji)
