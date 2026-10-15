from typing import Any
from xml.dom import Node

import pytest

from extruct.utils import parse_xmldom_html
from extruct.xmldom import (
    DomElementUnicodeResult,
    DomHtmlElementClassLookup,
    lxmlDomNodeType,
)


def test_dom_api() -> None:
    doc: Any = parse_xmldom_html(
        '<html><body><p id="a" class="c">x<b>y</b>z</p><i><!--c--></i></body></html>',
        "UTF-8",
    )
    p = doc.getElementById("a")
    assert (p.tagName, p.localName) == ("p", "p")
    assert p.parentNode.tag == "body"
    assert [n.tag for n in doc.getElementsByTagName("b")] == ["b"]
    p.setAttribute("title", "t")
    assert p.getAttribute("title") == "t"
    assert p.hasAttribute("class")
    assert p.attributes["class"].value == "c"
    assert p.cloneNode(True).toxml() == p.toxml()
    assert p.toxml(encoding="utf-8").startswith(b"<p")

    assert [
        (n.nodeType, n.data if n.nodeType == Node.TEXT_NODE else n.tag)
        for n in p.childNodes
    ] == [
        (Node.TEXT_NODE, "x"),
        (Node.ELEMENT_NODE, "b"),
        (Node.TEXT_NODE, "z"),
    ]

    children = list(p.childNodes_xpath)
    assert [lxmlDomNodeType(n) for n in children[1:2]] == [Node.ELEMENT_NODE]
    assert [children[0].data, children[2].data] == ["x", "z"]
    assert lxmlDomNodeType(p.xpath("@id")[0]) == Node.ATTRIBUTE_NODE
    assert lxmlDomNodeType(p.xpath("text()")[0]) == Node.TEXT_NODE
    assert lxmlDomNodeType(None) == Node.NOTATION_NODE
    assert list(doc.xpath("//i")[0].childNodes_xpath) == []

    with pytest.raises(RuntimeError):
        p.data
    with pytest.raises(RuntimeError):
        DomElementUnicodeResult("x").data


def test_lookup_unknown_node_type() -> None:
    assert DomHtmlElementClassLookup().lookup(None, None, None, "p") is None
