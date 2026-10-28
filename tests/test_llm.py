"""agent/llm.py testleri (aşama 4). API'ye gerçek request atan test, API key yoksa atlanır."""

import io
import time
import urllib.error
import urllib.request

import pytest

import config
from agent import llm


def test_request_body_uses_config_and_disables_thinking(monkeypatch):
    monkeypatch.setattr(config, "SMALL_MODEL_PROVIDERS", ["deepinfra", "parasail"])
    body = llm.request_body([{"role": "user", "content": "hi"}], None, None, config.SMALL_MODEL)
    assert body["model"] == config.SMALL_MODEL
    assert body["temperature"] == config.TEMPERATURE
    assert body["top_p"] == config.TOP_P
    assert body["max_tokens"] == config.MAX_NEW_TOKENS
    assert body["reasoning"] == {"enabled": False}
    assert body["chat_template_kwargs"] == {"enable_thinking": False}
    assert body["provider"] == {"order": ["deepinfra", "parasail"], "allow_fallbacks": False}
    assert "tools" not in body
    monkeypatch.setattr(config, "LARGE_MODEL_PROVIDERS", None)
    other = llm.request_body([], None, None, config.LARGE_MODEL)
    assert other["model"] == config.LARGE_MODEL and "provider" not in other


def test_large_model_goes_to_its_own_address_with_the_key(monkeypatch):
    monkeypatch.setattr(config, "SMALL_MODEL_URL", "http://127.0.0.1:8080/v1")
    monkeypatch.setattr(config, "LARGE_MODEL_URL", "https://api.example/v1")
    monkeypatch.setattr(llm, "api_key", lambda: "secret")
    sent = []

    def post(url, body, headers):
        sent.append((url, headers.get("Authorization")))
        return {"choices": [{"message": {"content": "ok"}}]}

    monkeypatch.setattr(llm, "post", post)
    llm.chat([], model=config.LARGE_MODEL)
    llm.chat([])
    assert sent == [("https://api.example/v1/chat/completions", "Bearer secret"),
                    ("http://127.0.0.1:8080/v1/chat/completions", None)]


def test_request_body_passes_given_values():
    tools = [{"type": "function", "function": {"name": "submit"}}]
    body = llm.request_body([], 0.0, tools, config.SMALL_MODEL)
    assert body["temperature"] == 0.0
    assert body["tools"] == tools


def test_local_server_needs_no_provider(monkeypatch):
    monkeypatch.setattr(config, "SMALL_MODEL_PROVIDERS", None)
    assert "provider" not in llm.request_body([], None, None, config.SMALL_MODEL)


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



def test_wrong_key_stops_the_run(monkeypatch):
    """401/402: her soru aynı hatayı alır; cevaplar kontrolsüz kabul edilmesin diye koşu durur."""
    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError("http://test", 401, "Unauthorized", {}, io.BytesIO(b"no auth"))

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(SystemExit):
        llm.post("http://test", {}, {})

def test_count_tokens():
    assert llm.count_tokens("SELECT 1") > 0
    assert llm.count_tokens("SELECT name FROM users") > llm.count_tokens("SELECT 1")


@pytest.mark.skipif(llm.api_key() is None, reason="API key yok (.env'de OPENROUTER_API_KEY)")
def test_api_answers():
    reply = llm.chat([{"role": "user", "content": "Reply with exactly one word: OK"}], temperature=0.0,
                     model=config.LARGE_MODEL)
    assert reply["text"].strip()
    assert reply["completion_tokens"] > 0
