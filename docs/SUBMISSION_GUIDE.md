# Submission guide: GitHub, Moodle and the marking criteria

Tanjim Ahmed Mahi, 12298057. Follow this top to bottom.

## Part 1. Before anything goes on GitHub (5 minutes)

1. **Make the `.env` file.** In the project folder, right click `.env.example`, copy, paste, rename the copy to `.env` (no `.example`). Open it in Notepad and replace `put-your-openai-key-here` with the real key. Save. Windows may warn about the file name, that's fine.
2. **Check `.gitignore` is there** and contains `.env`, `.venv/`, `logs/`, `data/agent_state.json`, `demo_output.txt`. It does, just confirm.
3. **Run `run_tests.bat`.** You should see `71 passed`. If the window closes instantly, the venv is missing, run `run.bat` once first.
4. **Run `run_server.bat`** and open http://127.0.0.1:8000. Ask the agent one thing. This confirms the `.env` works.
5. **Search the folder for the key.** In File Explorer search box type `sk-proj` with "File contents" on, or open each `.bat` file and check there is no `set OPENAI_API_KEY=` line. There shouldn't be. The key must only be in `.env`.

## Part 2. Put it on GitHub

### Option A: GitHub Desktop (easiest)

1. Install GitHub Desktop from desktop.github.com and sign in with your GitHub account.
2. File > Add local repository > choose the `expense-agent` folder. It will say it isn't a git repository, click "create a repository here". Name: `coit12204-expense-agent`. Untick "Initialize with README" because there already is one. Git ignore: none (there already is one).
3. In the Changes tab you'll see every file. Check `.env` and `.venv` are NOT in the list. If `.env` is there, stop and fix `.gitignore`.
4. Make the commits below one by one. Tick only the files listed, write the message, press Commit.
5. Click "Publish repository". Keep it **Private**, then add your marker or unit coordinator as a collaborator if they ask, or make it public only if the unit says so.
6. Copy the repository URL (Repository > View on GitHub) and put it in the report cover page and on Moodle.

### Option B: Command line

Open a terminal in the project folder.

```
git init
git config user.name "Tanjim Ahmed Mahi"
git config user.email "your-github-email@example.com"
git add .gitignore README.md requirements.txt pytest.ini .env.example
git commit -m "Project setup, requirements and README"
git add app/config.py app/logger.py app/models.py app/store.py data/expenses.json
git commit -m "Config, data models and the expense store with sample data"
git add app/tools.py app/prompts.py
git commit -m "LangChain tools and prompt templates"
git add app/agent.py run_demo.py run.bat
git commit -m "ExpenseAgent with AgentExecutor, parsing, retry and fallback rules"
git add app/state.py
git commit -m "AgentState with transition logging and JSON persistence"
git add app/main.py app/static/index.html run_server.bat
git commit -m "FastAPI endpoints, error handling, middleware and the web page"
git add tests/ run_tests.bat
git commit -m "pytest suite with fake model, monkeypatch and TestClient"
git add scripts/ run_eval.bat
git commit -m "Evaluation script for comparing prompt versions"
git add evaluation/
git commit -m "Evaluation results before and after the fixes"
git add docs/
git commit -m "Technical report, video script and submission guide"
git status
```

`git status` should say "nothing to commit". If it lists `.env`, do NOT add it.

Then on github.com click New repository, name it `coit12204-expense-agent`, Private, no README, create. Copy the two lines it shows under "push an existing repository" and run them:

```
git remote add origin https://github.com/YOUR-USERNAME/coit12204-expense-agent.git
git push -u origin main
```

(If it says `master` instead of `main`, use `git branch -M main` first.)

### After pushing

Open the repository in the browser and check: `.env` is not there, `.venv` is not there, `README.md` shows on the front page, and the `evaluation` and `docs` folders are there.

## Part 3. Moodle submission

Three things go on Moodle:

1. **Code.** Either the GitHub link, or a zip. To make the zip: copy the folder somewhere else, delete `.venv`, `.env`, `logs`, `.pytest_cache` and `__pycache__` folders from the copy, then right click > Compress to zip. Name it `COIT12204_A3_12298057.zip`.
2. **Report.** `docs/COIT12204_A3_Report_Tanjim_Ahmed_Mahi.docx` with the four screenshots pasted into the dashed boxes, then File > Save As > PDF.
3. **Video.** 5 to 7 minutes, recorded from `docs/COIT12204_A3_Video_Script_Tanjim_Ahmed_Mahi.docx`. Upload the mp4 or a link, whatever the unit asks for.

## Part 4. Marking criteria check

Go through this and make sure you could point a marker at each thing.

### Agent implementation (25%)

| Brief says | Where it is |
|---|---|
| Uses LangChain (tools, chains or agent executor) | `app/agent.py`: `create_tool_calling_agent` + `AgentExecutor` |
| At least one tool | `app/tools.py`: three `@tool` functions |
| Prompt template | `app/prompts.py`: `ChatPromptTemplate` with `MessagesPlaceholder("agent_scratchpad")` |
| Structured output | `AgentResult` pydantic model + `PydanticOutputParser` |
| Handles errors gracefully | parse retry, fallback rules, tools return error dicts, `try/except` around the executor |

### State management (15%)

| Brief says | Where it is |
|---|---|
| `AgentState` class | `app/state.py` |
| At least three tracked variables | eight: run_count, error_count, fallback_count, last_action, last_result, last_tool_call, last_error, history |
| Updates after each run | `record_run()` called at the end of `ExpenseAgent.run()` |
| Logging of state transitions | `_transition()` logs `STATE TRANSITION name: old -> new` |

### Endpoint integration (15%)

| Brief says | Where it is |
|---|---|
| At least one agent endpoint | three: `/api/agent/categorize_expense`, `/check_unusual_expense`, `/monthly_summary` |
| Input validation | pydantic request models, 422 on bad body, 404 on unknown id before the model runs |
| Error handling | one error shape for 400 / 404 / 422 / 500, model failure returns 200 with `fallback_used` |
| Logging | `REQUEST` / `RESPONSE` lines with a request id, `X-Request-ID` header |
| Output formatting | `format_response()` gives every endpoint the same JSON |

### Testing suite (20%)

| Brief says | Where it is |
|---|---|
| Agent wrapper functions | `tests/test_agent.py` |
| State transitions | `tests/test_state.py` (uses caplog to check the log text) |
| Tool behaviour | `tests/test_tools.py` |
| Endpoint integration | `tests/test_api.py` |
| Mocked LLM calls | `tests/fakes.py` FakeChatModel, `get_llm` blocked with monkeypatch |
| Fallback logic | `test_two_bad_replies_fall_back_to_rules`, `test_model_exception_falls_back`, `test_model_failure_still_returns_200_with_fallback` |
| Uses monkeypatch, TestClient, assertions on state, logs and outputs | yes, all three, see `conftest.py` |

### Evaluation and report (20%)

| Brief says | Where it is |
|---|---|
| Accuracy, reliability, consistency, failure modes, state behaviour, prompt effectiveness | report section 6, `evaluation/summary.md` |
| At least 3 failures | report has 5 (fenced JSON, confidence 0.9 on a missing expense, rate limit fallbacks, headphones keyword bug, over-use of tools) |
| At least 3 prompt refinements | v2 only JSON, v2 tool first, v3 confidence rules, v3 category rubric, v3 fixed window |
| At least 2 improvements after evaluation | max_retries 3 + pause, whole word keyword match, confidence cap when no answer |
| Screenshots of logs, state transitions, test outputs | the four dashed boxes in the report, take them before you export the PDF |
| Word count 1,800 to 2,000 | 2,049 in the body, each section inside its own range |

### Professionalism (5%)

README with setup steps, `.env.example`, `.gitignore`, comments in the code, clean commit history (see Part 2).

## Part 5. Bonus marks

| Optional extension | Done? | Where |
|---|---|---|
| A second agent | No | mentioned as future work in the conclusion |
| A multi tool agent | Yes | three tools, the unusual check uses two in one run |
| A summary agent with structured output | Yes | `monthly_summary` action returns `AgentResult` with a `summary` field |
| A visual debugging dashboard | Yes | `app/static/index.html`, live state, history and log |
| Persistent state storage | Yes | `data/agent_state.json`, survives a restart |

Four out of five. Mention them in the video close and they're already in the report conclusion.

## Part 6. Screenshots for the report

Take these before exporting the PDF. Windows key + Shift + S, then paste into the dashed box.

1. **Figure 1.** Web page, right column, after three or four runs. Make sure a few blue `STATE TRANSITION` lines are visible in the log panel.
2. **Figure 2.** The `run_server.bat` window right after asking the agent something. Should show `REQUEST`, `TOOL CALL`, `STATE TRANSITION`, `RESPONSE` with the same request id.
3. **Figure 3.** The `run_tests.bat` window with `71 passed` at the bottom.
4. **Figure 4.** `evaluation/summary.md` open in Notepad or VS Code, showing both tables. Optionally also a `BAD` line from `evaluation/eval_output.txt` with the rate limit message.

## Part 7. After it's marked

Go to platform.openai.com, API keys, and delete or rotate the key you used. It was pasted into a few places during development and it's good practice.
