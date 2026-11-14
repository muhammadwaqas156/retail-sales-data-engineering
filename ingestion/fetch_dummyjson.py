"""Fetch DummyJSON products, carts and users and save each response as JSON.

DummyJSON is synthetic demo data - not Tesco or any real retailer.
Usage: python -m ingestion.fetch_dummyjson
"""
import hashlib
import json
import logging
from datetime import datetime, timezone

import requests

from src.config import DUMMYJSON_BASE_URL, RAW_DIR

log = logging.getLogger(__name__)
ENDPOINTS = {"products": "products", "carts": "carts", "users": "users"}
LIST_KEYS = {"products": "products", "carts": "carts", "users": "users"}


def fetch_all(name: str, session: requests.Session) -> dict:
    """Page through an endpoint (limit/skip) so we don't rely on limit=0 behaviour."""
    url = f"{DUMMYJSON_BASE_URL}/{ENDPOINTS[name]}"
    key, items, skip, total = LIST_KEYS[name], [], 0, None
    while total is None or skip < total:
        r = session.get(url, params={"limit": 100, "skip": skip}, timeout=30)
        r.raise_for_status()
        page = r.json()
        total = page["total"]
        if not page[key]:
            break
        items.extend(page[key])
        skip += len(page[key])
    return {"total": total, key: items}


def save(name: str, payload: dict) -> dict:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = RAW_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}_{stamp}.json"
    body = json.dumps(payload, indent=2).encode()
    path.write_bytes(body)
    rec = {"source": name, "file": str(path), "rows": len(payload[LIST_KEYS[name]]),
           "sha256": hashlib.sha256(body).hexdigest()}
    log.info("saved %s", rec)
    return rec


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    with requests.Session() as s:
        for name in ENDPOINTS:
            save(name, fetch_all(name, s))


if __name__ == "__main__":
    main()
