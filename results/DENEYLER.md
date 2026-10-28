# Deneyler

Kullanıcı "deneylere başla" derse bu altı deney çalıştırılır. Kullanıcıya yalnızca soru sayısı sorulur (`n`, ör. 20). Aynı `n` hep aynı soruları seçer, yani altı deney aynı sorularda karşılaştırılır.

**Önce:** Yerel model sunucusu açık olmalı (`mlx_lm.server`, komut CLAUDE.md'de). Memory'de BIRD train olmalı (`experience/memory.sqlite`; yoksa bir kez `python -m harness.memory data/bird/train/train.json`). Komutlar proje kökünden, sanal ortamda ve **sırayla** çalışır; aynı anda çalışırsa API 429 hatası verir. Çıktı bir boruya verilmez, `results/`'a yazılır. Aynı adlı eski sonuçların üzerine yazılır.

| Deney | Ne ölçer | Komut |
|---|---|---|
| `base_small_<n>` | 0.8B, tool'suz tek SQL | `python baseline.py --name base_small_<n> --model models/Qwen3.5-0.8B --limit <n> > results/base_small_<n>.log 2>&1` |
| `base_large_<n>` | 9B, tool'suz tek SQL | `python baseline.py --name base_large_<n> --model qwen/qwen3.5-9b --limit <n> > results/base_large_<n>.log 2>&1` |
| `agentic_<n>` | Sistemin tamamı: 0.8B agent, 9B kontrol ve handoff | `python evaluate.py --name agentic_<n> --limit <n> > results/agentic_<n>.log 2>&1` |
| `agentic_no_memory_<n>` | Sistemin tamamı, memory olmadan (benzer çözülmüş sorular eklenmez) | `python evaluate.py --name agentic_no_memory_<n> --limit <n> --no-memory > results/agentic_no_memory_<n>.log 2>&1` |
| `agentic_no_handoff_<n>` | 0.8B tek başına; 9B yalnızca kontrol eder | `python evaluate.py --name agentic_no_handoff_<n> --limit <n> --no-handoff > results/agentic_no_handoff_<n>.log 2>&1` |
| `large_agentic_<n>` | 9B agent; 9B yalnızca kontrol eder (kendine devretmez) | `python evaluate.py --name large_agentic_<n> --limit <n> --large-model-agent > results/large_agentic_<n>.log 2>&1` |

**Sonra:** `python report.py results/*_<n>.jsonl` ile tek tablo. Kullanıcıya bu tabloyu, deneyler arasındaki farkı ve agentic deneylerin tek SQL'e göre hangi soruları kazanıp kaybettiğini kısaca anlat.

**Süre ve maliyet (20 soru, tahmini):** altı deney toplam yaklaşık 1 saat ve $0.25; en pahalısı `large_agentic` (~$0.12), `base_small` ücretsiz.
