import requests
import json

url = "http://localhost:3001/"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "X-API-Key": "your-secret-api-key-2024"
}
data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "user",
            "content": "Tell me a story"
        }
    ]
}

print("Testing with API key...")
response = requests.post(url, headers=headers, json=data)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    try:
        result = response.json()
        print("✅ Success! Response:")
        print(f"Model: {result.get('model', 'N/A')}")
        print(f"Content: {result['choices'][0]['message']['content'][:200]}...")
    except:
        print("Response is not valid JSON")
        print(f"Response Text: {response.text}")
else:
    print(f"❌ Error: {response.status_code}")
    print(f"Response: {response.text}")

# Test without API key
print("\n" + "="*50)
print("Testing without API key (should fail)...")
headers_no_key = {
    "Content-Type": "application/json", 
    "Accept": "application/json, text/event-stream"
}

response2 = requests.post(url, headers=headers_no_key, json=data)
print(f"Status Code: {response2.status_code}")
print(f"Response: {response2.text}")