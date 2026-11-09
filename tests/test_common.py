from decimal import Decimal
from datetime import datetime

import pytest
from pydantic import BaseModel, ValidationError

from orders_common import Address, EventType, Money, ORMModel, OrderEvent, Page, Sku, parse_event


class Item(BaseModel):
    sku: Sku
    price: Money


def test_types_normalise():
    item = Item(sku=" abc-1234 ", price="19.90")
    assert item.sku == "ABC-1234"
    assert item.price == Decimal("19.90")


@pytest.mark.parametrize("bad", [{"sku": "nope", "price": 1}, {"sku": "ABC-1234", "price": "-1"},
                                 {"sku": "ABC-1234", "price": "1.999"}, {"sku": 5, "price": 1}])
def test_types_reject(bad):
    with pytest.raises(ValidationError):
        Item(**bad)


def test_money_schema():
    props = Item.schema()["properties"]
    assert props["price"]["pattern"] == r"^\d+(\.\d{1,2})?$"
    assert props["sku"]["examples"] == ["ABC-1234"]


def test_address_rules():
    a = Address(line1=" 1 High St ", city="London", postcode="sw1a 1aa", country="gb")
    assert (a.line1, a.postcode, a.country) == ("1 High St", "SW1A1AA", "GB")
    with pytest.raises(ValidationError):
        Address(line1="x", city="y", postcode="1", country="GB")
    with pytest.raises(ValidationError):
        Address(line1="x", city="y", postcode="12345", country="GBR")


def test_orm_model_reads_attributes():
    class Row:
        id = 3
        name = " widget "

    class Out(ORMModel):
        id: int
        name: str

    assert Out.from_orm(Row()).dict() == {"id": 3, "name": "widget"}


def test_page_generic():
    page = Page[int](items=[1, 2], total=2)
    assert page.dict() == {"items": [1, 2], "total": 2, "offset": 0, "limit": 50}
    with pytest.raises(ValidationError):
        Page[int](items=["x"], total=1)


def test_event_round_trip():
    e = OrderEvent(event_type=EventType.STOCK_RESERVED, source="inventory", payload={"qty": 2})
    raw = e.to_message()
    assert b'"eventType": "stock.reserved"' in raw and b'"occurredAt"' in raw
    back = parse_event(raw)
    assert back.event_id == e.event_id and back.payload == {"qty": 2}


def test_event_needs_timezone():
    with pytest.raises(ValidationError):
        OrderEvent(event_type="stock.low", source="x", occurred_at=datetime(2026, 1, 1))
