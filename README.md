# Decision Engine

A simple decision-support web application to compare alternatives under uncertainty using expected value and risk-adjusted scoring.

Live app:
https://decisionengine-kdkzdeo8wqhrqsy4jwnofy.streamlit.app

---

## The Problem

When decisions involve uncertain outcomes, comparing options intuitively can be misleading.  
This tool provides a structured way to evaluate alternatives using probabilistic modeling.

---

## Approach

For each option, the model computes:

Expected value:
EV = Σ p_i x_i

Variance:
Var = Σ p_i (x_i − EV)^2

Risk-adjusted score:
Score = EV − λ Var

Where λ represents the user’s risk aversion.

---

## Features

- Compare two alternatives under uncertainty
- Adjustable risk aversion parameter
- Expected value and variance calculation
- Risk-adjusted recommendation
- Interactive web interface built with Streamlit

---

## Tech stack

- Python
- Streamlit
- GitHub
- Streamlit Cloud

---

## Future improvements

- Visualize risk vs expected value
- Support multiple alternatives
- Sensitivity analysis on λ
- CSV input support

---

Jiaqi Zhou
