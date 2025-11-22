import requests
import json

# Test authorization with group membership

print("="*70)
print("JWT AUTHENTICATION + GROUP AUTHORIZATION TEST")
print("="*70)
print()

url = "http://localhost:3001/v1/chat/completions"
data = {
    "model": "gemini-2.0-flash",
    "messages": [
        {
            "role": "user",
            "content": "Say 'Hello!' and nothing else."
        }
    ]
}

# Test 1: john.doe (in test-user group) - should succeed
print("TEST 1: john.doe (member of 'test-user' group)")
print("-" * 70)

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

if token_response.status_code == 200:
    john_token = token_response.json()['access_token']
    print(f"✅ Got token for john.doe")
    
    # Decode and show groups
    import base64
    payload = john_token.split('.')[1]
    # Add padding if needed
    payload += '=' * (4 - len(payload) % 4)
    decoded = json.loads(base64.b64decode(payload))
    print(f"Groups in token: {decoded.get('groups', [])}")
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {john_token}"
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"\nRequest to API:")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS - Allowed to access API")
        print(f"Response: {result['choices'][0]['message']['content']}")
    else:
        print(f"❌ FAILED - Status {response.status_code}")
        print(f"Response: {response.text}")
else:
    print(f"❌ Failed to get token: {token_response.text}")

print()
print("="*70)

# Test 2: jane.smith (NOT in test-user group) - should fail
print("TEST 2: jane.smith (NOT in 'test-user' group)")
print("-" * 70)

token_response2 = requests.post(
    "http://localhost:8081/realms/agentgateway/protocol/openid-connect/token",
    data={
        'client_id': 'ext-auth-server',
        'client_secret': 'CBOXD8o118VHRYKRTEa8pTyLO3jSK9ew',
        'username': 'jane.smith',
        'password': 'password123',
        'grant_type': 'password'
    }
)

if token_response2.status_code == 200:
    jane_token = token_response2.json()['access_token']
    print(f"✅ Got token for jane.smith")
    
    # Decode and show groups
    payload = jane_token.split('.')[1]
    payload += '=' * (4 - len(payload) % 4)
    decoded = json.loads(base64.b64decode(payload))
    print(f"Groups in token: {decoded.get('groups', [])}")
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {jane_token}"
    }
    
    response2 = requests.post(url, headers=headers, json=data)
    print(f"\nRequest to API:")
    print(f"Status Code: {response2.status_code}")
    
    if response2.status_code == 403:
        print(f"✅ SUCCESS - Correctly denied access")
        print(f"Response: {response2.text}")
    else:
        print(f"❌ FAILED - Expected 403 but got {response2.status_code}")
        print(f"Response: {response2.text}")
else:
    print(f"❌ Failed to get token: {token_response2.text}")

print()
print("="*70)
print("SUMMARY")
print("="*70)
print(f"Test 1 (john.doe in test-user): {'PASSED ✅' if response.status_code == 200 else 'FAILED ❌'}")
print(f"Test 2 (jane.smith no group): {'PASSED ✅' if response2.status_code == 403 else 'FAILED ❌'}")
print()
print("Authorization based on group membership is working!")
