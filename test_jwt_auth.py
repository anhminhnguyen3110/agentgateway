import requests
import json
import subprocess

# Get JWT token from Keycloak
print("🔐 Getting JWT token from Keycloak...")
token_response = requests.post(
    "http://localhost:8081/realms/agentgateway/protocol/openid-connect/token",
    data={
        'client_id': 'ext-auth-server',
        'client_secret': 'CBOXD8o118VHRYKRTEa8pTyLO3jSK9ew',
        'username': 'john.doe',
        'password': 'password123',
        'grant_type': 'password'
    }
)

if token_response.status_code != 200:
    print(f"❌ Failed to get token: {token_response.text}")
    exit(1)

access_token = token_response.json()['access_token']
print(f"✅ Got JWT token (length: {len(access_token)})")
print(f"Token preview: {access_token[:50]}...")
print()

# Test 1: Request WITH JWT token (should succeed)
print("="*60)
print("TEST 1: Request WITH JWT token (should succeed)")
print("="*60)

url = "http://localhost:3001/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "Authorization": f"Bearer {access_token}"
}
data = {
    "model": "gemini-2.0-flash",
    "messages": [
        {
            "role": "user",
            "content": "Say 'Hello from JWT authenticated request!' and nothing else."
        }
    ]
}

print(f"Sending request to: {url}")
print(f"With Authorization header: Bearer {access_token[:30]}...")
print()

response = requests.post(url, headers=headers, json=data)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    try:
        result = response.json()
        print("✅ Success! Response:")
        print(f"Model: {result.get('model', 'N/A')}")
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            print(f"Content: {content}")
        else:
            print(f"Full response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Response parsing error: {e}")
        print(f"Response Text: {response.text[:500]}")
else:
    print(f"❌ Error: {response.status_code}")
    print(f"Response: {response.text}")

# Test 2: Request WITHOUT JWT token (should fail with 401)
print("\n" + "="*60)
print("TEST 2: Request WITHOUT JWT token (should fail)")
print("="*60)

headers_no_token = {
    "Content-Type": "application/json", 
    "Accept": "application/json, text/event-stream"
}

print(f"Sending request to: {url}")
print("Without Authorization header")
print()

response2 = requests.post(url, headers=headers_no_token, json=data)
print(f"Status Code: {response2.status_code}")

if response2.status_code == 401:
    print("✅ Correctly rejected! (401 Unauthorized)")
    print(f"Response: {response2.text}")
else:
    print(f"❌ Expected 401 but got: {response2.status_code}")
    print(f"Response: {response2.text}")

# Test 3: Request WITH INVALID JWT token (should fail)
print("\n" + "="*60)
print("TEST 3: Request WITH INVALID JWT token (should fail)")
print("="*60)

invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

headers_invalid_token = {
    "Content-Type": "application/json", 
    "Accept": "application/json, text/event-stream",
    "Authorization": f"Bearer {invalid_token}"
}

print(f"Sending request to: {url}")
print(f"With INVALID token: {invalid_token[:50]}...")
print()

response3 = requests.post(url, headers=headers_invalid_token, json=data)
print(f"Status Code: {response3.status_code}")

if response3.status_code == 403 or response3.status_code == 401:
    print("✅ Correctly rejected! (Invalid token)")
    print(f"Response: {response3.text}")
else:
    print(f"❌ Expected 401/403 but got: {response3.status_code}")
    print(f"Response: {response3.text}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"✅ Test 1 (with valid JWT): {'PASSED' if response.status_code == 200 else 'FAILED'}")
print(f"✅ Test 2 (without JWT): {'PASSED' if response2.status_code in [401, 403] else 'FAILED'}")
print(f"✅ Test 3 (with invalid JWT): {'PASSED' if response3.status_code in [401, 403] else 'FAILED'}")
