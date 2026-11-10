"""Dynamic segment analysis for the bank customer-churn workflow."""

from datetime import datetime, timezone
from typing import Annotated

import pandas as pd
from zenml import pipeline, step, unmapped

try:
    from data_steps import load_customer_data
except ModuleNotFoundError:
    from pathlib import Path
    from sys import path

    path.append(str(Path(__file__).resolve().parents[1] / "00_domain"))
    from data_steps import load_customer_data


@step
def discover_segments(data: pd.DataFrame) -> Annotated[list[str], "segments"]:
    """Return only tenure cohorts that actually occur in runtime data.

    Args:
        data: Generated customer table.

    Returns:
        Segment names to analyze.
    """
    bounds = {
        "new": (0, 12),
        "established": (12, 60),
        "long_tenure": (60, 10_000),
    }
    return [
        name
        for name, (low, high) in bounds.items()
        if ((data["tenure_months"] >= low) & (data["tenure_months"] < high)).any()
    ]


@step(runtime="isolated")
def segment_metrics(data: pd.DataFrame, segment: str) -> Annotated[dict[str, float | int | str], "segment_metrics"]:
    """Calculate churn rate and average profile for a segment.

    Args:
        data: Customer table.
        segment: Tenure cohort name.

    Returns:
        Segment size, churn rate, and average tenure/charges.
    """
    bounds = {"new": (0, 12), "established": (12, 60), "long_tenure": (60, 10_000)}
    if segment not in bounds:
        raise ValueError(f"Unknown segment: {segment}")
    low, high = bounds[segment]
    subset = data[(data["tenure_months"] >= low) & (data["tenure_months"] < high)]
    return {
        "segment": segment,
        "customers": int(len(subset)),
        "churn_rate": float(subset["churned"].mean()),
        "avg_tenure_months": float(subset["tenure_months"].mean()),
        "avg_monthly_charges": float(subset["monthly_charges"].mean()),
    }


@step
def review_segments(
    metrics: list[dict[str, float | int | str]],
    minimum_customers: int = 50,
    high_churn_threshold: float = 0.08,
) -> Annotated[dict[str, object], "segment_review"]:
    """Aggregate segment diagnostics and flag small/high-churn cohorts.

    Args:
        metrics: Per-segment diagnostic outputs.
        minimum_customers: Minimum cohort size for stable interpretation.
        high_churn_threshold: Churn rate that routes a cohort to deeper review.

    Returns:
        Segment metrics and review flags.
    """
    reviewed = []
    for row in metrics:
        reviewed.append(
            {
                **row,
                "review": row["customers"] < minimum_customers
                or row["churn_rate"] > high_churn_threshold,
            }
        )
    return {"segments": reviewed}


@step
def assess_portfolio_risk(
    data: pd.DataFrame,
    escalation_threshold: float = 0.03,
) -> Annotated[dict[str, float | bool], "portfolio_risk"]:
    """Decide at runtime whether the overall churn rate needs escalation."""
    if not 0 <= escalation_threshold <= 1:
        raise ValueError("escalation_threshold must be between 0 and 1.")
    churn_rate = float(data["churned"].mean())
    return {
        "churn_rate": churn_rate,
        "threshold": escalation_threshold,
        "escalate": churn_rate >= escalation_threshold,
    }


@step
def escalate_portfolio(
    risk: dict[str, float | bool],
) -> Annotated[dict[str, float | str], "portfolio_action"]:
    """Record the higher-risk branch selected from runtime data."""
    return {
        "action": "escalate_for_review",
        "churn_rate": float(risk["churn_rate"]),
        "threshold": float(risk["threshold"]),
    }


@step
def monitor_portfolio(
    risk: dict[str, float | bool],
) -> Annotated[dict[str, float | str], "portfolio_action"]:
    """Record the monitor-only branch selected from runtime data."""
    return {
        "action": "continue_monitoring",
        "churn_rate": float(risk["churn_rate"]),
        "threshold": float(risk["threshold"]),
    }


@step(enable_cache=False)
def deep_dive_segment(data: pd.DataFrame, segment: str) -> Annotated[dict[str, float | int | str], "deep_dive"]:
    """Produce a fresh, timestamped review for a segment selected at runtime."""
    bounds = {"new": (0, 12), "established": (12, 60), "long_tenure": (60, 10_000)}
    low, high = bounds[segment]
    subset = data[(data["tenure_months"] >= low) & (data["tenure_months"] < high)]
    return {
        "segment": segment,
        "customers": int(len(subset)),
        "churn_rate": float(subset["churned"].mean()),
        "avg_support_calls": float(subset["support_calls_90d"].mean()),
        "avg_late_payments": float(subset["late_payments_12m"].mean()),
        "reviewed_at_utc": datetime.now(timezone.utc).isoformat(),
    }


@pipeline(name="02a-segment-deep-dive", dynamic=True)
def segment_deep_dive_subpipeline(
    segment: str,
    n_customers: int = 1200,
    seed: int = 17,
) -> None:
    """Reusable child workflow called only for cohorts selected at runtime."""
    data = load_customer_data(n_customers=n_customers, seed=seed)
    deep_dive_segment(data=data, segment=segment)


@pipeline(
    name="02-dynamic-segment-analysis",
    dynamic=True,
    settings={
        "docker": {
            "requirements": [
                "pandas>=2.2,<4",
                "numpy>=1.26,<3",
                "opentelemetry-api==1.43.0",
                "opentelemetry-sdk==1.43.0",
            ]
        }
    },
)
def dynamic_segment_analysis_pipeline(
    n_customers: int = 1200,
    seed: int = 17,
    minimum_customers: int = 50,
    high_churn_threshold: float = 0.08,
    portfolio_escalation_threshold: float = 0.03,
) -> None:
    """Fan out segment diagnostics and route the portfolio by runtime risk.

    Args:
        n_customers: Number of synthetic customer rows.
        seed: Data generation seed.
        minimum_customers: Minimum cohort size for review.
        high_churn_threshold: Churn rate that creates a deeper review branch.
        portfolio_escalation_threshold: Overall churn rate that selects escalation.
    """
    data = load_customer_data(n_customers=n_customers, seed=seed)
    portfolio_risk = assess_portfolio_risk(
        data=data,
        escalation_threshold=portfolio_escalation_threshold,
    )
    # The loaded step output controls which branch exists in this run's graph.
    if portfolio_risk.load()["escalate"]:
        escalate_portfolio(risk=portfolio_risk)
    else:
        monitor_portfolio(risk=portfolio_risk)

    segments = discover_segments(data=data)
    metrics = segment_metrics.map(data=unmapped(data), segment=segments)
    review = review_segments(
        metrics=metrics,
        minimum_customers=minimum_customers,
        high_churn_threshold=high_churn_threshold,
    )

    # Runtime results select which child workflows are added to this graph.
    reviewed_segments = [
        row["segment"] for row in review.load()["segments"] if row["review"]
    ]
    # Child pipeline parameters are scalar configuration. Regenerate the
    # deterministic dataset inside each child rather than passing a DataFrame
    # as a pipeline parameter.
    for segment in reviewed_segments:
        segment_deep_dive_subpipeline(
            segment=segment,
            n_customers=n_customers,
            seed=seed,
        )
