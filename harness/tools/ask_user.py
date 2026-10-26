"""Adım 3: ask_user tool'u. Soruyu terminaldeki kişiye sorar (run.py'de de evaluate.py'de de); cevap clarification
olarak saklanır ve candidate prompt'una girer (adım 7)."""

import threading

import config

terminal_lock = threading.Lock()


def run(question, context):
    """Agent ask_user(question) çağırınca run_steps bunu çağırır (adım 3).
    1. Bu soruda MAX_ASK_USER (5) kez sorulduysa sorulmaz, ret notu return edilir.
    2. Soru terminale yazılır, kullanıcının (ya da deneyi yürüten kişinin) cevabı beklenir. evaluate.py soruları aynı
       anda çalıştırdığı için terminal_lock soruların terminale tek tek gelmesini sağlar.
    3. Soru ve cevap context.clarifications'a eklenir; candidate'ler (adım 7) cevabı buradan görür.
    Return: agent'a gidecek metin, ör. "User's answer: the hero names" ya da ret notu."""
    if len(context.clarifications) >= config.MAX_ASK_USER:
        return f"Rejected: you can ask the user at most {config.MAX_ASK_USER} times for one question."
    with terminal_lock:  # evaluate.py soruları aynı anda çalıştırır; sorular terminale tek tek gelsin
        answer = input(f"\nQuestion: {context.question}\nAgent asks: {question}\nYour answer: ").strip()
    context.clarifications.append({"question": question, "answer": answer})
    return f"User's answer: {answer}"
