#!/usr/bin/env python3
"""
Test script to verify API authentication is working correctly.
Tests all protected endpoints with and without Bearer token.
"""
import requests
import os
import sys

# API Configuration
BASE_URL = "http://localhost/api/db"
API_SECRET_KEY = "jotadb_master_key_9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f"

# Test credentials
ORCHESTRATOR_ID = "jota_orchestrator"
ORCHESTRATOR_KEY = "jota_orchestrator_8f29c1a0e63847b592d8e428f7a6c9d0b51e39a02f374c18a5927d"

def test_endpoint(name, method, url, headers=None, json_data=None, expected_status=None):
    """Test an endpoint and report results."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Method: {method}")
    print(f"URL: {url}")
    if headers:
        print(f"Headers: {headers}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json_data)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"Status Code: {response.status_code}")
        
        if expected_status:
            if response.status_code == expected_status:
                print(f"✅ PASS - Got expected status {expected_status}")
                return True
            else:
                print(f"❌ FAIL - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")
                return False
        else:
            print(f"Response: {response.json() if response.headers.get('content-type') == 'application/json' else response.text}")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("="*60)
    print("JotaDB API Authentication Test Suite")
    print("="*60)
    
    results = []
    
    # Test 1: Health check (should be public)
    results.append(test_endpoint(
        "Health Check (Public)",
        "GET",
        f"{BASE_URL}/health",
        expected_status=200
    ))
    
    # Test 2: Protected endpoint without auth (should fail with 401)
    results.append(test_endpoint(
        "Events without Bearer token (should fail)",
        "GET",
        f"{BASE_URL}/events",
        expected_status=401
    ))
    
    # Test 3: Protected endpoint with invalid Bearer token (should fail with 403)
    results.append(test_endpoint(
        "Events with invalid Bearer token (should fail)",
        "GET",
        f"{BASE_URL}/events",
        headers={"Authorization": "Bearer invalid_key"},
        expected_status=403
    ))
    
    # Test 4: Protected endpoint with valid Bearer token (should succeed)
    results.append(test_endpoint(
        "Events with valid Bearer token (should succeed)",
        "GET",
        f"{BASE_URL}/events",
        headers={"Authorization": f"Bearer {API_SECRET_KEY}"},
        expected_status=200
    ))
    
    # Test 5: Tasks endpoint with valid Bearer token
    results.append(test_endpoint(
        "Tasks with valid Bearer token (should succeed)",
        "GET",
        f"{BASE_URL}/tasks",
        headers={"Authorization": f"Bearer {API_SECRET_KEY}"},
        expected_status=200
    ))
    
    # Test 6: Reminders endpoint with valid Bearer token
    results.append(test_endpoint(
        "Reminders with valid Bearer token (should succeed)",
        "GET",
        f"{BASE_URL}/reminders",
        headers={"Authorization": f"Bearer {API_SECRET_KEY}"},
        expected_status=200
    ))
    
    # Test 7: Auth endpoint without Bearer token (should fail)
    results.append(test_endpoint(
        "Auth validation without Bearer token (should fail)",
        "GET",
        f"{BASE_URL}/auth/internal",
        headers={
            "X-Service-ID": ORCHESTRATOR_ID,
            "X-API-Key": ORCHESTRATOR_KEY
        },
        expected_status=401
    ))
    
    # Test 8: Auth endpoint with Bearer token (should succeed)
    results.append(test_endpoint(
        "Auth validation with Bearer token (should succeed)",
        "GET",
        f"{BASE_URL}/auth/internal",
        headers={
            "Authorization": f"Bearer {API_SECRET_KEY}",
            "X-Service-ID": ORCHESTRATOR_ID,
            "X-API-Key": ORCHESTRATOR_KEY
        },
        expected_status=200
    ))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"❌ {total - passed} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
