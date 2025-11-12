import streamlit as st
from streamlit_chat import message
import time
import pandas as pd
import numpy as np
import random
import json 
from pathlib import Path

from core.prediction_functions import predict_dichotomy
from core.scoring import determine_final_score

st.set_page_config(
    page_title="AI Project: TherapyBot", 
    layout="wide"
)
 

def process_user_input(user_input, question_id, dichotomy=None):
    # Call models from core, dichotomy logic implemented there
    try:
        # Use provided dichotomy or get from session state, default to E/I (not ideal but better than getting an eror)
        if dichotomy is None:
            dichotomy = st.session_state.get("current_dichotomy", "E/I")
        
        # calling model function from core.prediction_functions
        label, prob = predict_dichotomy(question_id, user_input, dichotomy)
        
        # nice and pretty for update_scores
        return {
            dichotomy: {"label": label, "prob": prob}
        } #this return is saved into 'analysis'
    except Exception as e: #some error handling
        st.error(f"Error processing input: {e}")
        return None

def update_scores(current_scores, analysis): #curr scores is dict in SS, analysis from above!
    # here we keep track of scores across dichotomies for assess_results
    if analysis is None:
        return current_scores #empty meaning no user input to assess :3
    
    for dichotomy, prediction in analysis.items():
        if dichotomy not in current_scores:
            current_scores[dichotomy] = {"labels": [], "probs": []} 
        
        # appending the predicted label and probability
        current_scores[dichotomy]["labels"].append(prediction["label"])
        current_scores[dichotomy]["probs"].append(prediction["prob"])
    
    return current_scores #da loop, so we keep building on this until all questions are answered

def assess_results():
    # call scoring logic and display results for user

    scores = st.session_state.get('scores', {}) # all 20 questions processed
    
    if not scores or not any(scores.values()): # error handling fairy 
        st.warning("No assessment data available.")
        return
    
    st.markdown("## Assessment Results") #FIXME make this pretty later with the fonts when the work :(((
    st.markdown("Here is a summary of your personality assessment:")
    
    # calling scoring from core
    mbti_type, dichotomy_results = determine_final_score(scores)
    
    st.markdown("### Your MBTI Type: **" + mbti_type + "**")
    st.markdown("**Breakdown by dichotomy:**")
    
    # dichotomy breakdown w. confidence #FIXME makeit dropdowns???
    for dichotomy, result in dichotomy_results.items():
        label = result["label"]
        dominant_score = result["dominant_score"]
        other_score = result["other_score"]
        first_count = result["count_first"]
        second_count = result["count_second"]
        
        # Determine which trait is which for display
        trait_pair = dichotomy.split("/")
        first_trait = trait_pair[0]
        second_trait = trait_pair[1]
        
        # Display the trait scores as a balance
        st.markdown(
            f"- **{dichotomy}**: {label} "
            f"({dominant_score:.1%} confidence vs {other_score:.1%})"
        )
    
    
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
    response = random.choice( #i asked chat to make better anecdotes because mine were so awkward 
        [
        "I can see how that fits with what you’ve shared so far",
        "That really helps paint a clearer picture of how you move through the world",
        "You seem very self-aware about that — that’s great to see",
        "That’s consistent with the sense I’m getting from your other answers",
        "It sounds like that approach has served you well over time",
        "I can tell that’s something that comes naturally to you",
        "That adds a nice layer of insight into your personality",
        "You express that with a lot of clarity — it really shows your thought process",
        "That gives a good sense of your rhythm and how you like to handle things",
        "It sounds like you have a steady sense of what feels right for you",
        "I can feel the authenticity in that answer",
        "That response has a lot of grounded confidence behind it",
        "It feels like that choice really reflects your core way of operating",
        "That aligns nicely with the traits I’m picking up from you so far",
        "There’s a real sense of balance in how you describe yourself",
        "That comes across as very natural and true to your temperament",
        "It’s clear you’ve thought about what works best for you in those moments",
        "That perspective feels calm and intentional — very you",
        "That’s a thoughtful way of putting it, and it fits your tone perfectly",
        "I really like how genuine that answer feels"
        ]

    )
    return response 

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
    # display the current question and set session_state.current_q_id and current_dichotomy
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
    # store current id and dichotomy so next user response maps to it
    st.session_state.current_q_id = qid
    st.session_state.current_dichotomy = q.get("dichotomy", "E/I")  # default to E/I if missing
    return qid


def save_results():
    msg = st.toast("Saving results...")
    time.sleep(5)
    #FIXME implement actual saving logic
    # format a nice analysis with graphics maybe a word map!! that can be done with nlp 
    msg.toast("Results saved!")

#FIXME new session function? like a hard reset to avoid leftover values eh stretch goal
       

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

        analysis = process_user_input(resp, current_qid)  # nlp processing of user input
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
    
    assess_results() 

    if st.button("Save Results"):
        st.chat_message("athena").write("I'm saving your results now...")
        save_results()
    

else:
    # the convo: map user input to current question, advance, and present next question or assess
    if prompt := st.chat_input("Speak with Athena", max_chars=MAX_CHAR): #make into elif??

        user_name = st.session_state.get('user_name', None)
        current_qid = st.session_state.get("current_q_id")
        
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        analysis = process_user_input(prompt, current_qid)  # nlp processing of user input

        st.session_state['scores'] = update_scores(st.session_state.get('scores', {}), analysis) #update scores based on analysis

        will_respond = random.random() < 0.8 #80% chance to respond
        if will_respond:
            current_response = response_generator() + (f", {user_name}." if user_name else ".")
            st.chat_message("athena").write(current_response)
            #st.session_state.messages.append({"role": "athena", "content": current_response})

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
            assess_results() 
            # if st.button("Save Results"):
            #     st.chat_message("athena").write("I'm saving your results now...")
            #     save_results()
            st.chat_message("athena").write(f"Thank you for completing the assessment, {user_name}!" if user_name else "Thank you for completing the assessment!")


## RESULTS to be implemented bar graph? idk too many ideas
# with st.chat_message("assistant"):
#     st.write("Introvert-Extrovert Tendencies")
#     st.bar_chart(np.random.randn(30, 3)) #FIXME plot the weights of the E/I results
#     #Do the same for the other 3 dichotomies

