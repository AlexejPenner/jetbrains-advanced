"""Corrected chapter-05 inspection pipelines.

The examples intentionally exercise two common failure classes while keeping
successful runs executable: remote image dependency declarations and explicit
artifact schema contracts.
"""

from typing import Annotated

import pandas as pd
from zenml import pipeline, step

# Keep the dependency declaration next to the step that needs it. The previous
# version imported a package that did not exist in the remote image.
_REMOTE_REQUIREMENTS = [
    "pandas>=2.2,<4",
    "opentelemetry-api==1.43.0",
    "opentelemetry-sdk==1.43.0",
]


@step(settings={"docker": {"requirements": _REMOTE_REQUIREMENTS}})
def import_missing_remote_package() -> Annotated[str, "dependency_check"]:
    """Use a dependency that is declared for the remote step image."""
    # pandas is already a workshop dependency and is explicitly included above.
    import pandas as remote_pandas

    return remote_pandas.__version__


@pipeline(name="05-remote-dependency-missing")
def remote_dependency_pipeline() -> None:
    """Verify that the remote step image contains its declared dependency."""
    import_missing_remote_package()


@step(settings={"docker": {"requirements": _REMOTE_REQUIREMENTS}})
def produce_legacy_customer_table() -> Annotated[pd.DataFrame, "legacy_customer_table"]:
    """Produce the legacy-shaped table with the complete consumer contract.

    The old producer omitted ``churned``. Keeping the column in the artifact
    makes the contract explicit while retaining the small synthetic fixture.
    """
    return pd.DataFrame(
        {
            "customer_id": [101, 102],
            "monthly_spend": [80.0, 120.0],
            "churned": [0, 1],
        }
    )


@step(settings={"docker": {"requirements": _REMOTE_REQUIREMENTS}})
def validate_customer_contract(data: pd.DataFrame) -> Annotated[int, "validated_rows"]:
    """Validate the version-1 customer table contract."""
    required = {"customer_id", "monthly_spend", "churned"}
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(
            f"Customer table contract violation: missing required columns {missing}. "
            "Update the producer or version the consumer contract."
        )
    if not data["churned"].isin([0, 1]).all():
        raise ValueError("Customer table contract violation: churned must contain only 0 or 1.")
    return len(data)


@pipeline(name="05-schema-contract-mismatch")
def schema_contract_pipeline() -> None:
    """Produce and validate a compatible customer-table artifact."""
    validate_customer_contract(produce_legacy_customer_table())
