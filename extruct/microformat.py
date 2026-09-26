from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import mf2py


class MicroformatExtractor:
    def extract(
        self,
        htmlstring: str | bytes,
        base_url: str | None = None,
        encoding: str = "UTF-8",
    ) -> list[dict[str, Any]]:
        return list(self.extract_items(htmlstring, base_url=base_url))

    def extract_items(
        self, html: str | bytes, base_url: str | None = None
    ) -> Iterator[dict[str, Any]]:
        yield from mf2py.parse(html, html_parser="lxml", url=base_url)["items"]
