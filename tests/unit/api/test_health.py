"""
Tests for health check API endpoint.
"""

import pytest
from fastapi import status


def test_health_check(client):
    """Test health check endpoint returns successful response."""
    response = client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


def test_health_check_content_type(client):
    """Test health check endpoint returns JSON content type."""
    response = client.get("/health")
    
    assert response.headers["content-type"] == "application/json"


def test_health_check_no_authentication_required(client):
    """Test health check endpoint doesn't require authentication."""
    # Health check should work without any headers/auth
    response = client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK 