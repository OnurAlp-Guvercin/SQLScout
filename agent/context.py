"""Bir sorunun çözümü boyunca tutulan durum (Context): konuşma, budget, cache ve sayaçlar.
Agent loop (agent/loop.py) ve harness dosyaları hep bunu okur ve günceller."""

from dataclasses import dataclass, field


@dataclass
class Context:
    question: str
    evidence: str
    db_path: str
    seed: int = None
    question_id: int = None  # experience log için; run.py'de yok
    split: str = None
    gold_sql: str = None  # yalnızca user simulator görür (evaluate.py); agent'ın mesajlarına hiç girmez
    ambiguity: dict = None  # Mini-Interact'in belirsizlik notları; gold gibi yalnızca user simulator görür
    messages: list = field(default_factory=list)
    steps: list = field(default_factory=list)
    cache: dict = field(default_factory=dict)  # precheck.sql_key(sql) → gerçek sonuç (adım 5'in 3. sorusu)
    last_forecast: dict = field(default_factory=dict)  # precheck.sql_key(sql) → agent'ın bu SQL için son forecast'i
    search_notes: list = field(default_factory=list)  # search sonuçlarının candidate prompt'u için kopyası
    clarifications: list = field(default_factory=list)  # ask_user soruları ve kullanıcının cevapları
    first_mistake: dict = None  # ilk hatalı SQL ve aldığı not; database memory'ye yazılır
    teacher: bool = False  # handoff'tan sonra True: tool call'ları teacher yapar
    calls: int = 0
    budget_end: int = 0  # calls bu sayıya ulaşınca budget biter; teacher yeni bir budget alır
    coins: float = 0  # SIMULATE_COST açıkken başlangıç bird-coin'i (harness/cost.py)
    coins_left: float = 0
    executions: int = 0  # gerçek çalıştırma sayısı (candidate'ler dahil)
    forecasts: int = 0  # forecast'le karşılaştırılan sonuç sayısı
    forecast_hits: int = 0
    candidates_written: int = 0
    medium_notes: int = 0
    final_check_fails: int = 0
    world_model_calls: int = 0
    selected_sql: str = None  # en son seçilen cevap (adım 8; USE_CANDIDATES kapalıysa submit edilen SQL)
    last_ok_sql: str = None  # en son hatasız çalışan SQL; fallback answer'da kullanılır
    handoff_reason: str = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0.0

    def add(self, step, result):
        """Tool call'u ve sonucunu (observation) konuşmaya ekler."""
        if step["id"]:
            call = {"id": step["id"], "type": "function",
                    "function": {"name": step["tool"], "arguments": step["arguments"]}}
            self.messages.append({"role": "assistant", "content": step["text"], "tool_calls": [call]})
            self.messages.append({"role": "tool", "tool_call_id": step["id"], "content": result})
        else:
            self.messages.append({"role": "assistant", "content": step["text"]})
            self.messages.append({"role": "user", "content": result})
        self.steps.append({"tool": step["tool"], "args": step["args"], "text": step["text"], "result": result,
                           "by": "teacher" if self.teacher else "agent"})

    def count_usage(self, reply):
        self.prompt_tokens += reply["prompt_tokens"] or 0
        self.completion_tokens += reply["completion_tokens"] or 0
        self.cost += reply["cost"] or 0

    def answer(self, sql, label, answered_by="agent"):
        return {"sql": sql, "label": label, "answered_by": answered_by, "tool_calls": self.calls,
                "executions": self.executions, "forecasts": self.forecasts, "forecast_hits": self.forecast_hits,
                "candidates": self.candidates_written, "world_model_calls": self.world_model_calls,
                "coins_left": round(self.coins_left, 1) if self.coins else None,
                "clarifications": self.clarifications, "handoff_reason": self.handoff_reason, "steps": self.steps,
                "prompt_tokens": self.prompt_tokens, "completion_tokens": self.completion_tokens,
                "cost": round(self.cost, 6)}
