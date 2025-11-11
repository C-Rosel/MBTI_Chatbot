import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
import joblib
from sentence_transformers import SentenceTransformer

# load classifier
SN_model = joblib.load("models/sn_model.joblib")

# S/N
# read labeled data
df = pd.read_json("data/sn_training.jsonl", lines=True)

# embedding model
embed_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# adapt data to include question and aswer for training -> better accuracy
adapted_df = ("Q: " + df['question_id'].astype(str) + " A: " + df['text']).tolist()

# compute embeddings
embeddings = embed_model.encode(adapted_df, show_progress_bar=True, convert_to_numpy=True)

X = embeddings
y = (df["label"] == 'S').astype(int).values # label-based indexer, 1 = S, 0 = N

# 20% of data for testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# evaluate model
y_pred = SN_model.predict(X_test)
y_prob = SN_model.predict_proba(X_test)[:,1]

# accuracy
test_accuracy = accuracy_score(y_test, y_pred)
print(f"Test accuracy: {test_accuracy:.4f}")

# confusion matrix
conf_matrix = confusion_matrix(y_test, y_pred)

# detailed per-class metrics
print(classification_report(y_test, y_pred, target_names=['N', 'S']))

# visualize results
plt.figure(figsize=(6, 5))

sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Oranges', xticklabels=['N', 'S'], yticklabels=['N', 'S'])

plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('S/N Confusion Matrix')

plt.show()

