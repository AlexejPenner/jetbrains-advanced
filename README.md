# Advanced ZenML workshop: bank customer churn

Deterministic synthetic customer data illustrates how an end-user team turns tabular ML code into observable, reusable, automated workflows. The workshop assumes basic ZenML knowledge; participants do not need to provision a stack or share a common local environment.

## Workshop format

This is a demo-led advanced session with optional, portable code edits. Participants know basic ZenML; they do not need to provision a stack or share a common local environment. Remote steps, Sandbox, and step-operator examples use the prepared instructor environment.

## Workshop sequence

Pipeline names begin with their chapter number (`01`, `02`). Chapter 1 runs two YAML configurations with different thresholds so the comparison is visible under the same static pipeline.

1. `00_domain/`: deterministic synthetic features and labels for the churn use case.
2. `01_static_pipeline/`: per-step Docker requirements, local-client versus remote-image dependencies, YAML `PipelineRunConfiguration`, run tags, supported logging/cache overrides, and resolved snapshots. Two threshold configs demonstrate parameterized runs, tag-based discovery, and cache reuse.
3. `02_dynamic_pipeline/`: runtime-derived cohorts, mapped diagnostics, aggregation, an explicit data-driven `if/else` branch, and a runtime loop that launches child deep dives for selected cohorts.
4. `03_template_and_trigger/`: snapshot → run template → schedule or platform-event trigger, including ownership, concurrency, and deactivation.
5. `04_execution_choices/`: regular steps, `CommandStep`, Sandbox, and step operators, including dependency boundaries, artifact handoff, credentials, and specialized runtimes. The SageMaker example may launch billable compute.
6. `05_inspection/`: pipeline runs, snapshots, parameters, artifacts, logs, cache, and failures in the UI/CLI.

## What static means

A static pipeline has a graph whose steps and dependencies are known before its steps execute. Static does **not** mean the dataset, artifacts, model outputs, or run parameters must be fixed in advance. ZenML compiles the pipeline definition into a DAG; step outputs are not yet available for a normal Python `if` in that compile-time graph-building pass.

Advantages include a graph that is visible before work starts, predictable dependencies, simpler orchestration, and easier failure localization. Static execution is a good fit when topology is known in advance.

## What dynamic adds

A dynamic pipeline lets runtime results control which steps or child pipelines are created. That flexibility helps when the number of cohorts, routing, or next action depends on data. It also means the final graph is less predictable up front; `.load()` can move artifact data into the orchestrator; fan-out and child runs can add overhead; and failures can be harder to coordinate. Dynamic execution is most useful when its flexibility justifies that complexity.

## Additional advanced topics

- **Dependencies:** the control-plane/client integration environment is separate from each pipeline image. Relevant concerns include pins, native libraries, accelerators, package indexes, and dependency failures in step logs.
- **Non-ZenML execution:** `CommandStep` has no ZenML artifact inputs or outputs; Sandbox sessions have their own lifecycle and flavor-specific snapshot support.
- **Step operators:** the SageMaker example moves one specialized step while Kubernetes remains the orchestrator.
- **Resource pools:** resource requests, reservations, and fairness policies are relevant when workloads compete for capacity.

## Short release notes (optional)

ZenML 0.98.1 includes fixes for integration dependency installs and GCP runner OpenTelemetry compatibility. ZenML 0.98.0 added webhook event filters that can match provider event fields. These releases connect to dependency reliability and trigger design.

## Questions people may ask before the first run

- Why choose bank churn for this example, and which parts of the data are synthetic?
- What can the score justify, and what should it never decide automatically?
- Can I participate without ZenML Cloud, AWS credentials, or Docker?
- Is this a code-along or an instructor-led demo?
- What should I install if I want to try the code afterward?

## Setup

Use ZenML 0.98.1 or later, and install the optional tabular-ML dependencies from this folder:

```bash
pip install -r requirements.txt
```

From the project root, run the stage scripts from their folders:

```bash
cd 01_static_pipeline && python run.py
cd ../02_dynamic_pipeline && python run.py
```

The data is deterministic and synthetic. Metrics are illustrative, not a validated financial model or real retention policy. See `solutions/ADVANCED_NOTES.md` for advanced concepts and discussion questions.
