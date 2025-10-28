import streamlit as st
from streamlit_chat import message
import time
import pandas as pd
import numpy as np
import random
import json 
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "MBTI_Questions.json"
if "questions" not in st.session_state:
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            st.session_state.questions = json.load(f)
    except FileNotFoundError:
        st.session_state.questions = []
        st.error(f"Questions file not found at: {DATA_PATH}")
    except json.JSONDecodeError as e:
        st.session_state.questions = []
        st.error(f"Error parsing questions JSON: {e}")

def welcome_msg():
    for word in _WELCOME_MSG.split(" "):
        yield word + " "
        time.sleep(0.02)

def response_generator():
    response = random.choice(
        [
            "Interesting...",
            "Oh, I see.",
            "Great, let's move on",
            "Good progress",
            "Thank you for the insight",
        ]

    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


def select_questions_per_dichotomy(n=5):
    """Select up to `n` random question ids for each dichotomy and store them in session state.

    Stores:
      - st.session_state.selected_question_ids: list of question ids (shuffled)
      - st.session_state.q_index: current index in that list
      - st.session_state.answers: dict mapping question id -> user answer
    """
    questions = st.session_state.get("questions", [])
    by_dich = {}
    for q in questions:
        d = q.get("dichotomy")
        if not d:
            continue
        by_dich.setdefault(d, []).append(q)

    selected_ids = []
    for d, qlist in by_dich.items():
        if not qlist:
            continue
        take = min(n, len(qlist))
        sampled = random.sample(qlist, take)
        selected_ids.extend([q["id"] for q in sampled])

    # Shuffle the final ordering so dichotomies are mixed
    random.shuffle(selected_ids)

    st.session_state.selected_question_ids = selected_ids
    st.session_state.q_index = 0
    st.session_state.answers = {}


def get_question_by_id(qid):
    for q in st.session_state.get("questions", []):
        if q.get("id") == qid:
            return q
    return None


def question_stream(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.05)


def show_current_question():
    """Display the current question (streamed) and set session_state.current_q_id."""
    idx = st.session_state.get("q_index", 0)
    ids = st.session_state.get("selected_question_ids", [])
    if idx >= len(ids):
        return None
    qid = ids[idx]
    q = get_question_by_id(qid)
    if not q:
        return None
    question_text = q.get("question", "Question text missing.")
    # stream the question text in a new Athena chat message
    st.chat_message("athena").write_stream(question_stream(question_text))
    # store current id so next user response maps to it
    st.session_state.current_q_id = qid
    return qid


def assess_results():
    """Very small placeholder assessment: shows collected answers and counts per dichotomy.

    A real scoring function should replace this.
    """
    answers = st.session_state.get("answers", {})
    # Build a simple tally by dichotomy using the original question metadata
    tally = {}
    for qid, ans in answers.items():
        q = get_question_by_id(qid)
        if not q:
            continue
        d = q.get("dichotomy", "unknown")
        tally.setdefault(d, 0)
        # Naive: count non-empty answers as +1 for demonstration
        if isinstance(ans, str) and ans.strip():
            tally[d] += 1

    # Display results
    with st.chat_message("athena"):
        st.markdown("### Assessment complete")
        st.markdown("**Answers collected:**")
        for qid, ans in answers.items():
            q = get_question_by_id(qid)
            st.markdown(f"- **Q {qid}** ({q.get('dichotomy') if q else '??'}): {ans}")
        st.markdown("**Simple tally by dichotomy (demo):**")
        for d, c in tally.items():
            st.markdown(f"- {d}: {c}")
        st.markdown("\n_Add a scoring algorithm to convert these into MBTI letters._")

def save_results():
    msg = st.toast("Saving results...")
    time.sleep(5)
    #FIXME implement actual saving logic
    msg.toast("Results saved!")

_WELCOME_MSG = """
Hello, there. My name is Athena, I'm here to help you assess your personality and learn more about yourself.
We'll go through some questions to dig into what makes up who you are! Please answer conscisely and honestly!

Disclaimer: This is an AI not a licensed mental health professional. This is purely for entertainment purposes only.
Your personal data will not be stored or kept beyond the session. 

When you are ready to begin, please click the 'Begin' button below.
""" #but make it nice :) athena name
        
st.set_page_config(
    page_title="AI Project: TherapyBot", 
    layout="wide"
)

if "messages" not in st.session_state:
    st.session_state.messages = []


# for message in st.session_state.messages: #display msgs on app rerun
#     with st.chat_message(message["role"]): #author
#         st.markdown(message["content"]) #content


# Don't stream the welcome message at import time (blocks server startup).
# Stream the welcome message only when the user clicks Begin.

user_message = st.chat_message("user")

# Begin button: prepare selected questions and show first one
if st.button("Begin"):
    # stream a short welcome from Athena (non-blocking long-running work should be avoided at import)
    st.chat_message("athena").write_stream(welcome_msg)

    select_questions_per_dichotomy(5)
    # show first question
    qid = show_current_question()
    # record the displayed question into messages history so UI reruns can reuse it if needed
    if qid is not None:
        st.session_state.messages.append({"role": "athena", "content": get_question_by_id(qid).get("question")})

# React to user input: map user input to current question, advance, and present next question or assess
if prompt := st.chat_input("Speak with Athena"):
    # Display user message in chat message container
    user_message.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Map answer to current question id
    current_qid = st.session_state.get("current_q_id")
    if current_qid is not None:
        st.session_state.answers[current_qid] = prompt

    # Advance index
    st.session_state.q_index = st.session_state.get("q_index", 0) + 1

    # If there are more questions, show next one; otherwise run assessment
    if st.session_state.q_index < len(st.session_state.get("selected_question_ids", [])):
        next_qid = show_current_question()
        if next_qid is not None:
            st.session_state.messages.append({"role": "athena", "content": get_question_by_id(next_qid).get("question")})
    else:
        assess_results()


if st.button("Save Results"):
    save_results()

## RESULTS to be implemented
# with st.chat_message("assistant"):
#     st.write("Introvert-Extrovert Tendencies")
#     st.bar_chart(np.random.randn(30, 3)) #FIXME plot the weights of the E/I results
#     #Do the same for the other 3 dichotomies
