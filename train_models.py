import os
import time
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline

def main():
    print("=" * 60)
    print("STARTING MODEL TRAINING AND CACHING PIPELINE")
    print("All classifiers trained on TF-IDF text features")
    print("=" * 60)
    
    # Paths
    dir_path = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(dir_path, "amazon_products_sales_data_cleaned.csv")
    cache_dir = os.path.join(dir_path, "models_cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    # 1. Load and clean dataset
    print("-> Loading and preprocessing dataset...")
    df = pd.read_csv(dataset_path)
    
    # Drop columns not used in modeling
    cols_to_drop = [
        'product_image_url', 'product_page_url', 'data_collected_at', 
        'delivery_date', 'sustainability_tags', 'buy_box_availability'
    ]
    df.drop(columns=cols_to_drop, errors='ignore', inplace=True)
    df.drop_duplicates(inplace=True)
    df.dropna(subset=['product_rating'], inplace=True)
    
    # Fill remaining NaNs with median
    for col in ['total_reviews', 'purchased_last_month', 'discounted_price', 'original_price', 'discount_percentage']:
        df[col] = df[col].fillna(df[col].median())
        
    df.reset_index(drop=True, inplace=True)
    
    # Create target label (1 = Recommended (>= 4.5), 0 = Not Recommended (< 4.5))
    df["rating_class"] = df["product_rating"].apply(lambda r: "Recommended" if r >= 4.5 else "Not Recommended")
    
    # Define combined_text for text classification (same as Models.ipynb)
    df['combined_text'] = (
        df['product_title'].astype(str) + ' ' +
        df['product_category'].astype(str) + ' ' +
        df['is_best_seller'].astype(str) + ' ' +
        df['is_sponsored'].astype(str) + ' ' +
        df['has_coupon'].astype(str)
    )
    
    # 2. Encode the target label
    print("-> Encoding target labels...")
    rating_encoder = LabelEncoder()
    df['rating_class_enc'] = rating_encoder.fit_transform(df['rating_class'].astype(str))
    
    # Save the rating encoder for inference
    encoders = {"rating_encoder": rating_encoder}
    joblib.dump(encoders, os.path.join(cache_dir, "encoders.joblib"), compress=9)
    print("   Saved encoders.joblib (compressed).")
    
    # 3. Prepare TF-IDF text features
    X_text = df["combined_text"]
    y = df["rating_class_enc"]
    
    # Split dataset (same as notebook: test_size=0.2, random_state=42, stratify=y)
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_text, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 4. Train ALL classifiers as TF-IDF pipeline (matching Models.ipynb cell 99)
    text_classifiers = {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight='balanced'),
        "decision_tree": DecisionTreeClassifier(random_state=42, class_weight='balanced'),
        "random_forest": RandomForestClassifier(random_state=42, class_weight='balanced'),
        "knn": KNeighborsClassifier(),
        "svc": SVC(class_weight='balanced')
    }
    
    for model_name, clf in text_classifiers.items():
        print(f"-> Training TF-IDF {model_name} classifier pipeline...")
        t0 = time.time()
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english', max_features=5000)),
            ('clf', clf)
        ])
        pipeline.fit(X_train_text, y_train)
        elapsed = round(time.time() - t0, 2)
        
        model_path = os.path.join(cache_dir, f"clf_{model_name}.joblib")
        joblib.dump(pipeline, model_path, compress=9)
        print(f"   Saved clf_{model_name}.joblib in {elapsed}s (compressed pipeline).")
        
    # 5. Build and cache NLP content similarity engine
    print("-> Training NLP content similarity engine...")
    from sklearn.metrics.pairwise import cosine_similarity as _cs
    rec_df = df.drop_duplicates(subset="product_title").copy()
    rec_df.reset_index(drop=True, inplace=True)
    
    tfidf_rec = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf_rec.fit_transform(rec_df["combined_text"])
    indices = pd.Series(rec_df.index, index=rec_df["product_title"])
    
    nlp_engine = (rec_df, tfidf_rec, tfidf_matrix, indices)
    joblib.dump(nlp_engine, os.path.join(cache_dir, "nlp_engine.joblib"), compress=9)
    print("   Saved nlp_engine.joblib (compressed).")
    
    print("=" * 60)
    print("ALL MODELS HAVE BEEN SUCCESSFULLY TRAINED & CACHED!")
    print("=" * 60)

if __name__ == "__main__":
    main()
