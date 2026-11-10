# 02 — Dynamic pipeline execution

The parent pipeline is named `02-dynamic-segment-analysis`; its separately registered child is `02a-segment-deep-dive`. The `02a` prefix marks it as a subpipeline of chapter 2 in the UI. Dynamic execution makes runtime graph construction visible and raises the question of when its flexibility is worth the extra complexity.

A dynamic pipeline executes its graph-building logic as the run progresses. Runtime step outputs can drive loops and conditions that add work. This example demonstrates several patterns:

- **Runtime fan-out and fan-in:** discover cohorts in the data, map diagnostics across them, then aggregate the results.
- **An explicit conditional branch:** `.load()` reads the overall churn assessment, and an `if/else` adds either `escalate_portfolio` or `monitor_portfolio` to that run's graph.
- **A runtime loop with child pipelines:** flagged segments launch one child deep-dive pipeline each. The number of children is determined by the review results.

For the fixed seed and 1,200 synthetic customers, the churn rate is about 3.9%. `run.py` submits runs with 2% and 6% escalation thresholds, so one selects escalation and the other selects monitoring. The cohort review and child-pipeline loop run in both cases.

Dynamic execution is useful when the step count or route cannot be known up front. It also makes the final graph less predictable before execution; `.load()` brings artifact values into the orchestrator; many branches or child runs add overhead; and failure behavior needs more care. Fan-out should be bounded. Dynamic execution is not an automatic upgrade from static.

The parent and child are dynamic and use the same stack. The data has only three possible cohort labels. `.load()` brings a small control value into the dynamic graph-building process; the larger customer table remains an artifact passed between steps.

The selected child `deep_dive_segment` step disables caching because it emits a fresh review timestamp. Other steps remain eligible for cache reuse. This is an intentional demonstration of step-level cache control; for a deterministic production analysis, keep caching enabled unless freshness is part of the output contract.

## Questions to expect

- What advantage does this give us over the static pipeline we just saw?
- Which decision here genuinely needs dynamic execution?
- What operational complexity did we add to get that flexibility?
- What makes this dynamic if the possible cohort names are still defined in code?
- Could static mapping work, and what would we lose?
- What does `.load()` do to the orchestrator's workload?
- Which branch exists in each threshold run, and what changes the branch decision?
- What happens if the runtime result selects no segment for deeper review?
- Does `.map()` mean all cohorts execute concurrently? What limits concurrency?
- What happens when one mapped step fails?
- How do we cap fan-out on a larger dataset?
- Why use a child pipeline instead of another step?
- Why regenerate deterministic data in the child rather than pass a DataFrame parameter?
- What does the UI show for parent and child runs?
- Why does the timestamped deep-dive step run again even when its data is unchanged?
- Can I change the threshold when launching the saved snapshot from the UI?
