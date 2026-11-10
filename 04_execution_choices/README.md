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

## Questions to expect

- When should an existing script become a regular `@step` instead of a `CommandStep`?
- How can a command receive inputs or return an artifact without ZenML I/O?
- How are exit codes, retries, caching, and logs handled for an opaque command?
- What does this Sandbox isolate, and what security boundary does it provide?
- What survives when a Sandbox session ends? Can it be resumed or snapshotted?
- Why use a step operator for one step instead of moving the whole pipeline?
- Which image, Python version, and packages does SageMaker use?
- How do artifacts move between Kubernetes, SageMaker, and S3?
- Which role accesses data, and how are credentials supplied?
- What dependency belongs in the pipeline image versus one step image?
- How should we handle native libraries, package indexes, and version conflicts?
- Which parts can participants understand without AWS credentials?
