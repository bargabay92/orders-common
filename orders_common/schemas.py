"""Base schemas shared by services."""
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, root_validator, validator
from pydantic.generics import GenericModel

from orders_common.types import CountryCode

T = TypeVar("T")


class ORMModel(BaseModel):
    """Base for API schemas that are read from SQLAlchemy objects (`Schema.from_orm(row)`)."""

    class Config:
        orm_mode = True
        anystr_strip_whitespace = True
        allow_population_by_field_name = True


class Address(BaseModel):
    line1: str = Field(..., min_length=1, max_length=120)
    line2: Optional[str] = None
    city: str
    postcode: str
    country: CountryCode

    @validator("postcode")
    def postcode_upper(cls, v):
        return v.replace(" ", "").upper()

    @root_validator
    def uk_postcode_length(cls, values):
        if values.get("country") == "GB" and values.get("postcode") and not 5 <= len(values["postcode"]) <= 7:
            raise ValueError("GB postcodes have 5 to 7 characters")
        return values

    class Config:
        anystr_strip_whitespace = True


class Page(GenericModel, Generic[T]):
    """One page of results: `Page[ProductOut]`."""

    items: List[T]
    total: int = Field(..., ge=0)
    offset: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=500)
