"""Event envelope published on the message bus. Every service reads and writes this format."""
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict
from uuid import UUID, uuid4

import json

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


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

    @field_validator("occurred_at")
    @classmethod
    def must_be_aware(cls, v):
        if v.tzinfo is None:
            raise ValueError("occurred_at must include a timezone")
        return v

    # v1 used json_encoders. v2 already writes Decimal as a string in JSON; datetimes keep v1's
    # isoformat() ("+00:00", where v2 would write "Z").
    @field_serializer("occurred_at", when_used="json")
    def _occurred_at_iso(self, v: datetime) -> str:
        return v.isoformat()

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, use_enum_values=True)

    def to_message(self) -> bytes:
        """camelCase JSON, as consumers expect (same bytes as v1's .json(): json.dumps spacing)."""
        return json.dumps(self.model_dump(mode="json", by_alias=True)).encode()


def parse_event(raw: bytes) -> OrderEvent:
    return OrderEvent.model_validate_json(raw)
