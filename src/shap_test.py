from pathlib import Path
import joblib
import pandas as pd
import shap

__test__ = False

# Project root directory and paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "fraud_model.pkl"
DATA_PATH = BASE_DIR / "data" / "creditcard.csv"

if __name__ == "__main__":
    # Load model
    model = joblib.load(MODEL_PATH)

    print("Model loaded successfully!")

    # Load dataset
    data = pd.read_csv(DATA_PATH)

    # Select transaction
    row_number = 541

    transaction = data.iloc[[row_number]].drop(columns=["Class"])

    # Create SHAP explainer
    explainer = shap.TreeExplainer(model)

    # Calculate SHAP values
    shap_values = explainer.shap_values(transaction)

    print("\nTransaction:", row_number)

    print("\nPrediction:")
    print(model.predict(transaction))

    print("\nFraud Probability:")
    print(model.predict_proba(transaction)[0][1])

    print("\nSHAP values:")
    print(shap_values)