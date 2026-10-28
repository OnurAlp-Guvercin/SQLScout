"""evaluate.py testleri: BIRD kuralıyla puanlama, sabit alt küme ve experience log."""

import json

import pytest

import config
import evaluate
from agent import llm, prompts
from tests.fakes import execute_reply, submit_reply, text_reply


def gold(db, sql):
    return evaluate.run_gold({"db_path": db, "SQL": sql})


def test_same_rows_in_other_order_is_correct(db):
    assert evaluate.is_correct(db, "SELECT city FROM items ORDER BY id DESC", gold(db, "SELECT city FROM items"))


def test_other_rows_are_wrong(db):
    assert not evaluate.is_correct(db, "SELECT city FROM items WHERE id < 2", gold(db, "SELECT city FROM items"))


def test_failing_answer_is_wrong(db):
    assert not evaluate.is_correct(db, "SELECT nope FROM items", gold(db, "SELECT city FROM items"))


def test_failing_gold_makes_every_answer_wrong(db):
    failing = gold(db, "SELECT nope FROM items")
    assert not evaluate.is_correct(db, "SELECT city FROM items", failing)
    assert "nope" in failing["error"]


def test_failing_gold_is_reported(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply("SELECT COUNT(*) FROM items"), submit_reply("SELECT COUNT(*) FROM items")]
    question = {"question_id": 7, "db_id": "shop", "db_path": db, "question": "How many items?", "evidence": "",
                "SQL": "SELECT nope FROM items"}
    row = evaluate.run_one(question)
    assert row["correct"] is False and "nope" in row["gold_error"]


def test_gold_gets_the_long_timeout(db, monkeypatch):
    seen = []
    monkeypatch.setattr(evaluate.sqlite_db, "execute", lambda path, sql, timeout: seen.append(timeout))
    gold(db, "SELECT 1")
    assert seen == [config.ANSWER_TIMEOUT_SECONDS]


@pytest.mark.skipif(not (config.BIRD_DEV_DIR / "dev.json").exists(), reason="BIRD dev indirilmemiş")
def test_limit_takes_a_fixed_sample_in_dataset_order():
    questions = evaluate.load_questions()
    first, second = evaluate.sample(questions, 50), evaluate.sample(questions, 50)
    assert len(first) == 50
    assert [q["question_id"] for q in first] == [q["question_id"] for q in second]
    assert [q["question_id"] for q in first] == sorted(q["question_id"] for q in first)
    assert len({q["db_id"] for q in evaluate.sample(questions, 10)}) > 1  # ilk 10 soru gibi tek veritabanından değil

def test_evaluation_adds_split_and_correctness_to_the_experience_log(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply("SELECT COUNT(*) FROM items"), submit_reply("SELECT COUNT(*) FROM items")]
    question = {"question_id": 7, "db_id": "shop", "db_path": db, "question": "How many items?", "evidence": "",
                "SQL": "SELECT COUNT(id) FROM items"}
    row = evaluate.run_one(question)
    record = json.loads(config.EXPERIENCE_LOG.read_text())
    assert record["split"] == "dev" and record["question_id"] == 7 and record["correct"] is True
    assert row["correct"] is True and "messages" not in row  # konuşma sonuç dosyasına girmez


def test_evaluation_scores_the_sql_the_large_model_checked(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply("SELECT COUNT(*) FROM items"), submit_reply("SELECT COUNT(*) FROM items")]
    question = {"question_id": 7, "db_id": "shop", "db_path": db, "question": "How many items?", "evidence": "",
                "SQL": "SELECT COUNT(id) FROM items"}
    row = evaluate.run_one(question)
    assert row["large_model_checks"] == [{"sql": "SELECT COUNT(*) FROM items", "approved": True,
                                      "reason": "It answers the question.", "correct": True}]


def test_large_model_checked_sql_of_another_answer_is_scored_on_its_own(db, fake_model, monkeypatch):
    replies, _ = fake_model
    replies += [execute_reply("SELECT id FROM items"), submit_reply("SELECT id FROM items")]  # small model: large model "no"
    replies += [execute_reply("SELECT COUNT(*) FROM items"), submit_reply("SELECT COUNT(*) FROM items")]  # large model
    fake = llm.chat

    def large_model_says_no(messages, **kwargs):  # yalnızca agent'ın cevabına "no"
        if messages[0]["content"] == prompts.CHECK_ANSWER and "SELECT id FROM items" in messages[1]["content"]:
            return text_reply('{"reason": "It lists ids.", "correct": false}')
        return fake(messages, **kwargs)

    monkeypatch.setattr(llm, "chat", large_model_says_no)
    question = {"question_id": 7, "db_id": "shop", "db_path": db, "question": "How many items?", "evidence": "",
                "SQL": "SELECT COUNT(id) FROM items"}
    row = evaluate.run_one(question)
    assert row["correct"] is True and row["answered_by"] == "large_model"
    assert row["large_model_checks"] == [{"sql": "SELECT id FROM items", "approved": False, "reason": "It lists ids.",
                                      "correct": False}]
