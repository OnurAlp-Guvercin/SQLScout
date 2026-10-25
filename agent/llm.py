"""Modele request atar ve cevabı return eder. İstekler yerel mlx_lm.server'a ya da OpenRouter API'sine gider;
ikisi de aynı (OpenAI) biçimi konuşur, adres config.py'de.
Policy, candidate'ler ve teacher hep bunu kullanır. Denemek için: python -m agent.llm "soru" """

import functools
import http.client
import json
import os
import sys
import time
import urllib.error
import urllib.request

from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

import config


def chat(messages, temperature=None, tools=None, seed=None, model=None):
    """messages: [{"role": "system"/"user"/"assistant", "content": "..."}]. model yoksa policy modeli.
    Return: text, tool_calls, prompt_tokens, completion_tokens, cost (dolar, yalnızca API), seconds, provider."""
    body = request_body(messages, temperature, tools, seed, model or config.POLICY_MODEL)
    headers = {"Content-Type": "application/json"}
    key = api_key()
    if key:
        headers["Authorization"] = f"Bearer {key}"

    start = time.monotonic()
    answer = post(config.LLM_URL + "/chat/completions", body, headers)
    if "error" in answer or not answer.get("choices"):
        raise RuntimeError(f"Model API hatası: {json.dumps(answer)[:500]}")

    message = answer["choices"][0]["message"]
    usage = answer.get("usage", {})
    return {
        "text": message.get("content") or "",
        "tool_calls": message.get("tool_calls") or [],
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "cost": usage.get("cost"),
        "seconds": round(time.monotonic() - start, 2),
        "provider": answer.get("provider"),
    }


def request_body(messages, temperature, tools, seed, model):
    body = {
        "model": model,
        "messages": messages,
        "temperature": config.POLICY_TEMPERATURE if temperature is None else temperature,
        "top_p": config.POLICY_TOP_P,
        "max_tokens": config.MAX_NEW_TOKENS,
        # Thinking modu kapalı: ilki OpenRouter, ikincisi yerel mlx_lm.server için.
        "reasoning": {"enabled": False},
        "chat_template_kwargs": {"enable_thinking": False},
        "usage": {"include": True},  # OpenRouter request'in maliyetini de return eder
    }
    if config.POLICY_PROVIDER and model == config.POLICY_MODEL:
        body["provider"] = {"order": [config.POLICY_PROVIDER], "allow_fallbacks": False}
    if tools:
        body["tools"] = tools
    if seed is not None and config.SEND_SEED:
        body["seed"] = seed
    return body


def post(url, body, headers):
    # API bazen geçici hata verir (429: çok istek, 5xx: sunucu hatası); bunlarda bekleyip tekrar denenir.
    for attempt in range(config.LLM_RETRIES):
        last_attempt = attempt == config.LLM_RETRIES - 1
        request = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=config.LLM_TIMEOUT_SECONDS) as response:
                answer = json.load(response)
            # OpenRouter sağlayıcının hatasını bazen 200 cevabının içinde verir (ör. 504 zaman aşımı).
            code = (answer.get("error") or {}).get("code")
            temporary = isinstance(code, int) and (code == 429 or code >= 500)
            if not temporary or last_attempt:
                return answer
        except urllib.error.HTTPError as error:
            temporary = error.code == 429 or error.code >= 500
            if not temporary or last_attempt:
                detail = error.read().decode(errors="replace")[:500]
                raise RuntimeError(f"Model API hatası {error.code}: {detail}") from error
        except (OSError, http.client.HTTPException, json.JSONDecodeError) as error:
            # Bağlantı kurulamadı, okurken koptu, zaman aşımı ya da cevap JSON değil.
            if last_attempt:
                raise RuntimeError(f"Modele ulaşılamadı ({url}): {error}") from error
        time.sleep(5 * 2 ** attempt)


def api_key():
    """API key: önce environment variable, yoksa proje kökündeki .env dosyası. Yerel sunucuda gerekmez."""
    name = config.LLM_API_KEY_NAME
    if os.environ.get(name):
        return os.environ[name]
    env_file = config.PROJECT_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            key, _, value = line.partition("=")
            if key.strip().removeprefix("export ").strip() == name:
                return value.strip().strip("\"'")
    return None


def count_tokens(text):
    """Metnin Qwen tokenizer'ıyla kaç token olduğu. API gerekmez; tokenizer dosyası bir kez indirilir."""
    return len(tokenizer().encode(text).ids)


@functools.lru_cache(maxsize=None)
def tokenizer():
    return Tokenizer.from_file(hf_hub_download(config.TOKENIZER_MODEL, "tokenizer.json"))


if __name__ == "__main__":
    reply = chat([{"role": "user", "content": sys.argv[1]}])
    print(reply["text"])
    speed = reply["completion_tokens"] / reply["seconds"] if reply["seconds"] else 0
    print(f"\n[{config.POLICY_MODEL} @ {reply['provider']}: {reply['prompt_tokens']} prompt token, "
          f"{reply['completion_tokens']} cevap token, {reply['seconds']} sn, {speed:.1f} token/sn]")
