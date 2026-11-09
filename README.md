# orders-common

Shared library for the orders platform (Pydantic v1). Published to the internal package index as
`orders-common`; services pin it in their `requirements.txt`.

- `orders_common.types`: custom field types (`Money`, `Sku`, `CountryCode`)
- `orders_common.schemas`: `ORMModel` base (reads SQLAlchemy objects via `orm_mode`), `Address`, `Page`
- `orders_common.events`: `OrderEvent` envelope serialized to JSON for the message bus

Because services subclass `ORMModel` and embed these types in their own models, this library and every
service that uses it must move to Pydantic v2 together: a v1 model cannot be a field of a v2 model.

```bash
pip install -r requirements-dev.txt && pytest -q
```
