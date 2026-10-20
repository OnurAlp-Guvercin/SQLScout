# Kod yapısı

Bu doküman kodun nasıl düzenleneceğini, nasıl yazılacağını ve hangi sırayla yazılacağını anlatır. Akışın kendisi ve terimlerin anlamı [AGENTIC_FLOW.md](AGENTIC_FLOW.md) dosyasında.

## Kurallar

- **Her dosya akıştaki bir ya da iki adıma karşılık gelir.** Hangi adımın nerede olduğu aşağıdaki haritada.
- **Dosyalar kısa.** Kabaca 150 satırı geçen dosya bölünür.
- **Her dosyanın başında 1–2 satırlık açıklama** olur: dosyanın ne yaptığı ve akışta hangi adım olduğu.
- **Düz kod.** Normal `for` ve `if` kullanılır. Kısa fonksiyonlar, ne yaptığını söyleyen isimler. Lambda ya da liste üreteci serbest, ama zorunlu değil; okunması zorlaşıyorsa düz döngü yazılır.
- **Aşırı mühendislik yok.** Sınıf hiyerarşisi, eklenti sistemi ya da "ileride lazım olur" diye yazılmış soyutlama olmaz. Sınıf ancak gerçekten durum tutmak gerekiyorsa kullanılır.
- **Framework yok.** Harness düz bir Python döngüsüdür; hiçbir agent framework'ü kullanılmaz.
- **Sayılar tek yerde.** Eşikler, budget'lar ve candidate sayıları yalnızca `config.py` içinde durur; kodun içine sayı gömülmez. `config.py` ilk aşamada açılır ve gerektikçe büyür.
- **Terimler:** Projeye özgü teknik terimler (policy, world model, harness, gate, candidate, handoff...) kodda ve dokümanlarda İngilizce; açıklamalar Türkçe.
- **Parça parça.** Kod aşağıdaki "Yazım sırası"ndaki aşamalarla yazılır. Her aşama tek bir parça ekler ve çalışan bir sistem bırakır. Aşama bitince kullanıcıya ne yapıldığı ve nasıl denendiği anlatılır; kullanıcı onaylamadan sonraki aşamaya geçilmez.
- **Flag'ler parçayla gelir.** Bir ablation flag'i, parçası yazıldığı aşamada `config.py`'ye eklenir. Henüz yazılmamış bir parça, flag'i kapalıymış gibi davranır.

## Dosya haritası

Aşama 1–33'ün dosyaları yazıldı (Phase 1 ve Phase 2). `world_model/collect.py` ve `training/` isteğe bağlı eğitim bölümündedir, henüz yok.

| Dosya | Akıştaki yeri | Aşama | Ne yapar |
|---|---|---|---|
| `config.py` | | 1 | Tüm sabitler ve ablation flag'leri (aşağıdaki tablolar) |
| `requirements.txt` | | 4 | Bağımlılıklar; her yeni paket kullanıcıya sorularak eklenir |
| `db/sqlite_db.py` | Adım 5, 7 | 1 | `execute`, `explain`, `estimate_cost` (aşağıda) |
| `db/sqlite_schema.py` | Adım 1 | 1, 3 | `schema`, `profile` (aşağıda). Başka bir veritabanına geçince bu iki dosyanın aynı fonksiyonlarla bir eşi yazılır |
| `evaluate.py` | | 2, 29, 30 | Bir veri setini bir seed'le çalıştırır, BIRD kuralıyla puanlar (`score`), sonucu yazar: `python evaluate.py --name <deney> --seed 0 [--dataset bird\|mini_interact] [--subset] [--limit n] [--off USE_... ] [--simulate-cost]` → `results/<deney>_seed<n>.jsonl`. Her soru kendi veritabanının yolunu (`db_path`) taşır |
| `report.py` | | 29, 33 | Bir deneyin özeti (`summary`, evaluate.py sonunda yazar); birden çok sonuç dosyası için tek satırlık tablo (seed'ler, ablation'lar): `python report.py results/<deney>_*.jsonl` |
| `mini_interact.py` | | 30 | Mini-Interact görevlerini evaluate.py'nin soru biçimine çevirir: belirsiz soru, evidence olarak bilgi tabanı (görevin gizlediği maddeler hariç), belirsizlik notları (yalnızca simulator için), varsa doğru SQL (`data/mini_interact/mini_interact_gold.jsonl`) |
| `harness/prepare.py` | Adım 1 | 3, 14, 25 | `build_context`: başlangıç bağlamı. Soru, evidence, şema (açıklamalar, foreign key'ler), column profile'ları (aşama 3); sorudaki kelimelerin değer eşleşmeleri (aşama 14, `harness/value_matches.py`'den); database memory (aşama 25). Denemek için: `python -m harness.prepare <sqlite yolu> "soru" ["evidence"]` |
| `harness/value_matches.py` | Adım 1 | 14 | `find`: sorudaki kelime gruplarına yazılışça benzeyen değerler; aramayı `search.find_values` yapar |
| `harness/descriptions.py` | Adım 1, 3 | 3, 30 | `load`: sütun açıklamaları; BIRD'de `database_description/<tablo>.csv`, Mini-Interact'te `<db>_column_meaning_base.json` (JSON sütunlarının alanlarıyla) |
| `agent/llm.py` | | 4 | Modele istek atar ve cevabı döndürür; `count_tokens` ile token sayar. Geliştirmede OpenRouter API'sine (ucuz Qwen modelleri), sonda yerel `mlx_lm.server`'a gider (ikisi de OpenAI biçimi; adres `config.py`'de). Policy, candidate'ler, teacher, user simulator ve placeholder world model hep bunu kullanır |
| `agent/prompts.py` | | 5, 22, 24, 26 | Prompt metinleri: tool'suz SQL, agent, teacher'ın devralma notu, user simulator, placeholder world model |
| `agent/tools.py` | Adım 2 | 6 ve sonrası | Tool tanımları ve `offered`: agent'a ve teacher'a hangi tool'ların sunulduğu (flag'e göre) |
| `agent/policy.py` | Adım 2, 4, 8 | 5, 6 | `write_sql`: tool'suz tek bir SQL yazar (aşama 5; adım 8'de candidate'leri de bu yazar). `next_step`: sıradaki tool call'u okur (aşama 6) |
| `agent/loop.py` | Adım 2 | 6 ve sonrası | Agent loop: `answer_question`, `run_steps` (bir budget boyunca döngü; teacher da bunu kullanır), `run_query` (adım 4–7), `finish` (adım 8–10). Akışın kendisi burada; her tool bir dal |
| `agent/context.py` | | 6 ve sonrası | `Context`: bir soru boyunca tutulan durum (konuşma, budget, cache, sayaçlar) |
| `run.py` | | 6 | Tek bir soruyu çalıştırır: `python run.py --db <sqlite yolu> "soru" [--evidence "..."]` |
| `harness/precheck.py` | Adım 5, 7 | 8, 9, 27 | `check`: sorun yoksa `None`, varsa agent'a dönecek not; salt okuma ve `EXPLAIN` kontrolü (aşama 8). `run`: pre-check'ten geçen SQL'i cache'ten verir ya da gerçekten çalıştırıp experience log'a yazar (aşama 9); agent'ın SQL'leri, candidate'ler ve final check hep buradan geçer. World model'e gidilip gidilmeyeceği (aşama 27) |
| `harness/handoff.py` | Adım 11 | 6, 22 | `start_teacher`: teacher agent'ın konuşmasını devralma notuyla alır, yeni budget'la aynı döngüde devam eder (aşama 22). `fallback_answer` (aşama 6) |
| `harness/guards.py` | Her adım | 6, 9–11 | Bozuk çıktının reddi (`read_tool_call`, aşama 6; forecast'in biçimi de, aşama 15); aynı çağrının tekrarı (`is_repeat`, aşama 9), uzun sonucun kırpılması (`format_result`, `trim_rows`, aşama 10), bağlamın sıkıştırılması (`compress`, aşama 11) |
| `harness/search.py` | Adım 3 | 12, 13, 18 | `search_values` (aşama 12), `search_schema` (aşama 13); sonuçları search notes'a yazar (aşama 18) |
| `harness/compare.py` | Adım 7 | 15, 26 | Forecast ile gerçek sonucu karşılaştırır, surprise note yazar (aşama 15); world model'in prediction'ını da karşılaştırır (aşama 26) |
| `experience/log.py` | Adım 7 | 16 | Experience log'u `experience/log.jsonl` dosyasına yazar |
| `harness/final_check.py` | Adım 10 | 17 | Final check |
| `harness/candidates.py` | Adım 8 | 18, 19, 28 | Candidate üretir, çalıştırır, result key'e göre gruplar, cevabı seçer; pahalı candidate'leri world model'le eler (aşama 28) |
| `harness/gates.py` | Adım 6, 9 | 20, 21, 27 | Confidence gate (aşama 20), medium note (aşama 21); prediction gate ve audit (aşama 27) |
| `harness/ask_user.py` | Adım 3 | 23, 24, 31 | `run`: soruyu terminaldeki kişiye (aşama 23; `run.py`), BIRD'de gold SQL'i gören user simulator'e (aşama 24) ya da Mini-Interact'in kendi iki adımlı simulator'üne (aşama 31: encoder soruyu sınıflandırır, decoder cevaplar; prompt'lar BIRD-Interact'ten aynen) sorar ve clarification'ı saklar. Cevapta SQL varsa reddedilir. Gold SQL'i ve belirsizlik notlarını yalnızca simulator görür, agent'ın bağlamına hiç girmezler |
| `harness/cost.py` | Adım 2, 5 | 32 | Cost simulation (`SIMULATE_COST`): bird-coin başlangıcı (`start_coins`), harcama (`spend`), budget kaldı mı / az mı (`budget_left`, `budget_low`), simüle edilmiş sorgu maliyeti (`query_cost`) |
| `experience/memory.py` | Adım 1, offline | 25 | Database memory'yi okur ve yazar: `experience/memory/<db_id>.jsonl`. `evaluate.py` her deneyi ve seed'i boş bir memory ile başlatır |
| `world_model/predict.py` | Adım 6, 8 | 26, 33 | `predict`: SQL ve adım 1'in bağlamı → prediction (forecast biçiminde type, columns, rows; ek olarak values ve her biri için confidence). Bozuk çıktı "bilmiyorum", confidence'ı eksikse confidence 0 sayılır. İlk sürümde placeholder: LLM'e prompt'la sorar. Ölçüm (aşama 26, 33): `python -m world_model.predict [n]` experience log'un son n gerçek çalıştırmasıyla; `GATE_CHOICES`'taki her eşikte kaç prediction trusted olur, kaçı doğru. Eğitilmiş model gelirse (aşama 37) yalnızca bu dosyanın içi değişir |
| `world_model/collect.py` | | 36 | World model'in eğitim verisini toplar (SQL'leri çalıştırıp etiketler); isteğe bağlı eğitim bölümünde |
| `training/` | | 37–43 | World model eğitimi (aşama 37) ve policy eğitimi (38–43); isteğe bağlı, sistem uçtan uca çalıştıktan sonra |
| `tests/` | | her aşama | Testler. Test için birkaç satırlık küçük bir SQLite dosyası kod içinde oluşturulur |
| `data/` | | | Veri setleri ve hazırlanmış dosyalar; kod değil. `data/bird/dev/` (`dev.json`, `dev_databases/`), `data/prepared/<db_id>/` (adım 1 için hazırlanan column profile'ları ve search index'i; her veritabanı için bir kez üretilir) |
| `results/` | | | Deney sonuçları (aşağıda) |

Experience log (`experience/`) eğitim verisidir. `results/` ise makaledeki rakamların geldiği deney sonuçlarıdır.

## Tool'lar

Agent her turda tek bir tool call yapar. Tool call'lar Qwen'in kendi tool-call biçimiyle yazılır (chat template'in `tools` alanı). Her çağrı budget'tan bir düşer; reddedilen ve biçimi bozuk çağrılar da.

| Tool | Argümanlar | Agent'a dönen | Akıştaki yeri |
|---|---|---|---|
| `search_schema` | `query` | En ilgili 5 tablo/sütun ve açıklamaları | Adım 3 |
| `search_values` | `query` | Kelimeyi içeren ya da ona benzer yazılan en ilgili 5 değer: `tablo.sütun = 'değer'` | Adım 3 |
| `ask_user` | `question` | Kullanıcının cevabı (clarification). Soru başına en fazla 5 kez; gerekip gerekmediğine agent karar verir | Adım 3; `USE_ASK_USER` |
| `execute_sql` | `sql`, `forecast` | Gerçek sonuç (en fazla 20 satır) ve varsa surprise note; ya da kontrol hatası | Adım 4–7 |
| `submit` | `sql` | Cevap döner; ya da medium note veya final check notu | Adım 8–10 |
| `handoff` | `reason` | Bir şey dönmez; iş teacher'a geçer | Adım 11; `USE_HANDOFF` |

- **Forecast biçimi:** `{"type": "rows", "columns": ["category", "n"], "rows": "2-10", "trust": true}`
  - `type`: `error`, `empty` ya da `rows`.
  - `columns` ve `rows` yalnızca `type` `rows` ise yazılır. `rows`, satır aralıklarından biridir.
  - `trust`: `true` "güveniyorum" (trust), `false` "emin değilim" (unsure) demektir. Harness'ın kararlarını etkilemez; RL'deki forecast reward'unda kullanılır.
  - Forecast'in "tuttu" sayılması için `type` aynı olmalı; `rows` ise sütun sayısı ve satır aralığı da aynı olmalı. Sütun adları karşılaştırılmaz.
- **`search_schema`:** Tablo ve sütun adlarında ve BIRD'ün sütun açıklamalarında (`database_description` CSV'leri) kelime eşleşmesi arar.
- **`search_values`:** Metin sütunlarının farklı değerlerinden kurulmuş bir SQLite FTS5 index'inde arar. Index trigram'lıdır (kelimenin bir parçası da eşleşir); adaylar Python'un `difflib` modülüyle yazım benzerliğine göre sıralanır, böylece "Los Angles" araması "Los Angeles"ı bulur. Index her veritabanı için bir kez kurulur ve `data/prepared/<db_id>/` altında saklanır. FTS5 ve `difflib` Python'un kendi içinde var; ek paket gerekmez.

## `db/sqlite_db.py` ve `db/sqlite_schema.py` fonksiyonları

| Fonksiyon | Döndürdüğü |
|---|---|
| `execute(db_path, sql)` | `{"ok", "error", "columns", "rows", "row_count", "result_key"}`. `rows` en fazla 100 satır; `row_count` gerçek satır sayısı. `result_key` bütün satırlardan hesaplanır (aşağıda). Hata olursa `ok=False` ve `error` dolu |
| `explain(db_path, sql)` | `{"ok", "error", "plan"}`: `plan`, `EXPLAIN QUERY PLAN` satırları. Sözdizimi hatası, eksik tablo/sütun ya da ikinci bir komut varsa `ok=False` ve `error` dolu |
| `schema(db_path)` | Tablo listesi: her biri `{"name", "columns", "foreign_keys"}`. Sütun: `{"name", "type", "primary_key"}`; foreign key: `{"column", "ref_table", "ref_column"}`. Hedef sütunu yazılmamış foreign key, hedef tablonun primary key'ine bağlanır |
| `profile(db_path, table)` | `{"table", "row_count", "columns"}`. Her sütun için: tip, NULL oranı, farklı değer sayısı, en sık 5 değer ve sayıları (en fazla 30 farklı değer varsa hepsi); sayısal değerlerin min ve max'ı |
| `estimate_cost(db_path, sql)` | Tahmini taranacak satır sayısı; SQL hatalıysa `None`. SQLite'ın planında satır tahmini yok; bu yüzden baştan sona taranan her tablonun satır sayısı toplanır, indeksli aramalar küçük oldukları için sayılmaz. `EXPLAIN QUERY PLAN` tablo yerine takma adı (`T1`) yazdığı için taramalar `EXPLAIN` bytecode'undan okunur |

- **Salt okuma** iki katmanlıdır: veritabanı `mode=ro` ile açılır ve yalnızca `SELECT` / `WITH` ile başlayan sorgular kabul edilir.
- **Zaman aşımı:** 30 saniye.
- **Result key:** Bütün satırlar alınır, tekrarlar atılır, satırlar sıralanır ve bunun hash'i alınır. Satır sırası önemsizdir, sütun sırası önemlidir; bu BIRD'ün resmi karşılaştırma kuralıdır (`set(rows) == set(gold_rows)`). Candidate gruplama da puanlama da yalnızca bu anahtarı kullanır.

## Agent loop taslağı

`agent/loop.py` kabaca şöyle görünür (sadeleştirilmiş); AGENTIC_FLOW.md'deki adım 2 ile eşleşir. Teacher da aynı `run_steps`'i kullanır: `handoff` tool'u ona sunulmaz ve `submit`'i doğrudan final check'e gider. `step`, `harness/guards.py`'nin okuduğu tool call'dur (`tool`, `args`, `error`...).

```python
def answer_question(question, evidence, db_path, seed=None, ..., gold_sql=None):
    context = Context(...)                                          # gold_sql yalnızca user simulator için
    context.messages = [system prompt'u, prepare.build_context(question, evidence, db_path)]  # adım 1
    answer = run_steps(context)                                     # agent
    if answer is None and config.USE_HANDOFF:                       # adım 11
        handoff.start_teacher(context)
        answer = run_steps(context)                                 # teacher, yeni budget
    if answer is None:
        answer = handoff.fallback_answer(context)
    memory.write(context, answer)                                   # ok ve yolda hata varsa
    return answer


def run_steps(context):
    while context.calls < context.budget_end:
        step = policy.next_step(context, tools.offered(context.teacher))  # adım 2
        context.calls += 1

        if step["error"]:                                           # tool call okunamadı: reddedilir
            result = step["error"]
        elif guards.is_repeat(step, context):                       # aynı çağrı (submit hariç): önceki sonuç döner
            result = guards.repeat_note(step, context)
        elif step["tool"] in ("search_schema", "search_values"):
            result = search.run(step, context)                      # adım 3 (search notes'a da yazar)
        elif step["tool"] == "ask_user":
            result = ask_user.run(question, context)                # adım 3 (clarification'ı da saklar)
        elif step["tool"] == "execute_sql":
            result = run_query(sql, forecast, context)              # adım 4–7
        elif step["tool"] == "handoff":
            return None                                             # nedeni context.handoff_reason
        elif context.teacher:
            return teacher_submit(step, context)                    # doğrudan final check
        else:
            outcome = finish(sql, context)                          # adım 8–10
            if outcome["done"]:
                return context.answer(..., "ok")
            if outcome["handoff"]:
                return None                                         # low, ikinci medium ya da 2 kez final check
            result = outcome["note"]                                # medium note ya da final check notu → adım 2

        context.add(step, result)
    return None                                                     # budget bitti
```

`run_query` sırayla `precheck.check`, gerekirse `precheck.needs_world_model` → `world_model.predict` → `gates.trusted` / `gates.audit`, sonra `precheck.run` ve `compare`'i çağırır; `finish` ise `candidates`, `gates.confidence`, `final_check`'i.


## `config.py` sabitleri

| Sabit | Değer | Akıştaki yeri |
|---|---|---|
| Tool-call budget | 10 (teacher için de). Reddedilen istekler sayılır, candidate çalıştırmaları sayılmaz | Adım 2, 11 |
| `ask_user` sınırı | Soru başına 5 (agent ve teacher toplam); budget'tan düşer | Adım 3 |
| Search sonuç sayısı | 5 | Adım 3 |
| Değer index'i | 100 karakterden uzun metinler index'e girmez; bir aramada index'ten en fazla 200 aday benzerlikle sıralanır | Adım 3 |
| `search_schema` açıklaması | 200 karakterde kırpılır | Adım 3 |
| Başlangıç bağlamı | En fazla 16K token; taşarsa soruyla en az eşleşen tabloların ayrıntıları kısaltılır. Token'lar policy'nin tokenizer'ıyla sayılır | Adım 1 |
| Profilde bütün değerler | En fazla 30 farklı değeri olan sütunlarda | Adım 1 |
| Profilde değer uzunluğu | En fazla 40 karakter; uzun değerler kırpılır | Adım 1 |
| Önceden değer eşleşmesi | Sorudaki her kelime ya da en fazla 3 kelimelik grup için en iyi 2 değer; bir stopword ile başlayan ya da biten gruplar aranmaz. Yalnızca yazılışça benzeyen değerler (difflib ≥ 0.8); `search_values`'tan farkı, kelimeyi içeren değerleri saymaması. Gürültüye karşı: 4 harften kısa tek kelimeler ve tablo/sütun adları aranmaz, tek kelimelerde eşik 0.9 | Adım 1 |
| Benzer yazım eşiği | `difflib` benzerliği en az 0.8 | Adım 3 |
| Database memory | Soruya en çok benzeyen 3 kayıt (kelime örtüşmesiyle) | Adım 1 |
| Satır aralıkları (forecast) | `0`, `1`, `2-10`, `11-100`, `100+` | Adım 4, 7 |
| Pahalı sorgu | `estimate_cost` 1 milyondan fazla satır | Adım 5 |
| Budget az | Kalan tool-call budget başlangıcın %25'inin altında (Mini-Interact'te kalan bird-coin) | Adım 5 |
| Prediction gate eşiği | Result type ve result shape için confidence ≥ 0.9. Placeholder world model confidence'ı kendisi yazar (0–1) | Adım 6 |
| Audit payı | Trusted prediction'ların %5'i yine de çalıştırılır | Adım 6 |
| Zaman aşımı / satır sınırı | 30 saniye / 100 satır | Adım 7 |
| Agent'a gösterilen sonuç | En fazla 20 satır, hücre başına en fazla 100 karakter | Adım 7 |
| Bağlam sınırı | 32K token; aşılırsa en eski observation'lar tek satıra indirilir | Her adım |
| İlk ek candidate | 2 | Adım 8 |
| Toplam candidate | Consensus yoksa 8'e tamamlanır (agent'ın SQL'i dahil) | Adım 8 |
| Candidate temperature | 0.8; her candidate aynı prompt'tan ayrı bir örnek | Adım 8 |
| Confidence gate | High: 3/3 ya da ≥6/8 · Medium: 4–5/8 · Low: ≤3/8. Oran hep 8 üzerinden; elenen ya da hata veren candidate hiçbir gruba sayılmaz | Adım 9 |
| Medium note | En kalabalık 2 grup; her biri için temsilci SQL, candidate sayısı, sütunlar, satır sayısı, ilk 3 satır | Adım 9 |
| Medium tekrarı | En fazla 1 | Adım 9 |
| Final check tekrarı | 2 kez geçmezse handoff | Adım 10 |
| Cache | Aynı soru içinde; anahtar boşlukları sadeleştirilmiş SQL metni. Tekrar guardrail'i de aynı anahtarı kullanır (`execute_sql`'de forecast'e bakmaz) | Adım 5 |
| Policy ve teacher üretimi | Temperature 0.7, top_p 0.8; thinking modu kapalı | Adım 2, 11 |
| Model isteği | Cevap en fazla 1024 token; istek başına 300 saniye zaman aşımı; geçici API hatasında (429, 5xx, bağlantı) 8 deneme, bekleme 5 sn'den başlayıp her seferinde ikiye katlanır | |
| Değerlendirmede paralellik | Aynı anda 8 soru (`EVAL_WORKERS`; yerel sunucu istekleri batch'ler). API'de 4: 8'de sağlayıcı 429 hatası verdi | Değerlendirme |
| Modeller | Şu an bütün model çağrıları yerel `mlx_lm.server`'daki `Qwen/Qwen3.5-0.8B`'ye gider (yalnızca akışın çalıştığını görmek için; seed gönderilmez, çünkü sunucu seed'li istekleri batch'e almaz). Geliştirme ölçümleri için (aşama 4–34) OpenRouter'daki ucuz Qwen modelleri: policy yerine `qwen/qwen3.5-9b` (sağlayıcı DeepInfra, bf16), teacher ve user simulator `qwen/qwen3.6-27b`, placeholder world model `qwen/qwen3.5-9b` (prompt'la). Makale rakamları için (aşama 35) yerel modeller: policy `Qwen3.5-4B` (`mlx-community/Qwen3.5-4B-bf16`), world model placeholder olarak yerel bir Qwen (hangisi olduğu aşama 35'te ölçülerek seçilir; eğitim yapılırsa `Qwen3.5-0.8B` + LoRA), teacher ve user simulator `Qwen3.6-27B` (4-bit). MLX sürümleri; hazır MLX sürümü yoksa `mlx_lm.convert` ile dönüştürülür | |
| Bird-coin (cost simulation) | Yalnızca `SIMULATE_COST` açıkken. Maliyetler BIRD-Interact'teki gibi: `execute_sql` 1, `ask_user` 2, `submit` 3, bozuk çağrı 0.2; `search_schema` / `search_values` 0.5, `handoff` 0. Başlangıç: 6 + 2 × belirsizlik sayısı + kullanıcının sabrı (6). Tool-call budget'ı da geçerli kalır; hangisi önce biterse. Teacher yeni bir bird-coin budget'ı alır | Adım 2, 5 |
| Simüle edilmiş sorgu maliyeti | `SIMULATE_COST` açıkken `estimate_cost` × 1000: SQLite'ta da pahalı sorgu yolu (adım 6) denenir | Adım 5 |
| Eşik ölçümü | `GATE_CHOICES` = 0.5, 0.7, 0.8, 0.9, 0.95; world model ölçümü her eşikte trusted ve doğru sayısını verir | Adım 6 |
| Seed'ler | 0, 1, 2. Yerel sunucuda seed gönderilmez; seed'ler orada yalnızca audit kararını değiştirir, tekrarlar bağımsız örneklerdir | Değerlendirme |
| Aşama kontrol alt kümesi | BIRD dev'den seed 0 ile seçilmiş sabit 50 soru | Değerlendirme |

**Ablation flag'leri:**

| Flag | Varsayılan | Kapalıyken ne olur |
|---|---|---|
| `USE_AGENT_FORECAST` (adım 4) | Açık | `execute_sql` forecast istemez, surprise note yok. Final check'te boş sonuç hiç geçmez |
| `USE_CANDIDATES` (adım 8) | Açık | Adım 8 ve 9 atlanır; agent'ın SQL'i doğrudan final check'e gider |
| `USE_HANDOFF` (adım 11) | Açık | `handoff` tool'u sunulmaz; handoff gereken her noktada fallback answer döner |
| `USE_DB_MEMORY` (adım 1) | Açık | Database memory ne okunur ne yazılır |
| `USE_ASK_USER` (adım 3) | Açık | `ask_user` tool'u sunulmaz. Yalnızca literatürle karşılaştırma ölçümü için kapatılır |
| `USE_WORLD_MODEL` (adım 6, 8) | Açık (aşama 27'den itibaren) | Adım 5'in 4. sorusu sorulmaz, adım 6 hiç çalışmaz, adım 8'de world model ile eleme yapılmaz |
| `SIMULATE_COST` | Kapalı | Budget yalnızca tool call sayısıdır, sorgu maliyeti `estimate_cost`'un kendisidir. Phase 2'de (aşama 32) `evaluate.py --simulate-cost` ile açılır |

"Son cevap her zaman gerçekten çalıştırılır" kuralının flag'i yoktur; hiçbir zaman kapatılmaz.

Bunlar başlangıç değerleridir; Phase 2'de ölçülerek ayarlanır.

## Kayıt biçimleri

**`results/<deney>_seed<n>.jsonl`** (her deney ve seed için bir dosya, ör. `results/asama18_candidates_seed0.jsonl`):
- İlk satır deneyin kendisidir: deney adı, seed, veri seti (`bird` / `mini_interact`) ve split, alt küme mi, `--limit`, soru sayısı, bütün `config.py` değerleri (model adları ve flag'ler dahil) ve prompt metinleri.
- Sonraki her satır bir sorudur: `question_id`, `db_id`, `sql` (cevap), `label`, `answered_by` (agent / teacher), `correct` (doğru SQL'i yoksa boş), `tool_calls`, `executions` (gerçek çalıştırma sayısı), `handoff_reason` (handoff yoksa boş), `steps` (her tool call ve observation), `prompt_tokens`, `completion_tokens`, `cost` (dolar), `seconds`. Gold SQL hata verirse `gold_error`, model API'si cevap vermezse `error` da yazılır. Forecast sayısı ve tutanlar (`forecasts`, `forecast_hits`), üretilen candidate sayısı (`candidates`), world model'e gidiş sayısı (`world_model_calls`) `ask_user` soruları ile cevapları (`clarifications`) ve `SIMULATE_COST` açıkken kalan bird-coin (`coins_left`) da yazılır; `steps`'teki her adımın `by` alanı agent mı teacher mı olduğunu söyler.

**`experience/log.jsonl`** (her gerçek çalıştırma ve her world model prediction'ı bir satır): soru kimliği, split, veritabanı (`db_id` ve `db_path`), motor ve dialect, kim çalıştırdı (agent / candidate / teacher), SQL, agent forecast'i, world model prediction'ı, gerçek sonucun özeti (type, sütun sayısı, satır aralığı, result key; trusted prediction'da sorgu çalışmadığı için boş), forecast tuttu mu, prediction tuttu mu, süre, model adı, seed. Eğitime yalnızca `split = train` satırları girer.

**`experience/memory/<db_id>.jsonl`** (database memory): soru, ilk hatalı SQL, aldığı not (hata ya da surprise note), cevap SQL'i.

## Yazım sırası

Her aşama tek bir parça ekler. Her aşamanın sonunda:
1. `pytest tests/` geçer.
2. Model kullanan aşamalarda `run.py` ile 1–2 gerçek soru denenir. `evaluate.py` 50 soruluk alt kümede (seed 0) yalnızca her bölümün son aşamasında çalıştırılır (B1: 8, B2: 16, B3: 21, B4: 25, B5: 28; aşama 5–7 ayrıca tek tek ölçüldü) ve sonuç `results/` altına yazılır; böylece maliyet düşük kalır ve her bölümün katkısı görünür. Bölümün öteki aşamalarının ölçeceği şeylere (ör. forecast'lerin tutma oranı) bu son ölçümde bakılır. 50 soruda 1–3 soruluk fark şanstır. Bu rakamlar yalnızca ilerlemeyi görmek içindir, makaleye girmez.
3. Kullanıcıya 2–3 cümleyle ne yapıldığı ve nasıl denendiği anlatılır; kullanıcı onaylayınca sonraki aşamaya geçilir.

### Phase 1-A: Temel (model yok)

| # | Ne eklenir | Dosyalar | Nasıl denenir |
|---|---|---|---|
| 1 | Veritabanı katmanı | `config.py`, `db/sqlite_db.py` | Küçük test veritabanında: yazma sorgusu reddedilir, 100 satır sınırı çalışır, `row_count` doğru, aynı satırlar farklı sırada gelince `result_key` aynı kalır. Kurulacak Python'da FTS5 olduğu kontrol edilir |
| 2 | BIRD dev verisi ve puanlama | `evaluate.py` (veri okuma + puanlama) | BIRD dev kullanıcıyla birlikte indirilir. Her gold SQL kendisiyle karşılaştırılınca doğru çıkar; zaman aşımına giren gold SQL'ler listelenir |
| 3 | Başlangıç bağlamı | `harness/prepare.py` | Bir BIRD veritabanının bağlamı yazdırılır: şema, açıklamalar, foreign key'ler, column profile'ları, evidence. En büyük veritabanında bağlam 16K token'ı aşarsa kısaltmanın çalıştığı kontrol edilir |

### Phase 1-B1: İlk çalışan agent

Hedef: model çalışır ve agent tek bir soruyu uçtan uca cevaplar.

| # | Ne eklenir | Dosyalar | Nasıl denenir |
|---|---|---|---|
| 4 | Model çalıştırma | `requirements.txt` (kullanıcıya sorularak), `agent/llm.py` | Qwen3.5-4B yerelde yüklenir ve kısa bir cevap üretir; bellek ve hız ölçülür. Geliştirme boyunca aynı istekler OpenRouter API'sine gider |
| 5 | Tool'suz tek SQL (ilk baseline) | `agent/prompts.py`, `agent/policy.py` (`write_sql`) | Model bağlamdan tek bir SQL yazar, harness çalıştırır. 50 soruda ilk doğruluk rakamı |
| 6 | Agent loop iskeleti ve `submit` | `agent/policy.py` (`next_step`), `agent/loop.py`, `harness/guards.py` (bozuk çıktının reddi), `harness/handoff.py` (yalnızca fallback answer), `run.py` | Agent'ın tek tool'u `submit`. Tool call okunur, bozuk çıktı reddedilir, budget bitince fallback answer döner. `run.py` ile tek soru uçtan uca çalışır; 50 soruda aşama 5'ten kötü olmamalı |
| 7 | `execute_sql` tool'u | `agent/loop.py` (`run_query`) | Agent SQL'i deneyip sonucu görür, sonra `submit` eder. 50 soruda aşama 6 ile karşılaştırılır |
| 8 | Pre-check: salt okuma ve `EXPLAIN` | `harness/precheck.py` | Yazma sorgusu ve olmayan sütun çalıştırılmadan reddedilir; hata agent'a anlaşılır bir notla döner. B1'in 50 soruluk ölçümü |

### Phase 1-B2: Trial loop'u güçlendirme

Hedef: agent boşa dönmez, ihtiyaç duyduğu bilgiyi bulur ve forecast'iyle hatasını görür. Her guardrail ve her tool ayrı bir aşamadır.

| # | Ne eklenir | Dosyalar | Nasıl denenir |
|---|---|---|---|
| 9 | Guardrail: tekrar yok ve cache | `harness/guards.py`, `harness/precheck.py` (cache) | Aynı SQL iki kez (forecast'i farklı da olsa) gönderilir: ikincisi çalıştırılmaz, not döner, budget düşer (`submit` hariç) |
| 10 | Guardrail: uzun sonucun kırpılması | `harness/guards.py` | 100 satırlık sonuç agent'a 20 satır ve toplam satır sayısıyla gider |
| 11 | Guardrail: bağlamın sıkıştırılması | `harness/guards.py` | Bağlam 32K token'ı aşınca en eski observation'lar tek satıra iner |
| 12 | `search_values` tool'u | `harness/search.py` (değer arama) | "Los Angles" araması `city = 'Los Angeles'`ı bulur |
| 13 | `search_schema` tool'u | `harness/search.py` (şema arama) | "telefon" araması `schools.Phone` sütununu bulur. BIRD'de katkısı küçük olabilir |
| 14 | Adım 1'de değer eşleşmesi | `harness/prepare.py` | Soruda "Los Angles" geçince eşleşme adım 1 bağlamında görünür |
| 15 | Agent forecast ve surprise note | `harness/compare.py`; `USE_AGENT_FORECAST` | Forecast'siz istek reddedilir; tutmayan forecast surprise note üretir |
| 16 | Experience log | `experience/log.py` | Her gerçek çalıştırma "Kayıt biçimleri"ndeki alanlarla bir satır olarak yazılır. B2'nin 50 soruluk ölçümü: doğruluk, search çağrısı sayısı, forecast'lerin tutma oranı |

### Phase 1-B3: Cevabı doğrulama

Hedef: yanlış cevabı göndermeden yakalamak.

| # | Ne eklenir | Dosyalar | Nasıl denenir |
|---|---|---|---|
| 17 | Final check | `harness/final_check.py` | Henüz candidate yok: `submit` doğrudan final check'e gider. Forecast'i "boş" olmayan boş sonuç geçmez; 2 kez geçmezse fallback answer döner |
| 18 | Candidate'ler: 2 ek candidate, gruplama, seçim | `harness/candidates.py`, `harness/search.py` (search notes); `USE_CANDIDATES` | Candidate prompt'unda search notes var, agent'ın SQL'i yok. Result key ile gruplama, başa baş ve temsilci SQL kuralları testte denenir. Gate henüz yok: en kalabalık grubun cevabı final check'e gider |
| 19 | Adaptive rule: 8'e tamamlama | `harness/candidates.py` | 3'ü aynıysa durur, ayrışırsa 8'e tamamlar |
| 20 | Confidence gate: high ve low | `harness/gates.py` | High → final check; low → fallback answer (handoff henüz yok) |
| 21 | Medium note | `harness/gates.py` | Medium'da iki grubun özeti agent'a döner, agent bir kez daha çalışır; ikinci medium'da fallback answer döner. B3'ün 50 soruluk ölçümü: doğruluk ve gerçek çalıştırma sayısı |

### Phase 1-B4: Yardım ve hafıza

Hedef: agent takılınca teacher'a ya da kullanıcıya başvurur ve hatalarından öğrenir.

| # | Ne eklenir | Dosyalar | Nasıl denenir |
|---|---|---|---|
| 22 | Handoff | `harness/handoff.py` (teacher); `USE_HANDOFF` | Teacher API'den gelir (belleğe sığma ölçümü aşama 35'te). Zorunlu handoff noktaları ve agent'ın `handoff` tool'u çalışır; teacher'ın `submit`'i final check'e gider |
| 23 | `ask_user`: terminal | `harness/ask_user.py`; `USE_ASK_USER` | `run.py` ile belirsiz bir soruda agent sorar; cevap clarification olarak candidate prompt'una girer. Soru başına 5 sınırı denenir; cevabı şemada olan bir soruda agent'ın sormadığı kontrol edilir |
| 24 | User simulator | `harness/ask_user.py` (simulator) | `evaluate.py`'de simulator cevaplar. SQL'i ya da cevabı söylemediği ve gold SQL'in agent'ın bağlamına girmediği testte kontrol edilir |
| 25 | Database memory | `experience/memory.py`, `harness/prepare.py` (memory okuma); `USE_DB_MEMORY` | Testte hata → düzeltme → `ok` biten bir soru kayıt yazar. Aynı veritabanındaki sonraki benzer soru bu kaydı bağlamında görür. B4'ün 50 soruluk ölçümü: doğruluk, handoff oranı, `ask_user` sayısı |

### Phase 1-B5: World model (placeholder)

Hedef: akışın world model'li yolu (adım 6 ve adım 8'deki eleme) eğitim beklemeden çalışır. World model, prompt'la world model gibi davranan eğitilmemiş bir LLM'dir (placeholder).

| # | Ne eklenir | Dosyalar | Nasıl denenir |
|---|---|---|---|
| 26 | Placeholder world model ve ölçümü | `world_model/predict.py`, `agent/prompts.py` (world model prompt'u), `harness/compare.py` (prediction'ın karşılaştırılması) | Testte (sahte modelle) prediction ve confidence'lar okunur, bozuk çıktı "bilmiyorum" (confidence 0) sayılır. 50 sorunun experience log'undaki gerçek çalıştırmalar için world model tahmin eder: result type ve shape ne sıklıkla tuttu, confidence ≥ 0.9 dediklerinin yüzde kaçı doğru. Yalnızca ölçüm; henüz karar vermez |
| 27 | Prediction gate ve audit | `harness/precheck.py` (4. soru), `harness/gates.py` (prediction gate); `USE_WORLD_MODEL` | Testte üç yol denenir: trusted → prediction "prediction" etiketiyle agent'a döner; untrusted → gerçek çalıştırma; audit → trusted olsa da çalıştırılır. Son cevabın her zaman gerçekten çalıştırıldığı kontrol edilir |
| 28 | World model ile candidate eleme | `harness/candidates.py` | Pahalı bir candidate için "hata verir" ya da "boş döner" diye güvenle tahmin edilirse candidate çalıştırılmadan düşer; testte denenir. B5'in 50 soruluk ölçümü: doğruluk, gerçek çalıştırma sayısı, world model'e kaç kez gidildiği |

### Phase 1-B6: Phase 1 sonuçları

Hedef: tam sistemin ve her parçanın katkısının ilk büyük ölçümü. API modelleriyle alınır; ilerlemeyi ve ablation'ların yönünü gösterir. Makale rakamları aşama 35'te yerel modellerle alınır.

| # | Ne eklenir | Dosyalar | Nasıl denenir |
|---|---|---|---|
| 29 | Phase 1 sonuçları | `evaluate.py` | Tam BIRD dev, 3 seed. Ardından her flag tek tek kapatılarak ablation tablosu |

### Phase 2: Cost simulation

Hedef: çalıştırmanın ve kullanıcıya sormanın maliyetli olduğu bir ortamda world model'i ve `ask_user`'ı denemek.

| # | Ne eklenir | Dosyalar | Nasıl denenir |
|---|---|---|---|
| 30 | Mini-Interact verisi (300 SELECT görevi; `data/mini_interact/`, `hf download birdsql/mini-interact --repo-type dataset`) | `mini_interact.py`, `evaluate.py` (`--dataset mini_interact`), `harness/descriptions.py` (sütun anlamları) | Testte görev soruya dönüşür, görevin gizlediği bilgi tabanı maddesi evidence'a girmez, doğru SQL dosyası varsa okunur. Doğru SQL'ler açık dosyada yoktur (bird.bench25@gmail.com'dan istenir); yoksa sorular çalışır ama puanlanmaz |
| 31 | Mini-Interact'in kendi user simulator'ü | `harness/ask_user.py`, `agent/prompts.py` | Testte iki adım (encoder, decoder) çalışır; belirsizlik notları simulator'ün prompt'unda var, agent'ın mesajlarında yok |
| 32 | Cost simulation: bird-coin budget'ı, bird-coin'le "budget az" kuralı, simüle edilmiş sorgu maliyeti | `harness/cost.py`; `SIMULATE_COST` (`--simulate-cost`) | Testte bird-coin önce biterse döngü durur; "budget az" ve "pahalı" kararları simüle edilmiş değerlere bakar |
| 33 | Eşik ölçümü ve Phase 2 sonuçları | `world_model/predict.py` (eşik tablosu), `report.py` | Mini-Interact `--simulate-cost` ile 3 seed. Eşik train split'inin kayıtlarıyla seçilir; dev kayıtlarıyla yapılan ölçüm yalnızca bakmak içindir |

### Phase 3

| # | Ne eklenir |
|---|---|
| 34 | DuckDB adapter'ı (`db/duckdb_db.py`) ya da büyütülmüş BIRD veritabanları; gerçek gecikme ölçümü |

### Yerel modellere geçiş

| # | Ne eklenir | Nasıl denenir |
|---|---|---|
| 35 | Yerel modeller ve makale rakamları | `config.py`'de adres ve model adları yerel sunucuya çevrilir (komutlar CLAUDE.md'de). Policy (4B), teacher (27B, 4-bit) ve placeholder world model'in birlikte belleğe sığdığı ve hızı ölçülür. Tam BIRD dev ve Mini-Interact, 3 seed, ablation tablosu |

### Eğitim (isteğe bağlı)

Sistem uçtan uca çalıştıktan ve aşama 35'ten sonra, zaman kalırsa yapılır. Eğitimin hangi aşamalarının bu makineye sığdığı her aşamadan önce ölçülür; sığmayan bir aşama için kullanıcıya sorulur.

| # | Ne eklenir | Nasıl denenir |
|---|---|---|
| 36 | World model eğitim verisinin toplanması (`world_model/collect.py`) | BIRD train SQL'leri ve SynSQL-2.5M'den bir alt küme çalıştırılır, result type / shape / values etiketleri çıkar; experience log'un train satırları eklenir. Veri result type'a ve karmaşıklığa göre dengelenir. Dev SQL'i hiçbir zaman girmez |
| 37 | World model eğitimi ve calibration (`world_model/predict.py`, `training/`) | LoRA ile düz SFT; eğitilmiş model placeholder'ın yerini alır. Eğitimde görülmemiş train veritabanlarında, trusted denen prediction'ların en az %95'i doğru mu? Değilse eşik yükseltilir |
| 38 | Teacher izlerinin toplanması | Teacher harness içinde BIRD train'i çözer; yalnızca gold ile doğrulanan izler tutulur |
| 39 | SFT (LoRA) | Yolun tamamı üzerinde, observation'lar kayıptan maskelenerek. 50 soruda eğitilmemiş policy ile karşılaştırılır |
| 40 | On-policy distillation | Önce Qwen3.5 ile Qwen3.6 tokenizer'larının aynı olduğu doğrulanır; değilse OLIVE kullanılır |
| 41 | RL | DAPO; ana reward çalıştırma doğruluğu, yanında forecast reward (ARASTIRMA.md 9. bölüm) |
| 42 | Dyna tarzı imagination loop | RL'ye eklenir: tek adımlı hayal, reward her zaman gerçek çalıştırmadan |
| 43 | Promotion gate ve yeni sonuçlar | Yeni policy, eskisinden kötü değilse kullanıma alınır. Tam BIRD dev, 3 seed |

## Diyagram

Akış görseli `docs/diyagram/akis_diyagrami.py` ile üretilir; kullanımı dosyanın başında yazar. Akış değişirse görsel ve [AGENTIC_FLOW.md](AGENTIC_FLOW.md) birlikte güncellenir.
