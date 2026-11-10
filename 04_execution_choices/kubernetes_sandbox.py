"""Run a command in a temporary Kubernetes Sandbox session."""

from typing import cast

from zenml import pipeline, step
from zenml.client import Client
from zenml.enums import StackComponentType
from zenml.sandboxes.base import BaseSandbox
from zenml.stack.stack_component import StackComponent


@step
def run_kubernetes_sandbox_command() -> str:
    component = Client().get_stack_component(StackComponentType.SANDBOX)
    sandbox = cast(BaseSandbox, StackComponent.from_model(component))
    with sandbox.create_session(destroy_on_exit=True) as session:
        result = session.exec(
            ["python", "-c", "import socket; print(f'Hello from sandbox {socket.gethostname()}')"]
        ).collect()
    if result.exit_code != 0:
        raise RuntimeError(result.stderr)
    message = result.stdout.strip()
    print(message)
    return message


@pipeline(enable_cache=False)
def kubernetes_sandbox_workflow() -> str:
    return run_kubernetes_sandbox_command()


if __name__ == "__main__":
    kubernetes_sandbox_workflow()
