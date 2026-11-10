"""Tabular data and model steps for the static churn pipeline."""

from pathlib import Path
from sys import path
from typing import Annotated

import pandas as pd
from zenml import step
from zenml.types import HTMLString

path.append(str(Path(__file__).resolve().parents[1] / "00_domain"))
from data_steps import load_customer_data
from domain import FEATURES


@step()
def validate_and_split(data: pd.DataFrame, test_size: float = 0.25, seed: int = 17) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Validate schema and create a stratified train/test split.

    Args:
        data: Customer dataframe.
        test_size: Fraction reserved for evaluation.
        seed: Split seed.

    Returns:
        Training features, test features, training labels, test labels.

    Raises:
        ValueError: If required columns or labels are invalid.
    """
    # Keep ML-only imports inside the step so other step images stay lightweight.
    from sklearn.model_selection import train_test_split

    required = set(FEATURES + ["customer_id", "churned"])
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if not data["churned"].isin([0, 1]).all():
        raise ValueError("The churn target must contain only 0 or 1.")
    x_train, x_test, y_train, y_test = train_test_split(
        data[FEATURES], data["churned"], test_size=test_size, random_state=seed, stratify=data["churned"]
    )
    return x_train, x_test, y_train, y_test


@step()
def train_churn_model(x_train: pd.DataFrame, y_train: pd.Series, regularization: float = 1.0) -> Annotated[object, "churn_model"]:
    """Fit a scaled logistic-regression baseline.

    Args:
        x_train: Training features.
        y_train: Binary training labels.
        regularization: Inverse regularization strength.

    Returns:
        A fitted sklearn pipeline.
    """
    # Lazy imports keep scikit-learn requirements scoped to ML steps.
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    model = make_pipeline(StandardScaler(), LogisticRegression(C=regularization, max_iter=500, class_weight="balanced"))
    model.fit(x_train, y_train)
    return model


@step()
def evaluate_model(model: object, x_test: pd.DataFrame, y_test: pd.Series) -> Annotated[dict[str, float], "evaluation_metrics"]:
    """Evaluate on held-out data and report threshold-independent and thresholded metrics.

    Args:
        model: Fitted classifier.
        x_test: Held-out features.
        y_test: Held-out labels.

    Returns:
        ROC-AUC, precision, recall, F1, and accuracy.
    """
    # These metrics are needed only in this ML step's execution image.
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score

    probabilities = model.predict_proba(x_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    return {
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "accuracy": float(accuracy_score(y_test, predictions)),
    }


@step()
def score_customers(model: object, x_test: pd.DataFrame, threshold: float = 0.5) -> Annotated[pd.DataFrame, "customer_risk_scores"]:
    """Produce risk scores and a review flag for held-out customers.

    Args:
        model: Fitted classifier.
        x_test: Customer features to score.
        threshold: Churn probability threshold for the flag.

    Returns:
        Customer scores and binary risk flags.
    """
    probabilities = model.predict_proba(x_test)[:, 1]
    return pd.DataFrame({"customer_id": x_test.index, "churn_probability": probabilities, "high_risk": probabilities >= threshold})


@step(
    enable_cache=False,
)
def create_evaluation_report(
    metrics: dict[str, float],
    scores: pd.DataFrame,
    threshold: float,
) -> Annotated[HTMLString, "html_evaluation_report"]:
    """Create a fresh, browser-viewable evaluation report artifact.

    Caching is disabled so the report's generated-at timestamp is always fresh.
    Upstream data, training, and evaluation steps can still use their caches.
    """
    from datetime import datetime, timezone
    from html import escape

    metric_rows = "".join(
        f"<tr><th>{escape(name.replace('_', ' ').title())}</th><td>{value:.3f}</td></tr>"
        for name, value in metrics.items()
    )
    flagged = int(scores["high_risk"].sum())
    total = len(scores)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Customer churn evaluation</title>
<style>
body {{ font: 16px/1.5 system-ui, sans-serif; max-width: 900px; margin: 3rem auto; padding: 0 1rem; color: #172033; }}
h1, h2 {{ color: #123b67; }} .summary {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
.card {{ background: #f1f6fb; border-radius: .6rem; padding: 1rem 1.3rem; }}
table {{ border-collapse: collapse; min-width: 320px; }} th, td {{ border-bottom: 1px solid #ccd6e0; padding: .55rem .8rem; text-align: left; }}
small {{ color: #536477; }}
</style></head><body>
<h1>Bank customer churn: model evaluation</h1>
<p>Synthetic data demonstration. This score is for review and is not a validated retention policy.</p>
<div class="summary"><div class="card"><strong>Review threshold</strong><br>{threshold:.2f}</div>
<div class="card"><strong>Customers flagged</strong><br>{flagged} of {total} ({(flagged / total if total else 0):.1%})</div></div>
<h2>Held-out evaluation metrics (classification threshold 0.50)</h2>
<table><tbody>{metric_rows}</tbody></table>
<p><small>Generated at {generated_at}. The evaluation metrics use a fixed 0.50 cutoff; the review threshold above controls customer flags only.</small></p>
</body></html>"""
    return HTMLString(html)
