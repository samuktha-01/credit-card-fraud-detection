import pandas as pd
import pytest
from fastapi.testclient import TestClient

import src.api as api_module
from src.api import (
    app,
    calculate_risk,
    save_transaction,
    get_dataset,
    transaction_history,
    MAX_HISTORY,
)


def test_app_startup_metadata():
    """Verify application title and registered endpoints."""
    assert app.title == "Credit Card Fraud Detection API"
    routes = [route.path for route in app.routes]
    assert "/" in routes
    assert "/predict" in routes
    assert "/demo/normal" in routes
    assert "/demo/fraud" in routes
    assert "/transaction/{row_number}" in routes
    assert "/transactions" in routes
    assert "/explain/{row_number}" in routes


def test_calculate_risk_thresholds():
    """Test boundary logic for probability-to-risk conversion."""
    assert calculate_risk(0.95) == "CRITICAL"
    assert calculate_risk(0.90) == "CRITICAL"

    assert calculate_risk(0.89) == "HIGH"
    assert calculate_risk(0.70) == "HIGH"

    assert calculate_risk(0.69) == "MEDIUM"
    assert calculate_risk(0.30) == "MEDIUM"

    assert calculate_risk(0.29) == "LOW"
    assert calculate_risk(0.0) == "LOW"


def test_save_transaction_history_capping():
    """Verify in-memory history retains only the most recent MAX_HISTORY entries."""
    transaction_history.clear()
    total_to_add = MAX_HISTORY + 5

    for i in range(total_to_add):
        save_transaction(
            transaction_id=i,
            prediction="NORMAL",
            probability=0.05,
            risk_level="LOW",
        )

    assert len(transaction_history) == MAX_HISTORY
    # Earliest 5 should have been popped
    assert transaction_history[0]["transaction_id"] == 5
    assert transaction_history[-1]["transaction_id"] == total_to_add - 1


def test_dataset_is_cached_and_not_repeatedly_loaded(monkeypatch):
    """
    Verify that get_dataset() loads the CSV once and subsequent calls
    return the cached DataFrame without reading disk again.
    """
    original_cache = api_module._dataset_cache
    read_csv_call_count = 0
    real_read_csv = pd.read_csv

    def mock_read_csv(*args, **kwargs):
        nonlocal read_csv_call_count
        read_csv_call_count += 1
        return real_read_csv(*args, **kwargs)

    monkeypatch.setattr(pd, "read_csv", mock_read_csv)

    try:
        # Reset cache to simulate cold start
        api_module._dataset_cache = None

        # Call 1: cold load -> pd.read_csv called once
        df1 = get_dataset()
        assert df1 is not None
        assert read_csv_call_count == 1

        # Call 2: warm load -> pd.read_csv must NOT be called again
        df2 = get_dataset()
        assert read_csv_call_count == 1
        assert df1 is df2

        # Call 3: API endpoint using get_dataset -> must NOT read CSV again
        client = TestClient(app)
        response = client.get("/demo/normal")
        assert response.status_code == 200
        assert read_csv_call_count == 1
    finally:
        api_module._dataset_cache = original_cache


def test_cors_preflight_headers(client):
    """Verify CORS preflight OPTIONS returns allowed wildcard origin and methods."""
    headers = {
        "Origin": "http://127.0.0.1:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    response = client.options("/predict", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "*"
    assert "POST" in response.headers.get("access-control-allow-methods", "")


def test_cors_get_headers(client):
    """Verify CORS origin header is present on GET requests."""
    headers = {"Origin": "http://127.0.0.1:3000"}
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "*"
