"""
SWYNEX Final AI Application - Model Training Script
Trains TF-IDF + Logistic Regression announcement classifier on curated dataset
and serializes the pipeline to models/announcement_classifier.joblib.
"""

import sys
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def train_and_save():
    data_path = PROJECT_ROOT / "data" / "sample_announcements.csv"
    model_path = PROJECT_ROOT / "models" / "announcement_classifier.joblib"

    print(f"[1/3] Loading dataset from: {data_path}")
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    df = pd.read_csv(data_path)
    print(f"      Loaded {len(df)} announcements across categories: {df['category'].unique().tolist()}")

    print("[2/3] Constructing TF-IDF + Logistic Regression pipeline...")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=2500,
            sublinear_tf=True,
            stop_words="english",
        )),
        ("clf", LogisticRegression(
            C=1.5,
            max_iter=300,
            class_weight="balanced",
            random_state=42
        )),
    ])

    pipeline.fit(df["text"].tolist(), df["category"].tolist())
    print("      Model training complete.")

    print(f"[3/3] Serializing model to: {model_path}")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"SUCCESS: Announcement classifier successfully saved to {model_path}")


if __name__ == "__main__":
    train_and_save()
