# Advanced topics and discussion questions

## Static and dynamic graphs

A static pipeline has a known step topology and artifact dependency graph before step execution. Data and pipeline parameters may still vary at run time. Dynamic execution is useful when runtime values determine which steps or child pipelines are created. It adds runtime graph construction, artifact loading, fan-out, and failure-management complexity.

Mapped steps suit collection work; a runtime loop suits decisions that control later work; a child pipeline packages a reusable nested workflow at the cost of additional graph complexity.

## Parameters and dependencies

Thresholds, cohort size, random seeds, and model regularization are run parameters. Feature definitions and label construction affect the meaning of the model and belong in versioned code or configuration.

The local client environment and remote step images are separate dependency environments. Per-step image requirements can limit package installation to the steps that need those packages. Native libraries, accelerators, package indexes, secrets, and data access can introduce additional environment constraints.

## Execution boundaries

- `CommandStep` reuses an opaque command but has no ZenML artifact input/output interface. Data handoff, command exit status, credentials, and observability need explicit treatment.
- Sandbox lifecycle, filesystem, and snapshot behavior depend on its flavor. Sandbox state is distinct from a pipeline snapshot, and a local Sandbox is not a security boundary for arbitrary untrusted code.
- A step operator moves one specialized step to another execution environment while the pipeline orchestrator remains in place. The SageMaker example requires a compatible image, IAM/data access, and billable cloud compute.

## Snapshots and triggers

A snapshot represents runnable pipeline source and configuration. A run template stores reusable run configuration. A trigger submits a run based on a schedule or event. Duplicate events can cause duplicate runs; concurrency policy and trigger deactivation matter when workflows have side effects. Workshop triggers remain inactive.

## Discussion questions

- Which decision in the dynamic example genuinely requires a dynamic graph?
- What operational complexity is added by runtime graph construction?
- When should an artifact value be loaded into the dynamic orchestrator versus passed as an artifact to another step?
- Which configuration belongs in code, run YAML, or the stack?
- How should dependency conflicts, native libraries, or private package indexes be handled?
- What should happen when an upstream event is delivered more than once?
- When do resource reservations or fairness policies matter for a shared stack?

The churn data is synthetic and the risk score is illustrative, not a production retention policy. Real use would require validated data, governance, and human review.
