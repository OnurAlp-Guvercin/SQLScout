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

    # Konuşma: modelin gördüğü mesajlar ve sonuç dosyasına yazılan adımlar
    messages: list = field(default_factory=list)
    agent_messages: list = None  # handoff'tan sonra: agent'ın konuşması (teacher sıfırdan başlar; experience log)
    steps: list = field(default_factory=list)

    # Kararları yöneten durum
    teacher: bool = False  # handoff'tan sonra True: tool call'ları teacher yapar
    calls: int = 0  # soru boyunca toplam tool call (agent + teacher); sonuç dosyasına yazılır
    calls_left: int = 0  # bu budget'ta kalan tool call hakkı; teacher devralınca yeniden dolar
    cache: dict = field(default_factory=dict)  # execute_sql.sql_key(sql) → gerçek sonuç (adım 5)
    seen: set = field(default_factory=set)  # sonucunu agent'ın (handoff'tan sonra teacher'ın) gördüğü SQL'ler (execute_sql.sql_key); submit buna bakar
    stuck: bool = False  # son tool call reddedildi ya da tekrardı: sıradaki adım örneklenir (agent/loop.py next_step)
    final_check_fails: int = 0  # final check 2 kez geçmezse handoff
    wasted_calls: int = 0  # okunamayan, tekrarlanan ya da reddedilen çağrılar; agent'ın ilk 4 çağrısında 2 olursa handoff
    last_ok_sql: str = None  # en son hatasız ve dolu çalışan SQL; ilerleme sınırı (adım 2) buna bakar
    submitted_sql: str = None  # submit edilen ve final check'ten geçen son SQL; fallback answer bu (düşük güven)
    submitted_by: str = None  # submitted_sql'i kim submit etti: agent ya da teacher
    handoff_reason: str = None  # agent'ın döngüsü neden durdu (teacher'a geçiş nedeni)
    teacher_stop_reason: str = None  # teacher'ın döngüsü neden durdu (cevap kabul edilmeden)

    # Teacher (adım 7, 8): sonuç dosyasına yazılır
    teacher_check: dict = None  # agent'ın submit ettiği SQL ve teacher'ın kararı: {"sql", "approved"}
    teacher_error: str = None  # teacher'ın API'si birkaç denemeye rağmen cevap vermediyse hata; cevap yine de döner

    # Ölçüm sayaçları (new_stats)
    stats: dict = field(default_factory=new_stats)

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

    def answer(self, sql, label, answered_by="agent", error_message=None):
        """Sorunun sonucu: cevap, label ve sonuç dosyasına yazılacak her şey. error_message yalnızca cevap yoksa
        (no_answer) dolu: neden cevap olmadığı."""
        return {"sql": sql, "label": label, "answered_by": answered_by, "error_message": error_message,
                "tool_calls": self.calls, **self.stats, "cost": round(self.stats["cost"], 6),
                "handoff_reason": self.handoff_reason, "teacher_stop_reason": self.teacher_stop_reason,
                "teacher_check": self.teacher_check,
                "teacher_error": self.teacher_error, "steps": self.steps}
