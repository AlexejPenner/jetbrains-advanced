# 01 — Static graph, step environments, and run configuration

This chapter covers dependency isolation and per-run configuration for a known graph. The graph stays static while each step receives the packages and operational settings it needs.

## 1. Read the graph and dependency boundaries

Run `python run.py` from this folder. The pipeline is named `01-static-churn`; ZenML compiles its known step topology, then submits two runs from `run_config.yaml` and `run_config_threshold_065.yaml`. They share the same data/model inputs but use review thresholds 0.40 and 0.65. Both runs carry the chapter prefix.

Each step declares its image requirements beside the step definition:

- `load_customer_data` needs pandas to emit its DataFrame artifact.
- `validate_and_split`, `train_churn_model`, `evaluate_model`, and `score_customers` use scikit-learn and its numerical dependencies.
- `create_evaluation_report` only needs pandas plus ZenML's HTML artifact support.

This keeps the HTML/reporting node from inheriting the ML libraries just because another step needs them. The project `requirements.txt` serves the local client environment; a step's Docker requirements shape its remote execution image. The client still needs the ZenML Kubernetes connector and cloud authentication to submit the run.

The local client environment and the remote step image are separate dependency environments. A package missing from the client can prevent pipeline import or submission; a package missing from a step image causes that remote step to fail. Lazy ML imports inside step functions help keep non-ML step images independent of scikit-learn; the code comments mark this boundary.

## 2. Configure the run in YAML

The two YAML files are ZenML `PipelineRunConfiguration` objects loaded with `static_churn_pipeline.with_options(config_path=...)`. They set run parameters, add run tags, enable caching and artifact previews, and configure training-step logs.

The example separates three configuration scopes:

- **Step code:** step behavior and image requirements.
- **Run YAML:** parameter values and supported operational overrides for this run, such as step logs and cache behavior.
- **Stack:** shared infrastructure such as the Kubernetes orchestrator, artifact store, and registry.

The stable `workshop` and `chapter-01` tags make both runs discoverable together; `threshold-040` and `threshold-065` distinguish the scenarios. Tags are searchable metadata, separate from pipeline parameters and run names. They do not change the graph, parameters, or cache keys.

The resolved snapshot and run record what ZenML submitted: parameters, tags, step configuration, build, and artifacts. Versioned step code defines environment requirements; run YAML supplies reviewed run values and supported overrides; the stack defines shared infrastructure.

## 3. Make caching an explicit decision

Both YAML files enable caching for the run. `create_evaluation_report` opts out at the step level because it embeds a fresh timestamp; both files repeat that intent. Since the second run changes only the review threshold, data generation, split, training, and fixed-threshold evaluation remain eligible for cache reuse. Scoring changes because its threshold input changed, and the HTML report regenerates.

This is a deliberate teaching example, not a blanket recommendation to disable caching on reports. For a deterministic report with no freshness requirement, caching is usually useful.

## Questions to expect

- Which dependencies belong in the local client environment, and which belong in a step image?
- Why not install every dependency in every step image?
- If a dependency is declared on a step, does the local client need it too?
- Why are ML imports inside the step functions instead of at module scope?
- Which settings belong in code, run YAML, or the stack?
- What should be a tag versus a run parameter or part of the run name?
- Which stable tags make runs easier to discover across chapters or scenarios?
- How does the YAML configuration get applied to the pipeline call?
- What wins if code and YAML both set the same parameter or setting?
- Which parts of the resolved configuration are captured in the snapshot/run?
- Which step settings does this orchestrator support, and how can you tell when a setting is ignored?
- Why keep caching enabled for training but disable it for the timestamped report?
- What should change in the cache when only the review threshold changes?
- How would you pin a transitive dependency or use a private package index?
- What evidence would you inspect when a package imports locally but fails in the remote image?
- Would you put credentials or workspace-specific endpoints in this YAML file?
