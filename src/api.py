from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.explain import explain_transaction
from .predict import predict_fraud


# ============================================================
# PROJECT PATHS
# ============================================================

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Dataset path
DATA_PATH = BASE_DIR / "data" / "creditcard.csv"

# In-memory dataset cache
_dataset_cache = None


def get_dataset() -> pd.DataFrame:
    """
    Retrieve the dataset from memory cache or load from disk on first call.
    """
    global _dataset_cache
    if _dataset_cache is None:
        _dataset_cache = pd.read_csv(DATA_PATH)
    return _dataset_cache


# ============================================================
# TRANSACTION HISTORY
# ============================================================

# Stores transactions analyzed while the API is running
transaction_history = []

# Maximum number of transactions to remember
MAX_HISTORY = 20


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Credit Card Fraud Detection API"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

# Allows the frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# TRANSACTION INPUT MODEL
# ============================================================

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


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_risk(probability: float) -> str:
    """
    Convert fraud probability into a risk level.
    """

    if probability >= 0.90:
        return "CRITICAL"

    elif probability >= 0.70:
        return "HIGH"

    elif probability >= 0.30:
        return "MEDIUM"

    else:
        return "LOW"


def save_transaction(
    transaction_id: int,
    prediction: str,
    probability: float,
    risk_level: str
):
    """
    Save an analyzed transaction into the in-memory history.
    """

    transaction_history.append({

        "transaction_id": transaction_id,

        "prediction": prediction,

        "fraud_probability": float(probability),

        "risk_level": risk_level

    })

    # Keep only the latest MAX_HISTORY transactions
    if len(transaction_history) > MAX_HISTORY:

        transaction_history.pop(0)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Credit Card Fraud Detection API is running"
    }


# ============================================================
# MANUAL PREDICTION
# ============================================================

@app.post("/predict")
def predict(transaction: Transaction):

    transaction_data = transaction.model_dump()

    result, probability = predict_fraud(
        transaction_data
    )

    return {

        "prediction": result,

        "fraud_probability": float(
            probability
        )

    }


# ============================================================
# DEMO NORMAL TRANSACTION
# ============================================================

@app.get("/demo/normal")
def demo_normal():

    data = get_dataset()

    # Row 20000 is used as a known normal example
    transaction = (
        data.iloc[20000]
        .drop("Class")
        .to_dict()
    )

    result, probability = predict_fraud(
        transaction
    )

    return {

        "prediction": result,

        "fraud_probability": float(
            probability
        )

    }


# ============================================================
# DEMO FRAUD TRANSACTION
# ============================================================

@app.get("/demo/fraud")
def demo_fraud():

    data = get_dataset()

    # Row 541 is used as a known fraud example
    transaction = (
        data.iloc[541]
        .drop("Class")
        .to_dict()
    )

    result, probability = predict_fraud(
        transaction
    )

    return {

        "prediction": result,

        "fraud_probability": float(
            probability
        )

    }


# ============================================================
# ANALYZE TRANSACTION
# ============================================================

@app.get("/transaction/{row_number}")
def analyze_transaction(row_number: int):

    # Load dataset
    data = get_dataset()


    # --------------------------------------------------------
    # Check whether transaction exists
    # --------------------------------------------------------

    if row_number < 0 or row_number >= len(data):

        return {
            "error": "Transaction number is out of range"
        }


    # --------------------------------------------------------
    # Get transaction data
    # --------------------------------------------------------

    transaction = (
        data.iloc[row_number]
        .drop("Class")
        .to_dict()
    )


    # --------------------------------------------------------
    # Get actual result from dataset
    # --------------------------------------------------------

    actual_result = (

        "FRAUD"

        if data.iloc[row_number]["Class"] == 1

        else "NORMAL"

    )


    # --------------------------------------------------------
    # Run XGBoost model
    # --------------------------------------------------------

    prediction, probability = predict_fraud(
        transaction
    )


    # --------------------------------------------------------
    # Calculate risk
    # --------------------------------------------------------

    risk = calculate_risk(
        probability
    )


    # --------------------------------------------------------
    # Save transaction to history
    # --------------------------------------------------------

    save_transaction(

        row_number,

        prediction,

        probability,

        risk

    )


    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {

        "transaction_id": row_number,

        "prediction": prediction,

        "fraud_probability": float(
            probability
        ),

        "risk_level": risk,

        "actual_result": actual_result

    }


# ============================================================
# TRANSACTION HISTORY
# ============================================================

@app.get("/transactions")
def recent_transactions():

    return {

        "transactions": list(
            reversed(transaction_history)
        )

    }


# ============================================================
# SHAP EXPLANATION
# ============================================================

@app.get("/explain/{row_number}")
def explain(row_number: int):

    try:

        return explain_transaction(
            row_number
        )


    except ValueError as error:

        return {

            "error": str(error)

        }


    except Exception as error:

        return {

            "error": "Unable to generate explanation",

            "details": str(error)

        }