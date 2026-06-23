from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.agents import create_agent

load_dotenv()


#define a function to get the weather

def get_weather(city: str):   # here str is mentioned because if you are using a weatherapi, llm knows that city has to be sent as a str to get the weather info
    """Get weather for a given city"""
    return {'condition': 'sunny', 'temperature': 25} # normmally if you call an api the response might be a dict {'condition': 'sunny', 'temperature': 25}


def get_location():
    """Get user's current location. Use this when the user asks about weather
       without specifying a city"""  #important to specify the doc strings precisely
    return "Bangalore, India"

#Initialize Gemini Flash - model and temperature

llm = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash",
    temperature = 0.7
)

# very important. Check with and without system prompt. It changes the llm behavior.

system_prompt = """
You are a helpful weather assistant.
YOUR WORKFLOW:
1. If user asks about weather WITHOUT specifying a location, you MUST:
 - First call get_location() to find their location
 - Then call get_weather(city) with that location

2. If the user provides a city, call get_weather(city) directly.
"""

agent = create_agent(
    model = llm,
    tools = [get_weather, get_location],  # list of all the functions and tools the agent has access to.
    system_prompt = system_prompt
)


user_query = input("Enter your query: ")

# response = llm.invoke("Hi how are you ?")
# for agents the input must be a dict matching the graph state: {"messages": [...]}
response = agent.invoke({'messages': [{'role': 'user',
            'content': user_query}]})

print(response['messages'][-1].content)