# AWS setup (Phase 2)

## 1. Bucket (console, region eu-west-2)
S3 → Create bucket → name must be globally unique, e.g. `retail-de-<yourname>-<random digits>`.
- Block ALL public access: on
- Default encryption: SSE-S3: on
- Versioning: enabled (helps failure recovery)
Then create folders: `raw/transactions/`, `raw/products/`, `raw/carts/`, `raw/users/`, `archive/`.

## 2. Least-privilege IAM user
IAM → Policies → Create policy → JSON → paste `docs/iam_policy.json` with YOUR-BUCKET-NAME replaced → name `retail-s3-ingest`.
IAM → Users → Create user `retail-ingest` (no console access) → attach that policy.
Security credentials → Create access key → "Command Line Interface".
Download the key, store it in a password manager, never in the repo.

## 3. Configure locally (WSL)
    sudo apt install -y awscli     # or: pip install awscli
    aws configure --profile retail-ingest     # key, secret, region eu-west-2, output json
Then edit `.env`:
    AWS_PROFILE=retail-ingest
    S3_BUCKET=<your bucket name>
Credentials live in ~/.aws/credentials, outside the repo.

## 4. Run
    pip install -r requirements.txt
    python -m ingestion.upload_to_s3 --dry-run
    python -m ingestion.upload_to_s3
    python -m ingestion.upload_to_s3     # second run: should say skipped_duplicate
Check data/audit/ingestion_log.jsonl and the bucket console.

Later (Snowflake phase) the key is replaced by a Snowflake storage integration with an IAM role; the ingest user keeps write access only.
