"""Regression tests for the chapter-05 inspection fixes."""

import importlib.util
from pathlib import Path

import pandas as pd


MODULE_PATH = Path(__file__).parents[1] / "05_inspection" / "pipelines.py"


def load_module():
    spec = importlib.util.spec_from_file_location("inspection_pipelines", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_producer_emits_the_contract_columns():
    module = load_module()
    data = module.produce_legacy_customer_table.entrypoint()
    assert {"customer_id", "monthly_spend", "churned"} <= set(data.columns)
    assert data["churned"].isin([0, 1]).all()


def test_consumer_rejects_a_broken_contract():
    module = load_module()
    broken = pd.DataFrame({"customer_id": [1], "monthly_spend": [10.0]})
    try:
        module.validate_customer_contract.entrypoint(broken)
    except ValueError as exc:
        assert "missing required columns ['churned']" in str(exc)
    else:
        raise AssertionError("the consumer accepted an artifact without churned")


def test_dependency_step_uses_declared_dependency():
    module = load_module()
    assert "pandas>=2.2,<4" in module._REMOTE_REQUIREMENTS
    assert module.import_missing_remote_package.entrypoint()
