"""Create a named run template from an existing pipeline snapshot."""

import argparse

from zenml.client import Client


def main() -> None:
    """Create a template from a supplied snapshot ID."""
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot_id", help="Existing pipeline snapshot UUID")
    parser.add_argument("--name", default="advanced-bank-churn-workshop")
    args = parser.parse_args()
    template = Client().create_run_template(
        name=args.name,
        snapshot_id=args.snapshot_id,
        description="Synthetic bank customer churn pipeline template for the advanced workshop",
        tags=["workshop", "customer-churn"],
    )
    print(f"Created run template {template.name} ({template.id})")


if __name__ == "__main__":
    main()
