"""Regression tests for the corrected chapter-05 pipelines."""

import sys
from pathlib import Path

import pandas as pd


sys.path.insert(0, str(Path(__file__).parents[1] / "05_inspection"))
import pipelines  # noqa: E402


def test_remote_dependency_step_uses_declared_pandas():
    assert "pandas>=2.2,<4" in pipelines.import_missing_remote_package.configuration.settings["docker"].requirements
    assert pipelines.import_missing_remote_package.entrypoint()


def test_producer_emits_the_consumer_contract():
    data = pipelines.produce_legacy_customer_table.entrypoint()
    assert {"customer_id", "tenure_months", "churned"} <= set(data.columns)
    assert data["churned"].isin([0, 1]).all()
    assert pipelines.validate_customer_contract.entrypoint(data) == len(data)


def test_consumer_still_rejects_incompatible_artifacts():
    broken = pd.DataFrame({"customer_id": [1], "tenure_months": [10]})
    try:
        pipelines.validate_customer_contract.entrypoint(broken)
    except ValueError as exc:
        assert "missing required columns ['churned']" in str(exc)
    else:
        raise AssertionError("the consumer accepted an artifact without churned")
