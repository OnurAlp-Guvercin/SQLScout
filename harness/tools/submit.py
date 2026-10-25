"""Adım 7–9: submit tool'u. Submit edilen SQL'den cevap seçilir. Aynı model tool'suz ek SQL'ler (candidate) yazar; hepsi gerçek
sonuçlarına göre gruplanır ve en kalabalık grup seçilir (adım 7). Confidence gate grubun büyüklüğüne bakar (adım 8);
high ise cevap final check'ten geçer (adım 9)."""

import re
from concurrent.futures import ThreadPoolExecutor

import config
from agent import llm, prompts
from harness.tools import execute_sql


def run(sql, context):
    """Agent'ın submit'i. Return: {"done": cevap kabul edildi mi, "note": agent'a dönecek not, "handoff": nedeni}.
    Submit edilen SQL çalışmıyorsa candidate üretilmez; hata agent'a gider."""
    if result_of(sql, context) is None:
        error = execute_sql.check(context.db_path, sql) or execute_sql.run_sql(sql, context)["error"]
        return {"done": False, "note": f"Submit rejected: your query does not run: {error}", "handoff": None}
    groups, count = candidates(sql, context)  # adım 7
    context.selected_sql = groups[0]["sqls"][0] if groups else None
    level = confidence(groups, count)  # adım 8
    if level == "low":
        return {"done": False, "note": None, "handoff": "confidence low"}
    if level == "medium":
        context.medium_notes += 1
        if context.medium_notes > config.MAX_MEDIUM_NOTES:
            return {"done": False, "note": None, "handoff": "ikinci kez medium"}
        return {"done": False, "note": medium_note(groups, count), "handoff": None}

    note = final_check(context.selected_sql, context)  # adım 9
    if note is None:
        return {"done": True, "note": None, "handoff": None}
    context.final_check_fails += 1
    if context.final_check_fails >= config.FINAL_CHECK_TRIES:
        return {"done": False, "note": None, "handoff": "final check 2 kez geçmedi"}
    return {"done": False, "note": note, "handoff": None}


def candidates(agent_sql, context):
    """Agent'ın SQL'i ilk candidate'tir. Önce 2 ek candidate yazılır; sonuçları agent'ınkiyle aynı değilse toplam 8'e
    tamamlanır (adaptive rule). Return: (gruplar, candidate sayısı); en kalabalık grup başta."""
    sqls = [agent_sql]
    results = [result_of(agent_sql, context)]
    write_candidates(sqls, results, config.FIRST_EXTRA_CANDIDATES, context)
    agent_result = results[0]
    agree = agent_result is not None and all(
        result is not None and result["result_key"] == agent_result["result_key"] for result in results[1:])
    if not agree:
        write_candidates(sqls, results, config.TOTAL_CANDIDATES - len(sqls), context)
    return group(sqls, results), len(sqls)


def consensus_answer(context):
    """Hiçbir cevap kabul edilmediyse (fallback answer): tool'suz yazılan TOTAL_CANDIDATES candidate'in en kalabalık
    grubunun SQL'i; hepsi hata verirse None."""
    sqls, results = [], []
    write_candidates(sqls, results, config.TOTAL_CANDIDATES, context)
    groups = group(sqls, results)
    return groups[0]["sqls"][0] if groups else None


def write_candidates(sqls, results, count, context):
    """count candidate'i aynı anda ister (yerel sunucu bunları tek batch'te üretir), sonra sırayla çalıştırır.
    Prompt'ta adım 1'in bağlamı, search notes ve clarification'lar var; agent'ın SQL'i yok (kopyalamasın)."""
    prompt = candidate_prompt(context)
    seeds = []
    for _ in range(count):
        context.stats["candidates"] += 1
        # Her candidate ayrı bir örnek olsun diye seed'i farklı; aynı seed aynı SQL'i üretebilir.
        seeds.append(None if context.seed is None else context.seed * 100 + context.stats["candidates"])
    with ThreadPoolExecutor(count) as pool:
        replies = list(pool.map(lambda seed: write_sql(prompt, config.CANDIDATE_TEMPERATURE, seed), seeds))
    for reply in replies:
        context.count_usage(reply)
        sqls.append(reply["sql"])
        results.append(result_of(reply["sql"], context))


def candidate_prompt(context):
    prompt = context.messages[1]["content"]
    if context.search_notes:
        prompt += "\n\nSearch results found while working on this question:\n" + "\n".join(context.search_notes)
    if context.clarifications:
        prompt += "\n\nThe user clarified the question:"
        for item in context.clarifications:
            prompt += f"\n- Q: {item['question']} A: {item['answer']}"
    return prompt


def write_sql(prompt, temperature=None, seed=None):
    """Tool'suz tek bir SQL. Return: modelin cevabı, "sql" alanıyla."""
    messages = [{"role": "system", "content": prompts.WRITE_SQL}, {"role": "user", "content": prompt}]
    reply = llm.chat(messages, temperature=temperature, seed=seed)
    reply["sql"] = extract_sql(reply["text"])
    return reply


def extract_sql(text):
    """Modelin cevabından SQL'i çıkarır: önce ```sql bloğu, yoksa herhangi bir ``` bloğu, yoksa metnin tamamı
    (kapanmamış bir blok açılışı varsa o atılır)."""
    match = re.search(r"```sql\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if not match:
        match = re.search(r"```\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return re.sub(r"^```(sql)?", "", text.strip(), flags=re.IGNORECASE).strip()


def result_of(sql, context):
    """Candidate'in gerçek sonucu; pre-check'ten geçmeyen ya da hata veren: None."""
    if execute_sql.check(context.db_path, sql):
        return None
    result = execute_sql.run_sql(sql, context)
    return result if result["ok"] else None


def group(sqls, results):
    """Aynı result key'li candidate'ler bir gruptur; hata veren hiçbir gruba girmez. Kalabalık grup önce; başa baş
    olursa en önce üretilmiş candidate'i içeren (agent'ın SQL'i ilk olduğu için onun grubu)."""
    groups = {}
    for number in range(len(sqls)):
        result = results[number]
        if result is None:
            continue
        if result["result_key"] not in groups:
            groups[result["result_key"]] = {"sqls": [], "result": result, "first": number}
        groups[result["result_key"]]["sqls"].append(sqls[number])
    return sorted(groups.values(), key=lambda group: (-len(group["sqls"]), group["first"]))


def confidence(groups, candidate_count):
    """En kalabalık gruptaki candidate sayısı: high 3/3 ya da ≥6/8 · medium 4–5/8 · low ≤3/8."""
    largest = len(groups[0]["sqls"]) if groups else 0
    if largest == candidate_count or largest >= config.HIGH_MIN:
        return "high"
    if largest >= config.MEDIUM_MIN:
        return "medium"
    return "low"


def medium_note(groups, candidate_count):
    """Agent'a dönen not: en kalabalık 2 grubun temsilci SQL'i, candidate sayısı ve sonuç özeti."""
    lines = ["Medium confidence: other SQL queries written for this question give different results. "
             "The largest groups:"]
    for number, group in enumerate(groups[:config.MEDIUM_NOTE_GROUPS], start=1):
        result = group["result"]
        lines.append(f"Group {number} ({len(group['sqls'])} of {candidate_count} candidates): {group['sqls'][0]}")
        lines.append(f"  Columns: {', '.join(result['columns'])}; {result['row_count']} rows")
        for row in execute_sql.trim_rows(result["rows"][:config.MEDIUM_NOTE_ROWS]):
            lines.append("  " + " | ".join(row))
    lines.append("Decide which one answers the question: submit it, or run a new query first.")
    return "\n".join(lines)


def final_check(sql, context):
    """Geçerse None, geçmezse agent'a dönecek not. Cevap çalışmalı, hata vermemeli; boşsa agent bu SQL'i daha önce
    execute_sql ile çalıştırıp boş geldiğini görmüş olmalı."""
    note = execute_sql.check(context.db_path, sql)
    if note:
        return f"Final check failed: {note}"
    result = execute_sql.run_sql(sql, context)
    if not result["ok"]:
        return f"Final check failed: the query gives an error: {result['error']}"
    if result["row_count"] == 0 and execute_sql.sql_key(sql) not in context.ran_by_agent:
        return ("Final check failed: the query returns no rows. Check the values and conditions in the query; "
                "if an empty result is the right answer, run it with execute_sql first, then submit it again.")
    return None
