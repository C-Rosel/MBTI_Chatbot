import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
import joblib
from sentence_transformers import SentenceTransformer

# load classifiers
EI_model = joblib.load("models/ei_model.joblib")
SN_model = joblib.load("models/sn_model.joblib")
TF_model = joblib.load("models/tf_model.joblib")
JP_model = joblib.load("models/jp_model.joblib")


# E/I
# read labeled data
ei_df = pd.read_json("data/ei_training.jsonl", lines=True)

# embedding model
embed_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# adapt data to include question and aswer for training -> better accuracy
ei_adapted_df = ("Q: " + ei_df['question_id'].astype(str) + " A: " + ei_df['text']).tolist()

# compute embeddings
ei_embeddings = embed_model.encode(ei_adapted_df, show_progress_bar=True, convert_to_numpy=True)

# E/I training
ei_X = ei_embeddings
ei_y = (ei_df["label"] == 'E').astype(int).values # label-based indexer, 1 = E, 0 = I

# 20% of data for testing
X_train, X_test, y_train, y_test = train_test_split(ei_X, ei_y, test_size=0.2, random_state=42, stratify=ei_y)

# evaluate model
y_pred = EI_model.predict(X_test)
y_prob = EI_model.predict_proba(X_test)[:,1]

# accuracy
test_accuracy = accuracy_score(y_test, y_pred)
print(f"Test accuracy: {test_accuracy:.4f}")

# confusion matrix
ei_conf_matrix = confusion_matrix(y_test, y_pred)

# detailed per-class metrics
print(classification_report(y_test, y_pred, target_names=['I', 'E']))

# visualize results
plt.figure(figsize=(6, 5))

sns.heatmap(ei_conf_matrix, annot=True, fmt='d', cmap='Oranges', xticklabels=['I', 'E'], yticklabels=['I', 'E'])

plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('E/I Confusion Matrix')

plt.show()

