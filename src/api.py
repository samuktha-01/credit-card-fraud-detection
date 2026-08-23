from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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