import joblib
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import pandas as pd
import numpy as np

# load classifiers
EI_model = joblib.load("ei_model.joblib")
SN_model = joblib.load("sn_model.joblib")
TF_model = joblib.load("tf_model.joblib")
JP_model = joblib.load("jp_model.joblib")

# load embedding model
embed_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def predict_EI(question_id, user_answer):
    # prepare input as used during training
    text = f"Q: {question_id} A: {user_answer}"

    # get embedding
    # [text] equivalent to using tolist()
    embedding = embed_model.encode([text], convert_to_numpy=True)

    # predict label
    prob_E = EI_model.predict_proba(embedding)[0][1]

    if prob_E >= 0.5:
        pred_label = "E"
    else:
        pred_label = "I"

    return pred_label, prob_E

def predict_SN(question_id, user_answer):
    text = f"Q: {question_id} A: {user_answer}"

    embeddings = embed_model.encode([text], convert_to_numpy=True)

    prob_S = SN_model.predict_proba(embeddings)[0][1]

    if prob_S >= 0.5:
        pred_label = "S"
    else:
        pred_label = "N"

    return pred_label, prob_S

def predict_TF(question_id, user_answer):
    text = f"Q: {question_id} A: {user_answer}"

    embeddings = embed_model.encode([text], convert_to_numpy=True)

    prob_T = TF_model.predict_proba(embeddings)[0][1]

    if prob_T >= 0.5:
        pred_label = "T"
    else:
        pred_label = "F"

    return pred_label, prob_T

def predict_JP(question_id, user_answer):
    text = f"Q: {question_id} A: {user_answer}"

    embeddings = embed_model.encode([text], convert_to_numpy=True)

    prob_J = JP_model.predict_proba(embeddings)[0][1]

    if prob_J >= 0.5:
        pred_label = "J"
    else:
        pred_label = "P"

    return pred_label, prob_J

def predict_dichotomy(question_id, user_answer, dichotomy):
    text = f"Q: {question_id} A: {user_answer}"

    embedding = embed_model.encode([text], convert_to_numpy=True)

    if dichotomy == "E/I":
        prob = EI_model.predict_proba(embedding)[0][1]

        if prob >= 0.5:
            pred_label = "E"
        else:
            pred_label = "I"
    elif dichotomy == "S/N":
        prob = SN_model.predict_proba(embedding)[0][1]

        if prob >= 0.5:
            pred_label = "S"
        else:
            pred_label = "N"
    elif dichotomy == "T/F":
        prob = TF_model.predict_proba(embedding)[0][1]

        if prob >= 0.5:
            pred_label = "T"
        else:
            pred_label = "F"
    elif dichotomy == "J/P":
        prob = JP_model.predict_proba(embedding)[0][1]

        if prob >= 0.5:
            pred_label = "J"
        else:
            pred_label = "P"

    return pred_label, prob

# user_input = "I usually keep to myself unless someone talks to me first."
# label, probability = predict_EI(38, user_input)

# print(label, probability)