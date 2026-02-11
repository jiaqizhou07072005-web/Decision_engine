import streamlit as st

st.set_page_config(page_title="About", page_icon="ℹ️")

st.title("ℹ️ About the model")

st.markdown(
    """
## Model
For each option, we compute:

- **Expected Value (EV)**: average outcome
- **Variance (Var)**: uncertainty proxy
- **Risk-adjusted score**:  
  **Score = EV − λ · Var**

## Why it’s useful
The app helps you compare options when outcomes are uncertain and you want a clear, consistent criterion.

## Limitations
- Uses variance as a simplified risk proxy (doesn’t capture all human preferences).
- Requires probability estimates from the user.
- One-shot model (no sequential decisions / learning).
    """
)
