"""Shared data-generation step for the churn pipelines."""

from pathlib import Path
from sys import path
from typing import Annotated

import pandas as pd
from zenml import step

path.append(str(Path(__file__).resolve().parent))
from domain import make_customers


@step(
    settings={
        "docker": {
            "requirements": [
                "pandas>=2.2,<4",
                "opentelemetry-api==1.43.0",
                "opentelemetry-sdk==1.43.0",
            ]
        }
    }
)
def load_customer_data(
    n_customers: int = 1200, seed: int = 17
) -> Annotated[pd.DataFrame, "customer_data"]:
    """Generate a reproducible synthetic customer table."""
    return pd.DataFrame(make_customers(n_customers=n_customers, seed=seed))
