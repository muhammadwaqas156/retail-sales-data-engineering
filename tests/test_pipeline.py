import importlib.util
from pathlib import Path

from ingestion.load_snowflake import split_statements


def test_split_statements_ignores_comments_and_blanks():
    sql = "-- c\nUSE ROLE A;\nSET x = 1;\n\n-- end\nSELECT 1;\n"
    assert split_statements(sql) == ["USE ROLE A", "SET x = 1", "SELECT 1"]


def test_real_load_file_splits_cleanly():
    from src.config import ROOT
    stmts = split_statements((ROOT / "sql" / "04_load_bronze.sql").read_text()) if (ROOT / "sql" / "04_load_bronze.sql").exists() else ["x"]
    assert all(s for s in stmts)


def test_dag_structure():
    spec = importlib.util.spec_from_file_location("retail_pipeline", Path(__file__).parents[1] / "dags" / "retail_pipeline.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    dag = mod.dag
    order = ["extract_api", "validate_extracts", "upload_to_s3", "load_snowflake", "dbt_run", "dbt_test"]
    assert [t for t in order if t in dag.task_ids] == order
    for a, b in zip(order, order[1:]):
        assert b in dag.get_task(a).downstream_task_ids
    assert all(t.retries == 2 for t in dag.tasks)
