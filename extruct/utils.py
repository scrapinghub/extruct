# -*- coding: utf-8 -*-
import html5lib


def parse_html(html, encoding):
    return html5lib.parse(html, treebuilder='dom')


def parse_xmldom_html(html, encoding):
    return html5lib.parse(html, treebuilder='dom')
