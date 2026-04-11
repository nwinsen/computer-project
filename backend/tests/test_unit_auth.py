"""Unit tests for authentication utilities (password hashing, token generation)."""

import pytest
from app.utils.crypt import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_hash_password_creates_different_hashes():
    """Test that hashing the same password twice produces different hashes (due to salt)."""
    password = "mypassword123"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2


def test_verify_password_matches_correct_password():
    """Test that verify_password returns True for the correct password."""
    password = "testpass123"
    hashed = hash_password(password)

    assert verify_password(password, hashed)


def test_verify_password_rejects_wrong_password():
    """Test that verify_password returns False for an incorrect password."""
    password = "testpass123"
    hashed = hash_password(password)

    assert verify_password("test", hashed) == False
