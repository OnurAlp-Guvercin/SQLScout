"""evaluate.py testleri (aşama 2): BIRD kuralıyla puanlama ve sabit alt küme."""

import pytest

import config
import evaluate


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
def test_subset_is_fixed():
    first = evaluate.load_questions(subset=True)
    second = evaluate.load_questions(subset=True)
    assert len(first) == config.SUBSET_SIZE
    assert [q["question_id"] for q in first] == [q["question_id"] for q in second]
    assert [q["question_id"] for q in first] == sorted(q["question_id"] for q in first)
