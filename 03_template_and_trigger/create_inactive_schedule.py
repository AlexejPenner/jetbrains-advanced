"""Create an inactive weekly trigger attached to a pipeline snapshot."""

import argparse
from uuid import UUID

from zenml.client import Client


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot_id", type=UUID, help="Existing pipeline snapshot UUID")
    parser.add_argument("--name", default="bank-churn-inactive-weekly-trigger")
    args = parser.parse_args()

    client = Client()
    trigger = client.create_schedule_trigger(
        name=args.name, active=False, cron_expression="0 9 * * 1"
    )
    client.attach_trigger_to_snapshot(
        trigger_id=trigger.id, pipeline_snapshot_id=args.snapshot_id
    )
    print(f"Created inactive trigger {trigger.name} ({trigger.id})")
    print(f"Attached to snapshot {args.snapshot_id}; activate only when ready.")


if __name__ == "__main__":
    main()
