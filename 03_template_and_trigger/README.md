# 03 — Snapshots, templates, and triggers

Snapshots make a pipeline definition and its configuration runnable as a versioned unit. Run templates capture reusable run configuration, and triggers determine when a run is submitted. The lifecycle is pipeline definition → snapshot → run template → trigger.

`create_template.py` creates a persistent project object. `create_inactive_schedule.py` creates an inactive schedule trigger attached to a snapshot. The example trigger remains inactive.

Inspect supported platform events:

```bash
zenml trigger platform-event list-supported-events pipeline
zenml trigger platform-event list-supported-events pipeline_run
zenml trigger platform-event list-supported-events pipeline_snapshot
```

One event-driven pattern uses a completed static churn pipeline as the event source and the dynamic review snapshot as the target. The event trigger remains inactive. Source and target are separate concepts. Example shape; replace placeholders with real IDs and a supported event:

```bash
zenml trigger platform-event create churn-review-on-upstream-completion pipeline SOURCE_PIPELINE_ID --target_events run_completed --active false
zenml trigger platform-event attach churn-review-on-upstream-completion TARGET_SNAPSHOT_ID
```

## Questions to expect

- What does a snapshot preserve, and what still comes from the stack at run time?
- Why create a run template if the snapshot already has defaults?
- Does a trigger run the template or the attached snapshot?
- What is the difference between schedule, platform-event, and webhook triggers?
- Which event should start churn scoring: data refresh completion or a calendar time?
- What happens if the source emits the event twice?
- How do we prevent overlapping scheduled runs?
- What does `skip` concurrency mean?
- Can a trigger pass run parameters?
- If pipeline code changes, does an attached trigger automatically run the new version?
- How do I inspect, deactivate, or replace a trigger targeting an obsolete snapshot?
- When is a webhook a better fit than a platform event?
