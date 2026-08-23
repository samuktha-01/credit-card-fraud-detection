import joblib
import pandas as pd
import shap


# Load model
model = joblib.load("models/fraud_model.pkl")

print("Model loaded successfully!")


# Load dataset
data = pd.read_csv("data/creditcard.csv")


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