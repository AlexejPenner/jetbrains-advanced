"""Small, isolated pipelines for practicing failure diagnosis."""

from typing import Annotated

import pandas as pd
from zenml import pipeline, step


@step(settings={"docker": {"requirements": ["pandas>=2.2,<4"]}})
def import_missing_remote_package() -> str:
    """Use a dependency that is declared in the remote step image."""
    # Keep the import inside the step so the remote image boundary is tested.
    # pandas is declared below and in the repository requirements.
    import pandas as remote_pandas

    return remote_pandas.__version__


@pipeline(name="05-remote-dependency-missing", enable_cache=False)
def missing_dependency_pipeline() -> None:
    """Reach a remote step whose runtime dependency is intentionally missing."""
    import_missing_remote_package()


@step
def produce_legacy_customer_table() -> Annotated[pd.DataFrame, "legacy_customer_table"]:
    """Produce a table satisfying the current customer contract."""
    return pd.DataFrame(
        {
            "customer_id": [101, 102, 103],
            "tenure_months": [4, 18, 31],
            "churned": [0, 1, 0],
        }
    )


@step
def validate_customer_contract(data: pd.DataFrame) -> int:
    """Validate the customer table contract before downstream processing."""
    required = {"customer_id", "tenure_months", "churned"}
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(
            f"Customer table contract violation: missing required columns {missing}. "
            "Update the producer or version the consumer contract."
        )
    return len(data)


@pipeline(name="05-schema-contract-mismatch", enable_cache=False)
def schema_mismatch_pipeline() -> None:
    """Connect a legacy producer to a consumer with a newer schema contract."""
    data = produce_legacy_customer_table()
    validate_customer_contract(data=data)
