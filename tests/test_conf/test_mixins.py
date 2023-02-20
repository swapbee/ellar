import pytest

from ellar.cache.backends.local_cache import LocalMemCacheBackend
from ellar.core import Config


def test_invalid_cached_backend_config():
    with pytest.raises(ValueError, match="Expected BaseCacheBackend, received:"):
        Config(CACHES={"default": type("whatever", (), {})})


def test_cache_backend_without_default_raise_exception():
    with pytest.raises(
        ValueError, match="CACHES configuration must have a 'default' key"
    ):
        Config(CACHES={"local": LocalMemCacheBackend()})


def test_invalid_exception_handler_config():
    invalid_type = type("whatever", (), {})
    with pytest.raises(ValueError, match="Expected 'ExceptionHandler', received:"):
        Config(EXCEPTION_HANDLERS=[invalid_type])

    with pytest.raises(ValueError, match="Expected 'ExceptionHandler', received:"):
        Config(EXCEPTION_HANDLERS=[invalid_type()])


def test_invalid_versioning_config():
    invalid_type = type("whatever", (), {})
    with pytest.raises(ValueError, match=r"Expected BaseAPIVersioning, received: "):
        Config(VERSIONING_SCHEME=invalid_type())


def test_invalid_middleware_config():
    invalid_type = type("whatever", (), {})
    with pytest.raises(
        ValueError, match=r"Expected Type/instance of Middleware, received: "
    ):
        Config(MIDDLEWARE=[invalid_type()])


def test_invalid_event_handler_config():
    invalid_type = type("whatever", (), {})
    with pytest.raises(ValueError, match=r"Expected EventHandler, received:"):
        Config(ON_REQUEST_STARTUP=[invalid_type()])
