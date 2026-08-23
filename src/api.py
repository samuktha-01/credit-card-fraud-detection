from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.explain import explain_transaction

from .predict import predict_fraud


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Dataset path
DATA_PATH = BASE_DIR / "data" / "creditcard.csv"


# Create FastAPI application
app = FastAPI(title="Credit Card Fraud Detection API")


# Allow frontend to communicate with API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Transaction(BaseModel):
    Time: float

    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float

    Amount: float


@app.get("/")
def home():
    return {
        "message": "Credit Card Fraud Detection API is running"
    }


@app.post("/predict")
def predict(transaction: Transaction):

    transaction_data = transaction.model_dump()

    result, probability = predict_fraud(transaction_data)

    return {
        "prediction": result,
        "fraud_probability": float(probability)
    }


@app.get("/demo/normal")
def demo_normal():

    data = pd.read_csv(DATA_PATH)

    transaction = data.iloc[20000].drop("Class").to_dict()

    result, probability = predict_fraud(transaction)

    return {
        "prediction": result,
        "fraud_probability": float(probability)
    }


@app.get("/demo/fraud")
def demo_fraud():

    data = pd.read_csv(DATA_PATH)

    transaction = data.iloc[541].drop("Class").to_dict()

    result, probability = predict_fraud(transaction)

    return {
        "prediction": result,
        "fraud_probability": float(probability)
    }

@app.get("/transaction/{row_number}")
def analyze_transaction(row_number: int):

    # Check that the requested row exists
    data = pd.read_csv(DATA_PATH)

    if row_number < 0 or row_number >= len(data):
        return {
            "error": "Transaction number is out of range"
        }

    # Get the transaction
    transaction = data.iloc[row_number].drop("Class").to_dict()

    # Actual label from dataset
    actual_result = "FRAUD" if data.iloc[row_number]["Class"] == 1 else "NORMAL"

    # Model prediction
    prediction, probability = predict_fraud(transaction)

    # Risk classification
    if probability >= 0.90:
        risk = "CRITICAL"
    elif probability >= 0.70:
        risk = "HIGH"
    elif probability >= 0.30:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "transaction_id": row_number,
        "prediction": prediction,
        "fraud_probability": float(probability),
        "risk_level": risk,
        "actual_result": actual_result
    }

@app.get("/explain/{row_number}")
def explain(row_number: int):
    try:
        return explain_transaction(row_number)

    except ValueError as error:
        return {
            "error": str(error)
        }

    except Exception as error:
        return {
            "error": "Unable to generate explanation",
            "details": str(error)
        }

@app.get("/transactions")
def recent_transactions():

    data = pd.read_csv(DATA_PATH)

    # Selected transactions for the monitoring dashboard.
    # These are historical dataset rows, not live bank transactions.
    selected_rows = [
        20000,
        541,
        284797,
        284798,
        284799,
        284800,
        284801,
        284802,
        284803,
        284804
    ]

    transactions = []

    for row_number in selected_rows:

        # Make sure the row exists
        if row_number < 0 or row_number >= len(data):
            continue

        transaction = (
            data.iloc[row_number]
            .drop("Class")
            .to_dict()
        )

        # Run the actual XGBoost model
        prediction, probability = predict_fraud(transaction)

        # Determine risk level
        if probability >= 0.90:
            risk = "CRITICAL"

        elif probability >= 0.70:
            risk = "HIGH"

        elif probability >= 0.30:
            risk = "MEDIUM"

        else:
            risk = "LOW"

        transactions.append({
            "transaction_id": row_number,
            "prediction": prediction,
            "fraud_probability": float(probability),
            "risk_level": risk
        })

    return {
        "transactions": transactions
    }