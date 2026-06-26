import os
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# Data and Model Paths
# ---------------------------------------------------------------------------
_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(_DIR, "amazon_products_sales_data_cleaned.csv")
MODELS_CACHE_DIR = os.path.join(_DIR, "models_cache")

# Create cache directory if it doesn't exist
os.makedirs(MODELS_CACHE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Hardcoded accuracy metrics from Models.ipynb cell 99 (TF-IDF + Classifiers)
# ALL classifiers are trained on TF-IDF text features of combined_text
# ---------------------------------------------------------------------------
MODEL_METRICS = {
    "Logistic Regression": {
        "Accuracy": 77.87,
        "Precision": 80.59,
        "Recall": 79.19,
        "F1 Score": 79.88,
        "Training Time": "0.09s"
    },
    "Decision Tree": {
        "Accuracy": 72.13,
        "Precision": 74.09,
        "Recall": 76.51,
        "F1 Score": 75.28,
        "Training Time": "0.04s"
    },
    "Random Forest": {
        "Accuracy": 79.20,
        "Precision": 79.69,
        "Recall": 83.89,
        "F1 Score": 81.74,
        "Training Time": "0.15s"
    },
    "KNN": {
        "Accuracy": 78.40,
        "Precision": 79.57,
        "Recall": 82.17,
        "F1 Score": 80.85,
        "Training Time": "0.02s"
    },
    "SVC": {
        "Accuracy": 79.36,
        "Precision": 82.39,
        "Recall": 79.87,
        "F1 Score": 81.11,
        "Training Time": "37.54s"
    },
    "NLP-based Recommendation": {
        "Accuracy": 79.36,
        "Precision": 82.39,
        "Recall": 79.87,
        "F1 Score": 81.11,
        "Training Time": "37.54s"
    }
}

# Module-level cache so expensive operations only run once per session
_cache = {}

def _load_dataset() -> pd.DataFrame:
    """Load the cleaned dataset from CSV."""
    if "raw_df" not in _cache:
        df = pd.read_csv(DATASET_PATH)
        cols_to_drop = [
            'product_image_url', 'product_page_url', 'data_collected_at', 
            'delivery_date', 'sustainability_tags', 'buy_box_availability'
        ]
        df.drop(columns=cols_to_drop, errors='ignore', inplace=True)
        df.drop_duplicates(inplace=True)
        _cache["raw_df"] = df
    return _cache["raw_df"].copy()

# ===================================================================
# 1. NLP-based Content Recommendation (TF-IDF + Cosine Similarity)
# ===================================================================

def _build_nlp_recommendation_engine():
    """
    Build or load TF-IDF matrix for content-based product recommendation.
    Returns (rec_df, tfidf_vectorizer, tfidf_matrix, index_series).
    """
    if "nlp_engine" in _cache:
        return _cache["nlp_engine"]

    nlp_path = os.path.join(MODELS_CACHE_DIR, "nlp_engine.joblib")
    if os.path.exists(nlp_path):
        try:
            engine = joblib.load(nlp_path)
            _cache["nlp_engine"] = engine
            return engine
        except Exception:
            pass

    df = _load_dataset()

    rec_df = df.drop_duplicates(subset="product_title").copy()
    rec_df.reset_index(drop=True, inplace=True)

    rec_df["combined_text"] = (
        rec_df["product_title"].astype(str) + " " +
        rec_df["product_category"].astype(str) + " " +
        rec_df["is_best_seller"].astype(str) + " " +
        rec_df["is_sponsored"].astype(str) + " " +
        rec_df["has_coupon"].astype(str)
    )

    from sklearn.feature_extraction.text import TfidfVectorizer
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(rec_df["combined_text"])
    indices = pd.Series(rec_df.index, index=rec_df["product_title"])

    engine = (rec_df, tfidf, tfidf_matrix, indices)
    try:
        joblib.dump(engine, nlp_path, compress=9)
    except Exception:
        pass

    _cache["nlp_engine"] = engine
    return engine

def recommend_products_nlp(product_name: str, top_n: int = 5) -> pd.DataFrame:
    """
    Given an exact product title, return the top-N most similar products
    using TF-IDF cosine similarity computed dynamically.
    """
    rec_df, tfidf, tfidf_matrix, indices = _build_nlp_recommendation_engine()

    if product_name not in indices:
        return pd.DataFrame()

    idx = indices[product_name]
    query_vec = tfidf_matrix[idx]
    
    sim_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    sim_scores = list(enumerate(sim_scores))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1: top_n + 1]

    product_indices = [i[0] for i in sim_scores]
    scores = [round(i[1] * 100, 2) for i in sim_scores]

    result = rec_df.iloc[product_indices][[
        "product_title", "product_category",
        "product_rating", "discounted_price",
        "discount_percentage"
    ]].copy()
    result["match_score"] = scores
    result.reset_index(drop=True, inplace=True)
    return result

def search_products_nlp(query: str, top_n: int = 5) -> pd.DataFrame:
    """
    Free-text search: transform the query with the fitted TF-IDF vectorizer,
    compute cosine similarity dynamically against every product, and return top matches.
    """
    rec_df, tfidf, tfidf_matrix, _ = _build_nlp_recommendation_engine()

    query_vec = tfidf.transform([query])
    sim_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

    top_indices = sim_scores.argsort()[::-1][:top_n]

    result = rec_df.iloc[top_indices][[
        "product_title", "product_category",
        "product_rating", "discounted_price",
        "discount_percentage"
    ]].copy()
    result["match_score"] = [round(sim_scores[i] * 100, 2) for i in top_indices]
    result.reset_index(drop=True, inplace=True)
    return result

def get_all_product_titles() -> list:
    """Return a sorted list of all unique product titles."""
    rec_df, *_ = _build_nlp_recommendation_engine()
    return sorted(rec_df["product_title"].unique().tolist())

def get_all_categories() -> list:
    """Return a sorted list of all unique product categories."""
    df = _load_dataset()
    return sorted(df["product_category"].unique().tolist())

# ===================================================================
# 2. Classification-based prediction — ALL use TF-IDF pipelines
# ===================================================================

# Map display names to cache filenames
_ALGO_FILE_MAP = {
    "Logistic Regression": "logistic_regression",
    "Decision Tree":        "decision_tree",
    "Random Forest":        "random_forest",
    "KNN":                  "knn",
    "SVC":                  "svc",
}

def predict_recommendation_status(
    total_reviews: float,
    purchased_last_month: float,
    discounted_price: float,
    original_price: float,
    is_best_seller: str,
    is_sponsored: str,
    has_coupon: str,
    product_category: str,
    discount_percentage: float,
    algorithm: str = "Random Forest",
    product_title: str = ""
):
    """
    Load pre-trained TF-IDF classification pipeline and predict whether
    a product is recommended. Returns (prediction_label, confidence, metrics).
    """
    # Build combined text (same schema as training)
    combined_text = f"{product_title} {product_category} {is_best_seller} {is_sponsored} {has_coupon}"

    # Resolve filename for the algorithm
    model_filename = _ALGO_FILE_MAP.get(algorithm)
    if model_filename is None:
        raise ValueError(f"Unknown algorithm: {algorithm}. Valid options: {list(_ALGO_FILE_MAP.keys())}")

    model_path = os.path.join(MODELS_CACHE_DIR, f"clf_{model_filename}.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model for '{algorithm}' not found at {model_path}. Run train_models.py first."
        )

    # Load encoders for label inverse transform
    encoders_path = os.path.join(MODELS_CACHE_DIR, "encoders.joblib")
    if not os.path.exists(encoders_path):
        raise FileNotFoundError("Encoders not found in cache. Run train_models.py first.")
    encoders = joblib.load(encoders_path)

    # Load the TF-IDF pipeline and predict
    pipeline = joblib.load(model_path)
    prediction = pipeline.predict([combined_text])[0]
    label = encoders["rating_encoder"].inverse_transform([prediction])[0]

    # Predict probability/confidence if available
    confidence = None
    if hasattr(pipeline, "predict_proba"):
        proba = pipeline.predict_proba([combined_text])[0]
        confidence = round(max(proba) * 100, 2)

    metrics = MODEL_METRICS.get(algorithm, {})
    return label, confidence, metrics


def get_all_model_metrics() -> pd.DataFrame:
    """Return a DataFrame with pre-computed model metrics from models.ipynb."""
    rows = []
    for model_name, metrics in MODEL_METRICS.items():
        if model_name != "NLP-based Recommendation":
            rows.append({
                "Model": model_name,
                "Accuracy": metrics["Accuracy"],
                "Precision": metrics["Precision"],
                "Recall": metrics["Recall"],
                "F1 Score": metrics["F1 Score"],
                "Training Time": metrics["Training Time"]
            })
    return pd.DataFrame(rows).sort_values("Accuracy", ascending=False).reset_index(drop=True)
