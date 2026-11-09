"""Event envelope published on the message bus. Every service reads and writes this format."""
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


def to_camel(name: str) -> str:
    head, *rest = name.split("_")
    return head + "".join(p.title() for p in rest)


class EventType(str, Enum):
    STOCK_RESERVED = "stock.reserved"
    STOCK_RELEASED = "stock.released"
    STOCK_LOW = "stock.low"


class OrderEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str
    payload: Dict[str, Any] = {}

    @validator("occurred_at")
    def must_be_aware(cls, v):
        if v.tzinfo is None:
            raise ValueError("occurred_at must include a timezone")
        return v

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        use_enum_values = True
        json_encoders = {Decimal: str, datetime: lambda d: d.isoformat()}

    def to_message(self) -> bytes:
        """camelCase JSON, as consumers expect."""
        return self.json(by_alias=True).encode()


def parse_event(raw: bytes) -> OrderEvent:
    return OrderEvent.parse_raw(raw)
