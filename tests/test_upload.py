import gzip
import json

import boto3
from moto import mock_aws

from ingestion import upload_to_s3 as u


def test_users_sanitised_and_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(u, "RAW_DIR", tmp_path / "raw")
    monkeypatch.setattr(u, "STAGE_DIR", tmp_path / "staged")
    monkeypatch.setattr(u, "AUDIT_LOG", tmp_path / "audit" / "log.jsonl")
    d = tmp_path / "raw" / "users"
    d.mkdir(parents=True)
    (d / "users_20260101T000000Z.json").write_text(
        json.dumps({"total": 1, "users": [{"id": 1, "firstName": "A", "password": "x", "ssn": "1"}]}))
    path, rows = u.prepare_api("users")
    with gzip.open(path, "rt") as f:
        rec = json.loads(f.readline())
    assert rec == {"id": 1, "firstName": "A"} and rows == 1

    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-west-2")
        s3.create_bucket(Bucket="test-bucket-1", CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
        r1 = u.upload(s3, "test-bucket-1", "users", path, rows)
        r2 = u.upload(s3, "test-bucket-1", "users", path, rows)
        assert r1["status"] == "uploaded" and r2["status"] == "skipped_duplicate"
        assert s3.head_object(Bucket="test-bucket-1", Key=r1["s3_key"])["Metadata"]["sha256"] == r1["sha256"]


def test_prepared_files_are_deterministic(tmp_path, monkeypatch):
    import time
    import pandas as pd
    monkeypatch.setattr(u, "RAW_DIR", tmp_path / "raw")
    monkeypatch.setattr(u, "STAGE_DIR", tmp_path / "staged")
    d = tmp_path / "raw" / "carts"
    d.mkdir(parents=True)
    (d / "carts_1.json").write_text(json.dumps({"total": 1, "carts": [{"id": 1}]}))
    p1, _ = u.prepare_api("carts"); h1 = u.sha256_file(p1)
    x = tmp_path / "raw" / "o.xlsx"
    pd.DataFrame({"Invoice": ["1"], "Customer ID": ["2"]}).to_excel(x, index=False)
    t1, _ = u.prepare_transactions(x); g1 = u.sha256_file(t1)
    time.sleep(2)
    p2, _ = u.prepare_api("carts"); t2, _ = u.prepare_transactions(x)
    assert u.sha256_file(p2) == h1 and u.sha256_file(t2) == g1