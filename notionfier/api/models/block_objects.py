import dataclasses
from typing import Any, Dict, List, Optional

from notionfier.api.models.common_objects import ExternalFile, RichText, TextColor
from notionfier.api.models.consts import CodeLanguage


@dataclasses.dataclass
class BlockObject:
    pass


@dataclasses.dataclass
class Paragraph(BlockObject):
    @dataclasses.dataclass
    class Content:
        rich_text: List[RichText]
        children: Optional[List["BlockObject"]] = None
        color: TextColor = TextColor.default

    paragraph: Content


@dataclasses.dataclass
class Heading1(BlockObject):
    @dataclasses.dataclass
    class Content:
        rich_text: List[RichText]
        color: TextColor = TextColor.default

    heading_1: Content


@dataclasses.dataclass
class Heading2(BlockObject):
    @dataclasses.dataclass
    class Content:
        rich_text: List[RichText]
        color: TextColor = TextColor.default

    heading_2: Content


@dataclasses.dataclass
class Heading3(BlockObject):
    @dataclasses.dataclass
    class Content:
        rich_text: List[RichText]
        color: TextColor = TextColor.default

    heading_3: Content


# todo: Callout blocks


@dataclasses.dataclass
class Quote(BlockObject):
    @dataclasses.dataclass
    class Content:
        rich_text: List[RichText]
        color: TextColor = TextColor.default
        children: Optional[List["BlockObject"]] = None

    quote: Content


@dataclasses.dataclass
class BulletedListItem(BlockObject):
    @dataclasses.dataclass
    class Content:
        rich_text: List[RichText]
        children: Optional[List["BlockObject"]] = None
        color: TextColor = TextColor.default

    bulleted_list_item: Content


@dataclasses.dataclass
class NumberedListItem(BlockObject):
    @dataclasses.dataclass
    class Content:
        rich_text: List[RichText]
        children: Optional[List["BlockObject"]] = None
        color: TextColor = TextColor.default

    numbered_list_item: Content


@dataclasses.dataclass
class Code(BlockObject):
    @dataclasses.dataclass
    class Content:
        rich_text: List[RichText]
        caption: Optional[List[RichText]] = None
        language: CodeLanguage = CodeLanguage.plain_text

    code: Content


@dataclasses.dataclass
class Image(BlockObject):
    @dataclasses.dataclass
    class Content:
        external: ExternalFile

    image: Content


@dataclasses.dataclass
class Equation(BlockObject):
    @dataclasses.dataclass
    class Content:
        expression: str

    equation: Content


@dataclasses.dataclass
class Divider(BlockObject):
    divider: Dict[str, Any] = dataclasses.field(default_factory=lambda: {})
