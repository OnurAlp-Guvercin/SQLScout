# Kod yapısı

Bu doküman kodun nasıl düzenlendiğini, nasıl yazılacağını ve hangi sırayla yazıldığını anlatır. Akışın kendisi ve terimlerin anlamı [AGENTIC_FLOW.md](AGENTIC_FLOW.md) dosyasında.

## Kurallar

- **Her adım tek bir dosyada, her tool kendi dosyasında.** Bir şeyi anlamak için dosyadan dosyaya gidilmez: agent'ın her tool'u `harness/tools/` altında kendi adını taşıyan dosyadadır (giriş fonksiyonu `run`). Hangi adımın nerede olduğu aşağıdaki haritada.
- **Dosyalar kısa.** Kabaca 200 satırı geçen dosya bölünür.
- **Her dosyanın başında 1–2 satırlık açıklama** olur: dosyanın ne yaptığı ve akışta hangi adım olduğu.
- **Düz kod.** Normal `for` ve `if` kullanılır. Kısa fonksiyonlar, ne yaptığını söyleyen isimler. Okunması zorlaşıyorsa liste üreteci yerine düz döngü yazılır.
- **Aşırı mühendislik yok.** Sınıf hiyerarşisi, eklenti sistemi ya da "ileride lazım olur" diye yazılmış soyutlama olmaz. Sınıf ancak gerçekten durum tutmak gerekiyorsa kullanılır (`Context`).
- **Framework yok.** Harness düz bir Python döngüsüdür; hiçbir agent framework'ü kullanılmaz.
- **Sayılar tek yerde.** Eşikler, budget'lar ve sınırlar yalnızca `config.py` içinde durur.
- **Terimler:** Projeye özgü teknik terimler (policy, harness, final check, handoff...) kodda ve dokümanlarda İngilizce; açıklamalar Türkçe.
- **Flag yok.** Akışın her parçası görseldeki gibi hep açıktır. Bir parçanın katkısı ölçülmek istendiğinde (ablation) o parça için bir flag eklenir.

## Dosya haritası

| Dosya | Akıştaki yeri | Ne yapar |
|---|---|---|
| `agent/loop.py` | Adım 2, 8 | Akışın kendisi. `answer_question`: adım 1 → agent → (takılırsa) teacher → fallback → experience log. `run_steps`: bir budget boyunca döngü; her tool bir dal, her dal `harness/tools/<tool>.py`'nin `run`'ına gider; ilk 4 adımda ilerleme yoksa erken handoff. `next_step`: modelden sıradaki tool call (takılınca örnekleme). Handoff: `start_teacher`, `fallback_answer` (en son hatasız ve dolu çalışan SQL). `write_experience`: her soru bitince experience log |
| `agent/prompts.py` | | Modelin gördüğü her şey: prompt metinleri (agent, base'in tek SQL'i, tablo seçimi, teacher'ın devralma notu) ve tool tanımları (`TOOLS`) |
| `agent/llm.py` | | Modele istek atar (`chat`), token sayar (`count_tokens`). Policy yerel `mlx_lm.server`'a, teacher OpenRouter'a gider (`LLM_URL`, `TEACHER_URL`); ikisi de OpenAI biçimi, adresler `config.py`'de. Denemek için: `python -m agent.llm "soru"` |
| `agent/context.py` | | `Context`: bir soru boyunca tutulan durum (konuşma, budget, cache, sayaçlar) |
| `harness/prepare.py` | Adım 1 | `build_context`: başlangıç bağlamı (şema, açıklamalar, foreign key'ler, column profile'ları, evidence, soru). Bağlam 16K'yı aşarsa `select_tables`: soruya gereken tabloları LLM seçer. Denemek için: `python -m harness.prepare <sqlite yolu> "soru" ["evidence"]` |
| `harness/tools/search_values.py` | Adım 3 | Değer index'inde arama (FTS5 trigram + `difflib`). Değer bulunamazsa adı benzeyen sütunlar (`similar_columns`) |
| `harness/tools/execute_sql.py` | Adım 4–6 | `run`: agent'ın `execute_sql`'i. `check`: pre-check (salt okuma, `EXPLAIN`); `error_hint` hata notuna düzeltmek için gerekeni ekler (sorgudaki tabloların sütunları, alias, tablolar). `run_sql`: gerçek çalıştırma ya da cache. `format_result`: sonucu metne çevirir (20 satır; boşsa `search_values` hatırlatması). |
| `harness/tools/submit.py` | Adım 7 | `run`: agent'ın ve teacher'ın `submit`'i: en son çalıştırılan SQL cevaptır; 2 kez geçmezse handoff. `final_check`: çalıştırılmış bir SQL var mı, pre-check, hatasız çalışıyor mu |
| `harness/guards.py` | Her adım | `read_tool_call`: modelin cevabını bir adım olarak okur (tool call ya da ` ```sql ` bloğu); bozuk çıktının reddi. `earlier_calls`: aynı çağrının tekrarı (3. tekrarda handoff). `compress`: bağlamın sıkıştırılması |
| `db/sqlite_db.py` | Adım 5, 6 | `execute`, `explain` (aşağıda) |
| `db/sqlite_schema.py` | Adım 1 | `schema`, `profile`, `descriptions` (aşağıda). Başka bir veritabanına geçince bu iki dosyanın aynı fonksiyonlarla bir eşi yazılır |
| `config.py` | | Tüm sabitler (aşağıdaki tablo) |
| `run.py` | | Tek bir soruyu çalıştırır: `python run.py --db <sqlite yolu> "soru" [--evidence "..."]` |
| `evaluate.py` | | BIRD dev'i bir seed'le çalıştırır, BIRD kuralıyla puanlar (`score`), experience log satırına split, `question_id` ve cevabın doğru olup olmadığını ekletir, sonucu yazar: `python evaluate.py --name <deney> --seed 0 [--limit n]` → `results/<deney>_seed<n>.jsonl` |
| `baseline.py` | | Base: tool'suz tek SQL (temperature 0), agentic sistemle karşılaştırmak için: `python baseline.py --name <deney> [--model <model>] [--limit n]` → `results/<deney>_seed0.jsonl` |
| `report.py` | | Bir deneyin özeti (`summary`, evaluate.py sonunda yazar); birden çok sonuç dosyası için tek satırlık tablo: `python report.py results/<deney>_*.jsonl` |
| `requirements.txt` | | Bağımlılıklar; her yeni paket kullanıcıya sorularak eklenir |
| `tests/` | | Testler (API gerekmez). Test için küçük bir SQLite dosyası kod içinde oluşturulur |
| `data/` | | Veri setleri ve hazırlanmış dosyalar; kod değil. `data/bird/dev/`, `data/prepared/<db_id>/` (column profile'ları ve değer index'i; her veritabanı için bir kez üretilir) |
| `results/` | | Deney sonuçları (aşağıda) |

## Tool'lar

Agent her turda tek bir tool call yapar. Tool call'lar Qwen'in kendi tool-call biçimiyle yazılır; agent SQL'i mesajında bir ` ```sql ` bloğu olarak yazarsa o da `execute_sql` sayılır. Her çağrı budget'tan bir düşer; reddedilen ve biçimi bozuk çağrılar da.

| Tool | Argument'lar | Agent'a giden | Akıştaki yeri |
|---|---|---|---|
| `search_values` | `query` | Kelimeyi içeren ya da ona benzer yazılan en ilgili 5 değer: `tablo.sütun = 'değer'` | Adım 3 |
| `execute_sql` | `sql` | Gerçek sonuç (en fazla 20 satır; boşsa `search_values` hatırlatması) ya da pre-check notu | Adım 4–6 |
| `submit` | (yok) | En son çalıştırılan SQL cevap olarak return edilir ya da final check notu | Adım 7 |

- **`search_values`:** Metin sütunlarının farklı değerlerinden kurulmuş bir SQLite FTS5 index'inde arar. Index trigram'lıdır (kelimenin bir parçası da eşleşir); adaylar `difflib` ile yazım benzerliğine göre sıralanır, böylece "Los Angles" araması "Los Angeles"ı bulur. Index her veritabanı için bir kez kurulur ve `data/prepared/<db_id>/values.sqlite`'ta saklanır.

## `db/sqlite_db.py` ve `db/sqlite_schema.py` fonksiyonları

| Function | Return |
|---|---|
| `execute(db_path, sql)` | `{"ok", "error", "columns", "rows", "row_count", "result_key"}`. `rows` en fazla 100 satır; `row_count` gerçek satır sayısı. `result_key` bütün satırlardan hesaplanır (aşağıda). Hata olursa `ok=False` ve `error` dolu |
| `explain(db_path, sql)` | `{"ok", "error", "plan"}`: `plan`, `EXPLAIN QUERY PLAN` satırları. Sözdizimi hatası, eksik tablo/sütun ya da ikinci bir komut varsa `ok=False` ve `error` dolu |
| `schema(db_path)` | Tablo listesi: her biri `{"name", "columns", "foreign_keys"}`. Sütun: `{"name", "type", "primary_key"}`; foreign key: `{"column", "ref_table", "ref_column"}` |
| `profile(db_path, table)` | `{"table", "row_count", "columns"}`. Her sütun için: tip, NULL oranı, farklı değer sayısı, en sık 10 değer (en fazla 10 farklı değer varsa hepsi); sayısal değerlerin min ve max'ı |
| `descriptions(db_path)` | `{tablo: {sütun: açıklama}}`, BIRD'ün `database_description/<tablo>.csv` dosyalarından |

- **Salt okuma** iki katmanlıdır: veritabanı `mode=ro` ile açılır ve yalnızca `SELECT` / `WITH` ile başlayan sorgular kabul edilir.
- **Zaman aşımı:** 30 saniye.
- **Result key:** Bütün satırlar alınır, tekrarlar atılır, satırlar sıralanır ve bunun hash'i alınır. Satır sırası önemsizdir, sütun sırası önemlidir; bu BIRD'ün resmi karşılaştırma kuralıdır. Puanlama yalnızca bu anahtarı kullanır.

## Agent loop

`agent/loop.py`'nin özü (sadeleştirilmiş). Her dal tek bir dosyaya gider:

```python
def run_steps(context):
    context.calls_left = context.budget()                           # agent 10, teacher 5
    while context.calls_left > 0:
        guards.compress(context)
        step = next_step(context)                                   # adım 2
        context.calls_left -= 1
        earlier = guards.earlier_calls(step, context)

        if step["error"]:                                           # tool call okunamadı: reddedilir
            result = step["error"]
        elif len(own(earlier)) >= config.MAX_REPEATS:               # kendi 3. tekrarı: takıldı → adım 8
            return None
        elif earlier:                                               # aynı çağrı: önceki sonuç agent'a gider
            result = guards.repeat_note(earlier)
        elif step["tool"] == "search_values":
            result = search_values.run(query, context)              # adım 3
        elif step["tool"] == "execute_sql":
            result = execute_sql.run(sql, context)                  # adım 4–6
        else:
            outcome = submit.run(last_run_sql, context)             # adım 7: cevap en son çalıştırılan SQL
            if outcome["done"]:
                return context.answer(last_run_sql, "ok")
            if outcome["handoff"]:
                return None                                         # final check 2 kez geçmedi → adım 8
            result = outcome["note"]                                # final check notu → adım 2

        context.add(step, result)
        if agent and context.calls == 4 and no SQL returned rows:
            return None                                             # ilerleme yok → adım 8
    return None                                                     # budget bitti → adım 8
```

## `config.py` sabitleri

| Sabit | Değer | Akıştaki yeri |
|---|---|---|
| Tool-call budget | Agent 10, teacher bunun yarısı (5). Reddedilen istekler de sayılır | Adım 2, 8 |
| Kalan budget | Her sonucun altında yazar; son 2 hakta "submit et" hatırlatması da eklenir (`BUDGET_WARNING`) | Adım 2 |
| Tekrar sınırı | Aynı çağrı 3. kez tekrarlanırsa handoff (`MAX_REPEATS`); agent ve teacher yalnızca kendi tekrarlarıyla sayılır. `submit` tekrar sayılmaz | Adım 2, 8 |
| İlerleme sınırı | Agent ilk 4 tool call'ında dolu sonuç veren bir SQL çalıştıramadıysa handoff (`PROGRESS_CALLS`) | Adım 2, 8 |
| Search sonuç sayısı | 5 | Adım 3 |
| Değer index'i | 100 karakterden uzun metinler index'e girmez; bir aramada index'ten en fazla 200 aday benzerlikle sıralanır | Adım 3 |
| Benzer yazım eşiği | `difflib` benzerliği en az 0.8 | Adım 3 |
| Başlangıç bağlamı | En fazla 16K token; taşarsa policy modeli (temperature 0) soruya gereken tabloları seçer, diğerleri tek satıra iner | Adım 1 |
| Profildeki değerler | Metin sütunlarında en sık 10 değer (en fazla 10 farklı değer varsa hepsi), en fazla 40 karakter; sayısal sütunlarda yalnızca min ve max | Adım 1 |
| Zaman aşımı / satır sınırı | 30 saniye / 100 satır | Adım 6 |
| Agent'a gösterilen sonuç | En fazla 20 satır, hücre başına en fazla 100 karakter | Adım 6 |
| Bağlam sınırı | 32K token; aşılırsa en eski observation'lar tek satıra indirilir | Her adım |
| Final check tekrarı | 2 kez geçmezse handoff (`FINAL_CHECK_TRIES`) | Adım 7, 8 |
| Policy ve teacher üretimi | Temperature 0 (en olası cevap); son çağrı reddedildiyse ya da tekrarsa sıradaki adım temperature 0.7 ile örneklenir (`RETRY_TEMPERATURE`); top_p 0.8; thinking modu kapalı | Adım 2, 8 |
| Model isteği | Cevap en fazla 1024 token; istek başına 300 saniye zaman aşımı; geçici API hatasında 8 deneme, bekleme 5 sn'den başlayıp ikiye katlanır | |
| Değerlendirmede paralellik | Aynı anda 8 soru (`EVAL_WORKERS`; yerel sunucu istekleri batch'ler). API'de 4 | |
| Modeller | Policy yerel `mlx_lm.server`'daki `Qwen/Qwen3.5-0.8B` (seed gönderilmez, çünkü sunucu seed'li istekleri batch'e almaz). Teacher OpenRouter API'sindeki `qwen/qwen3.5-9b`; bf16 sunan sağlayıcılardan biri (`TEACHER_PROVIDERS`: DeepInfra, PrimeIntellect, Parasail), biri yoğunsa sıradakine geçilir; key `.env`'de. Teacher'ı da yerelde çalıştırmak ya da policy'yi API'ye almak `config.py`'deki yorumda. Hedef yerel modeller: policy `Qwen3.5-4B` (`mlx-community/Qwen3.5-4B-bf16`), teacher `Qwen3.6-27B` (4-bit) | |
| Seed'ler | 0, 1, 2 | |
| Örneklem | `--limit n`: soruların seed 0 ile seçilmiş sabit bir örneklemi, veri setindeki sırayla (`SAMPLE_SEED`). Aynı n hep aynı soruları seçer | |

## Kayıt biçimleri

**`results/<deney>_seed<n>.jsonl`** (her deney ve seed için bir dosya):
- İlk satır deneyin kendisidir: deney adı, seed, veri seti (`bird`), `--limit`, soru sayısı, bütün `config.py` değerleri ve prompt metinleri. `baseline.py`'nin dosyasında ise model, temperature ve prompt.
- Sonraki her satır bir sorudur: `question_id`, `db_id`, `sql` (cevap), `label`, `answered_by` (agent / teacher), `correct`, `tool_calls`, `executions` (gerçek çalıştırma sayısı), `handoff_reason`, `steps` (her tool call ve observation; `by` alanı agent mı teacher mı), `prompt_tokens`, `completion_tokens`, `cost`, `seconds`. Gold SQL hata verirse `gold_error`, model cevap vermezse `error` da yazılır.

**`experience/log.jsonl`** (experience log; ileride agent'ın eğitim verisi, kayıtlar birikir; `agent/loop.py` her soru bitince yazar): her satır bir soru: zaman, split (`use` kullanımda, `dev` değerlendirmede; `correct` yalnızca `dev`'de dolu), veri seti, `question_id`, `db_id`, soru, evidence, gold SQL, cevap SQL'i, `label`, `correct`, `answered_by`, `handoff_reason`, model adları, seed ve `messages` (agent'ın, handoff olduysa teacher'ın da gördüğü konuşmanın tamamı: sistem prompt'u, adım 1'in bağlamı, her tool call ve observation). Eğitime yalnızca `split = train` satırları girer.


## Yazım sırası

Sistem küçük aşamalarla yazıldı. Her aşama tek bir parça ekledi, `pytest tests/` ile denendi ve kullanıcı onaylayınca sonrakine geçildi. Yeni bir parça da aynı şekilde eklenir: parça yazılır, test edilir, kullanıcıya 2–3 cümleyle ne yapıldığı ve nasıl denendiği anlatılır.

| Bölüm | Aşamalar | Ne eklendi |
|---|---|---|
| Temel (model yok) | 1–3 | Veritabanı katmanı; BIRD dev verisi ve puanlama; başlangıç bağlamı |
| İlk çalışan agent | 4–8 | Model çalıştırma; tool'suz tek SQL (base, `baseline.py`); agent loop ve `submit`; `execute_sql`; pre-check |
| Trial loop | 9–15 | Tekrar guardrail'i ve cache; uzun sonucun kırpılması; bağlamın sıkıştırılması; `search_values` |
| Cevabı doğrulama | 17 | Final check |
| Yardım | 22 | Handoff (teacher, ilerlemeyen agent'ta erken) |
| Sonuçlar | 29 | Tam sistemle ölçüm |
| Yerel modeller | 35 | Policy ve teacher yerelde; belleğe sığma ve hız |
| Agent eğitimi (ileride) | | Experience log'la SFT → on-policy distillation → RL; yalnızca train kayıtlarıyla |

## Diyagram

Akış görseli `docs/diyagram/akis_diyagrami.py` ile üretilir; kullanımı dosyanın başında yazar. Akış değişirse görsel ve [AGENTIC_FLOW.md](AGENTIC_FLOW.md) birlikte güncellenir.
