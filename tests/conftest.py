"""
Shared pytest fixtures.

The env vars at the top have to be set BEFORE anything from app is imported, because
config.py reads them at import time. Otherwise the tests would write into the real
logs/agent.log and data/ files.
"""
import os
import tempfile
from datetime import date

_tmp = tempfile.mkdtemp(prefix="expense_agent_tests_")
os.environ["LOG_FILE"] = os.path.join(_tmp, "test.log")
os.environ["EXPENSES_FILE"] = os.path.join(_tmp, "expenses.json")
os.environ["STATE_FILE"] = os.path.join(_tmp, "state.json")
os.environ["OPENAI_API_KEY"] = ""  # make sure no real key is used in tests

import pytest
from fastapi.testclient import TestClient

import app.agent
import app.store
import app.tools
from app.agent import ExpenseAgent
from app.main import create_app
from app.state import AgentState
from app.store import ExpenseStore
from tests.fakes import FakeChatModel


FIXED_TODAY = date(2026, 9, 15)


@pytest.fixture
def fixed_today(monkeypatch):
    """Freeze the date so the seed data and the 'days ago' maths are stable."""
    monkeypatch.setattr(app.store, "today", lambda: FIXED_TODAY)
    monkeypatch.setattr(app.tools, "today", lambda: FIXED_TODAY)
    monkeypatch.setattr(app.agent, "today", lambda: FIXED_TODAY)
    return FIXED_TODAY


@pytest.fixture(autouse=True)
def no_real_llm(monkeypatch):
    """Safety net: if any test forgets to pass a fake, get_llm blows up instead of calling OpenAI."""

    def _blocked():
        raise RuntimeError("get_llm() was called in a test, that should not happen")

    monkeypatch.setattr(app.agent, "get_llm", _blocked)


@pytest.fixture
def store(tmp_path, fixed_today):
    return ExpenseStore(path=str(tmp_path / "expenses.json"))


@pytest.fixture
def state(tmp_path):
    return AgentState(path=str(tmp_path / "state.json"), history_limit=5)


@pytest.fixture
def make_agent(store, state):
    """Factory: make_agent([responses...]) gives an agent driven by the fake model."""

    def _make(responses=None, raise_error=False, prompt_version="v1"):
        fake = FakeChatModel(responses=list(responses or []), raise_error=raise_error)
        agent = ExpenseAgent(store, state, llm=fake, prompt_version=prompt_version)
        agent.fake = fake  # so tests can inspect what the model was sent
        return agent

    return _make


@pytest.fixture
def client(store, state, make_agent):
    """TestClient with the fake agent plugged in. client.agent.fake is the fake model."""
    agent = make_agent([])
    application = create_app(store=store, state=state, agent=agent)
    test_client = TestClient(application, raise_server_exceptions=False)
    test_client.agent = agent
    return test_client
