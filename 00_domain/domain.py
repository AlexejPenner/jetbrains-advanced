"""Deterministic synthetic bank-customer churn data generator."""

from __future__ import annotations

import random


FEATURES = [
    "tenure_months",
    "products_count",
    "monthly_charges",
    "support_calls_90d",
    "late_payments_12m",
    "usage_change_pct",
    "contract_months_remaining",
]


def make_customers(n_customers: int = 1200, seed: int = 17) -> list[dict[str, float | int]]:
    """Generate reproducible customer features and a synthetic churn label.

    Args:
        n_customers: Number of customer rows to generate.
        seed: Random seed for reproducibility.

    Returns:
        Rows containing customer ID, tabular features, and churn label.

    Raises:
        ValueError: If fewer than 100 rows are requested.
    """
    if n_customers < 100:
        raise ValueError("Use at least 100 customers for a train/test split.")
    rng = random.Random(seed)
    rows = []
    for index in range(n_customers):
        tenure = rng.randint(1, 120)
        products = rng.randint(1, 4)
        monthly = round(rng.uniform(15, 180), 2)
        support_calls = min(8, int(rng.expovariate(0.7)))
        late_payments = min(6, int(rng.expovariate(0.9)))
        usage_change = round(rng.uniform(-0.8, 0.5), 3)
        contract_remaining = rng.choice([0, 1, 2, 3, 6, 12, 18, 24])
        churn_signal = (
            -2.3
            - 0.018 * tenure
            - 0.38 * (products - 1)
            + 0.18 * support_calls
            + 0.28 * late_payments
            - 1.5 * usage_change
            - 0.08 * contract_remaining
            + (0.9 if contract_remaining == 0 else 0)
        )
        probability = 1 / (1 + pow(2.718281828, -churn_signal))
        churned = int(rng.random() < probability)
        rows.append(
            {
                "customer_id": index + 1,
                "tenure_months": tenure,
                "products_count": products,
                "monthly_charges": monthly,
                "support_calls_90d": support_calls,
                "late_payments_12m": late_payments,
                "usage_change_pct": usage_change,
                "contract_months_remaining": contract_remaining,
                "churned": churned,
            }
        )
    return rows
