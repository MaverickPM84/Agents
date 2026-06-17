# Blogger Agent — Line-by-Line Guide

A walkthrough of `agent.py`, the multi-agent blog writer built on Google's Agent Development Kit (ADK).

## The big picture first

This file builds a small **team of agents**, not one chatbot. The shape:

```
Blogger (root)                ← talks to you, decides what to call
 ├── planner_tool  ──► RobustBlogPlanner (LoopAgent)
 │                       ├── BlogPlanner            (writes outline)
 │                       └── OutlineValidationChecker (says "ok"/"retry")
 └── writer_tool   ──► RobustBlogWriter (LoopAgent)
                         ├── BlogWriter             (writes article)
                         └── BlogPostValidationChecker (says "ok"/"retry")
```

Two ideas make the whole thing work:
1. **Shared state.** Agents don't pass arguments to each other. Each writes its result into a session "state" dictionary under an `output_key`, and the next agent reads it by *name* in its instruction text. The state keys (`blog_outline`, `blog_post`) are the glue.
2. **Loop = self-correction.** A `LoopAgent` runs a worker, then a validator, and repeats (up to 3×) until the validator approves. This is how the agent fixes its own weak outputs.

---

## Imports and config (lines 1–13)

```python
import os
import sys
from pathlib import Path
import datetime
```
- `os` — used to read environment variables (`os.getenv`).
- `sys`, `Path` — imported but **not actually used** in the current code (leftover scaffolding; safe to remove).
- `datetime` — used to stamp today's date into the root agent's instruction.

```python
from dotenv import load_dotenv
from google.adk.agents import Agent, LoopAgent
from google.adk.tools import agent_tool
```
- `load_dotenv` — reads the local `.env` file into environment variables.
- `Agent` — the core ADK building block: one LLM with a name, model, instruction, and optional tools.
- `LoopAgent` — a special agent that runs its `sub_agents` in order, repeatedly, until a stop condition or `max_iterations`.
- `agent_tool` — lets you wrap an agent so another agent can call it like a function (an agent-as-a-tool).

```python
load_dotenv()
MODEL = os.getenv("MODEL", "gemini-flash-latest")
```
- Loads `.env`, then reads `MODEL`. If unset, defaults to `"gemini-flash-latest"`. Every agent below uses this one variable, so you can swap models in one place via `.env`.

---

## Sub-agent: the Planner (lines 16–31)

```python
blog_planner = Agent(
    name="BlogPlanner",
    model=MODEL,
    description="Creates a practical, skimmable outline in Markdown.",
    instruction="""...produce a clear Markdown outline...""",
    output_key="blog_outline",
)
```
- `name` — identifier shown in traces/logs; must be unique.
- `model` — which LLM runs this agent.
- `description` — a short summary. This matters when the agent is used *as a tool*: the caller reads the description to decide whether to call it.
- `instruction` — the system prompt. This one asks for a Title, intro, 4–6 sections, and a conclusion.
- **`output_key="blog_outline"`** — the important line. Whatever this agent returns is stored in session state under the key `blog_outline`. Other agents read it by writing `blog_outline` in their own instructions.

**About the lines you selected (25–29):**
```
If `codebase_context` exists in state, weave in specific sections/snippets.
Return only the outline in Markdown.
""",
   output_key="blog_outline",
```
- `If codebase_context exists in state...` — this is *instruction text*, telling the model: if some upstream step put a value named `codebase_context` into shared state, incorporate it. In the current code **nothing ever sets `codebase_context`**, so this branch is dormant — it's a hook for a future feature (e.g., feeding in real code to blog about). It does no harm; the model just ignores it when the key is absent.
- `Return only the outline in Markdown.` — keeps the output clean so the next agent gets just an outline, no chatter.
- `"""` — closes the multi-line instruction string.
- `output_key="blog_outline"` — as above, names where this agent's output lands in state.

---

## Sub-agent: the Outline Validator (lines 33–44)

```python
class OutlineValidationChecker(Agent):
    def __init__(self):
        super().__init__(
            name="OutlineValidationChecker",
            model=MODEL,
            description="Validates that the outline is usable.",
            instruction="""Check the outline in state `blog_outline`...
respond exactly "ok" ... Otherwise respond exactly "retry"...""",
            output_key="validation_result",
        )
```
- This is an `Agent` defined as a **subclass** instead of a plain instance. Functionally similar to `blog_planner`, but subclassing is a clean way to bundle fixed config and (optionally) override behavior later.
- It **reads** `blog_outline` from state (named in its instruction) and **writes** a verdict to `validation_result`.
- It is told to answer *exactly* `"ok"` or `"retry"` — that precise wording is what the surrounding `LoopAgent` keys off of to decide whether to stop or loop again.

---

## Wrapping planner + validator in a loop (lines 46–51)

```python
robust_blog_planner = LoopAgent(
    name="RobustBlogPlanner",
    description="Retries planning if validation fails.",
    sub_agents=[blog_planner, OutlineValidationChecker()],
    max_iterations=3,
)
```
- `LoopAgent` runs its `sub_agents` **in order**: first `blog_planner` (produces outline), then the validator (judges it).
- If the outline isn't good, the loop runs again — the planner sees the validator's feedback in state and tries to improve.
- `max_iterations=3` — a safety cap so it can't loop forever. After 3 tries it stops regardless.
- Net effect: `RobustBlogPlanner` behaves like "make an outline, and keep refining until it's actually complete (or we hit 3 attempts)."

---

## Sub-agent: the Writer (lines 54–69)

```python
blog_writer = Agent(
    name="BlogWriter",
    ...
    instruction="""Write a complete Markdown article from the outline in `blog_outline`...""",
    output_key="blog_post",
)
```
- Reads `blog_outline` (the planner's output) and writes a full article to `blog_post`.
- The instruction sets the audience (software engineers), asks for the *how and why*, code snippets, and H2/H3 structure matching the outline.
- This is the planner→writer handoff in action: **no function arguments**, just one agent writing `blog_outline` and the next reading it.

---

## Sub-agent: the Post Validator (lines 71–82)

```python
class BlogPostValidationChecker(Agent):
    def __init__(self):
        super().__init__(
            ...
            instruction="""Check `blog_post` for: intro, sections..., conclusion...
If passes, respond "ok". Else respond "retry" with the specific fixes.""",
            output_key="validation_result",
        )
```
- Same idea as the outline validator, but checks the finished article (`blog_post`) instead of the outline.
- Also writes to `validation_result`. (Both validators reuse this key; that's fine because each loop runs independently in its own turn.)

---

## Wrapping writer + validator in a loop (lines 84–89)

```python
robust_blog_writer = LoopAgent(
    name="RobustBlogWriter",
    description="Retries writing if validation fails.",
    sub_agents=[blog_writer, BlogPostValidationChecker()],
    max_iterations=3,
)
```
- Identical pattern to the planner loop: write → validate → retry up to 3×.

---

## Turning the loops into callable tools (lines 91–93)

```python
planner_tool = agent_tool.AgentTool(agent=robust_blog_planner)
writer_tool  = agent_tool.AgentTool(agent=robust_blog_writer)
```
- `AgentTool` wraps an agent so it can be **called like a function by another agent**.
- After this, the root agent can "use the planner" or "use the writer" as if they were tools in its toolbox. The agent's `description` is what the root agent reads to know what each tool does.

---

## The Root Agent (lines 95–112)

```python
root_agent = Agent(
    name="Blogger",
    model=MODEL,
    description="Minimal multi-agent blogger that plans and writes.",
    instruction=f"""
If the user gives a topic:
1) Call the planner tool to generate the outline.
2) Call the writer tool to produce the full draft.
3) End with 3 alternate titles and 2 tweet-length hooks.

Date: {datetime.datetime.now().strftime("%Y-%m-%d")}
""",
    tools=[planner_tool, writer_tool],
)
```
- **`root_agent` is the required entry point.** ADK discovers this agent by importing the package and looking for a module-level variable literally named `root_agent`. Rename it and `adk web` won't find the agent.
- It's a plain `Agent`, but its `tools` are the two wrapped loop-agents, so it can call them.
- The `f"""..."""` instruction is an **f-string**, so `{datetime.datetime.now().strftime("%Y-%m-%d")}` is evaluated **once at import time** and baked in as today's date. (Note: it won't update while the server runs — it reflects whenever the module was loaded.)
- The instruction is the orchestration logic: plan, then write, then add titles + hooks.

---

## How a single run flows

1. You type a topic into the ADK web UI.
2. `Blogger` (root) reads its instruction, calls `planner_tool`.
3. `RobustBlogPlanner` loops: `BlogPlanner` writes `blog_outline` → `OutlineValidationChecker` writes `ok`/`retry` → repeat until ok or 3 tries.
4. `Blogger` calls `writer_tool`.
5. `RobustBlogWriter` loops: `BlogWriter` reads `blog_outline`, writes `blog_post` → `BlogPostValidationChecker` judges → repeat.
6. `Blogger` returns the article plus 3 alternate titles and 2 hooks.

## The one rule to remember when editing

**State keys are the contract.** `output_key` is how an agent hands its result to the next one, and the next agent picks it up by naming that key in its instruction. If you rename `blog_outline` on the planner but forget to update the writer's instruction, the chain breaks silently — no error, just an empty/confused article.

## Try-it experiments

- Change `max_iterations` to `1` to see validation without retries.
- Add a third worker (e.g., an "SEO editor") that reads `blog_post` and writes `blog_post_final`, then add it to the root's flow.
- Actually set `codebase_context` in state before running to activate the dormant branch in the planner's instruction (lines 25–29).
