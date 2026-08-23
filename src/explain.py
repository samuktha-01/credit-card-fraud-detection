import joblib
import pandas as pd
import shap


# Load model
model = joblib.load("models/fraud_model.pkl")

# Load dataset
data = pd.read_csv("data/creditcard.csv")

# Create SHAP explainer
explainer = shap.TreeExplainer(model)


def explain_transaction(row_number):

    # Check transaction number
    if row_number < 0 or row_number >= len(data):
        raise ValueError("Transaction number is out of range")

    # Get transaction
    transaction = data.iloc[[row_number]]

    # Remove actual target
    features = transaction.drop(columns=["Class"])

    # Prediction
    prediction = int(model.predict(features)[0])

    # Fraud probability
    probability = float(
        model.predict_proba(features)[0][1]
    )

    # SHAP values
    shap_values = explainer.shap_values(features)

    # Get values for this transaction
    values = shap_values[0]

    # Feature names
    feature_names = features.columns.tolist()

    # Build explanation
    explanation = []

    for feature, value in zip(feature_names, values):

        explanation.append({
            "feature": feature,
            "shap_value": float(value),
            "direction": (
                "FRAUD"
                if value > 0
                else "NORMAL"
            )
        })

    # Sort by absolute impact
    explanation.sort(
        key=lambda x: abs(x["shap_value"]),
        reverse=True
    )

    return {
        "transaction_id": row_number,
        "prediction": (
            "FRAUD"
            if prediction == 1
            else "NORMAL"
        ),
        "fraud_probability": probability,
        "explanations": explanation
    }


if __name__ == "__main__":

    result = explain_transaction(541)

    print(result)