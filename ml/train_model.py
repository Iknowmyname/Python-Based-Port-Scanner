# ml/train_model.py
import argparse, joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

def load_data(path):
    df = pd.read_csv(path)
    X_text = df['banner'].fillna("").astype(str)
    y = df['label'].astype(str).values
    return X_text, y

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="ml/train_data.csv")
    p.add_argument("--out", default="ml/model_baseline.pkl")
    args = p.parse_args()

    X_text, y = load_data(args.data)
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_text, y, test_size=0.2, stratify=None, random_state=42
    )

    model = make_pipeline(TfidfVectorizer(ngram_range=(1,2), max_features=20000), LogisticRegression(max_iter=2000, class_weight='balanced'))
    model.fit(X_train_text, y_train)

    preds = model.predict(X_test_text)
    print("CLASSIFICATION REPORT:\n")
    print(classification_report(y_test, preds))
    print("CONFUSION MATRIX:\n", confusion_matrix(y_test, preds))

    joblib.dump(model, args.out)
    print("Saved", args.out)
