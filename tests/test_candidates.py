"""harness/candidates.py ve harness/gates.py testleri (aşama 18–21): gruplama, seçim ve confidence gate."""

from harness import candidates, gates


def result(key):
    return {"ok": True, "result_key": key, "columns": ["n"], "rows": [(key,)], "row_count": 1}


def test_grouping_ties_and_errors():
    sqls = ["agent", "b1", "c1", "b2", "c2", "broken"]
    results = [result("a"), result("b"), result("c"), result("b"), result("c"), None]
    groups = candidates.group(sqls, results)
    assert [group["sqls"] for group in groups] == [["b1", "b2"], ["c1", "c2"], ["agent"]]  # hata veren grupsuz
    tie = candidates.group(["agent", "b1"], [result("a"), result("b")])
    assert tie[0]["sqls"] == ["agent"]  # başa başta agent'ın grubu


def test_confidence_levels():
    def groups_of(size):
        return [{"sqls": ["x"] * size}]
    assert gates.confidence(groups_of(3), 3) == "high"
    assert gates.confidence(groups_of(6), 8) == "high"
    assert gates.confidence(groups_of(5), 8) == "medium"
    assert gates.confidence(groups_of(4), 8) == "medium"
    assert gates.confidence(groups_of(3), 8) == "low"
    assert gates.confidence([], 8) == "low"  # hepsi hata verdi
