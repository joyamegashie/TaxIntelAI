#!/usr/bin/env python3
"""
Comprehensive test script for TaxIntel AI system
Tests backend API endpoints, database connectivity, and AI model imports
"""

import requests
import json
import sys
import time
from pathlib import Path


def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Backend health check passed")
            return True
        else:
            print(f"✗ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Backend health check failed: {e}")
        return False


def test_api_docs():
    """Test API documentation endpoint"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✓ API documentation accessible")
            return True
        else:
            print(f"✗ API documentation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ API documentation failed: {e}")
        return False


def test_auth_endpoints():
    """Test authentication endpoints"""
    try:
        # Test login endpoint exists
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"username": "test", "password": "test"},
            timeout=5,
        )
        # We expect this to fail with 401 or 422, but not 404
        if response.status_code in [401, 422]:
            print("✓ Authentication endpoint accessible")
            return True
        else:
            print(
                f"✗ Authentication endpoint unexpected response: {response.status_code}"
            )
            return False
    except Exception as e:
        print(f"✗ Authentication endpoint failed: {e}")
        return False


def test_business_endpoints():
    """Test business-related endpoints"""
    try:
        response = requests.get("http://localhost:8000/api/v1/businesses", timeout=5)
        # We expect 401 (unauthorized) since we're not authenticated
        if response.status_code == 401:
            print("✓ Business endpoints accessible (requires auth)")
            return True
        else:
            print(f"✗ Business endpoints unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Business endpoints failed: {e}")
        return False


def test_database_models():
    """Test database model imports"""
    try:
        sys.path.append("backend")
        from models import User, InformalBusiness, TaxOpportunity, PolicySimulation

        print("✓ Database models import successfully")
        return True
    except Exception as e:
        print(f"✗ Database models import failed: {e}")
        return False


def test_ai_models():
    """Test AI model imports"""
    try:
        sys.path.append("ai_models")
        from business_detector import BusinessDetector
        from tax_estimator import TaxEstimator
        from report_generator import ReportGenerator

        print("✓ AI models import successfully")
        return True
    except Exception as e:
        print(f"✗ AI models import failed: {e}")
        return False


def test_frontend_build():
    """Test if frontend build exists"""
    try:
        dist_path = Path("frontend/taxintel-frontend/dist")
        if dist_path.exists() and (dist_path / "index.html").exists():
            print("✓ Frontend build exists")
            return True
        else:
            print("✗ Frontend build not found")
            return False
    except Exception as e:
        print(f"✗ Frontend build check failed: {e}")
        return False


def main():
    """Run all tests"""
    print("TaxIntel AI System Test Suite")
    print("=" * 40)

    tests = [
        ("Backend Health", test_backend_health),
        ("API Documentation", test_api_docs),
        ("Authentication Endpoints", test_auth_endpoints),
        ("Business Endpoints", test_business_endpoints),
        ("Database Models", test_database_models),
        ("AI Models", test_ai_models),
        ("Frontend Build", test_frontend_build),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        if test_func():
            passed += 1

    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! System is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
