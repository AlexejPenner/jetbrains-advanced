"""Compare two static pipeline runs configured through YAML."""

from pathlib import Path

from pipeline import static_churn_pipeline

if __name__ == "__main__":
    for config_name, label in (
        ("run_config.yaml", "review threshold 0.40"),
        ("run_config_threshold_065.yaml", "review threshold 0.65"),
    ):
        print(f"Launching {label} from {config_name}")
        config_path = Path(__file__).with_name(config_name)
        static_churn_pipeline.with_options(config_path=str(config_path))()
