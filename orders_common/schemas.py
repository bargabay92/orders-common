"""Base schemas shared by services."""
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from orders_common.types import CountryCode
from typing_extensions import Annotated

T = TypeVar("T")


class ORMModel(BaseModel):
    """Base for API schemas that are read from SQLAlchemy objects (`Schema.from_orm(row)`)."""
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True, populate_by_name=True)


class Address(BaseModel):
    line1: str = Field(..., min_length=1, max_length=120)
    line2: Optional[str] = None
    city: str
    postcode: str
    country: CountryCode

    @field_validator("postcode")
    @classmethod
    def postcode_upper(cls, v):
        return v.replace(" ", "").upper()

    # v1 root_validator (post) -> v2 "after" model validator: runs on the built model, once fields are valid
    @model_validator(mode="after")
    def uk_postcode_length(self):
        if self.country == "GB" and self.postcode and not 5 <= len(self.postcode) <= 7:
            raise ValueError("GB postcodes have 5 to 7 characters")
        return self
    model_config = ConfigDict(str_strip_whitespace=True)


class Page(BaseModel, Generic[T]):
    """One page of results: `Page[ProductOut]`."""

    items: List[T]
    total: Annotated[int, Field(ge=0)]
    offset: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=500)] = 50
