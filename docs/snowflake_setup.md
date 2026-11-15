# Snowflake setup (Phase 3)

Keep real account IDs, role ARNs and external IDs out of Git. The SQL files use placeholders; edit a local copy or paste into Snowsight.

## 1. Snowflake objects
Run `sql/01_setup.sql` in a Snowsight worksheet (as ACCOUNTADMIN).

## A. AWS: IAM policy + role for Snowflake
1. IAM -> Policies -> Create policy (JSON), name `snowflake-s3-read`:
```json
{"Version":"2012-10-17","Statement":[
 {"Effect":"Allow","Action":["s3:GetObject","s3:GetObjectVersion"],"Resource":"arn:aws:s3:::YOUR-BUCKET/raw/*"},
 {"Effect":"Allow","Action":"s3:GetBucketLocation","Resource":"arn:aws:s3:::YOUR-BUCKET"},
 {"Effect":"Allow","Action":"s3:ListBucket","Resource":"arn:aws:s3:::YOUR-BUCKET",
  "Condition":{"StringLike":{"s3:prefix":["raw/*"]}}}]}
```
2. IAM -> Roles -> Create role -> Trusted entity: AWS account -> This account -> tick "Require external ID", enter `0000` (temporary). Attach `snowflake-s3-read`. Name it `snowflake-s3-role`. Copy its ARN.

## 2. Create the integration
Edit placeholders in `sql/02_storage_integration.sql`, run it, and note `STORAGE_AWS_IAM_USER_ARN` and `STORAGE_AWS_EXTERNAL_ID` from the DESC output.

## B. AWS: finish the trust policy
IAM -> Roles -> snowflake-s3-role -> Trust relationships -> Edit:
```json
{"Version":"2012-10-17","Statement":[{"Effect":"Allow",
 "Principal":{"AWS":"<STORAGE_AWS_IAM_USER_ARN>"},"Action":"sts:AssumeRole",
 "Condition":{"StringEquals":{"sts:ExternalId":"<STORAGE_AWS_EXTERNAL_ID>"}}}]}
```

## 3. Stage, tables, load
Run `sql/03_stage_and_bronze_tables.sql` (`LIST @STG_RAW` must show your files), then `sql/04_load_bronze.sql`. Run 04 a second time: row counts must not change (idempotent).
