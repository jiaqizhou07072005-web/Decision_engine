import re
import json
import io
import csv
import streamlit as st
from decision_model import risk_adjusted_score

st.set_page_config(page_title="Decision Engine", page_icon="🎯", layout="wide")

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

def unit_display(unit: str):
    return "" if unit == "None" else unit

def init_state():
    if "scenarios" not in st.session_state:
        st.session_state.scenarios = {}  # name -> payload
    if "last_results" not in st.session_state:
        st.session_state.last_results = None  # list of dict

def get_current_payload(num_options: int):
    payload = {
        "unit": st.session_state.unit,
        "risk_aversion": st.session_state.risk_aversion,
        "num_options": int(num_options),
        "options": []
    }
    for i in range(int(num_options)):
        name = st.session_state.get(f"name_{i}", f"Option {i+1}")
        outcomes = st.session_state.get(f"outcomes_{i}", "")
        probs = st.session_state.get(f"probs_{i}", "")
        payload["options"].append({"name": name, "outcomes": outcomes, "probs": probs})
    return payload

def load_payload(payload):
    st.session_state.unit = payload.get("unit", "None")
    st.session_state.risk_aversion = float(payload.get("risk_aversion", 0.10))
    st.session_state.num_options = int(payload.get("num_options", 2))
    options = payload.get("options", [])
    for i, opt in enumerate(options):
        st.session_state[f"name_{i}"] = opt.get("name", f"Option {i+1}")
        st.session_state[f"outcomes_{i}"] = opt.get("outcomes", "")
        st.session_state[f"probs_{i}"] = opt.get("probs", "")

def results_to_csv_bytes(rows):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    return output.getvalue().encode("utf-8")

# ---------------------------
# App
# ---------------------------
init_state()

st.title("🎯 Decision Engine")
st.write("A mini decision-support product to compare multiple options under uncertainty.")

# ---------------------------
# Sidebar (Product controls)
# ---------------------------
st.sidebar.header("Controls")

st.sidebar.selectbox(
    "Unit of measure",
    ["None", "€", "$", "hours", "points"],
    key="unit"
)
st.sidebar.slider(
    "Risk aversion (λ)",
    min_value=0.0,
    max_value=1.0,
    value=0.10,
    step=0.01,
    key="risk_aversion",
    help="λ = 0 means you only care about EV. Higher λ penalizes risk more."
)

st.sidebar.number_input(
    "Number of options",
    min_value=2,
    max_value=6,
    value=2,
    step=1,
    key="num_options"
)

st.sidebar.divider()
st.sidebar.subheader("Scenarios")

scenario_name = st.sidebar.text_input("Scenario name", value="My scenario", key="scenario_name")

col_save, col_load = st.sidebar.columns(2)
with col_save:
    if st.button("Save", use_container_width=True, key="save_scenario"):
        payload = get_current_payload(st.session_state.num_options)
        st.session_state.scenarios[scenario_name] = payload
        st.sidebar.success("Saved.")

with col_load:
    scenario_list = ["—"] + sorted(st.session_state.scenarios.keys())
    chosen = st.selectbox("Load", scenario_list, key="scenario_to_load", label_visibility="collapsed")
    if chosen != "—" and st.button("Apply", use_container_width=True, key="apply_scenario"):
        load_payload(st.session_state.scenarios[chosen])
        st.sidebar.success("Loaded.")

st.sidebar.divider()
st.sidebar.subheader("Import / Export")
st.sidebar.divider()
st.sidebar.subheader("Reset")

if st.sidebar.button("Clear all", key="clear all"):
    for key in list(st.session_state.keys()):
        if key.startswith(("name_", "outcomes_", "probs_")):
            del st.session_state[key]

    st.session_state.num_options = 2
    st.session_state.risk_aversion = 0.10
    st.session_state.unit = "None"

    st.sidebar.success("All inputs cleared.")
    st.rerun()

# Export current scenario JSON
payload_json = json.dumps(get_current_payload(st.session_state.num_options), indent=2)
st.sidebar.download_button(
        "Download scenario (.json)",
        data=payload_json.encode("utf-8"),
        file_name="decision_engine_scenario.json",
        mime="application/json",
        use_container_width=True,
        key="download_scenario_json"
        ) 


uploaded = st.sidebar.file_uploader(
    "Import scenario (.json)",
    type=["json"],
    key="upload_scenario_json"
)

if uploaded is not None:
    try:
        imported = json.load(uploaded)
        load_payload(imported)
        st.sidebar.success("Imported.")
    except Exception:
        st.sidebar.error("Invalid JSON file.")

# ---------------------------
# Explanations
# ---------------------------
with st.expander("What do these terms mean?"):
    st.markdown(
        """
### Expected Value (EV)
Average result if you repeated the decision many times.

### Variance (Var)
How *unpredictable* outcomes are (higher = more uncertainty).

### Risk aversion (λ)
How much you penalize uncertainty:
**Score = EV − λ · Var**
        """
    )
# ---------------------------
# Inputs
# ---------------------------
    st.subheader("Define your options")

defaults = [
    {"name": "Option 1", "outcomes": "10€, 0€", "probs": "0.5, 0.5"},
    {"name": "Option 2", "outcomes": "6€, 6€", "probs": "1, 0"},
    {"name": "Option 3", "outcomes": "12€, -2€", "probs": "0.7, 0.3"},
    {"name": "Option 4", "outcomes": "8€, 3€", "probs": "0.6, 0.4"},
    {"name": "Option 5", "outcomes": "15€, -5€", "probs": "0.5, 0.5"},
    {"name": "Option 6", "outcomes": "5€, 5€", "probs": "1, 0"},
]

for i in range(int(st.session_state.num_options)):
    with st.container(border=True):
        cols = st.columns([1, 2, 2])
        with cols[0]:
            st.text_input(
                f"Name",
                value=st.session_state.get(f"name_{i}", defaults[i]["name"]),
                key=f"name_{i}"
            )
        with cols[1]:
            st.text_input(
                "Outcomes (comma-separated)",
                value=st.session_state.get(f"outcomes_{i}", defaults[i]["outcomes"]),
                key=f"outcomes_{i}",
                help="You can include units like €, $, hours, etc. Example: '10€, 0€'."
            )
        with cols[2]:
            st.text_input(
                "Probabilities (comma-separated)",
                value=st.session_state.get(f"probs_{i}", defaults[i]["probs"]),
                key=f"probs_{i}",
                help="Must match outcomes length and sum to 1 (e.g., '0.5, 0.5')."
            )

    # ---------------------------
    # Compute + Output
    # ---------------------------
if st.button("Compute", type="primary", key="compute"):
    try:
        results = []
        u = unit_display(st.session_state.unit)

        for i in range(int(st.session_state.num_options)):
            name = st.session_state.get(f"name_{i}", f"Option {i+1}")
            outcomes = parse_list(st.session_state.get(f"outcomes_{i}", ""))
            probs = parse_list(st.session_state.get(f"probs_{i}", ""))

            if len(outcomes) != len(probs):
                st.error(f"{name}: outcomes and probabilities must have the same length.")
                st.stop()

            ok, msg = validate_probs(probs)
            if not ok:
                st.error(f"{name}: {msg}")
                st.stop()

            ev, var, score = risk_adjusted_score(outcomes, probs, st.session_state.risk_aversion)

            results.append({
                "Option": name,
                "EV": round(ev, 2),
                "Var": round(var, 2),
                "Score": round(score, 2)
            })
        # Sort by Score
        results_sorted = sorted(results, key=lambda r: r["Score"], reverse=True)
        st.session_state.last_results = results_sorted

        st.divider()
        st.subheader("Results (sorted by score)")

        # Display table with units on EV/Score
        display_rows = []
        for r in results_sorted:
            display_rows.append({
                "Option": r["Option"],
                f"EV {u}".strip(): r["EV"],
                "Var": r["Var"],
                f"Score {u}".strip(): r["Score"],
            })

            st.dataframe(display_rows, use_container_width=True)

            st.divider()
            st.subheader("Recommendation")
            best = results_sorted[0]
            st.success(f"Best choice: **{best['Option']}** (highest risk-adjusted score).")
            st.caption("Model: Score = EV − λ · Var")

                # Export CSV of results
            csv_bytes = results_to_csv_bytes(display_rows)
            st.download_button(
            "Download results (CSV)",
            data=csv_bytes,
            file_name="decision_engine_results.csv",
            mime="text/csv",
            key="download_results_csv_main"
        )

    except ValueError:
        st.error("Please enter valid numbers separated by commas (e.g., 10, 0).")
