"""B5 testleri: placeholder world model (aşama 26), prediction gate ve audit (aşama 27), candidate eleme (aşama 28)."""

import json

import config
from agent import loop
from tests.fakes import execute_reply, json_reply, sql_reply, submit_reply
from world_model import predict

COUNT_SQL = "SELECT COUNT(*) FROM items WHERE price > 100"  # price'ta index yok: tablo taranır
SURE = {"type": "rows", "columns": ["n"], "rows": "1", "values": [[150]],
        "confidence": {"type": 0.95, "shape": 0.95, "values": 0.5}}


def test_prediction_is_read_and_broken_output_means_unknown():
    assert predict.read_prediction("Here: " + json.dumps(SURE))["confidence"]["shape"] == 0.95
    assert predict.read_prediction("no json") == predict.UNKNOWN
    assert predict.read_prediction(json.dumps(dict(SURE, type="many"))) == predict.UNKNOWN
    no_confidence = predict.read_prediction(json.dumps(dict(SURE, confidence={"type": 2, "shape": 1, "values": 0})))
    assert no_confidence["type"] == "rows" and no_confidence["confidence"] == {"type": 0, "shape": 0, "values": 0}


def expensive(monkeypatch, audit_share=0):
    monkeypatch.setattr(config, "USE_WORLD_MODEL", True)
    monkeypatch.setattr(config, "EXPENSIVE_ROWS", 0)  # test tablosunu taramak da "pahalı" sayılsın
    monkeypatch.setattr(config, "AUDIT_SHARE", audit_share)


def test_trusted_prediction_is_not_run_but_final_answer_is(db, fake_model, monkeypatch):
    expensive(monkeypatch)
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL), json_reply(SURE), submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert seen[2][-1]["content"].startswith("Prediction (the query was NOT run, this is a model's guess): "
                                             "1 column(s) (n), 1 row(s).")
    assert answer["label"] == "ok" and answer["world_model_calls"] == 1
    assert answer["executions"] == 1  # yalnızca final check çalıştırdı: son cevap her zaman gerçekten çalışır
    first_log = json.loads(config.EXPERIENCE_LOG.read_text().splitlines()[0])
    assert first_log["prediction"]["type"] == "rows" and first_log["result"] is None


def test_untrusted_prediction_is_run_and_compared(db, fake_model, monkeypatch):
    expensive(monkeypatch)
    replies, seen = fake_model
    unsure = dict(SURE, confidence={"type": 0.95, "shape": 0.5, "values": 0.1})
    replies += [execute_reply(COUNT_SQL), json_reply(unsure), submit_reply(COUNT_SQL)]
    loop.answer_question("How many items?", "", db)
    assert seen[2][-1]["content"].startswith("Columns: COUNT(*)\n1 rows:\n83")
    log = json.loads(config.EXPERIENCE_LOG.read_text().splitlines()[0])
    assert log["prediction_hit"] is True and log["result"]["type"] == "rows"


def test_audit_runs_a_trusted_prediction(db, fake_model, monkeypatch):
    expensive(monkeypatch, audit_share=1)
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL), json_reply(SURE), submit_reply(COUNT_SQL)]
    loop.answer_question("How many items?", "", db)
    assert seen[2][-1]["content"].startswith("Columns: COUNT(*)")


def test_world_model_drops_expensive_candidate_predicted_empty(db, fake_model, monkeypatch):
    expensive(monkeypatch)
    monkeypatch.setattr(config, "USE_CANDIDATES", True)
    replies, _ = fake_model
    empty = {"type": "empty", "confidence": {"type": 0.95, "shape": 0.95, "values": 0.9}}
    replies += [submit_reply(COUNT_SQL), sql_reply(COUNT_SQL), sql_reply("SELECT id FROM items WHERE price < 0"),
                json_reply(empty)] + [sql_reply(COUNT_SQL)] * 5
    answer = loop.answer_question("How many items?", "", db)
    assert answer["world_model_calls"] == 1
    assert answer["candidates"] == 7 and answer["label"] == "ok"  # 7/8 aynı sonuç: elenen hiçbir gruba girmez
    assert answer["executions"] == 1  # elenen candidate çalıştırılmadı, aynı SQL'ler cache'ten geldi
