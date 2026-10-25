"""Adım 3: ask_user tool'u. Soruyu terminaldeki kişiye sorar (run.py'de de evaluate.py'de de); cevap clarification
olarak saklanır ve candidate prompt'una girer (adım 7)."""

import threading

import config

terminal_lock = threading.Lock()


def run(question, context):
    """Return: agent'a gidecek metin (kullanıcının cevabı ya da sınır aşıldıysa ret notu)."""
    if len(context.clarifications) >= config.MAX_ASK_USER:
        return f"Rejected: you can ask the user at most {config.MAX_ASK_USER} times for one question."
    with terminal_lock:  # evaluate.py soruları aynı anda çalıştırır; sorular terminale tek tek gelsin
        answer = input(f"\nQuestion: {context.question}\nAgent asks: {question}\nYour answer: ").strip()
    context.clarifications.append({"question": question, "answer": answer})
    return f"User's answer: {answer}"
