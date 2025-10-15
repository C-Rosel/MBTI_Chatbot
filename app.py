import streamlit as st
from streamlit_chat import message


st.set_page_config(
    page_title="AI Project: TherapyBot", 
    layout="wide"
)


if 'user_inputs' not in st.session_state:
    st.session_state['user_inputs'] = []
if 'bot_responses' not in st.session_state:
    st.session_state['bot_responses'] = []
if 'question_index' not in st.session_state:
    st.session_state['question_index'] = 0


placeholders = [
    "Welcome, let's try to figure you out! How are you feeling today?",
    "Placeholder question"
]


st.title("TherapyBot")


for i in range(len(st.session_state['bot_responses'])):
    message(st.session_state['bot_responses'][i], key=str(i))
    if i < len(st.session_state['user_inputs']):
        message(st.session_state['user_inputs'][i], is_user=True, key=str(i) + '_user')


user_input = st.chat_input("Type your answer here...")
    # def get_text():
    #     input_text = st.text_input("You: ","Hello, how are you?", key="input")
    #     return input_text 


    # user_input = get_text()


if user_input:
    st.session_state['user_inputs'].append(user_input)

    
    if st.session_state['question_index'] < len(placeholders) - 1:
        st.session_state['question_index'] += 1
        bot_response = placeholders[st.session_state['question_index']]
    else:
        bot_response = "Thanks for answering! I’ll now analyze your cognitive functions."

    st.session_state['bot_responses'].append(bot_response)
    st.rerun()
