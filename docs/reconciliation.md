# Reconciliation report

Generated 2026-11-18 02:37 UTC by `ingestion/reconcile.py`.

| Check | Left | Right | Status |
|---|---|---|---|
| S3 audit vs Bronze (transactions) | s3_audit=1067371 | bronze=1067371 | **PASS** |
| Bronze load audit vs Bronze (transactions) | load_audit=1067371 | bronze=1067371 | **PASS** |
| S3 audit vs Bronze (products) | s3_audit=194 | bronze=194 | **PASS** |
| Bronze load audit vs Bronze (products) | load_audit=194 | bronze=194 | **PASS** |
| S3 audit vs Bronze (carts) | s3_audit=208 | bronze=208 | **PASS** |
| Bronze load audit vs Bronze (carts) | load_audit=208 | bronze=208 | **PASS** |
| S3 audit vs Bronze (users) | s3_audit=208 | bronze=208 | **PASS** |
| Bronze load audit vs Bronze (users) | load_audit=208 | bronze=208 | **PASS** |
| Gold fact vs Bronze minus exact duplicates | fact_sales=1033036 | bronze-34335 dups=1033036 | **PASS** |
| Duplicate lines in Gold | dup_line_ids=0 | expected=0 | **PASS** |
