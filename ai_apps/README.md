# ai_apps

A hands-on learning playground for building AI-powered apps with **LangChain** and **Google Gemini**. Each file is a small, self-contained step — from a first LLM call, to feeding a document into a model, to building a tool-using agent.

These are practice scripts (a learning journey, not a packaged product). Run them one at a time.

## Projects

| File | What it does | Concept |
|---|---|---|
| `day_1.ipynb` | Jupyter notebook contrasting plain Python functions with the idea of an LLM-powered function | "Code before and after AI" — the mental model shift |
| `llm_connect.py` | The smallest possible LLM call: connect to Gemini and print a reply | Connecting to an LLM with `init_chat_model` |
| `main.py` | Reads `anime.txt` and asks the model to compare its contents | Feeding a document into a prompt |
| `weather_agent.py` | A tool-using agent with **mock** tools (`get_location()`, `get_weather()` return hardcoded values) to answer weather questions | Agents, tools, and system prompts |
| `main_real.py` | The same weather agent wired to **live APIs** — `get_weather()` calls OpenWeatherMap and `get_location()` calls ipapi for real data | Tools that hit real external APIs |
| `anime.txt` | Sample input data used by `main.py` | — |

## Setup

All commands run from inside `ai_apps/`.

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### API key

These scripts call the Google Gemini API and need a **Google AI Studio API key** (https://aistudio.google.com/apikey). `main_real.py` additionally needs a free **OpenWeatherMap API key** (https://openweathermap.org/api) for live weather data.

- `weather_agent.py` and `main_real.py` load keys from a `.env` file via `python-dotenv`. Create a `.env` in this directory:

  ```
  GOOGLE_API_KEY=your-key-here
  OPENWEATHER_API_KEY=your-openweathermap-key-here   # only needed by main_real.py
  ```

- `llm_connect.py` and `main.py` currently read the key from a `GOOGLE_API_KEY` variable defined at the top of the file. Paste your key there before running, **or** (preferred) switch them to use `.env` like the weather agents do.

> ⚠️ Never commit your API key. `.env` is gitignored — keep keys out of tracked files. If you hardcode a key while experimenting, remove it before committing.

## Running

```powershell
python llm_connect.py        # first LLM call
python main.py               # compare the anime in anime.txt
python weather_agent.py      # interactive weather agent with mock tools
python main_real.py          # same agent, but calling live weather/location APIs
```

`day_1.ipynb` is a Jupyter notebook — open it in VS Code or JupyterLab and run the cells.

## How the weather agent works

`weather_agent.py` is the most complete example. It shows the core agent loop:

1. Two Python functions (`get_weather`, `get_location`) are passed to the agent as **tools**.
2. A **system prompt** tells the model *when* to use each tool — e.g. if the user doesn't name a city, call `get_location()` first, then `get_weather()`.
3. The agent (built with `create_agent`) decides which tools to call, in what order, to answer the query.

Try running it with and without the system prompt to see how much the instructions change the agent's behavior. The tool docstrings and type hints also matter — they're how the model learns what each tool is for and what to pass it.

`main_real.py` is the same agent with the mock tools swapped for real ones: `get_weather()` queries OpenWeatherMap and converts Celsius to Fahrenheit, and `get_location()` resolves your location from your IP via ipapi. Compare it with `weather_agent.py` to see how little the agent wiring changes when you move from hardcoded stubs to live APIs.

## Notes

- Model names in the scripts vary (`gemini-2.5-flash`, etc.). If a call fails with a model-not-found error, check the [current Gemini model list](https://ai.google.dev/gemini-api/docs/models) and update the string.
- No tests or linter are configured — this is exploratory code.
