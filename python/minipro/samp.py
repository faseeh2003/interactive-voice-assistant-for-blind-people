import openai

openai.api_key = "your_openai_api_key_here"

response = openai.Completion.create(
    engine="text-davinci-003",
    prompt="What is the capital of France?",
    max_tokens=50,
)
print(response.choices[0].text.strip())