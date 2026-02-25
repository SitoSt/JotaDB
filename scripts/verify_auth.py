
import requests
import sys

BASE_URL = "http://localhost:8002"

def test_auth():
    print("--- Testing Auth ---")
    
    # 1. No Key
    print("1. Testing No Key (Expect 422)...")
    try:
        r = requests.post(f"{BASE_URL}/chat/conversation", json={"title": "Test No Key"})
        if r.status_code == 422:
            print("PASS: Got 422")
        else:
            print(f"FAIL: Got {r.status_code}")
    except Exception as e:
        print(f"FAIL: {e}")

    # 2. Invalid Key
    print("\n2. Testing Invalid Key (Expect 401)...")
    r = requests.post(f"{BASE_URL}/chat/conversation", json={"title": "Test Invalid"}, headers={"X-API-Key": "invalid"})
    if r.status_code == 401:
        print("PASS: Got 401")
    else:
        print(f"FAIL: Got {r.status_code}")

    # 3. Valid Client Key
    print("\n3. Testing Valid Client Key (Expect 201)...")
    # Note: client_id is NOT in body anymore
    r = requests.post(
        f"{BASE_URL}/chat/conversation", 
        json={"title": "Test Valid Client"}, 
        headers={"X-API-Key": "desktop_client_01"}
    )
    if r.status_code == 201:
        print(f"PASS: Got 201. Conv ID: {r.json()['id']}")
        conv_id = r.json()['id']
    else:
        print(f"FAIL: Got {r.status_code} - {r.text}")
        return

    # 4. Service Key WITHOUT Client ID (Expect 400)
    print("\n4. Testing Service Key No ClientID (Expect 400)...")
    r = requests.post(
        f"{BASE_URL}/chat/conversation", 
        json={"title": "Test Service No ID"}, 
        headers={"X-API-Key": "change_this_secure_key"}
    )
    if r.status_code == 400:
        print("PASS: Got 400")
    else:
        print(f"FAIL: Got {r.status_code} - {r.text}")

    # 5. Service Key WITH Client ID (Expect 201)
    print("\n5. Testing Service Key WITH ClientID (Expect 201)...")
    # We need to know the client ID. The init script printed it, but let's assume valid ID is found via previous step or predictable.
    # In integration test we might need to fetch it.
    # But wait, create_conversation endpoint infers client_id from auth.
    # If using Service Auth, it infers from X-Client-ID.
    
    # We need a valid client ID. Let's use '1' if we assume clean DB or query it.
    # Actually, step 3 created a conversation, which returns client_id in response if model has it?
    # Conversation model: client_id field exists.
    client_id = r.json()['client_id']
    
    r = requests.post(
        f"{BASE_URL}/chat/conversation", 
        json={"title": "Test Service With ID"}, 
        headers={"X-API-Key": "change_this_secure_key", "X-Client-ID": str(client_id)}
    )
    if r.status_code == 201:
        print("PASS: Got 201")
    else:
        print(f"FAIL: Got {r.status_code} - {r.text}")

if __name__ == "__main__":
    try:
        test_auth()
    except Exception as e:
        print(f"Error: {e}")
