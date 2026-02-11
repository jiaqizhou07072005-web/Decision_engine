import streamlit as st

st.set_page_config(page_title="Examples")

st.title("Examples")
st.write("Click an example to auto-fill the main app (go back to **Decision Engine** page afterwards).")

examples = {
    "Investment (risky vs stable)": {
        "unit": "€",
        "risk_aversion": 0.10,
        "num_options": 3,
        "options": [
            {"name": "Startup bet", "outcomes": "2000€, -500€", "probs": "0.2, 0.8"},
            {"name": "Index fund", "outcomes": "300€, 50€", "probs": "0.6, 0.4"},
            {"name": "Savings", "outcomes": "100€, 100€", "probs": "1, 0"},
        ],
    },
    "Study plan (time payoff)": {
        "unit": "hours",
        "risk_aversion": 0.15,
        "num_options": 2,
        "options": [
            {"name": "Plan A", "outcomes": "8 hours saved, 0", "probs": "0.6, 0.4"},
            {"name": "Plan B", "outcomes": "5 hours saved, 5 hours saved", "probs": "1, 0"},
        ],
    },
}

def load_payload(payload):
    st.session_state.unit = payload["unit"]
    st.session_state.risk_aversion = float(payload["risk_aversion"])
    st.session_state.num_options = int(payload["num_options"])
    for i, opt in enumerate(payload["options"]):
        st.session_state[f"name_{i}"] = opt["name"]
        st.session_state[f"outcomes_{i}"] = opt["outcomes"]
        st.session_state[f"probs_{i}"] = opt["probs"]

for title, payload in examples.items():
    if st.button(f"Load: {title}", use_container_width=True):
        load_payload(payload)
        st.success("Loaded. Now go back to the **Decision Engine** page and press Compute.")
