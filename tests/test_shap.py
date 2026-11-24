import pytest


def test_explain_valid_fraud_transaction(client):
    """Verify SHAP explanation structure and direction for row 541."""
    response = client.get("/explain/541")
    assert response.status_code == 200
    data = response.json()

    assert data["transaction_id"] == 541
    assert data["prediction"] == "FRAUD"
    assert isinstance(data["fraud_probability"], float)
    assert isinstance(data["explanations"], list)
    assert len(data["explanations"]) == 30

    # Verify schema of each explanation item
    for item in data["explanations"]:
        assert "feature" in item
        assert "shap_value" in item
        assert "direction" in item
        assert item["direction"] in ["FRAUD", "NORMAL"]

    # Verify descending sort order by absolute impact
    abs_values = [abs(item["shap_value"]) for item in data["explanations"]]
    assert abs_values == sorted(abs_values, reverse=True)


def test_explain_valid_normal_transaction(client):
    """Verify SHAP explanation structure for row 20000."""
    response = client.get("/explain/20000")
    assert response.status_code == 200
    data = response.json()

    assert data["transaction_id"] == 20000
    assert data["prediction"] == "NORMAL"
    assert len(data["explanations"]) == 30


def test_explain_out_of_range(client):
    """Verify out-of-range row returns error payload."""
    response = client.get("/explain/999999")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "out of range" in data["error"].lower()


def test_explain_negative_row(client):
    """Verify negative row number returns error payload."""
    response = client.get("/explain/-1")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "out of range" in data["error"].lower()
