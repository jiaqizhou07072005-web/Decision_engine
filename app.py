import streamlit as st
from decision_model import risk_adjusted_score

st.title("Decision Engine")
st.write("Compare options under uncertainty using EV and a risk penalty (EV − λ·Var).")

st.subheader("Option A")
outcomes_a_str = st.text_input("Outcomes A (comma-separated)", value="10, 0")
probs_a_str = st.text_input("Probabilities A (comma-separated)", value="0.5, 0.5")

st.subheader("Option B")
outcomes_b_str = st.text_input("Outcomes B (comma-separated)", value="6, 6")
probs_b_str = st.text_input("Probabilities B (comma-separated)", value="1, 0")

risk_aversion = st.slider("Risk aversion (λ)", min_value=0.0, max_value=1.0, value=0.1, step=0.01)

def parse_list(s):
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

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Results — Option A")
            st.write(f"**Expected Value (EV):** {ev_a:.4f}")
            st.write(f"**Variance (Var):** {var_a:.4f}")
            st.write(f"**Score:** {score_a:.4f}")

        with col2:
            st.markdown("### Results — Option B")
            st.write(f"**Expected Value (EV):** {ev_b:.4f}")
            st.write(f"**Variance (Var):** {var_b:.4f}")
            st.write(f"**Score:** {score_b:.4f}")

        st.markdown("### Recommendation")
        if score_a > score_b:
            st.success("Pick **Option A** (higher risk-adjusted score).")
        elif score_b > score_a:
            st.success("Pick **Option B** (higher risk-adjusted score).")
        else:
            st.info("Tie: both options have the same score.")

        st.divider()
        st.subheader("Recommendation")

        if score_a > score_b:
            st.success("Option A has the higher risk-adjusted score.")
        elif score_b > score_a:
            st.success("Option B has the higher risk-adjusted score.")
        else:
            st.info("Both options have the same score.")


    except ValueError:
        st.error("Please enter valid numbers separated by commas (e.g., 10, 0).")
