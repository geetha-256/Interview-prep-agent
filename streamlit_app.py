import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go

BACKEND = "http://127.0.0.1:8000"
ASSIGNMENT_FILE_URL = "/mnt/data/AI Agent Building Assignment - Eightfold.pdf"

st.set_page_config(page_title="Interview Practice Agent", layout="centered")
st.title("Interview Practice Agent")

# session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "history" not in st.session_state:
    st.session_state.history = []
if "questions" not in st.session_state:
    st.session_state.questions = []


role = st.selectbox("Role", ["software_engineer", "sales", "retail_associate"])
num_q = st.slider("Number of questions", 3, 10, 6)

if st.button("Start Interview"):
    try:
        r = requests.post(
            f"{BACKEND}/start",
            json={"role": role, "num_questions": num_q, "assignment_file_url": ASSIGNMENT_FILE_URL},
            timeout=10,
        )
        if r.status_code != 200:
            st.error(f"Backend error: {r.status_code}")
            st.text(r.text)
        else:
            data = r.json()
            st.session_state.session_id = data.get("session_id")
            st.session_state.history = [{"q": data.get("first_question"), "a": ""}]
            st.session_state.questions = data.get("questions", [])
    except Exception as e:
        st.error("Could not contact backend: " + str(e))

st.markdown("---")

if not st.session_state.session_id:
    st.info("Start the interview to see questions here.")
else:
    for i, item in enumerate(st.session_state.history):
        st.markdown(f"**Q{i+1}:** {item.get('q')}")
        st.write(f"**A{i+1}:** {item.get('a') or '_(not answered yet)_'}")

    answer = st.text_area("Your answer")

    if st.button("Submit Answer"):
        try:
            r = requests.post(
                f"{BACKEND}/answer",
                json={"session_id": st.session_state.session_id, "user_answer": answer, "assignment_file_url": ASSIGNMENT_FILE_URL},
                timeout=30,
            )
            if r.status_code != 200:
                st.error(f"Backend error: {r.status_code}")
                st.text(r.text)
            else:
                data = r.json()
                if data.get("agent_reply") == "NEXT":
                    nxt = data.get("next_question")
                    st.session_state.history[-1]["a"] = answer
                    st.session_state.history.append({"q": nxt, "a": ""})
                elif data.get("agent_reply") == "FINISH":
                    st.session_state.history[-1]["a"] = answer
                    st.success("Interview finished.")
                else:
                    st.session_state.history[-1]["a"] = answer
                    ar = data.get("agent_reply")
                    if isinstance(ar, str) and ar:
                        st.session_state.history.append({"q": ar, "a": ""})
                    else:
                        st.warning("No agent reply; check backend logs.")
        except Exception as e:
            st.error("Request failed: " + str(e))

st.markdown("---")

# Feedback block 
def render_feedback(feedback_response: dict):
    """
    Expects the backend feedback response with keys:
      - feedback_text (string)
      - feedback (dict) possibly containing 'scores' dict with numeric scores
    """
    fb_text = feedback_response.get("feedback_text") or ""
    fb_struct = feedback_response.get("feedback") or {}

    st.header("Feedback")
    if fb_text:
        st.markdown(fb_text)

    # Try to get numeric scores
    scores = None
    if isinstance(fb_struct, dict) and "scores" in fb_struct and isinstance(fb_struct["scores"], dict):
        scores = fb_struct["scores"]
    else:
        if isinstance(fb_struct, dict):
            candidate = {k: v for k, v in fb_struct.items() if isinstance(v, (int, float))}
            if candidate:
                scores = candidate

    if scores:
        # build dataframe for display
        df = pd.DataFrame(list(scores.items()), columns=["Category", "Score"])
        # Ensure numeric dtype
        df["Score"] = pd.to_numeric(df["Score"], errors="coerce").fillna(0)

        # Plotly bar chart
        fig = go.Figure(go.Bar(x=df["Category"], y=df["Score"]))
        fig.update_layout(
            title="Score breakdown",
            yaxis=dict(range=[0, 5], title="Score (1-5)"),
            xaxis_title="Category",
            margin=dict(t=40, l=10, r=10, b=30),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

        # show table below chart
        st.table(df.set_index("Category"))

    # Raw structured feedback (collapsible)
    with st.expander("Show full feedback JSON"):
        st.json(fb_struct)

    # Download button for feedback JSON
    full_export = {"feedback_text": fb_text, "feedback": fb_struct}
    st.download_button("Download feedback (JSON)", data=json.dumps(full_export, indent=2), file_name="feedback.json", mime="application/json")


if st.button("Get Feedback (End Interview)"):
    if not st.session_state.session_id:
        st.error("No active session")
    else:
        try:
            r = requests.post(f"{BACKEND}/feedback", json={"session_id": st.session_state.session_id}, timeout=30)
            if r.status_code != 200:
                st.error(f"Backend error: {r.status_code}")
                st.text(r.text)
            else:
                fb = r.json()
                render_feedback(fb)
        except Exception as e:
            st.error("Request failed: " + str(e))
