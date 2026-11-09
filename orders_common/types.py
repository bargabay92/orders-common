"""Custom field types shared by every service (Pydantic v1 style)."""
import re
from decimal import Decimal, InvalidOperation

from pydantic import ConstrainedStr

SKU_RE = re.compile(r"^[A-Z]{3}-\d{4}$")


class Money(Decimal):
    """A non-negative amount with at most 2 decimal places."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string", pattern=r"^\d+(\.\d{1,2})?$", examples=["19.99"])

    @classmethod
    def validate(cls, value):
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise TypeError("invalid money amount")
        if amount < 0:
            raise ValueError("money must be non-negative")
        if amount.as_tuple().exponent < -2:
            raise ValueError("money has at most 2 decimal places")
        return cls(amount)


class Sku(str):
    """Stock keeping unit like ABC-1234 (normalised to upper case)."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(pattern=SKU_RE.pattern, examples=["ABC-1234"])

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            raise TypeError("sku must be a string")
        value = value.strip().upper()
        if not SKU_RE.match(value):
            raise ValueError("sku must look like ABC-1234")
        return cls(value)


class CountryCode(ConstrainedStr):
    """ISO 3166-1 alpha-2 country code, upper case."""

    min_length = 2
    max_length = 2
    to_upper = True
    regex = re.compile(r"^[A-Za-z]{2}$")
