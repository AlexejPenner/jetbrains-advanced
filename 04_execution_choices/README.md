# 04 — Dependencies and execution boundaries

Execution choices determine where code runs and how dependencies, data, credentials, and outputs cross execution boundaries. The examples compare these contracts without requiring participants to provision infrastructure.

| Workload need | Candidate | Contract to discuss |
| --- | --- | --- |
| Common Python | `@step` with pipeline requirements | Shared image, typed artifact inputs/outputs |
| One specialized package/runtime | Step Docker settings | Image build, caching, dependency compatibility |
| Existing opaque command | `CommandStep` | No ZenML artifact inputs/outputs; explicit handoff |
| Interactive/isolated command | Sandbox session | Flavor, lifecycle, filesystem, security boundary |
| Specialized compute for one step | Step operator | Integration, image, credentials, data movement |

`command_step.py` runs a remote command. Its dynamic pipeline wrapper is required because ZenML requires a step operator for `CommandStep` in a static pipeline; this is a platform constraint, not a claim that the command needs data-dependent graph construction.

The prepared stack has a Kubernetes Sandbox. `kubernetes_sandbox.py` starts a temporary session and returns captured output as an artifact. Sandbox state is distinct from pipeline snapshots, and a local Sandbox is not a security boundary for arbitrary untrusted code.

`sagemaker_step_operator.py` demonstrates `@step(step_operator=True)`: Kubernetes remains the pipeline orchestrator while SageMaker executes one step. Running it starts billable cloud compute; inspect its code and registered component unless a live run is intended.

