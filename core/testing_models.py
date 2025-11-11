import joblib
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import pandas as pd
import numpy as np

SN_model = joblib.load("sn_model.joblib")

embed_model = SentenceTransformer("embed_model_all_mpnet")

def predict_SN(question_id, user_answer):
    text = f"Q: {question_id} A: {user_answer}"

    embeddings = embed_model.encode([text], convert_to_numpy=True)

    prob_S = SN_model.predict_proba(embeddings)[0][1]

    if prob_S >= 0.5:
        pred_label = "S"
    else:
        pred_label = "N"

    return pred_label, prob_S

user_input = "I appreciate more nuanced, layered conversations"
label, probability = predict_SN(17, user_input)

print(label, probability)