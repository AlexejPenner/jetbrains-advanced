# 05 — Diagnose failed pipeline runs

These small pipelines create three recognizable failure signatures in the ZenML UI:

| Pipeline | Failure to investigate | Expected evidence |
| --- | --- | --- |
| `05-remote-dependency-missing` | A remote step imports a package that is absent from its step image. | The run reaches the step, then fails with an import error in the remote step logs. |
| `05-schema-contract-mismatch` | A producer emits a table that violates the consumer's required schema. | The consumer step fails with a clear validation error; inspect its input artifact and logs. |

The examples use isolated pipeline names and synthetic data. They do not alter Chapter 1 or Chapter 2 artifacts.

## Run order

Run each example from this directory against the prepared remote stack. Both examples fail on their first run:

```bash
python run_remote_dependency_missing.py
python run_schema_contract_mismatch.py
```

## Investigation sequence

For each failed run, follow the same evidence trail:

1. Identify the failed step and distinguish a step failure from a pipeline submission or image-build failure.
2. Read the complete step log and record the exception or missing evidence.
3. Inspect the step's inputs, outputs, configuration, and cache status.
4. Compare the observed failure with the expected signature above. Check whether the evidence is sufficient to explain the failure without guessing.
5. State the smallest next diagnostic action: add the missing package to the correct image or repair the producer-consumer schema contract.

The dependency example tests the boundary between the local client and remote step image. The schema example tests whether artifact lineage makes a data contract violation easy to locate. These failures are deliberately bounded and deterministic; they do not simulate Kubernetes eviction, network outages, or production data loss.

## Questions for review

- Did the run fail during submission, image preparation, or step execution?
- What exact evidence identifies the root cause?
- Which parts of the failure remain visible in ZenML after the step stops?
- What would need to be captured from Kubernetes, the image builder, or external logs to complete the diagnosis?
- Which code, dependency, or artifact contract should change before retrying?
- What evidence would make this failure easier to diagnose on the next run?
