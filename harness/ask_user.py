"""Adım 3: ask_user (aşama 23, 24, 31). Agent'ın netleştirme sorusunu run.py'de terminaldeki kişiye, evaluate.py'de
user simulator'e sorar: BIRD'de gold SQL'i gören tek adımlı simulator, Mini-Interact'te benchmark'ın kendi iki adımlı
simulator'ü. Cevap clarification olarak saklanır: candidate prompt'una girer, teacher konuşmada görür.
Gold SQL'i ve belirsizlik notlarını yalnızca simulator görür; agent'ın mesajlarına hiç girmezler."""

import json
import re
from pathlib import Path

import config
from agent import llm, prompts

REFUSAL = "Sorry, I can only explain what I meant, not write the query."


def run(question, context):
    if len(context.clarifications) >= config.MAX_ASK_USER:
        return f"Rejected: you can ask the user at most {config.MAX_ASK_USER} times for one question."
    if context.ambiguity is not None:
        answer = simulate_mini_interact(question, context)
    elif context.gold_sql is not None:
        answer = simulate(question, context)
    else:
        answer = input(f"\nAgent asks: {question}\nYour answer: ").strip()
    if re.search(r"\bselect\b.+\bfrom\b", answer, re.IGNORECASE | re.DOTALL):  # simulator SQL'i söylemesin
        answer = REFUSAL
    context.clarifications.append({"question": question, "answer": answer})
    return f"User's answer: {answer}"


def simulate(question, context):
    """BIRD'ün user simulator'ü: gold SQL'i görerek kullanıcı gibi tek cümleyle cevap verir."""
    request = (f"Your question: {context.question}\nEvidence: {context.evidence or '-'}\n"
               f"Secret SQL (what you meant): {context.gold_sql}\n\nThe assistant asks: {question}")
    messages = [{"role": "system", "content": prompts.USER_SIMULATOR}, {"role": "user", "content": request}]
    return ask_model(messages, context)


def simulate_mini_interact(question, context):
    """Mini-Interact'in simulator'ü: encoder soruyu sınıflandırır (labeled / unlabeled / unanswerable), decoder bu
    karara göre cevaplar. Resmi kodda olup burada olmayanlar: gold SQL yoksa "(not available)" yazılır, SQL tek parça
    verilir (resmi kod parçalara böler) ve netleştirilmiş soru yerine belirsiz soru verilir (o, LiveSQLBench'tedir)."""
    gold = context.gold_sql or "(not available)"
    notes = json.dumps(context.ambiguity, indent=4)
    encoder = (prompts.MINI_INTERACT_ENCODER.replace("[[amb_json]]", notes).replace("[[SQL_Glot]]", gold)
               .replace("[[clarification_Q]]", question))
    action = ask_model([{"role": "user", "content": encoder}], context).splitlines()[0]

    db_id = Path(context.db_path).stem
    schema = (Path(context.db_path).parent / f"{db_id}_schema.txt").read_text()
    decoder = (prompts.MINI_INTERACT_DECODER.replace("[[DB_schema]]", schema).replace("[[amb_json]]", notes)
               .replace("[[GT_SQL]]", gold).replace("[[SQL_Glot]]", gold).replace("[[clarification_Q]]", question)
               .replace("[[Action]]", action).replace("[[clear_query]]", context.question))
    return ask_model([{"role": "user", "content": decoder}], context)


def ask_model(messages, context):
    """Simulator modeline sorar. Prompt'lar "<s>" ile biter; cevap "</s>"e kadar olan kısımdır."""
    reply = llm.chat(messages, model=config.SIMULATOR_MODEL, temperature=0)
    context.count_usage(reply)
    return reply["text"].replace("<s>", "").split("</s>")[0].strip() or REFUSAL
