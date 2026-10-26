"""Handoff testleri: teacher agent'ın kaldığı yerden devam eder ve submit'i de final check'ten geçer."""

import config
from agent import loop
from tests.fakes import execute_reply, submit_reply, text_reply, observation

COUNT_SQL = "SELECT COUNT(*) FROM items"


def test_teacher_continues_after_forced_handoff(db, fake_model):
    replies, seen = fake_model
    replies += [submit_reply("SELECT town FROM items"), submit_reply("SELECT town FROM items"),  # agent: 2 kez geçmedi
                execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]  # teacher
    answer = loop.answer_question("How many items?", "", db)
    takeover = observation(seen[2][-1])
    assert takeover.startswith("A smaller agent worked on this question and handed it over to you. "
                               "Reason: final check 2 kez geçmedi.")
    assert answer["label"] == "ok" and answer["answered_by"] == "teacher" and answer["sql"] == COUNT_SQL
    assert answer["steps"][-1]["by"] == "teacher"


def test_teacher_submit_goes_through_the_final_check(db, fake_model):
    replies, seen = fake_model
    replies += [text_reply("I am not sure.")] * config.PROGRESS_CALLS
    replies += [submit_reply("SELECT town FROM items"),  # teacher: önce çalışmayan bir SQL
                execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == "ilerleme yok"
    assert observation(seen[-2][-1]).startswith("Final check failed: Rejected before running: no such column: town")
    assert answer["label"] == "ok" and answer["answered_by"] == "teacher" and answer["sql"] == COUNT_SQL
