# Preprocesing architecture:
# * Prepare training data
# * Train a lightweight classifier
# * Embed user response (with all-mpnet-base-v2 (SentenceTransformers))
# * Pass embedding into your classifier to get E/I, S/N, ..., score
# * Get probability score for each dichotomy ({ "E": 0.92, "I": 0.08 })
# * Accumulate all answers and compute final MBTI (scoring)

# install required libraries
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import joblib
import pandas as pd
import numpy as np

# embedding example/testing from documentation using SentenceTransformer
# sentences = ["This is an example sentence", "Each sentence is converted"]

# model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
# embeddings = model.encode(sentences)
# print(embeddings)

# read labeled data
df = pd.read_json("data/jp_training.jsonl", lines=True)

# embedding model
embed_model = SentenceTransformer("embed_model_all_mpnet")

# adapt data to include question and aswer for training -> better accuracy
adapted_df = ("Q: " + df['question_id'].astype(str) + "A: " + df['text']).tolist()

# compute embeddings
embeddings = embed_model.encode(adapted_df, show_progress_bar=True, convert_to_numpy=True)

# E/I training
X = embeddings
y = (df["label"] == 'J').astype(int).values # label-based indexer, 1 = J, 0 = P

# 20% of data for testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# create Logistic Regression model
JP_model = LogisticRegression(max_iter=1000)

# train model
JP_model.fit(X_train, y_train)

# evaluate model
y_pred = JP_model.predict(X_test)
y_prob =  JP_model.predict_proba(X_test)[:,1]

print("Acc:", accuracy_score(y_test, y_pred))
print("AUC:", roc_auc_score(y_test, y_prob))
print(classification_report(y_test, y_pred))

# save model
joblib.dump(JP_model, "jp_model.joblib")