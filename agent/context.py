"""Bir sorunun çözümü boyunca tutulan durum (Context): soru, konuşma, kararları yöneten durum ve ölçüm sayaçları.
Agent loop (agent/loop.py) ve harness dosyaları hep bunu okur ve günceller."""

from dataclasses import dataclass, field

import config


def new_stats():
    """Yalnızca sonuç dosyasına yazılan sayaçlar; hiçbir kararı etkilemezler."""
    return {"executions": 0,  # gerçek çalıştırma sayısı
            "prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0}


@dataclass
class Context:
    # Soru
    question: str
    evidence: str
    db_path: str
    seed: int = None

    # Konuşma: modelin gördüğü mesajlar ve sonuç dosyasına yazılan adımlar
    messages: list = field(default_factory=list)
    steps: list = field(default_factory=list)

    # Kararları yöneten durum
    teacher: bool = False  # handoff'tan sonra True: tool call'ları teacher yapar
    calls: int = 0  # soru boyunca toplam tool call (agent + teacher); sonuç dosyasına yazılır
    calls_left: int = 0  # bu budget'ta kalan tool call hakkı; teacher devralınca yeniden (yarım) dolar
    cache: dict = field(default_factory=dict)  # execute_sql.sql_key(sql) → gerçek sonuç (adım 5)
    stuck: bool = False  # son tool call reddedildi ya da tekrardı: sıradaki adım örneklenir (agent/loop.py next_step)
    final_check_fails: int = 0  # final check 2 kez geçmezse handoff
    last_run_sql: str = None  # agent'ın en son yazdığı SQL; submit bunu cevap olarak gönderir
    last_ok_sql: str = None  # en son hatasız ve dolu çalışan SQL; fallback answer'da kullanılır
    handoff_reason: str = None

    # Ölçüm sayaçları (new_stats)
    stats: dict = field(default_factory=new_stats)

    def budget(self):
        """Tool-call budget'ı: agent'a MAX_TOOL_CALLS, devraldıktan sonra teacher'a bunun yarısı."""
        return config.MAX_TOOL_CALLS // 2 if self.teacher else config.MAX_TOOL_CALLS

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
        """Bir model isteğinin token'larını ve maliyetini sayaçlara ekler."""
        for name in ("prompt_tokens", "completion_tokens", "cost"):
            self.stats[name] += reply.get(name) or 0

    def answer(self, sql, label, answered_by="agent"):
        """Sorunun sonucu: cevap, label ve sonuç dosyasına yazılacak her şey."""
        return {"sql": sql, "label": label, "answered_by": answered_by, "tool_calls": self.calls, **self.stats,
                "cost": round(self.stats["cost"], 6),
                "handoff_reason": self.handoff_reason, "steps": self.steps}
