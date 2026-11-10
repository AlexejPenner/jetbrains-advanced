"""Illustrate an opaque command inside a ZenML pipeline."""

from zenml import CommandStep, pipeline


@pipeline(dynamic=True)
def opaque_command_pipeline() -> None:
    """Run an existing command with no ZenML artifact interface."""
    command = CommandStep(
        command=["python", "-c", "print('External churn scoring command completed')"]
    )
    command()


if __name__ == "__main__":
    opaque_command_pipeline()
