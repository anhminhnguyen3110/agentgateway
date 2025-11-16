import openai

client = openai.OpenAI(
    api_key="anything",
    base_url="http://localhost:3001"
)

response = client.chat.completions.create(model="gpt-4o-mini", messages = [
    {
        "role": "user",
        "content": "this is a test request, write a short poem"
    }
])

print(response)