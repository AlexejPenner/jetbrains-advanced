# 02 — Dynamic pipeline execution

The parent pipeline is named `02-dynamic-segment-analysis`; its separately registered child is `02a-segment-deep-dive`. The `02a` prefix marks it as a subpipeline of chapter 2 in the UI. Dynamic execution makes runtime graph construction visible and raises the question of when its flexibility is worth the extra complexity.

A dynamic pipeline executes its graph-building logic as the run progresses. Runtime step outputs can drive loops and conditions that add work. This example demonstrates several patterns:

- **Runtime fan-out and fan-in:** discover cohorts in the data, map diagnostics across them, then aggregate the results. Each mapped `segment_metrics` invocation uses `runtime="isolated"`, so ZenML executes it in its own isolated step environment instead of inside the dynamic orchestrator.
- **An explicit conditional branch:** `.load()` reads the overall churn assessment, and an `if/else` adds either `escalate_portfolio` or `monitor_portfolio` to that run's graph.
- **A runtime loop with child pipelines:** flagged segments launch one child deep-dive pipeline each. The number of children is determined by the review results.

For the fixed seed and 1,200 synthetic customers, the churn rate is about 3.9%. `run.py` submits runs with 2% and 6% escalation thresholds, so one selects escalation and the other selects monitoring. The cohort review and child-pipeline loop run in both cases.

Dynamic execution is useful when the step count or route cannot be known up front. It also makes the final graph less predictable before execution; `.load()` brings artifact values into the orchestrator; many branches or child runs add overhead; and failure behavior needs more care. Fan-out should be bounded. Dynamic execution is not an automatic upgrade from static.

The parent and child are dynamic and use the same stack. The data has only three possible cohort labels. `.load()` brings a small control value into the dynamic graph-building process; the larger customer table remains an artifact passed between steps. On the Kubernetes orchestrator, isolated mapped invocations can run concurrently when cluster capacity and scheduling allow it; isolation does not guarantee that all mapped jobs start at the same instant. The `review_segments` fan-in waits for the mapped results.

The selected child `deep_dive_segment` step disables caching because it emits a fresh review timestamp. Other steps remain eligible for cache reuse. This is an intentional demonstration of step-level cache control; for a deterministic production analysis, keep caching enabled unless freshness is part of the output contract.

