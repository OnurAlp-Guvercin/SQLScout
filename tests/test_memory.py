"""harness/memory.py testleri (adım 1): benzer çözülmüş soruların seçimi ve bağlama eklenmesi. Embedding modeli
yüklenmez; conftest.py'deki sahte embedding kelime paylaşımına bakar."""

import json

import config
from agent import llm, loop, prompts
from harness import memory, prepare
from tests.fakes import execute_reply, submit_reply

COUNT_SQL = "SELECT COUNT(*) FROM items"


def row(question, sql="SELECT 1", split="train", run=None, correct=True, label=None):
    return {"question": question, "evidence": "", "sql": sql, "split": split, "run": run, "correct": correct,
            "label": label}


def test_most_similar_questions_come_first():
    memory.add([row("How many items are in Boston?", "SELECT 1"), row("List the names of the stores", "SELECT 2"),
                row("How many items are in Chicago?", "SELECT 3")])
    found = memory.similar("How many items are in Boston?", "", None)
    assert [example["sql"] for example in found] == ["SELECT 1", "SELECT 3"]  # alakasız soru eşiğin altında kaldı


def test_at_most_the_configured_number_of_examples():
    memory.add([row("How many items are in Boston?") for _ in range(config.MEMORY_EXAMPLES + 2)])
    assert len(memory.similar("How many items are in Boston?", "", None)) == config.MEMORY_EXAMPLES


def test_candidate_rules():
    assert memory.is_candidate(row("q", correct=True), "run_a")  # train: gold'a göre doğru
    assert not memory.is_candidate(row("q", correct=False), "run_a")
    assert memory.is_candidate(row("q", split="dev", run="run_a", correct=False, label="ok"), "run_a")  # onay yeter
    assert not memory.is_candidate(row("q", split="dev", run="run_a", correct=True, label="fallback"), "run_a")
    assert not memory.is_candidate(row("q", split="dev", run="run_b", label="ok"), "run_a")  # başka koşu sızmaz
    assert not memory.is_candidate(row("q", split="use", label="ok"), "run_a")  # değerlendirmede yalnızca train + bu koşu
    assert memory.is_candidate(row("q", split="dev", run="run_b", label="ok"), None)  # kullanımda hepsi
    assert not memory.is_candidate(row("q", split="use", label="unchecked"), None)


def test_examples_are_shown_before_the_evidence_and_question(db):
    examples = [{"question": "How many stores?", "evidence": "", "sql": "SELECT COUNT(*) FROM stores"}]
    context = prepare.build_context("How many items?", "item = row", db, examples)
    assert context.index("Similar questions answered before") < context.index("1. Question: How many stores?")
    assert context.index("SQL: SELECT COUNT(*) FROM stores") < context.index("Evidence: item = row")
    assert "Similar questions" not in prepare.build_context("How many items?", "", db)


def test_a_solved_question_helps_the_next_one(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)] * 2
    loop.answer_question("How many items are there?", "", db)
    loop.answer_question("How many items are there in total?", "", db)
    assert f"SQL: {COUNT_SQL}" not in seen[0][1]["content"]  # ilk soruda bellek boş
    assert f"SQL: {COUNT_SQL}" in seen[2][1]["content"]  # ikinci soru ilkinin cevabını görüyor
    record = json.loads(config.EXPERIENCE_LOG.read_text().splitlines()[1])
    assert f"SQL: {COUNT_SQL}" in record["messages"][1]["content"]  # eğitim verisi de aynı bağlamı taşır


def test_the_reviewer_does_not_see_the_examples(db, fake_model, monkeypatch):
    memory.add([row("How many items are there?", COUNT_SQL)])
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    reviews = []
    fake = llm.chat

    def recording(messages, **kwargs):
        if messages[0]["content"] == prompts.CHECK_ANSWER:
            reviews.append(messages[1]["content"])
        return fake(messages, **kwargs)

    monkeypatch.setattr(llm, "chat", recording)
    loop.answer_question("How many items are there?", "", db)
    assert "Similar questions" in seen[0][1]["content"]  # small model örneği gördü
    assert reviews and "Similar questions" not in reviews[0]  # kontrol eden large model görmedi


def test_without_memory_nothing_is_read_or_written(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "MEMORY", False)
    memory.add([row("How many items are there?", COUNT_SQL)])
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    loop.answer_question("How many items are there?", "", db)
    assert "Similar questions" not in seen[0][1]["content"]
    assert len(memory.read_rows()) == 1  # yalnızca elle eklenen satır


def test_bird_train_is_added_as_correct_examples(tmp_path):
    path = tmp_path / "train.json"
    path.write_text(json.dumps([{"question": "How many items?", "evidence": "", "SQL": COUNT_SQL, "db_id": "shop"}]))
    memory.add_bird_train(path)
    rows = memory.read_rows()
    assert len(rows) == 1 and rows[0]["split"] == "train" and rows[0]["correct"] == 1 and rows[0]["sql"] == COUNT_SQL


def test_an_answer_accepted_without_a_check_is_not_an_example(db, fake_model, monkeypatch):
    """Large model'e ulaşılamazsa cevap kontrolsüz kabul edilir; memory'ye "unchecked" girer, örnek olmaz."""
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    fake = llm.chat

    def large_model_down(messages, **kwargs):
        if messages[0]["content"] == prompts.CHECK_ANSWER:
            raise RuntimeError("Modele ulaşılamadı")
        return fake(messages, **kwargs)

    monkeypatch.setattr(llm, "chat", large_model_down)
    loop.answer_question("How many items are there?", "", db)
    assert [row["label"] for row in memory.read_rows()] == ["unchecked"]
    assert memory.similar("How many items are there?", "", None) == []


def test_missing_evidence_does_not_break_the_memory():
    memory.add([row("How many items are there?") | {"evidence": None}])
    assert len(memory.similar("How many items are there?", None, None)) == 1
