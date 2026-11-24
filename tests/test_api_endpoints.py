import pytest


def test_get_root_endpoint(client):
    """Verify health check / welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Credit Card Fraud Detection API is running"
    }


def test_predict_valid_fraud_transaction(client, sample_fraud_transaction):
    """Verify POST /predict classifies known fraud with probability >= 0.5."""
    response = client.post("/predict", json=sample_fraud_transaction)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == "FRAUD"
    assert data["fraud_probability"] >= 0.5
    assert isinstance(data["fraud_probability"], float)


def test_predict_valid_normal_transaction(client, sample_normal_transaction):
    """Verify POST /predict classifies known normal transaction with probability < 0.5."""
    response = client.post("/predict", json=sample_normal_transaction)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == "NORMAL"
    assert data["fraud_probability"] < 0.5
    assert isinstance(data["fraud_probability"], float)


def test_predict_missing_feature(client, sample_incomplete_transaction):
    """Verify POST /predict returns 422 Unprocessable Entity when Amount is omitted."""
    response = client.post("/predict", json=sample_incomplete_transaction)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # Check that Amount is identified as missing
    missing_fields = [
        err["loc"][-1]
        for err in data["detail"]
        if err.get("type") == "missing"
    ]
    assert "Amount" in missing_fields


def test_predict_invalid_feature_type(client, sample_invalid_type_transaction):
    """Verify POST /predict returns 422 Unprocessable Entity when a float field is passed a string."""
    response = client.post("/predict", json=sample_invalid_type_transaction)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_predict_empty_payload(client):
    """Verify POST /predict returns 422 when empty JSON is passed."""
    response = client.post("/predict", json={})
    assert response.status_code == 422


def test_demo_normal_endpoint(client):
    """Verify GET /demo/normal returns prediction for benchmark normal row 20000."""
    response = client.get("/demo/normal")
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == "NORMAL"
    assert data["fraud_probability"] < 0.5


def test_demo_fraud_endpoint(client):
    """Verify GET /demo/fraud returns prediction for benchmark fraud row 541."""
    response = client.get("/demo/fraud")
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == "FRAUD"
    assert data["fraud_probability"] >= 0.5


def test_transaction_lookup_valid_fraud(client):
    """Verify lookup of row 541 returns correct prediction, risk level, and actual label."""
    response = client.get("/transaction/541")
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == 541
    assert data["prediction"] == "FRAUD"
    assert data["actual_result"] == "FRAUD"
    assert data["risk_level"] == "CRITICAL"
    assert data["fraud_probability"] >= 0.9


def test_transaction_lookup_valid_normal(client):
    """Verify lookup of row 20000 returns correct prediction, risk level, and actual label."""
    response = client.get("/transaction/20000")
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == 20000
    assert data["prediction"] == "NORMAL"
    assert data["actual_result"] == "NORMAL"
    assert data["risk_level"] == "LOW"
    assert data["fraud_probability"] < 0.3


def test_transaction_lookup_out_of_range(client):
    """Verify lookup beyond dataset size returns error payload."""
    response = client.get("/transaction/999999")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "out of range" in data["error"].lower()


def test_transaction_lookup_negative(client):
    """Verify lookup of negative index returns error payload."""
    response = client.get("/transaction/-1")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "out of range" in data["error"].lower()


def test_transaction_lookup_non_integer(client):
    """Verify non-integer parameter triggers 422 validation failure."""
    response = client.get("/transaction/invalid_row_id")
    assert response.status_code == 422


def test_recent_transactions_endpoint(client):
    """Verify GET /transactions returns reverse-chronological list of scored rows."""
    # Analyze row 541 then row 20000
    client.get("/transaction/541")
    client.get("/transaction/20000")

    response = client.get("/transactions")
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert len(data["transactions"]) == 2
    # Reverse order check
    assert data["transactions"][0]["transaction_id"] == 20000
    assert data["transactions"][1]["transaction_id"] == 541
