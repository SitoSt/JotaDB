#!/usr/bin/env python3
"""
Test script for /auth/internal endpoint with header-based authentication.
Tests the synchronization between InferenceCenter and JotaDB.
"""

import requests
import sys

BASE_URL = "http://localhost:8002"

def test_auth_internal():
    print("=" * 60)
    print("Testing /auth/internal Header-Based Authentication")
    print("=" * 60)
    
    # Test 1: Valid credentials via headers (expect 200)
    print("\n1. Testing Valid Credentials via Headers (Expect 200)...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/internal",
            headers={
                "X-Client-ID": "orchestrator_service",
                "X-API-Key": "change_this_secure_key"
            }
        )
        if response.status_code == 200:
            print(f"✓ PASS: Got 200 OK")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ FAIL: Got {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    # Test 2: Missing X-Client-ID header (expect 422)
    print("\n2. Testing Missing X-Client-ID Header (Expect 422)...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/internal",
            headers={
                "X-API-Key": "change_this_secure_key"
            }
        )
        if response.status_code == 422:
            print(f"✓ PASS: Got 422 Unprocessable Entity")
        else:
            print(f"✗ FAIL: Got {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    # Test 3: Missing X-API-Key header (expect 422)
    print("\n3. Testing Missing X-API-Key Header (Expect 422)...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/internal",
            headers={
                "X-Client-ID": "orchestrator_service"
            }
        )
        if response.status_code == 422:
            print(f"✓ PASS: Got 422 Unprocessable Entity")
        else:
            print(f"✗ FAIL: Got {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    # Test 4: Missing both headers (expect 422)
    print("\n4. Testing Missing Both Headers (Expect 422)...")
    try:
        response = requests.get(f"{BASE_URL}/auth/internal")
        if response.status_code == 422:
            print(f"✓ PASS: Got 422 Unprocessable Entity")
        else:
            print(f"✗ FAIL: Got {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    # Test 5: Invalid client_id (expect 401)
    print("\n5. Testing Invalid Client ID (Expect 401)...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/internal",
            headers={
                "X-Client-ID": "invalid_client",
                "X-API-Key": "change_this_secure_key"
            }
        )
        if response.status_code == 401:
            print(f"✓ PASS: Got 401 Unauthorized")
        else:
            print(f"✗ FAIL: Got {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    # Test 6: Invalid api_key (expect 401)
    print("\n6. Testing Invalid API Key (Expect 401)...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/internal",
            headers={
                "X-Client-ID": "orchestrator_service",
                "X-API-Key": "invalid_key"
            }
        )
        if response.status_code == 401:
            print(f"✓ PASS: Got 401 Unauthorized")
        else:
            print(f"✗ FAIL: Got {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    # Test 7: Query parameters should NOT work anymore (expect 422)
    print("\n7. Testing Query Parameters (Should NOT Work - Expect 422)...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/internal?client_id=orchestrator_service&api_key=change_this_secure_key"
        )
        if response.status_code == 422:
            print(f"✓ PASS: Got 422 - Query params correctly rejected")
        else:
            print(f"✗ FAIL: Got {response.status_code} - Query params should not work!")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    print("\n" + "=" * 60)
    print("Testing /auth/client Header-Based Authentication")
    print("=" * 60)
    
    # Test 8: Valid external client key via header (expect 200)
    print("\n8. Testing Valid External Client Key via Header (Expect 200)...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/client",
            headers={
                "X-API-Key": "desktop_client_01"
            }
        )
        if response.status_code == 200:
            print(f"✓ PASS: Got 200 OK")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ FAIL: Got {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    # Test 9: Missing X-API-Key header for /auth/client (expect 422)
    print("\n9. Testing Missing X-API-Key Header for /auth/client (Expect 422)...")
    try:
        response = requests.get(f"{BASE_URL}/auth/client")
        if response.status_code == 422:
            print(f"✓ PASS: Got 422 Unprocessable Entity")
        else:
            print(f"✗ FAIL: Got {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    # Test 10: Invalid client key for /auth/client (expect 401)
    print("\n10. Testing Invalid Client Key for /auth/client (Expect 401)...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/client",
            headers={
                "X-API-Key": "invalid_desktop_key"
            }
        )
        if response.status_code == 401:
            print(f"✓ PASS: Got 401 Unauthorized")
        else:
            print(f"✗ FAIL: Got {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    # Test 11: Query parameter should NOT work for /auth/client (expect 422)
    print("\n11. Testing Query Parameter for /auth/client (Should NOT Work - Expect 422)...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/client?client_key=desktop_client_01"
        )
        if response.status_code == 422:
            print(f"✓ PASS: Got 422 - Query params correctly rejected")
        else:
            print(f"✗ FAIL: Got {response.status_code} - Query params should not work!")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    
    print("\n" + "=" * 60)
    print("Test Suite Completed")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_auth_internal()
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Cannot connect to JotaDB at", BASE_URL)
        print("  Make sure JotaDB is running: docker-compose up -d")
        sys.exit(1)
    except Exception as e:
        print(f"✗ ERROR: {e}")
        sys.exit(1)
