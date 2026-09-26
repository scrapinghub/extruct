from __future__ import annotations

from collections.abc import Iterator
from copy import copy, deepcopy
from typing import TYPE_CHECKING, Any, cast
from xml.dom import Node
from xml.dom.minidom import Attr, NamedNodeMap

import lxml.etree
from lxml.etree import ElementBase, XPath, _ElementUnicodeResult, tostring
from lxml.html import HtmlElement, HtmlElementClassLookup, HTMLParser

if TYPE_CHECKING:
    from typing import Literal

    from typing_extensions import Self

    _DomHtmlMixinBase = HtmlElement
else:
    _DomHtmlMixinBase = object

# _ElementStringResult is removed in lxml >= 5.1.1.
_ElementStringResult: type[bytes] | None = getattr(
    lxml.etree, "_ElementStringResult", None
)
_TEXT_RESULT_TYPES: tuple[type, ...] = (_ElementUnicodeResult,) + (
    (_ElementStringResult,) if _ElementStringResult else ()
)


class DomElementUnicodeResult:
    CDATA_SECTION_NODE = Node.CDATA_SECTION_NODE
    ELEMENT_NODE = Node.ELEMENT_NODE
    TEXT_NODE = Node.TEXT_NODE

    def __init__(self, text: str) -> None:
        self.text = text
        self.nodeType = Node.TEXT_NODE

    @property
    def data(self) -> str:
        if isinstance(self.text, _ElementUnicodeResult):
            return self.text
        else:
            raise RuntimeError


class DomTextNode:
    CDATA_SECTION_NODE = Node.CDATA_SECTION_NODE
    ELEMENT_NODE = Node.ELEMENT_NODE
    TEXT_NODE = Node.TEXT_NODE

    def __init__(self, text: str) -> None:
        self.data = text
        self.nodeType = Node.TEXT_NODE


def lxmlDomNodeType(node: object) -> int:
    if isinstance(node, ElementBase):
        return Node.ELEMENT_NODE

    elif isinstance(node, _TEXT_RESULT_TYPES):
        if node.is_attribute:  # type: ignore[attr-defined]
            return Node.ATTRIBUTE_NODE
        else:
            return Node.TEXT_NODE
    else:
        return Node.NOTATION_NODE


class DomHtmlMixin(_DomHtmlMixinBase):
    CDATA_SECTION_NODE = Node.CDATA_SECTION_NODE
    ELEMENT_NODE = Node.ELEMENT_NODE
    TEXT_NODE = Node.TEXT_NODE

    _xp_childrennodes = XPath("child::node()")

    @property
    def documentElement(self) -> HtmlElement:
        return self.getroottree().getroot()

    @property
    def nodeType(self) -> int:
        return Node.ELEMENT_NODE

    @property
    def nodeName(self) -> str:
        # FIXME: this is a simplification
        return cast(str, self.tag)

    @property
    def tagName(self) -> str:
        return cast(str, self.tag)

    @property
    def localName(self) -> str:
        return cast(str, self.xpath("local-name(.)"))

    def hasAttribute(self, name: str) -> bool:
        return name in self.attrib

    def getAttribute(self, name: str) -> str | None:
        return self.get(name)

    def setAttribute(self, name: str, value: str) -> None:
        self.set(name, value)

    def cloneNode(self, deep: bool) -> Self:
        return deepcopy(self) if deep else copy(self)

    @property
    def attributes(self) -> NamedNodeMap:
        attrs = {}
        for name, value in self.attrib.items():
            a = Attr(name)
            a.value = value
            attrs[name] = a
        return NamedNodeMap(attrs, {}, self)  # type: ignore[arg-type]

    @property
    def parentNode(self) -> HtmlElement | None:
        return self.getparent()

    @property
    def childNodes_xpath(self) -> Iterator[Any]:
        for n in cast("list[Any]", self._xp_childrennodes(self)):

            if isinstance(n, ElementBase):
                yield n

            elif isinstance(n, _TEXT_RESULT_TYPES):

                if isinstance(n, _ElementUnicodeResult):
                    n = DomElementUnicodeResult(n)
                else:
                    n.nodeType = Node.TEXT_NODE  # type: ignore[attr-defined]
                    n.data = n  # type: ignore[attr-defined]
                yield n

    @property
    def childNodes(self) -> Iterator[HtmlElement | DomTextNode]:
        if self.text:
            yield DomTextNode(self.text)
        for n in self.iterchildren():
            yield n
            if n.tail:
                yield DomTextNode(n.tail)

    def getElementsByTagName(self, name: str) -> Iterator[HtmlElement]:
        return self.iterdescendants(name)

    def getElementById(self, i: str) -> HtmlElement:
        return self.get_element_by_id(i)

    @property
    def data(self) -> str:
        if isinstance(self, _TEXT_RESULT_TYPES):
            return cast(str, self)
        else:
            raise RuntimeError

    def toxml(self, encoding: str | None = None) -> str | bytes:
        return tostring(self, encoding=encoding if encoding is not None else "unicode")


class DomHtmlElementClassLookup(HtmlElementClassLookup):
    def __init__(self) -> None:
        super().__init__()
        self._lookups: dict[tuple[Any, ...], type[HtmlElement]] = {}

    def lookup(
        self,
        node_type: Literal["element", "comment", "PI", "entity"] | None,
        document: object,
        namespace: object,
        name: str,  # type: ignore[override]
    ) -> type[HtmlElement] | None:
        k = (node_type, document, namespace, name)
        t = self._lookups.get(k)
        if t is None:
            cur = super().lookup(node_type, document, namespace, name)
            if cur is None:
                return None
            newtype = cast(
                "type[HtmlElement]",
                type("Dom" + cur.__name__, (cur, DomHtmlMixin), {}),
            )
            self._lookups[k] = newtype
            return newtype
        else:
            return t


class XmlDomHTMLParser(HTMLParser):
    """An HTML parser that is configured to return XmlDomHtmlElement
    objects, compatible with xml.dom API
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        parser_lookup = DomHtmlElementClassLookup()
        self.set_element_class_lookup(parser_lookup)
