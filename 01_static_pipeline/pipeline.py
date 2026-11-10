"""Static train/evaluate/score version of the customer-churn workflow."""

from zenml import pipeline

from steps import create_evaluation_report, evaluate_model, score_customers, train_churn_model, validate_and_split
from data_steps import load_customer_data

@pipeline(name="01-static-churn")
def static_churn_pipeline(n_customers: int = 1200, seed: int = 17, test_size: float = 0.25, regularization: float = 1.0, threshold: float = 0.5) -> None:
    """Build a statically known tabular churn ML DAG.

    Args:
        n_customers: Number of synthetic customers to generate.
        seed: Reproducibility seed for data and split.
        test_size: Fraction reserved for final evaluation.
        regularization: Inverse regularization strength for logistic regression.
        threshold: Churn probability threshold for the review flag.
    """
    data = load_customer_data(n_customers=n_customers, seed=seed)
    x_train, x_test, y_train, y_test = validate_and_split(data=data, test_size=test_size, seed=seed)
    model = train_churn_model(x_train=x_train, y_train=y_train, regularization=regularization)
    metrics = evaluate_model(model=model, x_test=x_test, y_test=y_test)
    scores = score_customers(model=model, x_test=x_test, threshold=threshold)
    create_evaluation_report(metrics=metrics, scores=scores, threshold=threshold)
