"""agent/llm.py testleri (aşama 4). API'ye gerçek request atan test, API key yoksa atlanır."""

import io
import time
import urllib.request

import pytest

import config
from agent import llm


def test_request_body_uses_config_and_disables_thinking(monkeypatch):
    monkeypatch.setattr(config, "POLICY_PROVIDER", "deepinfra")
    body = llm.request_body([{"role": "user", "content": "hi"}], None, None, None, config.POLICY_MODEL)
    assert body["model"] == config.POLICY_MODEL
    assert body["temperature"] == config.POLICY_TEMPERATURE
    assert body["top_p"] == config.POLICY_TOP_P
    assert body["max_tokens"] == config.MAX_NEW_TOKENS
    assert body["reasoning"] == {"enabled": False}
    assert body["chat_template_kwargs"] == {"enable_thinking": False}
    assert body["provider"] == {"order": ["deepinfra"], "allow_fallbacks": False}
    assert "tools" not in body
    assert "seed" not in body
    other = llm.request_body([], None, None, None, "qwen/qwen3.6-27b")  # ör. teacher
    assert other["model"] == "qwen/qwen3.6-27b" and "provider" not in other


def test_request_body_passes_given_values(monkeypatch):
    tools = [{"type": "function", "function": {"name": "submit"}}]
    body = llm.request_body([], 0.0, tools, 7, config.POLICY_MODEL)
    assert body["temperature"] == 0.0
    assert body["tools"] == tools
    assert "seed" not in body  # yerel sunucu seed'li istekleri batch'e almaz
    monkeypatch.setattr(config, "SEND_SEED", True)
    assert llm.request_body([], None, None, 7, config.POLICY_MODEL)["seed"] == 7


def test_local_server_needs_no_provider(monkeypatch):
    monkeypatch.setattr(config, "POLICY_PROVIDER", None)
    assert "provider" not in llm.request_body([], None, None, None, config.POLICY_MODEL)


def test_api_key_is_read_from_env_file(tmp_path, monkeypatch):
    monkeypatch.delenv(config.LLM_API_KEY_NAME, raising=False)
    monkeypatch.setattr(config, "PROJECT_DIR", tmp_path)
    assert llm.api_key() is None
    (tmp_path / ".env").write_text(f'OTHER=1\nexport {config.LLM_API_KEY_NAME}="secret-123"\n')
    assert llm.api_key() == "secret-123"
    monkeypatch.setenv(config.LLM_API_KEY_NAME, "from-environment")
    assert llm.api_key() == "from-environment"


def test_dropped_connection_is_retried(monkeypatch):
    attempts = []

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(request, timeout):
        attempts.append(1)
        if len(attempts) == 1:
            raise ConnectionResetError("bağlantı koptu")
        return Response(b'{"choices": []}')

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    assert llm.post("http://test", {}, {}) == {"choices": []}
    assert len(attempts) == 2


def test_count_tokens():
    assert llm.count_tokens("SELECT 1") > 0
    assert llm.count_tokens("SELECT name FROM users") > llm.count_tokens("SELECT 1")


@pytest.mark.skipif(llm.api_key() is None, reason="API key yok (.env'de OPENROUTER_API_KEY)")
def test_api_answers():
    reply = llm.chat([{"role": "user", "content": "Reply with exactly one word: OK"}], temperature=0.0, max_tokens=5)
    assert reply["text"].strip()
    assert reply["completion_tokens"] > 0
