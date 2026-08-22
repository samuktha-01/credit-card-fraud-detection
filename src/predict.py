import joblib
import pandas as pd

# Load trained model
model = joblib.load("models/fraud_model.pkl")


def predict_fraud(transaction):
    """
    Predict whether a credit card transaction is fraudulent.

    transaction should contain the same features
    used during model training.
    """

    # Convert transaction into a DataFrame
    transaction = pd.DataFrame([transaction])

    # Get fraud probability
    probability = model.predict_proba(transaction)[0][1]

    # Use 0.5 as the prediction threshold
    prediction = int(probability >= 0.5)

    if prediction == 1:
        result = "FRAUD"
    else:
        result = "NORMAL"

    return result, probability

