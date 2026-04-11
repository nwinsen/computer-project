"""Integration tests for authentication endpoints (signup, login, token refresh)."""

import pytest
from fastapi.testclient import TestClient


def test_user_signup_success(client, sample_user_data):
    """Test that a user can successfully sign up with valid credentials."""
    # TODO:
    # - POST to /api/user/signup with sample_user_data
    res = client.post("/api/user/signup", json=sample_user_data)
    # - Assert response status is 200
    assert res.status_code == 200
    # - Assert response contains the user email
    assert "email" in res.json()


def test_user_login_success(client, sample_user_data):
    """Test that a user can successfully log in after signup."""
    # TODO:
    # - First signup (POST /api/user/signup)
    # - Then login (POST /api/user/login) with same credentials
    # - Assert response status is 200
    # - Assert response contains "access_token"
    pass


def test_verify_token_with_valid_token(client, sample_user_data):
    """Test that verify-token endpoint accepts a valid access token."""
    # TODO:
    # - Signup and login to get an access token
    # - GET /api/user/verify-token with Authorization: Bearer {token}
    # - Assert response status is 200
    pass
