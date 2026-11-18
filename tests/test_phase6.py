from ingestion.reconcile import compare, expected_rows_from_audit


def test_latest_uploaded_record_per_key_wins():
    recs = [
        {"source": "users", "s3_key": "k1", "rows": 208, "status": "uploaded"},
        {"source": "users", "s3_key": "k1", "rows": 208, "status": "uploaded"},   # overwrite of same key
        {"source": "users", "s3_key": "k1", "rows": 208, "status": "skipped_duplicate"},
        {"source": "users", "s3_key": "k2", "rows": 10, "status": "failed"},
        {"source": "products", "s3_key": "k3", "rows": 194, "status": "uploaded"},
    ]
    assert expected_rows_from_audit(recs) == {"users": 208, "products": 194}


def test_compare_pass_fail_and_none():
    assert compare("c", "a", 5, "b", 5)["status"] == "PASS"
    assert compare("c", "a", 5, "b", 6)["status"] == "FAIL"
    assert compare("c", "a", None, "b", 6)["status"] == "FAIL"


def test_s3_prefix_override(tmp_path, monkeypatch):
    import boto3
    from moto import mock_aws
    from ingestion import upload_to_s3 as u
    monkeypatch.setattr(u, "AUDIT_LOG", tmp_path / "log.jsonl")
    f = tmp_path / "x.gz"; f.write_bytes(b"abc")
    monkeypatch.setenv("S3_PREFIX", "archive/drill")
    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-west-2")
        s3.create_bucket(Bucket="test-bucket-2", CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
        rec = u.upload(s3, "test-bucket-2", "users", f, 1)
    assert rec["s3_key"].startswith("archive/drill/users/")


def test_same_content_different_source_is_not_skipped(tmp_path, monkeypatch):
    import boto3
    from moto import mock_aws
    from ingestion import upload_to_s3 as u
    monkeypatch.setattr(u, "AUDIT_LOG", tmp_path / "log.jsonl")
    f = tmp_path / "x.gz"; f.write_bytes(b"abc")
    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-west-2")
        s3.create_bucket(Bucket="test-bucket-3", CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
        a = u.upload(s3, "test-bucket-3", "carts", f, 1)
        b = u.upload(s3, "test-bucket-3", "users", f, 1)
        c = u.upload(s3, "test-bucket-3", "users", f, 1)
    assert (a["status"], b["status"], c["status"]) == ("uploaded", "uploaded", "skipped_duplicate")
