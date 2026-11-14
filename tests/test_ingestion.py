from unittest.mock import MagicMock

from ingestion.fetch_dummyjson import fetch_all


def _resp(payload):
    m = MagicMock()
    m.json.return_value = payload
    return m


def test_fetch_all_paginates_until_total():
    s = MagicMock()
    s.get.side_effect = [
        _resp({"total": 3, "products": [{"id": 1}, {"id": 2}]}),
        _resp({"total": 3, "products": [{"id": 3}]}),
    ]
    out = fetch_all("products", s)
    assert [p["id"] for p in out["products"]] == [1, 2, 3]
    assert s.get.call_count == 2


def test_fetch_all_stops_on_empty_page():
    s = MagicMock()
    s.get.return_value = _resp({"total": 5, "carts": []})
    assert fetch_all("carts", s)["carts"] == []
