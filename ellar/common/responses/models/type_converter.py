import typing as t
from dataclasses import is_dataclass

from ellar.common.constants import primitive_types
from ellar.common.converters import TypeDefinitionConverter
from ellar.common.serializer import (
    BaseSerializer,
    DataclassSerializer,
    Serializer,
    SerializerBase,
    convert_dataclass_to_pydantic_model,
)
from pydantic.v1 import BaseModel


class ResponseTypeDefinitionConverter(TypeDefinitionConverter):
    _registry: t.Dict[t.Any, t.Type[BaseSerializer]] = {}

    def _get_modified_type(
        self, outer_type_: t.Type
    ) -> t.Union[t.Type[BaseSerializer], t.Any]:
        if not isinstance(outer_type_, type):
            raise Exception(f"{outer_type_} is not a type")

        if issubclass(outer_type_, DataclassSerializer):
            schema_model = outer_type_.get_pydantic_model()
            cls = type(outer_type_.__name__, (schema_model, SerializerBase), {})
            return t.cast(t.Type[BaseSerializer], cls)

        if isinstance(outer_type_, type) and issubclass(outer_type_, (BaseSerializer,)):
            return outer_type_

        if issubclass(outer_type_, BaseModel):
            cls = type(outer_type_.__name__, (outer_type_, Serializer), {})
            return t.cast(t.Type[BaseSerializer], cls)

        if is_dataclass(outer_type_):
            if hasattr(outer_type_, "__pydantic_model__"):
                schema_model = outer_type_.__pydantic_model__
                return self._get_modified_type(t.cast(type, schema_model))
            return self._get_modified_type(
                t.cast(type, convert_dataclass_to_pydantic_model(outer_type_))
            )

        if outer_type_ in primitive_types:
            return outer_type_

        attrs = {"__annotations__": getattr(outer_type_, "__annotations__", ())}
        cls = type(outer_type_.__name__, (outer_type_, Serializer), attrs)

        return t.cast(t.Type[BaseSerializer], cls)

    def get_modified_type(self, outer_type_: t.Type) -> t.Type[BaseSerializer]:
        if outer_type_ not in self._registry:
            self._registry[outer_type_] = self._get_modified_type(outer_type_)
        return self._registry[outer_type_]
