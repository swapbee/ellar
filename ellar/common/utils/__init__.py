import asyncio
import functools
import inspect
import re
import typing as t
import uuid

class_base_function_regex: t.Pattern[t.Any] = re.compile(
    "<\\w+ ((\\w+\\.(<\\w+>)\\.)+)?(\\w+)\\.(\\w+) at \\w+>", re.IGNORECASE
)


def generate_operation_unique_id(
    *, name: str, path: str, methods: t.Sequence[str]
) -> str:
    _methods = "_".join(sorted(methods))
    operation_id = name + path
    operation_id = re.sub("[^0-9a-zA-Z_]", "_", operation_id)
    operation_id = operation_id + "_" + _methods.lower()
    return operation_id


def generate_controller_operation_unique_id(
    *,
    path: str,
    methods: t.Sequence[str],
    versioning: t.Sequence[str],
    extra_string: str = "",
) -> int:
    _methods = "_".join(sorted(methods)).lower()
    _versioning = "_".join(sorted(versioning)).lower()
    return hash(path + _methods + _versioning + extra_string)


def get_unique_control_type() -> t.Type:
    return type(f"{uuid.uuid4().hex:4}_ModuleRouter", (), {})


def get_name(endpoint: t.Union[t.Callable, t.Type, object]) -> str:
    if inspect.isfunction(endpoint) or inspect.isclass(endpoint):
        return endpoint.__name__
    return endpoint.__class__.__name__  # pragma: no cover


def is_async_callable(obj: t.Any) -> bool:
    while isinstance(obj, functools.partial):  # pragma: no cover
        obj = obj.func

    return asyncio.iscoroutinefunction(obj) or (
        callable(obj) and asyncio.iscoroutinefunction(obj.__call__)
    )


def build_init_kwargs(obj: t.Type, init_kwargs: t.Dict) -> t.Dict:
    _result = {}
    if hasattr(obj, "__init__"):
        signature = inspect.signature(obj.__init__)
        for k, v in signature.parameters.items():
            if (
                v.kind == inspect.Parameter.KEYWORD_ONLY
                or v.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            ) and v.default != inspect.Parameter.empty:
                _result[k] = v.default
    _result.update(init_kwargs)
    return _result
