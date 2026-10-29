"""Bir sorunun çözümü boyunca tutulan durum (Context): soru, konuşma, kararları yöneten durum ve ölçüm sayaçları.
Agent loop (agent/loop.py) ve harness dosyaları hep bunu okur ve günceller."""

from dataclasses import dataclass, field

import config


def new_stats():
    """Yalnızca sonuç dosyasına yazılan sayaçlar; hiçbir kararı etkilemezler."""
    return {"executions": 0,  # gerçek çalıştırma sayısı
            "prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0,
            "retries": 0}  # modele giden isteklerin yeniden deneme sayısı (yavaş ya da hata veren API)


@dataclass
class Context:
    # Soru
    question: str
    evidence: str
    db_path: str

    # Konuşma: modelin gördüğü mesajlar ve sonuç dosyasına yazılan adımlar
    messages: list = field(default_factory=list)
    small_model_messages: list = None  # handoff'tan sonra: small model'in konuşması (large model sıfırdan başlar; experience log)
    steps: list = field(default_factory=list)

    # Kararları yöneten durum
    large_model: bool = False  # handoff'tan sonra True: tool call'ları large model yapar
    calls: int = 0  # soru boyunca toplam tool call (small model + large model); sonuç dosyasına yazılır
    calls_left: int = 0  # bu budget'ta kalan tool call hakkı; large model devralınca yeniden dolar
    cache: dict = field(default_factory=dict)  # execute_sql.sql_key(sql) → gerçek sonuç (adım 5)
    stuck: bool = False  # son tool call reddedildi ya da tekrardı: sıradaki adım örneklenir (agent/loop.py next_step)
    final_check_fails: int = 0  # final check 2 kez geçmezse handoff
    wasted_in_a_row: int = 0  # arka arkaya boşa giden (okunamayan, tekrarlanan, reddedilen) çağrılar; 5 olursa handoff
    last_ok_sql: str = None  # en son hatasız ve dolu çalışan SQL; ilerleme sınırı (adım 2) buna bakar
    submitted_sql: str = None  # submit edilen ve hatasız çalışan son SQL; fallback answer bu (düşük güven)
    submitted_by: str = None  # submitted_sql'i kim submit etti: small model ya da large model
    handoff_reason: str = None  # small model'in döngüsü neden durdu (large model'e geçiş nedeni)
    large_model_stop_reason: str = None  # large model'in döngüsü neden durdu (cevap kabul edilmeden)

    # Large model (adım 7, 8): sonuç dosyasına yazılır
    large_model_checks: list = field(default_factory=list)  # small model'in her submit'ine large model'in kararı: {"sql", "approved", "reason"}
    large_model_error: str = None  # large model'in API'si birkaç denemeye rağmen cevap vermediyse hata; cevap yine de döner

    show_step: object = None  # verilirse her adım olduğu anda bu fonksiyonla yazdırılır (run.py)

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
                           "by": "large_model" if self.large_model else "small_model"})
        if self.show_step:
            self.show_step(len(self.steps), self.steps[-1])

    def count_usage(self, reply):
        """Bir model isteğinin token'larını ve maliyetini sayaçlara ekler."""
        for name in ("prompt_tokens", "completion_tokens", "cost", "retries"):
            self.stats[name] += reply.get(name) or 0

    def answer(self, sql, label, answered_by="small_model", error_message=None):
        """Sorunun sonucu: cevap, label ve sonuç dosyasına yazılacak her şey. error_message yalnızca cevap yoksa
        (no_answer) dolu: neden cevap olmadığı."""
        return {"sql": sql, "label": label, "answered_by": answered_by, "error_message": error_message,
                "tool_calls": self.calls, **self.stats, "cost": round(self.stats["cost"], 6),
                "handoff_reason": self.handoff_reason, "large_model_stop_reason": self.large_model_stop_reason,
                "large_model_checks": self.large_model_checks,
                "large_model_error": self.large_model_error, "steps": self.steps}
