from typing import Any, List, Optional, Tuple

import mistune.renderers

from notionfier.api.models.block_objects import (
    BlockObject,
    BulletedListItem,
    Code,
    Divider,
    ExternalFile,
    Heading1,
    Heading2,
    Heading3,
    Image,
    NumberedListItem,
    Paragraph,
    Quote,
)
from notionfier.api.models.common_objects import Annotation, LinkObject, RichText, Text
from notionfier.api.models.consts import CodeLanguage
from notionfier.api.models.utils import NotionObject


def _split_list_of_notion_objects(
    notion_objects: List[NotionObject],
) -> Tuple[List[RichText], List[BlockObject]]:
    rich_texts: List[RichText] = []
    block_objects: List[BlockObject] = []
    for obj in notion_objects:
        if isinstance(obj, RichText):
            rich_texts.append(obj)
        elif isinstance(obj, BlockObject):
            block_objects.append(obj)
    return rich_texts, block_objects


def _process_annotation(text: RichText, key: str, value: Any) -> RichText:
    if text.annotations is None:
        text.annotations = Annotation()
    setattr(text.annotations, key, value)
    return text


class MyRenderer(mistune.renderers.HTMLRenderer):
    def text(self, text: str):
        assert isinstance(text, str)
        return [Text(text=Text.Content(content=text))]

    def link(
        self,
        link: str,
        children_objects: Optional[List[NotionObject]] = None,
        title=None,
    ):
        children_objects = children_objects or []
        text_objects, block_objects = _split_list_of_notion_objects(children_objects)
        assert len(block_objects) == 0
        result = []
        if len(text_objects) > 0:
            for obj in text_objects:
                assert isinstance(obj, Text)  # todo: check this
                result.append(
                    Text(
                        text=Text.Content(content=obj.text.content, link=LinkObject(url=link)),
                        annotations=obj.annotations,
                    )
                )
        else:
            result.append(Text(text=Text.Content(content=link, link=LinkObject(url=link))))
        return result

    def image(self, src, alt="", title: Optional[List[NotionObject]] = None):
        # todo: image caption
        block = Image(
            image=Image.Content(
                external=ExternalFile(url=src), caption=[Text(text=Text.Content(content=alt))]
            )
        )
        return [block]

    def emphasis(self, children_objects: List[NotionObject]):
        text_objects, block_objects = _split_list_of_notion_objects(children_objects)
        assert len(block_objects) == 0
        return [_process_annotation(x, "italic", True) for x in text_objects]

    def strong(self, children_objects: List[NotionObject]):
        text_objects, block_objects = _split_list_of_notion_objects(children_objects)
        assert len(block_objects) == 0
        return [_process_annotation(x, "bold", True) for x in text_objects]

    def codespan(self, code: str):
        return [Text(text=Text.Content(content=code), annotations=Annotation(code=True))]

    def linebreak(self):
        return [Text(text=Text.Content(content="\n"))]

    def inline_html(self, html):
        return [Text(text=Text.Content(content=html))]

    def paragraph(self, children_objects: List[NotionObject]):
        text_objects, block_objects = _split_list_of_notion_objects(children_objects)
        return [
            Paragraph(
                paragraph=Paragraph.Content(rich_text=text_objects, children=block_objects or None)
            )
        ]

    def heading(self, children_objects: List[NotionObject], level: int):
        text_objects, block_objects = _split_list_of_notion_objects(children_objects)
        assert len(block_objects) == 0
        max_level = 2
        if level > max_level:
            level = max_level

        if level == 1:
            return [Heading1(heading_1=Heading1.Content(rich_text=text_objects))]
        else:
            return [Heading2(heading_2=Heading2.Content(rich_text=text_objects))]

    def newline(self):
        return []

    def thematic_break(self):
        return [Divider()]

    def block_text(self, children_objects: List[NotionObject]):
        return children_objects

    def block_code(self, code: str, info: Optional[str] = None):
        block = Code(code=Code.Content(rich_text=[Text(text=Text.Content(content=code))]))
        if info is not None:
            language = info.strip().lower()

            # todo: consider aliases, like js-javascript
            if language in CodeLanguage.__members__:
                block.code.language = CodeLanguage(language)

        return [block]

    def block_quote(self, children_objects: List[NotionObject]):
        text_objects, block_objects = _split_list_of_notion_objects(children_objects)
        assert len(text_objects) == 0

        rich_text = []
        children = []
        if len(block_objects) > 0:
            first_obj = block_objects[0]
            if isinstance(first_obj, Paragraph):
                rich_text = first_obj.paragraph.rich_text
                children = block_objects[1:]
            elif isinstance(first_obj, Heading1):
                rich_text = first_obj.heading_1.rich_text
                children = block_objects[1:]
            elif isinstance(first_obj, Heading2):
                rich_text = first_obj.heading_2.rich_text
                children = block_objects[1:]
            elif isinstance(first_obj, Heading3):
                rich_text = first_obj.heading_3.rich_text
                children = block_objects[1:]
            else:
                children = block_objects
        return [Quote(quote=Quote.Content(rich_text=rich_text, children=children or None))]

    def block_html(self, html: str):
        return [
            Paragraph(
                paragraph=Paragraph.Content(rich_text=[Text(text=Text.Content(content=html))])
            )
        ]

    def block_error(self, html):
        return [
            Paragraph(
                paragraph=Paragraph.Content(rich_text=[Text(text=Text.Content(content=html))])
            )
        ]

    def list(self, children_objects: List[NotionObject], ordered, level, start=None):
        if not ordered:
            return children_objects

        result = []

        for child in children_objects:
            assert isinstance(child, BulletedListItem)
            result.append(
                NumberedListItem(
                    numbered_list_item=NumberedListItem.Content(
                        rich_text=child.bulleted_list_item.rich_text,
                        children=child.bulleted_list_item.children,
                        color=child.bulleted_list_item.color,
                    )
                )
            )
        return result

    def list_item(self, children_objects: List[NotionObject], level):
        text_objects, block_objects = _split_list_of_notion_objects(children_objects)
        if len(text_objects) == 0 and len(block_objects) > 0:
            first_block = block_objects[0]
            if isinstance(first_block, Paragraph):
                text_objects = first_block.paragraph.rich_text
                block_objects = block_objects[1:]
        return [
            BulletedListItem(
                bulleted_list_item=BulletedListItem.Content(
                    rich_text=text_objects, children=block_objects or None
                )
            )
        ]

    def footnote_ref(self, key, index, dup):
        return [Text(text=Text.Content(content=f"[{index}]"))]

    def footnotes(self, children_objects: List[NotionObject]):
        return [Divider()] + children_objects

    def footnote_item(self, children_objects: List[NotionObject], key, index):
        # todo: support multi-paragraph footnotes.
        text_objects, block_objects = _split_list_of_notion_objects(children_objects)
        if len(text_objects) == 0 and len(block_objects) > 0:
            first_block = block_objects[0]
            if isinstance(first_block, Paragraph):
                text_objects = first_block.paragraph.rich_text
                block_objects = block_objects[1:]
        return [
            NumberedListItem(
                numbered_list_item=NumberedListItem.Content(
                    rich_text=text_objects, children=block_objects
                )
            )
        ]

    def strikethrough(self, children_objects: List[NotionObject]):
        text_objects, block_objects = _split_list_of_notion_objects(children_objects)
        assert len(block_objects) == 0
        return [_process_annotation(x, "strikethrough", True) for x in text_objects]

    def finalize(self, data):
        return [item for sublist in data for item in sublist]
