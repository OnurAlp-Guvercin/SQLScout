"""evaluate.py testleri: BIRD kuralıyla puanlama, sabit alt küme ve experience log."""

import json

import pytest

import config
import evaluate
from tests.fakes import execute_reply, submit_reply


def test_same_rows_in_other_order_is_correct(db):
    assert evaluate.score(db, "SELECT city FROM items ORDER BY id DESC", "SELECT city FROM items") == (True, None)


def test_other_rows_are_wrong(db):
    assert evaluate.score(db, "SELECT city FROM items WHERE id < 2", "SELECT city FROM items") == (False, None)


def test_failing_answer_is_wrong(db):
    assert evaluate.score(db, "SELECT nope FROM items", "SELECT city FROM items") == (False, None)


def test_failing_gold_is_reported(db):
    correct, gold_error = evaluate.score(db, "SELECT city FROM items", "SELECT nope FROM items")
    assert not correct
    assert "nope" in gold_error


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
    replies += [execute_reply("SELECT COUNT(*) FROM items"), submit_reply()]
    question = {"question_id": 7, "db_id": "shop", "db_path": db, "question": "How many items?", "evidence": "",
                "SQL": "SELECT COUNT(id) FROM items"}
    row = evaluate.run_one(question, seed=0)
    record = json.loads(config.EXPERIENCE_LOG.read_text())
    assert record["split"] == "dev" and record["question_id"] == 7 and record["correct"] is True
    assert row["correct"] is True and "messages" not in row  # konuşma sonuç dosyasına girmez
