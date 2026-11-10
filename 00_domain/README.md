# 00 — Churn problem and synthetic data

The example models bank-customer churn using deterministic synthetic features and probabilistic labels from `domain.py`. This makes runs repeatable; it is not evidence about a real bank or a production churn policy. Feature discussion can cover predictive signals, label leakage, and the limits of using risk scores to guide customer outreach.

## Questions to expect

- How are the synthetic churn labels generated?
- Does the model learn a real customer behavior pattern or the synthetic labeling formula?
- Which features could leak the churn outcome?
- Why use synthetic data for the workshop instead of real bank records?
- What would need to change before using a real dataset?
- Is a churn score a prediction of certainty, and what does it mean for customer outreach?
