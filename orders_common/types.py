"""Custom field types shared by every service."""
import re
from decimal import Decimal, InvalidOperation

from typing import Any

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, StringConstraints
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing_extensions import Annotated

SKU_RE = re.compile(r"^[A-Z]{3}-\d{4}$")


class Money(Decimal):
    """A non-negative amount with at most 2 decimal places."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls.validate,
            # v1 wrote Decimal values as JSON numbers; keep the same output for every service
            serialization=core_schema.plain_serializer_function_ser_schema(float, when_used="json"),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"type": "string", "pattern": r"^\d+(\.\d{1,2})?$", "examples": ["19.99"]}

    @classmethod
    def validate(cls, value):
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise ValueError("invalid money amount")
        if amount < 0:
            raise ValueError("money must be non-negative")
        if amount.as_tuple().exponent < -2:
            raise ValueError("money has at most 2 decimal places")
        return cls(amount)


class Sku(str):
    """Stock keeping unit like ABC-1234 (normalised to upper case)."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"type": "string", "pattern": SKU_RE.pattern, "examples": ["ABC-1234"]}

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            raise ValueError("sku must be a string")
        value = value.strip().upper()
        if not SKU_RE.match(value):
            raise ValueError("sku must look like ABC-1234")
        return cls(value)


# ISO 3166-1 alpha-2 country code, upper case. v1's ConstrainedStr subclass becomes an Annotated type.
CountryCode = Annotated[str, StringConstraints(min_length=2, max_length=2, to_upper=True, pattern=r"^[A-Za-z]{2}$")]
