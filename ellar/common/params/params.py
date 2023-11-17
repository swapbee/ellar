import typing as t
from enum import Enum

from pydantic.v1.fields import FieldInfo, ModelField, Undefined

from ..constants import MULTI_RESOLVER_FORM_GROUPED_KEY, MULTI_RESOLVER_KEY
from .resolvers import (
    BaseRouteParameterResolver,
    BodyParameterResolver,
    BulkBodyParameterResolver,
    BulkFormParameterResolver,
    BulkParameterResolver,
    CookieParameterResolver,
    FileParameterResolver,
    FormParameterResolver,
    HeaderParameterResolver,
    PathParameterResolver,
    QueryParameterResolver,
    WsBodyParameterResolver,
)


class ParamTypes(Enum):
    query = "query"
    header = "header"
    path = "path"
    cookie = "cookie"
    body = "body"


class ParamFieldInfo(FieldInfo):
    in_: ParamTypes = ParamTypes.query
    resolver: t.Type[BaseRouteParameterResolver] = QueryParameterResolver
    bulk_resolver: t.Type[BulkParameterResolver] = BulkParameterResolver

    def __init__(
        self,
        default: t.Any = ...,
        *,
        alias: t.Optional[str] = None,
        title: t.Optional[str] = None,
        description: t.Optional[str] = None,
        gt: t.Optional[float] = None,
        ge: t.Optional[float] = None,
        lt: t.Optional[float] = None,
        le: t.Optional[float] = None,
        min_length: t.Optional[int] = None,
        max_length: t.Optional[int] = None,
        regex: t.Optional[str] = None,
        example: t.Any = Undefined,
        examples: t.Optional[t.Dict[str, t.Any]] = None,
        deprecated: t.Optional[bool] = None,
        include_in_schema: bool = True,
        **extra: t.Any,
    ) -> None:
        self.deprecated = deprecated
        self.example = example
        self.examples = examples
        super().__init__(
            default,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            include_in_schema=include_in_schema,
            regex=regex,
            **extra,
        )

    def create_resolver(self, model_field: ModelField) -> BaseRouteParameterResolver:
        multiple_resolvers = model_field.field_info.extra.get(MULTI_RESOLVER_KEY)
        if multiple_resolvers:
            model_field.field_info.extra.clear()
            return self.bulk_resolver(
                model_field=model_field, resolvers=multiple_resolvers
            )
        return self.resolver(model_field)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.default})"


class PathFieldInfo(ParamFieldInfo):
    in_ = ParamTypes.path
    resolver: t.Type[BaseRouteParameterResolver] = PathParameterResolver

    def __init__(
        self,
        default: t.Any = ...,
        *,
        alias: t.Optional[str] = None,
        title: t.Optional[str] = None,
        description: t.Optional[str] = None,
        gt: t.Optional[float] = None,
        ge: t.Optional[float] = None,
        lt: t.Optional[float] = None,
        le: t.Optional[float] = None,
        min_length: t.Optional[int] = None,
        max_length: t.Optional[int] = None,
        regex: t.Optional[str] = None,
        example: t.Any = Undefined,
        examples: t.Optional[t.Dict[str, t.Any]] = None,
        deprecated: t.Optional[bool] = None,
        include_in_schema: bool = True,
        **extra: t.Any,
    ) -> None:
        super().__init__(
            ...,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            example=example,
            examples=examples,
            **extra,
        )


class QueryFieldInfo(ParamFieldInfo):
    in_ = ParamTypes.query
    resolver: t.Type[BaseRouteParameterResolver] = QueryParameterResolver


class HeaderFieldInfo(ParamFieldInfo):
    in_ = ParamTypes.header
    resolver: t.Type[BaseRouteParameterResolver] = HeaderParameterResolver

    def __init__(
        self,
        default: t.Any,
        *,
        alias: t.Optional[str] = None,
        convert_underscores: bool = True,
        title: t.Optional[str] = None,
        description: t.Optional[str] = None,
        gt: t.Optional[float] = None,
        ge: t.Optional[float] = None,
        lt: t.Optional[float] = None,
        le: t.Optional[float] = None,
        min_length: t.Optional[int] = None,
        max_length: t.Optional[int] = None,
        regex: t.Optional[str] = None,
        example: t.Any = Undefined,
        examples: t.Optional[t.Dict[str, t.Any]] = None,
        deprecated: t.Optional[bool] = None,
        include_in_schema: bool = True,
        **extra: t.Any,
    ):
        self.convert_underscores = convert_underscores
        super().__init__(
            default,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            example=example,
            examples=examples,
            **extra,
        )


class CookieFieldInfo(ParamFieldInfo):
    in_ = ParamTypes.cookie
    resolver: t.Type[BaseRouteParameterResolver] = CookieParameterResolver


class BodyFieldInfo(ParamFieldInfo):
    in_ = ParamTypes.body
    MEDIA_TYPE: str = "application/json"
    resolver: t.Type[BaseRouteParameterResolver] = BodyParameterResolver
    bulk_resolver: t.Type[BulkParameterResolver] = BulkBodyParameterResolver

    def __init__(
        self,
        default: t.Any = ...,
        *,
        embed: bool = False,
        media_type: t.Optional[str] = None,
        alias: t.Optional[str] = None,
        title: t.Optional[str] = None,
        description: t.Optional[str] = None,
        gt: t.Optional[float] = None,
        ge: t.Optional[float] = None,
        lt: t.Optional[float] = None,
        le: t.Optional[float] = None,
        min_length: t.Optional[int] = None,
        max_length: t.Optional[int] = None,
        regex: t.Optional[str] = None,
        example: t.Any = Undefined,
        examples: t.Optional[t.Dict[str, t.Any]] = None,
        include_in_schema: bool = True,
        **extra: t.Any,
    ) -> None:
        self.embed = embed
        self.media_type = media_type or self.MEDIA_TYPE

        super().__init__(
            default,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            examples=examples,
            include_in_schema=include_in_schema,
            example=example,
            **extra,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.default})"


class WsBodyFieldInfo(BodyFieldInfo):
    resolver: t.Type[BaseRouteParameterResolver] = WsBodyParameterResolver


class FormFieldInfo(ParamFieldInfo):
    in_ = ParamTypes.body
    resolver: t.Type[BaseRouteParameterResolver] = FormParameterResolver
    MEDIA_TYPE: str = "application/form-data"
    bulk_resolver: t.Type[BulkParameterResolver] = BulkFormParameterResolver

    def __init__(
        self,
        default: t.Any,
        *,
        media_type: t.Optional[str] = None,
        alias: t.Optional[str] = None,
        title: t.Optional[str] = None,
        description: t.Optional[str] = None,
        gt: t.Optional[float] = None,
        ge: t.Optional[float] = None,
        lt: t.Optional[float] = None,
        le: t.Optional[float] = None,
        min_length: t.Optional[int] = None,
        max_length: t.Optional[int] = None,
        regex: t.Optional[str] = None,
        example: t.Any = Undefined,
        examples: t.Optional[t.Dict[str, t.Any]] = None,
        include_in_schema: bool = True,
        **extra: t.Any,
    ):
        super().__init__(
            default,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            example=example,
            examples=examples,
            include_in_schema=include_in_schema,
            **extra,
        )
        self.embed = True
        self.media_type = media_type or self.MEDIA_TYPE

    def create_resolver(self, model_field: ModelField) -> BaseRouteParameterResolver:
        model_field.field_info.extra.setdefault(MULTI_RESOLVER_KEY, [])
        model_field.field_info.extra.setdefault(MULTI_RESOLVER_FORM_GROUPED_KEY, False)

        multiple_resolvers = model_field.field_info.extra.pop(MULTI_RESOLVER_KEY)
        is_grouped = model_field.field_info.extra.pop(MULTI_RESOLVER_FORM_GROUPED_KEY)

        if multiple_resolvers:
            return self.bulk_resolver(
                model_field=model_field,
                resolvers=multiple_resolvers,
                is_grouped=is_grouped,
            )
        return self.resolver(model_field)


class FileFieldInfo(FormFieldInfo):
    resolver: t.Type[BaseRouteParameterResolver] = FileParameterResolver
    MEDIA_TYPE: str = "multipart/form-data"
