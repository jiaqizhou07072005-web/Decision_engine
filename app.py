import streamlit as st
from decision_model import risk_adjusted_score

st.set_page_config(page_title="Decision Engine")
st.title("Decision Engine")
st.write("Answer a few questions and the app will compare **Option A vs Option B** under uncertainty.")

with st.expander("What do these terms mean? (click to expand)"):
    st.markdown(
        """
- **Outcome**: a possible result (e.g., +10€, 0€, -5€).
- **Probability**: how likely that outcome is (all probabilities must sum to **1**).
- **Expected Value (EV)**: the average result you’d get if you repeated the choice many times.
- **Variance (Var)**: how “risky / spread out” the outcomes are.
- **Risk aversion (λ)**: how much you penalize risk. Higher λ = you dislike uncertainty more.
        """
    )

st.header("1) Define Option A")
st.caption("Option A is the first choice you want to evaluate (e.g., job offer A, investment A, plan A).")

outcomes_a_str = st.text_input(
    "A) Outcomes (comma-separated)",
    value="10, 0",
    help="Example: '10, 0' means either you get 10 or you get 0."
)

probs_a_str = st.text_input(
    "A) Probabilities (comma-separated)",
    value="0.5, 0.5",
    help="Probabilities must match the outcomes and sum to 1. Example: '0.5, 0.5'."
)

st.header("2) Define Option B")
st.caption("Option B is the alternative choice you want to compare against Option A.")

outcomes_b_str = st.text_input(
    "B) Outcomes (comma-separated)",
    value="6, 6",
    help="Example: '6, 6' means the outcome is always 6 (no uncertainty)."
)

probs_b_str = st.text_input(
    "B) Probabilities (comma-separated)",
    value="1, 0",
    help="Example: '1, 0' means the first outcome always happens."
)

st.header("3) How risk-averse are you?")
risk_aversion = st.slider(
    "Risk aversion (λ)",
    min_value=0.0,
    max_value=1.0,
    value=0.10,
    step=0.01,
    help="λ = 0 means you only care about EV. Higher λ penalizes risk more."
)

st.caption("Tip: Start with λ = 0.1. Try changing it to see how the recommendation changes.")

def parse_list(s: str):
    return [float(x.strip()) for x in s.split(",") if x.strip()]

def validate_probs(probs):
    if len(probs) == 0:
        return False, "Probabilities list is empty."
    if any(p < 0 for p in probs):
        return False, "Probabilities cannot be negative."
    total = sum(probs)
    if abs(total - 1.0) > 1e-6:
        return False, f"Probabilities must sum to 1. Current sum = {total:.6f}"
    return True, ""

if st.button("Compute"):
    try:
        outcomes_a = parse_list(outcomes_a_str)
        probs_a = parse_list(probs_a_str)
        outcomes_b = parse_list(outcomes_b_str)
        probs_b = parse_list(probs_b_str)

        if len(outcomes_a) != len(probs_a):
            st.error("Option A: outcomes and probabilities must have the same length.")
            st.stop()
        if len(outcomes_b) != len(probs_b):
            st.error("Option B: outcomes and probabilities must have the same length.")
            st.stop()

        ok_a, msg_a = validate_probs(probs_a)
        ok_b, msg_b = validate_probs(probs_b)
        if not ok_a:
            st.error(f"Option A: {msg_a}")
            st.stop()
        if not ok_b:
            st.error(f"Option B: {msg_b}")
            st.stop()

        ev_a, var_a, score_a = risk_adjusted_score(outcomes_a, probs_a, risk_aversion)
        ev_b, var_b, score_b = risk_adjusted_score(outcomes_b, probs_b, risk_aversion)

        st.divider()
        st.subheader("Results")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Option A")
            st.write(f"**Expected Value (EV):** {ev_a:.4f}")
            st.write(f"**Variance (Var):** {var_a:.4f}")
            st.write(f"**Risk-adjusted score:** {score_a:.4f}")

        with col2:
            st.markdown("### Option B")
            st.write(f"**Expected Value (EV):** {ev_b:.4f}")
            st.write(f"**Variance (Var):** {var_b:.4f}")
            st.write(f"**Risk-adjusted score:** {score_b:.4f}")

        st.divider()
        st.subheader("Recommendation")
        if score_a > score_b:
            st.success("Pick **Option A** (higher risk-adjusted score).")
        elif score_b > score_a:
            st.success("Pick **Option B** (higher risk-adjusted score).")
        else:
            st.info("Both options have the same score.")

        st.caption("The score is computed as: Score = EV − λ · Var")

    except ValueError:
        st.error("Please enter valid numbers separated by commas (e.g., 10, 0).")
