from langchain.chat_models import init_chat_model

GOOGLE_API_KEY = ""

model = init_chat_model(
    model = "gemini-3.5-flash",
    model_provider="google-genai",
    api_key = GOOGLE_API_KEY)

response = model.invoke("Hi how are you ?")
print(response.content[0]['text'])