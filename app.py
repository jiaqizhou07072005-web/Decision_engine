import re
import streamlit as st
from decision_model import risk_adjusted_score

st.set_page_config(page_title="Decision Engine")
st.title("Decision Engine")
st.write("Answer a few questions and the app will compare multiple options under uncertainty.")

# ---------------------------
# Helpers
# ---------------------------
def parse_list(s: str):
    """Extract numbers from free text (supports €, $, words, etc.)."""
    numbers = re.findall(r"-?(?:\d+\.?\d*|\.\d+)", s)
    return [float(n) for n in numbers]

def validate_probs(probs):
    if len(probs) == 0:
        return False, "Probabilities list is empty."
    if any(p < 0 for p in probs):
        return False, "Probabilities cannot be negative."
    total = sum(probs)
    if abs(total - 1.0) > 1e-6:
        return False, f"Probabilities must sum to 1. Current sum = {total:.6f}"
    return True, ""

def fmt_unit(unit: str):
    return "" if unit == "None" else unit

# ---------------------------
# Explanations
# ---------------------------
with st.expander("What do these terms mean? (click to expand)"):
    st.markdown(
        """
### Expected Value (EV)
The **expected value** is the average result you would obtain if you repeated the same decision many times.

Example:
- 50% chance of winning 10
- 50% chance of winning 0  
EV = 5

EV measures the average payoff, not the risk.

---

### Variance (Var)
Variance measures how unpredictable the outcomes are.

High variance → outcomes swing a lot  
Low variance → outcomes are stable and predictable  

Example:
- 0 or 10 → higher variance  
- always 5 → variance = 0

Variance is used here as a simple proxy for uncertainty / risk.

---

### Risk aversion (λ)
Risk aversion controls how much you penalize uncertainty.

Score = EV − λ · Var

- λ = 0 → only EV matters  
- higher λ → safer options become more attractive
        """
    )

# ---------------------------
# Global settings
# ---------------------------
unit = st.selectbox(
    "Unit of measure",
    ["None", "€", "$", "hours", "points"]
)
unit_display = fmt_unit(unit)

num_options = st.number_input(
    "How many options do you want to compare?",
    min_value=2,
    max_value=6,
    value=2,
    step=1
)

risk_aversion = st.slider(
    "Risk aversion (λ)",
    min_value=0.0,
    max_value=1.0,
    value=0.10,
    step=0.01,
    help="λ = 0 means you only care about EV. Higher λ penalizes risk more."
)

st.caption("Tip: Start with λ = 0.1. Try changing it to see how the recommendation changes.")

# ---------------------------
# Inputs for N options
# ---------------------------
st.divider()
st.subheader("Define your options")

default_outcomes = ["10€, 0€", "6€, 6€", "12€, -2€", "8€, 3€", "15€, -5€", "5€, 5€"]
default_probs = ["0.5, 0.5", "1, 0", "0.7, 0.3", "0.6, 0.4", "0.5, 0.5", "1, 0"]

options_raw = []

for i in range(int(num_options)):
    st.header(f"Option {i + 1}")

    name = st.text_input(
        f"Name (optional) for Option {i + 1}",
        value=f"Option {i + 1}",
        key=f"name_{i}",
        help="Example: 'Job A', 'Investment B', 'Plan C'..."
    )

    outcomes_str = st.text_input(
        f"Outcomes for {name} (comma-separated)",
        value=default_outcomes[i] if i < len(default_outcomes) else "10, 0",
        key=f"outcomes_{i}",
        help="You can include units like €, $, hours, etc. Example: '10€, 0€' or '10 hours, 0 hours'."
    )

    probs_str = st.text_input(
        f"Probabilities for {name} (comma-separated)",
        value=default_probs[i] if i < len(default_probs) else "0.5, 0.5",
        key=f"probs_{i}",
        help="Probabilities must match outcomes length and sum to 1 (e.g., '0.5, 0.5')."
    )

    options_raw.append((name, outcomes_str, probs_str))

# ---------------------------
# Compute
# ---------------------------
if st.button("Compute"):
    try:
        results = []

        for idx, (name, outcomes_str, probs_str) in enumerate(options_raw, start=1):
            outcomes = parse_list(outcomes_str)
            probs = parse_list(probs_str)

            if len(outcomes) != len(probs):
                st.error(f"{name}: outcomes and probabilities must have the same length.")
                st.stop()

            ok, msg = validate_probs(probs)
            if not ok:
                st.error(f"{name}: {msg}")
                st.stop()

            ev, var, score = risk_adjusted_score(outcomes, probs, risk_aversion)
            results.append(
                {
                    "Option": name,
                    "EV": ev,
                    "Var": var,
                    "Score": score,
                }
            )

        # Sort by score descending
        results_sorted = sorted(results, key=lambda r: r["Score"], reverse=True)

        st.divider()
        st.subheader("Results (sorted by score)")

        # Display: keep EV/Score with unit, Var without unit for clarity
        display_rows = []
        for r in results_sorted:
            display_rows.append(
                {
                    "Option": r["Option"],
                    f"EV {unit_display}".strip(): round(r["EV"], 2),
                    "Var": round(r["Var"], 2),
                    f"Score {unit_display}".strip(): round(r["Score"], 2),
                }
            )

        st.dataframe(display_rows, use_container_width=True)

        # Recommendation
        st.divider()
        st.subheader("Recommendation")

        best = results_sorted[0]
        # Tie handling: if top 2 are extremely close
        if len(results_sorted) >= 2 and abs(results_sorted[0]["Score"] - results_sorted[1]["Score"]) < 1e-9:
            st.info("Tie: multiple options have the same score.")
        else:
            st.success(f"Best choice: **{best['Option']}** (highest risk-adjusted score).")

        st.caption("Model: Score = EV − λ · Var")

    except ValueError:
        st.error("Please enter valid numbers separated by commas (e.g., 10, 0).")

