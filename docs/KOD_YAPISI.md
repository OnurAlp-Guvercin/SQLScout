# Kod yapısı

Bu doküman kodun nasıl düzenlendiğini, nasıl yazılacağını ve hangi sırayla yazıldığını anlatır. Akışın kendisi ve terimlerin anlamı [AGENTIC_FLOW.md](AGENTIC_FLOW.md) dosyasında.

## Kurallar

- **Her adım tek bir dosyada.** Bir şeyi anlamak için dosyadan dosyaya gidilmez: akışın bir ya da birkaç ardışık adımı bir dosyadadır. Hangi adımın nerede olduğu aşağıdaki haritada.
- **Dosyalar kısa.** Kabaca 200 satırı geçen dosya bölünür.
- **Her dosyanın başında 1–2 satırlık açıklama** olur: dosyanın ne yaptığı ve akışta hangi adım olduğu.
- **Düz kod.** Normal `for` ve `if` kullanılır. Kısa fonksiyonlar, ne yaptığını söyleyen isimler. Okunması zorlaşıyorsa liste üreteci yerine düz döngü yazılır.
- **Aşırı mühendislik yok.** Sınıf hiyerarşisi, eklenti sistemi ya da "ileride lazım olur" diye yazılmış soyutlama olmaz. Sınıf ancak gerçekten durum tutmak gerekiyorsa kullanılır (`Context`).
- **Framework yok.** Harness düz bir Python döngüsüdür; hiçbir agent framework'ü kullanılmaz.
- **Sayılar tek yerde.** Eşikler, budget'lar ve candidate sayıları yalnızca `config.py` içinde durur.
- **Terimler:** Projeye özgü teknik terimler (policy, harness, gate, candidate, handoff...) kodda ve dokümanlarda İngilizce; açıklamalar Türkçe.
- **Flag yok.** Akışın her parçası görseldeki gibi hep açıktır. Bir parçanın katkısı ölçülmek istendiğinde (ablation) o parça için bir flag eklenir.

## Dosya haritası

| Dosya | Akıştaki yeri | Ne yapar |
|---|---|---|
| `agent/loop.py` | Adım 2, 10 | Akışın kendisi. `answer_question`: adım 1 → agent → (takılırsa) teacher → fallback → memory. `run_steps`: bir budget boyunca döngü; her tool bir dal, her dal tek bir dosyaya gider. `next_step`: modelden sıradaki tool call. Handoff: `start_teacher`, `teacher_submit`, `fallback_answer` (adım 7'nin seçtiği SQL → candidate consensus'u → en son çalışan SQL). `write_experience`: her soru bitince experience log |
| `agent/prompts.py` | | Modelin gördüğü her şey: prompt metinleri (agent, candidate, tablo seçimi, teacher'ın devralma notu) ve tool tanımları (`TOOLS`) |
| `agent/llm.py` | | Modele istek atar (`chat`), token sayar (`count_tokens`). Yerel `mlx_lm.server` ya da OpenRouter; ikisi de OpenAI biçimi, adres `config.py`'de. Denemek için: `python -m agent.llm "soru"` |
| `agent/context.py` | | `Context`: bir soru boyunca tutulan durum (konuşma, budget, cache, sayaçlar) |
| `harness/prepare.py` | Adım 1 | `build_context`: başlangıç bağlamı (şema, açıklamalar, foreign key'ler, column profile'ları, database memory, evidence, soru). Bağlam 16K'yı aşarsa `select_tables`: soruya gereken tabloları LLM seçer. Denemek için: `python -m harness.prepare <sqlite yolu> "soru" ["evidence"]` |
| `harness/tools.py` | Adım 3 | `search_values`: değer index'inde arama (FTS5 trigram + `difflib`). `ask_user`: soruyu terminaldeki kişiye sorar (`run.py`'de de `evaluate.py`'de de; aynı anda gelen sorular tek tek). Bulunanların kopyası search notes'a / clarification'lara yazılır |
| `harness/execute.py` | Adım 4–6 | `run_query`: agent'ın `execute_sql`'i. `check`: pre-check (salt okuma, `EXPLAIN`). `run`: gerçek çalıştırma ya da cache. `format_result`: sonucu metne çevirir (20 satır; boşsa `search_values` hatırlatması). `remember_mistake`: sorudaki ilk hata (memory için) |
| `harness/answer.py` | Adım 7–9 | `finish`: agent'ın `submit`'i. `candidates`: ek SQL'ler (`write_sql`), gruplama, seçim. `confidence`: confidence gate. `medium_note`. `final_check`. `consensus_answer`: fallback answer için candidate consensus'u |
| `harness/guards.py` | Her adım | `read_tool_call`: bozuk çıktının reddi. `is_repeat`: aynı çağrının tekrarı. `compress`: bağlamın sıkıştırılması |
| `harness/memory.py` | Adım 1, soru bittikten sonra | Database memory'yi okur (TF-IDF ile en benzer 3 kayıt) ve yazar: `experience/memory/<db_id>.jsonl` |
| `db/sqlite_db.py` | Adım 5, 6 | `execute`, `explain` (aşağıda) |
| `db/sqlite_schema.py` | Adım 1 | `schema`, `profile`, `descriptions` (aşağıda). Başka bir veritabanına geçince bu iki dosyanın aynı fonksiyonlarla bir eşi yazılır |
| `config.py` | | Tüm sabitler (aşağıdaki tablo) |
| `run.py` | | Tek bir soruyu çalıştırır: `python run.py --db <sqlite yolu> "soru" [--evidence "..."]` |
| `evaluate.py` | | Bir veri setini bir seed'le çalıştırır, BIRD kuralıyla puanlar (`score`), experience log satırına split, `question_id` ve cevabın doğru olup olmadığını ekletir, sonucu yazar: `python evaluate.py --name <deney> --seed 0 [--dataset bird\|mini_interact] [--limit n]` → `results/<deney>_seed<n>.jsonl` |
| `report.py` | | Bir deneyin özeti (`summary`, evaluate.py sonunda yazar); birden çok sonuç dosyası için tek satırlık tablo: `python report.py results/<deney>_*.jsonl` |
| `mini_interact.py` | | Mini-Interact görevlerini evaluate.py'nin soru biçimine çevirir: belirsiz soru, evidence olarak bilgi tabanı (görevin gizlediği maddeler hariç), varsa doğru SQL (`data/mini_interact/mini_interact_gold.jsonl`) |
| `requirements.txt` | | Bağımlılıklar; her yeni paket kullanıcıya sorularak eklenir |
| `tests/` | | Testler (API gerekmez). Test için küçük bir SQLite dosyası kod içinde oluşturulur |
| `data/` | | Veri setleri ve hazırlanmış dosyalar; kod değil. `data/bird/dev/`, `data/mini_interact/`, `data/prepared/<db_id>/` (column profile'ları ve değer index'i; her veritabanı için bir kez üretilir) |
| `results/` | | Deney sonuçları (aşağıda) |

## Tool'lar

Agent her turda tek bir tool call yapar. Tool call'lar Qwen'in kendi tool-call biçimiyle yazılır. Her çağrı budget'tan bir düşer; reddedilen ve biçimi bozuk çağrılar da.

| Tool | Argument'lar | Agent'a giden | Akıştaki yeri |
|---|---|---|---|
| `search_values` | `query` | Kelimeyi içeren ya da ona benzer yazılan en ilgili 5 değer: `tablo.sütun = 'değer'` | Adım 3 |
| `ask_user` | `question` | Kullanıcının cevabı (clarification). Soru başına en fazla 5 kez | Adım 3 |
| `execute_sql` | `sql` | Gerçek sonuç (en fazla 20 satır; boşsa `search_values` hatırlatması) ya da pre-check notu | Adım 4–6 |
| `submit` | `sql` | Cevap return edilir; ya da SQL çalışmıyorsa hata, medium note veya final check notu | Adım 7–9 |

- **`search_values`:** Metin sütunlarının farklı değerlerinden kurulmuş bir SQLite FTS5 index'inde arar. Index trigram'lıdır (kelimenin bir parçası da eşleşir); adaylar `difflib` ile yazım benzerliğine göre sıralanır, böylece "Los Angles" araması "Los Angeles"ı bulur. Index her veritabanı için bir kez kurulur ve `data/prepared/<db_id>/values.sqlite`'ta saklanır.

## `db/sqlite_db.py` ve `db/sqlite_schema.py` fonksiyonları

| Function | Return |
|---|---|
| `execute(db_path, sql)` | `{"ok", "error", "columns", "rows", "row_count", "result_key"}`. `rows` en fazla 100 satır; `row_count` gerçek satır sayısı. `result_key` bütün satırlardan hesaplanır (aşağıda). Hata olursa `ok=False` ve `error` dolu |
| `explain(db_path, sql)` | `{"ok", "error", "plan"}`: `plan`, `EXPLAIN QUERY PLAN` satırları. Sözdizimi hatası, eksik tablo/sütun ya da ikinci bir komut varsa `ok=False` ve `error` dolu |
| `schema(db_path)` | Tablo listesi: her biri `{"name", "columns", "foreign_keys"}`. Sütun: `{"name", "type", "primary_key"}`; foreign key: `{"column", "ref_table", "ref_column"}` |
| `profile(db_path, table)` | `{"table", "row_count", "columns"}`. Her sütun için: tip, NULL oranı, farklı değer sayısı, en sık 10 değer (en fazla 10 farklı değer varsa hepsi); sayısal değerlerin min ve max'ı |
| `descriptions(db_path)` | `{tablo: {sütun: açıklama}}`. BIRD'de `database_description/<tablo>.csv`, Mini-Interact'te `<db>_column_meaning_base.json` |

- **Salt okuma** iki katmanlıdır: veritabanı `mode=ro` ile açılır ve yalnızca `SELECT` / `WITH` ile başlayan sorgular kabul edilir.
- **Zaman aşımı:** 30 saniye.
- **Result key:** Bütün satırlar alınır, tekrarlar atılır, satırlar sıralanır ve bunun hash'i alınır. Satır sırası önemsizdir, sütun sırası önemlidir; bu BIRD'ün resmi karşılaştırma kuralıdır. Candidate gruplama da puanlama da yalnızca bu anahtarı kullanır.

## Agent loop

`agent/loop.py`'nin özü (sadeleştirilmiş). Her dal tek bir dosyaya gider:

```python
def run_steps(context):
    context.calls_left = context.budget()                           # agent 10, teacher 5
    while context.calls_left > 0:
        guards.compress(context)
        step = next_step(context)                                   # adım 2
        context.calls_left -= 1

        if step["error"]:                                           # tool call okunamadı: reddedilir
            result = step["error"]
        elif guards.is_repeat(step, context):                       # aynı çağrı: önceki sonuç agent'a gider
            result = guards.repeat_note(step, context)
        elif step["tool"] == "search_values":
            result = tools.search_values(query, context)            # adım 3
        elif step["tool"] == "ask_user":
            result = tools.ask_user(question, context)              # adım 3
        elif step["tool"] == "execute_sql":
            result = execute.run_query(sql, context)                # adım 4–6
        elif context.teacher:
            return teacher_submit(step, context)                    # doğrudan final check
        else:
            outcome = answer.finish(sql, context)                   # adım 7–9
            if outcome["done"]:
                return context.answer(..., "ok")
            if outcome["handoff"]:
                return None                                         # low, ikinci medium ya da 2 kez final check
            result = outcome["note"]                                # medium note ya da final check notu → adım 2

        context.add(step, result)
    return None                                                     # budget bitti → adım 10
```

## `config.py` sabitleri

| Sabit | Değer | Akıştaki yeri |
|---|---|---|
| Tool-call budget | Agent 10, teacher bunun yarısı (5). Reddedilen istekler sayılır, candidate çalıştırmaları sayılmaz | Adım 2, 10 |
| Kalan budget | Her sonucun altında yazar; son 2 hakta "submit et" hatırlatması da eklenir (`BUDGET_WARNING`) | Adım 2 |
| Tekrar sınırı | Aynı çağrı 3. kez tekrarlanırsa handoff (`MAX_REPEATS`) | Adım 2, 10 |
| `ask_user` sınırı | Soru başına 5 (agent ve teacher toplam); budget'tan düşer | Adım 3 |
| Search sonuç sayısı | 5 | Adım 3 |
| Değer index'i | 100 karakterden uzun metinler index'e girmez; bir aramada index'ten en fazla 200 aday benzerlikle sıralanır | Adım 3 |
| Benzer yazım eşiği | `difflib` benzerliği en az 0.8 | Adım 3 |
| Başlangıç bağlamı | En fazla 16K token; taşarsa policy modeli (temperature 0) soruya gereken tabloları seçer, diğerleri tek satıra iner | Adım 1 |
| Profildeki değerler | Metin sütunlarında en sık 10 değer (en fazla 10 farklı değer varsa hepsi), en fazla 40 karakter; sayısal sütunlarda yalnızca min ve max | Adım 1 |
| Database memory | Soruya en çok benzeyen 3 kayıt (TF-IDF benzerliği) | Adım 1 |
| Zaman aşımı / satır sınırı | 30 saniye / 100 satır | Adım 6 |
| Agent'a gösterilen sonuç | En fazla 20 satır, hücre başına en fazla 100 karakter | Adım 6 |
| Bağlam sınırı | 32K token; aşılırsa en eski observation'lar tek satıra indirilir | Her adım |
| İlk ek candidate | 2 | Adım 7 |
| Toplam candidate | Consensus yoksa 8'e tamamlanır (agent'ın SQL'i dahil) | Adım 7 |
| Candidate temperature | 0.8; her candidate aynı prompt'tan ayrı bir örnek | Adım 7 |
| Confidence gate | High: 3/3 ya da ≥6/8 · Medium: 4–5/8 · Low: ≤3/8. Oran hep 8 üzerinden; hata veren candidate hiçbir gruba sayılmaz | Adım 8 |
| Medium note | En kalabalık 2 grup; her biri için temsilci SQL, candidate sayısı, sütunlar, satır sayısı, ilk 3 satır. En fazla 1 kez | Adım 8 |
| Final check tekrarı | 2 kez geçmezse handoff | Adım 9 |
| Policy ve teacher üretimi | Temperature 0.7, top_p 0.8; thinking modu kapalı | Adım 2, 10 |
| Model isteği | Cevap en fazla 1024 token; istek başına 300 saniye zaman aşımı; geçici API hatasında 8 deneme, bekleme 5 sn'den başlayıp ikiye katlanır | |
| Değerlendirmede paralellik | Aynı anda 8 soru (`EVAL_WORKERS`; yerel sunucu istekleri batch'ler). API'de 4 | |
| Modeller | Şu an bütün model çağrıları yerel `mlx_lm.server`'daki `Qwen/Qwen3.5-0.8B`'ye gider (yalnızca akışın çalıştığını görmek için; seed gönderilmez, çünkü sunucu seed'li istekleri batch'e almaz). API'ye dönüş `config.py`'deki yorumda: policy `qwen/qwen3.5-9b` (DeepInfra, bf16), teacher `qwen/qwen3.6-27b`. Hedef yerel modeller: policy `Qwen3.5-4B` (`mlx-community/Qwen3.5-4B-bf16`), teacher `Qwen3.6-27B` (4-bit) | |
| Seed'ler | 0, 1, 2 | |
| Örneklem | `--limit n`: soruların seed 0 ile seçilmiş sabit bir örneklemi, veri setindeki sırayla (`SAMPLE_SEED`). Aynı n hep aynı soruları seçer | |

## Kayıt biçimleri

**`results/<deney>_seed<n>.jsonl`** (her deney ve seed için bir dosya):
- İlk satır deneyin kendisidir: deney adı, seed, veri seti (`bird` / `mini_interact`), `--limit`, soru sayısı, bütün `config.py` değerleri ve prompt metinleri.
- Sonraki her satır bir sorudur: `question_id`, `db_id`, `sql` (cevap), `label`, `answered_by` (agent / teacher), `correct` (doğru SQL'i yoksa boş), `tool_calls`, `executions` (gerçek çalıştırma sayısı), `candidates`, `clarifications`, `handoff_reason`, `steps` (her tool call ve observation; `by` alanı agent mı teacher mı), `prompt_tokens`, `completion_tokens`, `cost`, `seconds`. Gold SQL hata verirse `gold_error`, model cevap vermezse `error` da yazılır.

**`experience/log.jsonl`** (experience log; ileride agent'ın eğitim verisi, kayıtlar birikir; `agent/loop.py` her soru bitince yazar): her satır bir soru: zaman, split (`use` kullanımda, `dev` değerlendirmede; `correct` yalnızca `dev`'de dolu), veri seti, `question_id`, `db_id`, soru, evidence, gold SQL, cevap SQL'i, `label`, `correct`, `answered_by`, `handoff_reason`, model adları, seed ve `messages` (agent'ın, handoff olduysa teacher'ın da gördüğü konuşmanın tamamı: sistem prompt'u, adım 1'in bağlamı, her tool call ve observation). Eğitime yalnızca `split = train` satırları girer. `experience/executions.jsonl` eski biçimde (her SQL çalıştırması bir satır) yazılmış kayıtlardır.

**`experience/memory/<db_id>.jsonl`** (database memory): soru, ilk hatalı SQL, aldığı not, cevap SQL'i.

## Yazım sırası

Sistem küçük aşamalarla yazıldı. Her aşama tek bir parça ekledi, `pytest tests/` ile denendi ve kullanıcı onaylayınca sonrakine geçildi. Yeni bir parça da aynı şekilde eklenir: parça yazılır, test edilir, kullanıcıya 2–3 cümleyle ne yapıldığı ve nasıl denendiği anlatılır.

| Bölüm | Aşamalar | Ne eklendi |
|---|---|---|
| Phase 1-A: Temel (model yok) | 1–3 | Veritabanı katmanı; BIRD dev verisi ve puanlama; başlangıç bağlamı |
| Phase 1-B1: İlk çalışan agent | 4–8 | Model çalıştırma; tool'suz tek SQL (baseline); agent loop ve `submit`; `execute_sql`; pre-check |
| Phase 1-B2: Trial loop | 9–15 | Tekrar guardrail'i ve cache; uzun sonucun kırpılması; bağlamın sıkıştırılması; `search_values` |
| Phase 1-B3: Cevabı doğrulama | 17–21 | Final check; candidate'ler; adaptive rule (8'e tamamlama); confidence gate; medium note |
| Phase 1-B4: Yardım ve hafıza | 22–25 | Handoff (teacher); `ask_user`; database memory |
| Phase 1 sonuçları | 29 | Tam sistemle ölçüm |
| Phase 2: Mini-Interact | 30, 33 | Mini-Interact verisi; ölçüm |
| Yerel modeller | 35 | Policy ve teacher yerelde; belleğe sığma ve hız |
| Agent eğitimi (ileride) | | Experience log'la SFT → on-policy distillation → RL; yalnızca train kayıtlarıyla |

## Diyagram

Akış görseli `docs/diyagram/akis_diyagrami.py` ile üretilir; kullanımı dosyanın başında yazar. Akış değişirse görsel ve [AGENTIC_FLOW.md](AGENTIC_FLOW.md) birlikte güncellenir.
