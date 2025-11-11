import joblib
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import pandas as pd
import numpy as np

from prediction_functions import predict_JP

user_input = "guide events through careful planning and choice"
label, probability = predict_JP(27, user_input)

print(label, probability)