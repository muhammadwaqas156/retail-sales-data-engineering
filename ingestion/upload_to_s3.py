"""Prepare local extracts and upload them to S3 with an audit trail.

- UCI workbook -> one gzipped CSV (Snowflake cannot read .xlsx)
- DummyJSON JSON -> gzipped NDJSON, sensitive fake fields removed
- Key layout: <S3_PREFIX, default raw>/<source>/ingest_date=YYYY-MM-DD/<file>
- Idempotent: a file whose sha256 is already in the audit log is skipped
- Audit log: data/audit/ingestion_log.jsonl (one JSON line per file)

Credentials come from the AWS profile/role (AWS_PROFILE), never from code.
Usage: python -m ingestion.upload_to_s3 [--dry-run]
"""
import argparse
import gzip
import hashlib
import io
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import DATA_DIR, RAW_DIR

log = logging.getLogger(__name__)
AUDIT_LOG = DATA_DIR / "audit" / "ingestion_log.jsonl"
STAGE_DIR = DATA_DIR / "staged"
SENSITIVE_USER_FIELDS = {"password", "ssn", "bank", "crypto", "ein", "macAddress", "ip", "userAgent"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def prepare_transactions(xlsx: Path) -> tuple[Path, int]:
    sheets = pd.read_excel(xlsx, sheet_name=None, dtype={"Customer ID": "string"})
    frames = []
    for name, df in sheets.items():
        df = df.copy()
        df["source_sheet"] = name
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    out = STAGE_DIR / "online_retail_II.csv.gz"
    df.to_csv(out, index=False, compression={"method": "gzip", "mtime": 0})  # mtime=0 => deterministic hash
    return out, len(df)


def prepare_api(name: str) -> tuple[Path, int] | None:
    files = sorted((RAW_DIR / name).glob(f"{name}_*.json"))
    if not files:
        return None
    records = json.loads(files[-1].read_text())[name]
    if name == "users":
        records = [{k: v for k, v in r.items() if k not in SENSITIVE_USER_FIELDS} for r in records]
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    out = STAGE_DIR / f"{files[-1].stem}.ndjson.gz"
    with open(out, "wb") as raw, gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as gz, \
            io.TextIOWrapper(gz, encoding="utf-8") as f:  # mtime=0 => deterministic hash
        f.writelines(json.dumps(r) + "\n" for r in records)
    return out, len(records)


def already_uploaded(sha: str, source: str) -> bool:
    if not AUDIT_LOG.exists():
        return False
    for line in AUDIT_LOG.read_text().splitlines():
        rec = json.loads(line)
        if rec.get("sha256") == sha and rec.get("source") == source and rec.get("status") == "uploaded":
            return True
    return False


def write_audit(rec: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def upload(s3, bucket: str, source: str, path: Path, rows: int, dry_run: bool = False) -> dict:
    now = datetime.now(timezone.utc)
    sha = sha256_file(path)
    key = f"{os.getenv('S3_PREFIX', 'raw')}/{source}/ingest_date={now:%Y-%m-%d}/{path.name}"
    rec = {"ts": now.isoformat(), "source": source, "file": path.name, "rows": rows,
           "bytes": path.stat().st_size, "sha256": sha, "s3_key": key}
    if already_uploaded(sha, source):
        rec["status"] = "skipped_duplicate"
    elif dry_run:
        rec["status"] = "dry_run"
    else:
        try:
            s3.upload_file(str(path), bucket, key, ExtraArgs={
                "Metadata": {"sha256": sha, "rows": str(rows)}, "ServerSideEncryption": "AES256"})
            rec["status"] = "uploaded"
        except Exception as exc:  # log failures too, then re-raise for Airflow later
            rec.update(status="failed", error=str(exc))
            write_audit(rec)
            raise
    write_audit(rec)
    log.info("%s", rec)
    return rec


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    bucket = os.environ["S3_BUCKET"]
    import boto3
    s3 = boto3.Session(profile_name=os.getenv("AWS_PROFILE") or None,
                       region_name=os.getenv("AWS_REGION", "eu-west-2")).client("s3")
    xlsx = RAW_DIR / "online_retail_II.xlsx"
    if xlsx.exists():
        p, n = prepare_transactions(xlsx)
        upload(s3, bucket, "transactions", p, n, args.dry_run)
    for name in ("products", "carts", "users"):
        prepared = prepare_api(name)
        if prepared:
            upload(s3, bucket, name, *prepared, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
