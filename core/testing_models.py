import joblib
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import pandas as pd
import numpy as np

JP_model = joblib.load("jp_model.joblib")

embed_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def predict_JP(question_id, user_answer):
    text = f"Q: {question_id} A: {user_answer}"

    embeddings = embed_model.encode([text], convert_to_numpy=True)

    prob_J = JP_model.predict_proba(embeddings)[0][1]

    if prob_J >= 0.5:
        pred_label = "J"
    else:
        pred_label = "P"

    return pred_label, prob_J

user_input = "guide events through careful planning and choice"
label, probability = predict_JP(27, user_input)

print(label, probability)