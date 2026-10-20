"""Adım 8: candidate generation & selection (aşama 18, 19). Agent'ın submit ettiği SQL de bir candidate'tir;
diğerlerini aynı model tool'suz ve aynı anda yazar. Prompt'ta adım 1 bağlamı, search notes ve clarification'lar var,
agent'ın SQL'i yok (kopyalamasın).
Hepsi gerçek sonuçlarına (result key) göre gruplanır; en kalabalık grubun cevabı seçilir. Pahalı bir candidate,
world model "hata verir" ya da "boş döner" diye güvenle tahmin ederse çalıştırılmadan düşer (aşama 28)."""

from concurrent.futures import ThreadPoolExecutor

import config
from agent import policy
from experience import log as experience_log
from harness import gates, precheck
from world_model import predict as world_model


def run(agent_sql, context):
    """Döner: (gruplar, candidate sayısı). Grup: {"sqls": üretim sırasıyla, "result": gerçek sonuç}; seçilen grup başta."""
    sqls = [agent_sql]
    results = [execute(agent_sql, context, "agent")]
    add_candidates(sqls, results, config.FIRST_EXTRA_CANDIDATES, context)
    agent_result = results[0]
    agree = agent_result is not None and all(
        result is not None and result["result_key"] == agent_result["result_key"] for result in results[1:])
    if not agree:  # adaptive rule: ayrıştılar, 8'e tamamla
        add_candidates(sqls, results, config.TOTAL_CANDIDATES - len(sqls), context)
    return group(sqls, results), len(sqls)


def add_candidates(sqls, results, count, context):
    """count candidate'i aynı anda ister (yerel sunucu bunları tek bir batch'te üretir), sonra sırayla çalıştırır."""
    prompt = candidate_prompt(context)
    seeds = []
    for _ in range(count):
        context.candidates_written += 1
        # Her candidate ayrı bir örnek olsun diye seed'i farklı; aynı seed aynı SQL'i üretebilir.
        seeds.append(None if context.seed is None else context.seed * 100 + context.candidates_written)
    with ThreadPoolExecutor(count) as pool:
        replies = list(pool.map(lambda seed: policy.write_sql(prompt, config.CANDIDATE_TEMPERATURE, seed), seeds))
    for reply in replies:
        context.count_usage(reply)
        sqls.append(reply["sql"])
        results.append(execute(reply["sql"], context, "candidate"))


def candidate_prompt(context):
    """Adım 1 bağlamı, search notes ve clarification'lar; agent'ın SQL'i yok."""
    prompt = context.messages[1]["content"]
    if context.search_notes:
        prompt += "\n\nSearch results found while working on this question:\n" + "\n".join(context.search_notes)
    if context.clarifications:
        prompt += "\n\nThe user clarified the question:"
        for item in context.clarifications:
            prompt += f"\n- Q: {item['question']} A: {item['answer']}"
    return prompt


def execute(sql, context, run_by):
    """Candidate'in gerçek sonucu (pre-check → cache ya da gerçek çalıştırma). Reddedilen, elenen ya da hata veren: None."""
    if run_by == "candidate" and eliminated(sql, context):
        return None
    note, result = precheck.run(sql, context, run_by)
    if note or not result["ok"]:
        return None
    return result


def eliminated(sql, context):
    """Aşama 28: daha önce çalışmamış pahalı bir candidate için world model'e sorulur; "hata verir" ya da "boş döner"
    diye güvenle (trusted) tahmin edilirse candidate düşer. Candidate'ler budget kullanmadığı için "budget az" sorulmaz."""
    if not config.USE_WORLD_MODEL or precheck.sql_key(sql) in context.cache or precheck.check(context.db_path, sql):
        return False
    if not precheck.is_expensive(sql, context.db_path):
        return False
    prediction = world_model.predict(sql, context)
    experience_log.write(context, sql, forecast=None, actual=None, seconds=0, run_by="candidate", prediction=prediction)
    return gates.trusted(prediction) and prediction["type"] in ("error", "empty")


def group(sqls, results):
    """Aynı result key'li candidate'ler bir gruptur; hata veren hiçbir gruba girmez. Sıra: kalabalık olan önce,
    başa başta en önce üretilmiş candidate'i içeren. Agent'ın SQL'i ilk üretilen olduğu için başa başta onun grubu seçilir."""
    groups = {}
    for number in range(len(sqls)):
        result = results[number]
        if result is None:
            continue
        if result["result_key"] not in groups:
            groups[result["result_key"]] = {"sqls": [], "result": result, "first": number}
        groups[result["result_key"]]["sqls"].append(sqls[number])
    return sorted(groups.values(), key=lambda group: (-len(group["sqls"]), group["first"]))
