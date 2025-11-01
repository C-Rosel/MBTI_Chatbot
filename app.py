import streamlit as st
from streamlit_chat import message
import time
import pandas as pd
import numpy as np
import random
import json 
from pathlib import Path

from core.processing import process_user_input
from core.scoring import update_scores, assess_results

DATA_PATH = Path(__file__).parent / "data" / "MBTI_Questions.json"
if "questions" not in st.session_state:
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            st.session_state.questions = json.load(f) #add list of questions to session state! to be accessed later
    except FileNotFoundError:
        st.session_state.questions = []
        st.error(f"Questions file not found at: {DATA_PATH}")
    except json.JSONDecodeError as e:
        st.session_state.questions = []
        st.error(f"Error parsing questions JSON: {e}")

# streaming :))
def welcome_msg(): 
    for word in _WELCOME_MSG.split(" "):
        yield word + " "
        time.sleep(0.02)

def question_stream(text): 
    for word in text.split():
        yield word + " "
        time.sleep(0.05) #slower 

def response_generator(): #this is random bs go haha. we can make it better later
    response = random.choice(
        [
            "Interesting...",
            "Thank you for sharing",
            "Great, let's move on",
            "Good progress",
        ]

    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05) 


def select_questions_per_dichotomy(n=5): #n is number of questions per dichotomy
    # st.session_state.selected_question_ids: list of question ids (shuffled)
    # st.session_state.q_index: current index in that list
    # st.session_state.answers: dict mapping question id -> user answer

    questions = st.session_state.get("questions", []) #the second parameter is default value if key not found like on the first run btw!
    by_dich = {}
    for q in questions:
        d = q.get("dichotomy") #from the question metadata
        if not d:
            continue
        by_dich.setdefault(d, []).append(q)

    selected_ids = [] #random selections of q ids
    for d, qlist in by_dich.items():
        if not qlist:
            continue
        take = min(n, len(qlist))
        sampled = random.sample(qlist, take)
        selected_ids.extend([q["id"] for q in sampled])

    # Shuffle the final ordering so dichotomies are mixed
    random.shuffle(selected_ids)

    st.session_state.selected_question_ids = selected_ids #add random sample to session state
    st.session_state.q_index = 0 
    st.session_state.answers = {} #init empty answers dict


def get_question_by_id(qid): #fetch from big list of qs id from our sample set 
    for q in st.session_state.get("questions", []):
        if q.get("id") == qid:
            return q
    return None


def show_current_question():
    # display the current question and set session_state.current_q_id
    idx = st.session_state.get("q_index", 0)  
    ids = st.session_state.get("selected_question_ids", []) 
    if idx >= len(ids):
        return None
    qid = ids[idx]
    q = get_question_by_id(qid)
    if not q:
        return None
    question_text = q.get("question", "Question text missing.")
    # stream it~
    st.chat_message("athena").write_stream(question_stream(question_text))
    # store current id so next user response maps to it
    st.session_state.current_q_id = qid
    return qid


def save_results():
    msg = st.toast("Saving results...")
    time.sleep(5)
    #FIXME implement actual saving logic
    # format a nice analysis with graphics maybe a word map!! that can be done with nlp 
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


# for message in st.session_state.messages: #display msgs on app rerun eh perhaps not
#     with st.chat_message(message["role"]): #author
#         st.markdown(message["content"]) #content


user_message = st.chat_message("user") 

# begin sequence: welcome user, get name, select qs
if st.button("Begin"):
    
    st.chat_message("athena").write_stream(welcome_msg) #not saved for now.

    user_name = st.text_input("What is your name?") #FIXME list: add to sessiono_state, Athena uses it in responses, "Prefer not to say" button, If "Developer" feed in placeholder_responses for testing. 
    if st.button("Prefer not to say"):
        user_name = None
        st.session_state['user_name'] = user_name # or idk something to omit it from athena responses
        st.chat_message("athena").write_stream("Understood. Let's get started then. :)")
    if user_name:
        st.session_state['user_name'] = user_name
        st.chat_message("athena").write_stream("Nice to meet you, {user_name}! Let's get started then. :)")
        
    
    select_questions_per_dichotomy(5) #we can adjust the length of the assessment here
    # show first question
    qid = show_current_question()
    # record the displayed question into messages history so UI reruns can reuse it if needed
    if qid is not None:
        st.session_state.messages.append({"role": "athena", "content": get_question_by_id(qid).get("question")})

# the convo: map user input to current question, advance, and present next question or assess
if prompt := st.chat_input("Speak with Athena"):

    user_name = st.session_state.get('user_name', None)
    user_message.markdown(prompt) 
    st.session_state.messages.append({"role": "user", "content": prompt})

    analysis = process_user_input(prompt) #nlp processing of user input #FIXME expand this to do actual analysis

    st.session_state['scores'] = update_scores(st.session_state.get('scores', {}), analysis) #update scores based on analysis


    #placeholder Athena response 
    with st.chat_message("athena"):
        current_response = response_generator() + ", {user_name}." if user_name else response_generator()
        st.chat_message("athena").write_stream(current_response)

    # map user answer to curr q in the dict
    current_qid = st.session_state.get("current_q_id")
    if current_qid is not None:
        st.session_state.answers[current_qid] = prompt #map q id to user answer


    st.session_state.q_index = st.session_state.get("q_index", 0) + 1 # NEXT!

    # cont or end assessment
    if st.session_state.q_index < len(st.session_state.get("selected_question_ids", [])): #curr to end of sample
        next_qid = show_current_question()
        if next_qid is not None:
            st.session_state.messages.append({"role": "athena", "content": get_question_by_id(next_qid).get("question")})
    else:
        st.chat_message("athena").write("Thank you for completing the assessment, {user_name}!" if user_name else "Thank you for completing the assessment!")
        assess_results() #FIXME implement this to show final results
        if st.button("Save Results"):
            st.chat_message("athena").write("I'm saving your results now...")
            save_results()


## RESULTS to be implemented bar graph? idk too many ideas
# with st.chat_message("assistant"):
#     st.write("Introvert-Extrovert Tendencies")
#     st.bar_chart(np.random.randn(30, 3)) #FIXME plot the weights of the E/I results
#     #Do the same for the other 3 dichotomies

