import pandas as pd
import numpy as np
import pickle
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import os

# Paths
DATA_PATH = 'data/final_triage_data_50k_v2.csv'
MODEL_PATH = 'triage_xgboost_v2.pkl'

def train_model(data_path=DATA_PATH, model_path=MODEL_PATH):
    print(f"Loading Dataset from {data_path}...")
    try:
        df = pd.read_csv(data_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        return False, str(e)
    
    # 1. Encoders
    le_dict = {}
    cat_cols = ['Gender', 'Symptoms', 'Consciousness', 'Pre_Existing_Conditions']
    
    # Ensure all required columns exist
    required_cols = cat_cols + ['Age', 'Blood_Pressure', 'Heart_Rate', 'Temperature', 'O2_Saturation', 'Pain_Severity', 'Risk_Level']
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        return False, f"Missing columns in CSV: {missing}"

    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        le_dict[col] = le
        
    # Target Encoding
    le_risk = LabelEncoder()
    df['Risk_Level'] = le_risk.fit_transform(df['Risk_Level'].astype(str))
    
    X = df[['Age', 'Gender', 'Symptoms', 'Blood_Pressure', 'Heart_Rate', 'Temperature', 'O2_Saturation', 'Pain_Severity', 'Consciousness', 'Pre_Existing_Conditions']]
    y = df['Risk_Level']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train XGBoost
    print("Training XGBoost...")
    model = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=len(le_risk.classes_),
        n_estimators=200,
        learning_rate=0.1,
        max_depth=6,
        eval_metric='mlogloss',
        use_label_encoder=False
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n🏆 Model Accuracy: {acc * 100:.2f}%")
    
    # Save
    # os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump({
            'model': model,
            'le_dict': le_dict,
            'le_risk': le_risk
        }, f)
    print(f"✅ Model saved to {model_path}")
    return True, {"accuracy": acc, "path": model_path}

if __name__ == "__main__":
    train_model()
