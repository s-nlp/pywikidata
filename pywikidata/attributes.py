from collections.abc import Hashable, Mapping
from typing import ItemsView, Iterator, KeysView, ValuesView
from .config import WIKIDATA_URI
import requests
from requests.compat import urljoin

# https://www.wikidata.org/wiki/Special:EntityData/Q189.json


class _WikidataAttributes(Mapping, Hashable):
    """_WikidataAttributes - Object for storing Wikidata Entities attributes"""

    def __init__(self, idx: str) -> None:
        super().__init__()
        self.idx = idx
        self._attributes = None

    def _load(self):
        r = requests.get(
            urljoin(WIKIDATA_URI, f"/wiki/Special:EntityData/{self.idx}.json"),
        )
        self._attributes = r.json()["entities"][self.idx]

    def __hash__(self) -> int:
        return hash(self.idx)

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            raise TypeError(
                f"expected an instance of {type(self).__module__}.{type(self).__qualname__}, "
                f"not {other!r}"
            )
        return other.idx == self.idx

    def __getitem__(self, key: str) -> object:
        if self._attributes is None:
            self._load()

        return self._attributes.get(key)

    def __iter__(self) -> Iterator:
        if self._attributes is None:
            self._load()

        claims = self._attributes.get("claims") or {}
        for prop_id in claims:
            yield prop_id

    def __len__(self) -> int:
        if self._attributes is None:
            self._load()

        claims = self._attributes.get("claims") or {}
        return len(claims)

    def keys(self) -> KeysView:
        if self._attributes is None:
            self._load()

        return self._attributes.keys()

    def items(self) -> ItemsView:
        if self._attributes is None:
            self._load()

        return self._attributes.items()

    def values(self) -> ValuesView:
        if self._attributes is None:
            self._load()

        return self._attributes.values()
