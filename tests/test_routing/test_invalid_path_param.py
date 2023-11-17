from typing import Dict, List, Tuple

import pytest
from ellar.common import ModuleRouter
from ellar.core.routing import ModuleRouterFactory
from pydantic.v1 import BaseModel

mr = ModuleRouter("")


def test_invalid_sequence():
    with pytest.raises(AssertionError):

        class Item(BaseModel):
            title: str

        @mr.get("/items/{id}")
        def read_items(id: List[Item]):
            pass  # pragma: no cover

        ModuleRouterFactory.build(mr)


def test_invalid_tuple():
    with pytest.raises(AssertionError):

        class Item(BaseModel):
            title: str

        @mr.get("/items/{id}")
        def read_items(id: Tuple[Item, Item]):
            pass  # pragma: no cover

        ModuleRouterFactory.build(mr)


def test_invalid_dict():
    with pytest.raises(AssertionError):

        class Item(BaseModel):
            title: str

        @mr.get("/items/{id}")
        def read_items(id: Dict[str, Item]):
            pass  # pragma: no cover

        ModuleRouterFactory.build(mr)


def test_invalid_simple_list():
    with pytest.raises(AssertionError):

        @mr.get("/items/{id}")
        def read_items(id: list):
            pass  # pragma: no cover

        ModuleRouterFactory.build(mr)


def test_invalid_simple_tuple():
    with pytest.raises(AssertionError):

        @mr.get("/items/{id}")
        def read_items(id: tuple):
            pass  # pragma: no cover

        ModuleRouterFactory.build(mr)


def test_invalid_simple_set():
    with pytest.raises(AssertionError):

        @mr.get("/items/{id}")
        def read_items(id: set):
            pass  # pragma: no cover

        ModuleRouterFactory.build(mr)


def test_invalid_simple_dict():
    with pytest.raises(AssertionError):

        @mr.get("/items/{id}")
        def read_items(id: dict):
            pass  # pragma: no cover

        ModuleRouterFactory.build(mr)
