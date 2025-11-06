import streamlit as st
from streamlit_chat import message
import time
import pandas as pd
import numpy as np
import random
import json 
from pathlib import Path

#from core.preprocessing import process_user_input
#from core.scoring import update_scores, assess_results

st.set_page_config(
    page_title="AI Project: TherapyBot", 
    layout="wide"
)

#FIXME Placeholder functions: Remove once real functions are implemented

def process_user_input(user_input):
    # Placeholder: In real implementation, analyze the input text
    # For demo, return random analysis
    analysis = {
        "E/I": random.choice(["E", "I"]),
        "S/N": random.choice(["S", "N"]),
        "T/F": random.choice(["T", "F"]),
        "J/P": random.choice(["J", "P"]),
    }
    return analysis

def update_scores(current_scores, analysis):
    # Placeholder: Update scores based on analysis
    for dichotomy, trait in analysis.items():
        current_scores[dichotomy] = current_scores.get(dichotomy, {})
        current_scores[dichotomy][trait] = current_scores[dichotomy].get(trait, 0) + 1
    return current_scores

def assess_results():
    # Placeholder: Display final results based on scores
    scores = st.session_state.get('scores', {})
    st.markdown("## Assessment Results")
    st.markdown("Here is a summary of your personality assessment:")
    tally = {}
    for dichotomy, traits in scores.items():
        dominant_trait = max(traits, key=traits.get)
        tally[dichotomy] = dominant_trait
    st.markdown("**Your dominant traits by dichotomy:**")
    for d, t in tally.items():
        st.markdown(f"- {d}: {t}")
    st.markdown("**Your answers:**")
    answers = st.session_state.get('answers', {})
    for qid, ans in answers.items():
        q = get_question_by_id(qid)
        st.markdown(f"- **Q {qid}** ({q.get('dichotomy') if q else '??'}): {ans}")
    st.markdown("**Simple tally by dichotomy (demo):**")
    for d, c in tally.items():
        st.markdown(f"- {d}: {c}")
    st.markdown("\n_Add a scoring algorithm to convert these into MBTI letters._")

# consts 
MAX_CHAR = 150

_WELCOME_MSG = """
Disclaimer: This is an AI not a licensed mental health professional. This is purely for entertainment purposes only.
Your personal data will not be stored or kept beyond the session. 

Hello, there. My name is Athena, I'm here to help you assess your personality and learn more about yourself.
We'll go through some questions to dig into what makes up who you are! Please answer conscisely and honestly!
""" #but make it nice :) athena name

DATA_PATH = Path(__file__).parent / "data" / "MBTI_Questions.json"

PLACEHOLDER_RESPONSES = Path(__file__).parent / "testing" / "placeholder_responses.json"
 
# session state inits (persistent across reruns)

if "dev_mode" not in st.session_state:
    dev_mode = False

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

if "messages" not in st.session_state:
    st.session_state.messages = []

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

#rand functions

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

#FIXME new session function? like a hard reset to avoid leftover values
       

# for message in st.session_state.messages: #display msgs on app rerun eh perhaps not
#     with st.chat_message(message["role"]): #author
#         st.markdown(message["content"]) #content


# state tracking flags
if "begun" not in st.session_state:
    st.session_state["begun"] = False
if "name_confirmed" not in st.session_state:
    st.session_state["name_confirmed"] = False
if "questions_selected" not in st.session_state:
    st.session_state["questions_selected"] = False

# begin sequence: welcome user, get name, select qs
if st.button("Begin"):
    # mark that we've started the flow and stream the welcome message
    st.session_state["begun"] = True
    st.session_state["name_confirmed"] = False
    st.session_state["questions_selected"] = False
    st.chat_message("athena").write_stream(welcome_msg)

# one flag down, two to go. need name
if st.session_state.get("begun") and not st.session_state.get("name_confirmed"):
    # use a persistent text input bound to session_state so it survives reruns
    st.text_input("What is your name?", key="name_input", max_chars=MAX_CHAR)

    cols = st.columns([1, 1]) # formatting buttons side by side
    with cols[0]:
        if st.button("Submit Name"):
            provided = st.session_state.get("name_input", "").strip() # roundabout wayyyyy
            if provided == "Developer":
                st.session_state['user_name'] = "Developer"
                st.session_state['dev_mode'] = True
            else:
                st.session_state['user_name'] = provided
                st.session_state['dev_mode'] = False

            st.session_state["name_confirmed"] = True #thats two down
            greeting = f"Nice to meet you, {st.session_state.get('user_name') or 'friend'}! Let's get started then. :)"
            st.chat_message("athena").write_stream(question_stream(greeting))

    with cols[1]:
        if st.button("Prefer not to say"):
            st.session_state['user_name'] = None
            st.session_state['dev_mode'] = False
            st.session_state["name_confirmed"] = True
            st.chat_message("athena").write_stream(question_stream("Understood. Let's get started then. :)"))

# and finally we select questions 
if st.session_state.get("name_confirmed") and not st.session_state.get("questions_selected"):
    select_questions_per_dichotomy(5)
    st.session_state["questions_selected"] = True
    # show first question
    qid = show_current_question()
    if qid is not None:
        st.session_state.messages.append({"role": "athena", "content": get_question_by_id(qid).get("question")})

if st.session_state.get('dev_mode', False) == True:
    try:
        with open(PLACEHOLDER_RESPONSES, "r", encoding="utf-8") as f:
            dev_responses = json.load(f) 
    except FileNotFoundError:
        dev_responses = []
        st.error(f"Questions file not found at: {PLACEHOLDER_RESPONSES}")
    except json.JSONDecodeError as e:
        dev_responses = []
        st.error(f"Error parsing questions JSON: {e}")

    dev_dict = {item['question_id']: item['response'] for item in dev_responses}

    # Fill remaining developer responses in one pass (avoid blocking while loop which hangs Streamlit)
    remaining_ids = st.session_state.get("selected_question_ids", [])[st.session_state.get('q_index', 0):]
    for current_qid in remaining_ids:
        # get developer response for this question id (skip if missing)
        resp = dev_dict.get(current_qid)
        if resp is None:
            # skip missing test data
            st.session_state.q_index = st.session_state.get("q_index", 0) + 1
            continue

        st.session_state.answers[current_qid] = resp
        with st.chat_message("developer"):
            st.markdown(resp)
        st.session_state.messages.append({"role": "developer", "content": resp})

        analysis = process_user_input(resp)  # nlp processing of user input (placeholder)
        st.session_state['scores'] = update_scores(st.session_state.get('scores', {}), analysis)

        # advance index and show next question (non-blocking)
        st.session_state.q_index = st.session_state.get("q_index", 0) + 1
        next_qid = show_current_question()
        if next_qid is not None:
            st.session_state.messages.append({"role": "athena", "content": get_question_by_id(next_qid).get("question")})


    st.chat_message("athena").write("All assessment answers have been filled in, Developer.")
    time.sleep(1)
    st.chat_message("athena").write("Final scoring is next...")
    time.sleep(2)
    
    assess_results() #FIXME implement this to show final results

    if st.button("Save Results"):
        st.chat_message("athena").write("I'm saving your results now...")
        save_results()
    

else:
    # the convo: map user input to current question, advance, and present next question or assess
    if prompt := st.chat_input("Speak with Athena", max_chars=MAX_CHAR): #make into elif??

        user_name = st.session_state.get('user_name', None)
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        analysis = process_user_input(prompt) #nlp processing of user input #FIXME expand this to do actual analysis

        st.session_state['scores'] = update_scores(st.session_state.get('scores', {}), analysis) #update scores based on analysis

        #placeholder Athena response
        # current_response = response_generator() + ", {user_name}." if user_name else response_generator()
        # st.chat_message("athena").write_stream(current_response) #maybe a random probability of athena responding at all. 

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

