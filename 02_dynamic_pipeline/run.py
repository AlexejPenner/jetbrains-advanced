"""Run dynamic segment diagnostics for churn."""

from datetime import datetime, timezone

from pipeline import dynamic_segment_analysis_pipeline

if __name__ == "__main__":
    run_stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    
    for threshold, label in ((0.02, "escalate"), (0.06, "monitor")):
        dynamic_segment_analysis_pipeline.with_options(
            run_name=f"02-dynamic-{label}-{run_stamp}"
        )(
            n_customers=1200,
            seed=17,
            minimum_customers=50,
            high_churn_threshold=0.08,
            portfolio_escalation_threshold=threshold,
        )
