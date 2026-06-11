# Build an AI Agent with Google ADK

This project is part of a building AI Agents series, I build a basic blog-writing agent that plans and writes content without external tools, showcasing the core concepts of reasoning and acting.

## What Are AI Agents?

At the simplest level, an agent is software that doesn’t just answer — it can decide and take action. Instead of generating a single response like a traditional chatbot, it looks at your request, figures out what steps to take, maybe calls an API, runs code, looks at the result, and then decides what to do next.

One of the clearest explanations comes from the research paper *ReAct: Synergizing Reasoning and Acting in Language Models*. The idea in that paper was simple but powerful: language models shouldn’t just generate text in one go. They can actually reason step by step, take an action like calling a tool or API, observe the result, and then decide what to do next.

That cycle of reasoning, acting, observing, and adjusting is the foundation of how modern AI agents work. And it lines up with how Google Cloud defines them: systems with reasoning, planning, and memory, with enough autonomy to adapt and make decisions on behalf of the user.

## Three Agent Behavior Patterns

Not all agents behave the same way. A useful way to think about them is in three broad patterns:

1.  **Sequential agents**: These run step by step like an assembly line: Step 1, then Step 2, then Step 3. They’re predictable, but rigid.
2.  **Reactive agents**: These decide in the moment. They look at the current state and ask, ‘What should I do next?’ Maybe Tool A one time, Tool B the next. They’re flexible, but don’t plan ahead.
3.  **Deliberative, or planning agents**: These pause to sketch a plan, then execute. Think about booking travel — you don’t just buy a flight randomly, you pick dates, hotels, order the steps, and then follow through.

Which of these is the ‘right’ one? It depends on the problem. For simple, predictable flows, sequential is fine. For dynamic tasks, reactive works better. For multi-step goals with dependencies, you want planning agents.

## How to Run

When you clone the parent `Agents` repository, follow these steps to run this specific agent:

### 1. Navigate to the Project Directory
```bash
cd build-ai-agent-google-adk
```

### 2. Setup Environment Variables
Create a `.env` file in this directory (or edit the existing one) and add your Google AI Studio API key:
```
MODEL=gemini-flash-latest
GOOGLE_API_KEY=your_actual_api_key
```

### 3. Install Dependencies
We recommend using a virtual environment.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the Agent
Start the ADK web interface:
```bash
adk web
```
*(Note: If `adk` command is not found, you may need to use the full path or ensure it is in your PATH after installation.)*

Open your browser and navigate to the local link provided (usually `http://127.0.0.1:8000` or similar).