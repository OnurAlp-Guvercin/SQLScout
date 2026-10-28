"""Handoff testleri: large model soruyu sıfırdan çözer ve submit'i de final check'ten geçer."""

import config
from agent import loop
from tests.fakes import execute_reply, submit_reply, text_reply, observation

COUNT_SQL = "SELECT COUNT(*) FROM items"


def test_large_model_continues_after_forced_handoff(db, fake_model):
    replies, seen = fake_model
    replies += [submit_reply("SELECT town FROM items"), submit_reply("SELECT town FROM items"),  # agent: 2 kez geçmedi
                execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]  # large model
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == f"the final check failed {config.FINAL_CHECK_TRIES} times"
    assert len(seen[2]) == 2  # large model yalnızca sistem prompt'u ve adım 1'in bağlamıyla başladı
    assert answer["label"] == "ok" and answer["answered_by"] == "large_model" and answer["sql"] == COUNT_SQL
    assert answer["steps"][-1]["by"] == "large_model"


def test_large_model_submit_goes_through_the_final_check(db, fake_model):
    replies, seen = fake_model
    replies += [text_reply("I am not sure.")] * config.WASTED_CALLS
    replies += [submit_reply("SELECT town FROM items"),  # large model: önce çalışmayan bir SQL
                execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == f"{config.WASTED_CALLS} calls in a row were wasted"
    assert observation(seen[-2][-1]).startswith("Final check failed: Rejected before running: no such column: town")
    assert answer["label"] == "ok" and answer["answered_by"] == "large_model" and answer["sql"] == COUNT_SQL
