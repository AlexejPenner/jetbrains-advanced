"""Optional SageMaker step-operator example for the prepared AWS stack."""

from typing import Annotated

import pandas as pd
from zenml import pipeline, step
from zenml.integrations.aws.flavors.sagemaker_step_operator_flavor import (
    SagemakerStepOperatorSettings,
)

try:
    from steps import load_customer_data
except ModuleNotFoundError:
    from pathlib import Path
    from sys import path

    path.append(str(Path(__file__).resolve().parents[1] / "01_static_pipeline"))
    from steps import load_customer_data


@step(
    step_operator=True,
    settings={
        "docker": {"requirements": ["pandas>=2.2,<4"]},
        "step_operator": SagemakerStepOperatorSettings(
            estimator_args={"instance_type": "ml.m5.large", "instance_count": 1}
        ),
    },
)
def summarize_churn_cohort(
    data: pd.DataFrame,
) -> Annotated[dict[str, float | int], "cohort_summary"]:
    return {
        "customers": int(len(data)),
        "churn_rate": float(data["churned"].mean()),
        "mean_tenure_months": float(data["tenure_months"].mean()),
    }


@pipeline
def sagemaker_step_operator_pipeline(n_customers: int = 1200, seed: int = 17) -> None:
    data = load_customer_data(n_customers=n_customers, seed=seed)
    summarize_churn_cohort(data=data)


if __name__ == "__main__":
    sagemaker_step_operator_pipeline()
