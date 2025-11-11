import joblib
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import pandas as pd
import numpy as np

TF_model = joblib.load("tf_model.joblib")

embed_model = SentenceTransformer("embed_model_all_mpnet")

def predict_TF(question_id, user_answer):
    text = f"Q: {question_id} A: {user_answer}"

    embeddings = embed_model.encode([text], convert_to_numpy=True)

    prob_T = TF_model.predict_proba(embeddings)[0][1]

    if prob_T >= 0.5:
        pred_label = "T"
    else:
        pred_label = "F"

    return pred_label, prob_T

user_input = "With others and with myself, I tend to be more firm and objective"
label, probability = predict_TF(33, user_input)

print(label, probability)