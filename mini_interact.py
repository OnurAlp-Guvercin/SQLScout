"""Mini-Interact (aşama 30): BIRD-Interact'in SQLite'lı küçük sürümü; 300 belirsiz SELECT görevi, 26 veritabanı.
Görevleri evaluate.py'nin soru biçimine çevirir. Agent'ın evidence'ı veritabanının bilgi tabanıdır (<db>_kb.jsonl);
görevin gizlediği maddeler (deleted_knowledge) çıkarılır; agent onları ask_user ile öğrenebilir.
Doğru SQL'ler (sol_sql) açık dosyada yoktur: bird.bench25@gmail.com'dan istenip MINI_INTERACT_GOLD dosyasına
(her satır {"instance_id", "sol_sql"}) konursa okunur; yoksa sorular çalışır ama puanlanmaz."""

import json

import config


def load_questions():
    gold = {}
    if config.MINI_INTERACT_GOLD.exists():
        for line in config.MINI_INTERACT_GOLD.read_text().splitlines():
            task = json.loads(line)
            sol_sql = task["sol_sql"]
            gold[task["instance_id"]] = sol_sql[0] if isinstance(sol_sql, list) else sol_sql

    questions = []
    for line in (config.MINI_INTERACT_DIR / "mini_interact.jsonl").read_text().splitlines():
        task = json.loads(line)
        db_id = task["selected_database"]
        questions.append({
            "question_id": task["instance_id"], "db_id": db_id,
            "db_path": str(config.MINI_INTERACT_DIR / db_id / f"{db_id}.sqlite"),
            "question": task["amb_user_query"], "evidence": knowledge(task), "SQL": gold.get(task["instance_id"]),
        })
    return questions


def knowledge(task):
    """Veritabanının bilgi tabanı, görevde gizlenen maddeler hariç; her madde tek satır."""
    hidden = set()
    for item in task["knowledge_ambiguity"]:
        hidden.add(item.get("deleted_knowledge"))
    db_id = task["selected_database"]
    lines = ["Knowledge base of this database:"]
    for line in (config.MINI_INTERACT_DIR / db_id / f"{db_id}_kb.jsonl").read_text().splitlines():
        item = json.loads(line)
        if item["id"] not in hidden:
            lines.append(f"- {item['knowledge']}: {item['definition']}")
    return "\n".join(lines)
