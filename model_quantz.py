from google import genai


# 🔑 Put your Gemini API key directly here
api_key = "api"

# Initialize the client with the key
client = genai.Client(api_key=api_key)
# Generate content using Gemini
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how AI works in a few words"
)

# Print the result
print(response.text)
