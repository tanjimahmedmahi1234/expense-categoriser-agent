# Expense Categoriser Agent (COIT12204 Assessment 3)

Tanjim Ahmed Mahi (Student ID 12298057)

A single LangChain agent inside a small personal finance app. It can:

- categorise an expense into one of nine categories (food, transport, rent, utilities, entertainment, shopping, health, education, other)
- check if an expense is unusually large compared to the average for its category
- give a summary of the last N days of spending

The agent uses three tools (`lookup_expense`, `list_recent_expenses`, `category_totals`) to look at real data before it answers. Every answer comes back in the same JSON shape (`AgentResult`). If the model fails or returns bad JSON, the agent falls back to simple rules so the API always returns a result.

Model: `gpt-4o` through `langchain-openai`. LangChain 0.3 (`create_tool_calling_agent` + `AgentExecutor`).

## Setup

You need Python 3.10 or newer and an OpenAI API key.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac / Linux
python -m pip install -r requirements.txt
copy .env.example .env          # then open .env and paste your key in
```

The `.env` file is ignored by git, so the key never goes into the repository.

On Windows you can also just double click the `.bat` files. `run.bat` does the venv and install for you the first time.

## Run it

| What | Command | Windows shortcut |
|---|---|---|
| Web page + API | `python -m uvicorn app.main:app --reload` then open http://127.0.0.1:8000 | `run_server.bat` |
| Quick terminal demo | `python run_demo.py` | `run.bat` |
| Tests (71, under a second, no network) | `python -m pytest` | `run_tests.bat` |
| Evaluation against the real model | `python -m scripts.evaluate --versions v1 v2 v3 --repeats 2 --pause 5` | `run_eval.bat` |

The API docs are at http://127.0.0.1:8000/docs.

## Endpoints

| Method | Path | What it does |
|---|---|---|
| POST | `/api/agent/categorize_expense` | body `{"expense_id": 5}` or `{"description": "Spotify", "amount": 12.99}` |
| POST | `/api/agent/check_unusual_expense` | body `{"expense_id": 14}` |
| POST | `/api/agent/monthly_summary` | body `{"days": 30}` |
| GET | `/api/agent/state` | the AgentState snapshot |
| GET | `/api/agent/history?limit=20` | last runs and tool calls |
| GET | `/api/agent/logs?lines=40` | tail of `logs/agent.log` |
| POST | `/api/agent/state/reset` | clears the state |
| GET / POST | `/api/expenses` | list or add expenses |
| GET | `/api/expenses/{id}` | one expense |
| GET | `/health` | model name, prompt version, run count |

Errors always look like `{"error": ..., "detail": ..., "request_id": ...}`. 400 is a rejected input (prompt injection or too long), 404 is an unknown expense id, 422 is a bad body, 500 is an unexpected crash. A model failure is still a 200 with `fallback_used: true`.

## How a run works

1. The endpoint validates the body. An unknown id gets a 404 before the model is called.
2. `ExpenseAgent.run()` builds the human message. For a saved expense the model only gets the id, so it has to call `lookup_expense`.
3. `AgentExecutor` runs the tool loop (max 4 steps). Every tool call is logged as `TOOL CALL` / `TOOL RESULT` and recorded in the state.
4. The text is parsed into `AgentResult`. Bad JSON gets one retry. If that fails, or the API raised, the fallback rules answer with confidence 0.3.
5. Output guardrails fix a wrong action, an unknown category, or a confidence outside 0 to 1.
6. `AgentState.record_run()` updates the counters and logs `STATE TRANSITION` lines, then saves to `data/agent_state.json`.

## Prompt versions

`app/prompts.py` has three system prompts. `v1` is the first attempt. `v2` tells the model to reply with only JSON and to call the tool first. `v3` adds confidence rules, a category rubric and a fixed window for the unusual check. The default is `v3` (set `PROMPT_VERSION` in `.env` to change it). The evaluation results for all three are in `evaluation/`.

## Project layout

```
app/
  config.py      settings from .env, limits, the category list
  logger.py      one logger writing to the terminal and logs/agent.log
  models.py      Expense, request bodies, AgentResult
  store.py       JSON backed ExpenseStore with sample data
  tools.py       the three @tool functions
  prompts.py     system prompts v1 v2 v3, human templates, the output parser
  state.py       AgentState with transition logging and JSON persistence
  agent.py       ExpenseAgent: executor, parsing, retry, fallback rules, guardrails
  main.py        FastAPI app, middleware, error handlers, all routes
  static/index.html   the web page
scripts/evaluate.py  runs the fixed cases against the real model
tests/               71 pytest tests with a fake model (no network)
evaluation/          results JSON and summary.md from the real runs
docs/                the report and the video script
data/expenses.json   sample data (regenerated with dates relative to today if deleted)
```

## Bonus items covered

Multi tool agent (three tools), a summary action with structured output, persistent state in a JSON file, and a visual debugging page (the web page shows state, history and the log live).
