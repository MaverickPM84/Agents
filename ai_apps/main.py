from langchain.chat_models import init_chat_model

GOOGLE_API_KEY = ""

model = init_chat_model(
    model = "gemini-3.5-flash",
    model_provider="google-genai",
    api_key = GOOGLE_API_KEY)

with open('anime.txt') as file:
    anime = file.read()

response = model.invoke(f"which anime is the best of these 2 and why: {anime}")
print(response.content[0]['text'])