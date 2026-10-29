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
- **Terimler:** Projeye özgü teknik terimler (small model, harness, final check, handoff...) kodda ve dokümanlarda İngilizce; açıklamalar Türkçe.
- **Flag yok.** Akışın her parçası görseldeki gibi hep açıktır. Bir parçanın katkısı ölçülmek istendiğinde (ablation) o parça için bir flag eklenir.

## Dosya haritası

| Dosya | Akıştaki yeri | Ne yapar |
|---|---|---|
| `agent/loop.py` | Adım 2, 8 | Akışın kendisi. `answer_question`: adım 1 → small model → (takılırsa ya da small model cevap vermezse) large model → fallback → experience log. `run_steps`: bir budget boyunca döngü. `take_step`: tek bir tool call; her tool bir dal, her dal `harness/tools/<tool>.py`'nin `run`'ına gider. `early_handoff`: ilk 6 adımda ilerleme yoksa ya da arka arkaya 5 çağrı boşa gittiyse erken handoff. `add_budget_note`: kalan tool call sayısı. `next_step`: modelden sıradaki tool call (takılınca örnekleme). Handoff: `start_large_model` (large model soruyu sıfırdan çözer: small model'in konuşmasını görmez, yalnızca small model'in sistem prompt'u ve adım 1'in bağlamıyla ve tam budget'la başlar; ne yapacağını small model gibi kendisi seçer), `fallback_answer` (submit edilen ve hatasız çalışan son SQL, düşük güven; yoksa `no_answer` ve `error_message`; large model'in API'si cevap vermezse de, `large_model_error`). `stop`: döngünün neden durduğu (small model için `handoff_reason`, large model için `large_model_stop_reason`). `write_experience`: her soru bitince experience log; `remember`: cevabı memory'ye yazar (kontrolsüz kabul edilen cevap `unchecked`) |
| `agent/prompts.py` | | Modelin gördüğü her şey: prompt metinleri (small model ve large model, base'in tek SQL'i, large model kontrolü) ve tool tanımları (`TOOLS`) |
| `agent/llm.py` | | Modele istek atar (`chat`), token sayar (`count_tokens`). Small model yerel `mlx_lm.server`'a, large model OpenRouter'a gider (`SMALL_MODEL_URL`, `LARGE_MODEL_URL`); ikisi de OpenAI biçimi, adresler `config.py`'de. Denemek için: `python -m agent.llm "soru"` |
| `agent/context.py` | | `Context`: bir soru boyunca tutulan durum (konuşma, budget, cache, sayaçlar) |
| `harness/prepare.py` | Adım 1 | `build_context`: başlangıç bağlamı (şema, açıklamalar, foreign key'ler, column profile'ları, varsa memory'den benzer sorular, evidence, soru). `is_near_unique`: neredeyse her satırı farklı metin sütunu; bunlarda az örnek gösterilir. Denemek için: `python -m harness.prepare <sqlite yolu> "soru" ["evidence"]` |
| `harness/memory.py` | Adım 1 | Memory: daha önce çözülmüş sorular embedding'leriyle `experience/memory.sqlite`'ta. `similar`: soruya en benzer, aday olan en fazla 3 satır (eşiğin üstündekiler). `is_candidate`: train'de `correct`, değerlendirmede ve kullanımda `label = ok`; değerlendirmede (`run` verilince) yalnızca train ve aynı koşu. `add`: satırları embed edip yazar. `embed`: `Qwen3-Embedding-0.6B`, MLX ile (son token'ın vektörü; yeni paket gerekmez). BIRD train'i eklemek için: `python -m harness.memory <train.json>` |
| `harness/tools/search_values.py` | Adım 3 | Değer index'inde arama (FTS5 trigram + `difflib`; 3 harften kısa metinde tam eşleşme; harfleri birebir tutan önce). Birden çok kelimeli metin bulunamazsa kelimeler tek tek aranır. Değer bulunamazsa adı benzeyen sütunlar (`similar_columns`; `execute_sql`'in hata notu da kullanır) |
| `harness/tools/execute_sql.py` | Adım 4–6 | `run`: small model'in `execute_sql`'i. `check`: pre-check (salt okuma, `EXPLAIN`); `error_hint` hata notuna düzeltmek için gerekeni ekler (sorgudaki tabloların sütunları, alias, tablolar). `run_sql`: gerçek çalıştırma ya da cache; keşif sorgusu 50, submit edilen ana sorgu (`answer=True`) 200 saniye çalışabilir, keşifteki zaman aşımı cache'e girmez. `format_result`: sonucu metne çevirir (20 satır; kırpıldıysa `TRIMMED_HINT`; boşsa ya da yalnızca 0/NULL ise `search_values` hatırlatması; large model kontrolü notsuz görür). `has_rows`: sonuç gerçekten dolu mu (tek satırı yalnızca 0/NULL olan sonuç dolu değildir; ilerleme sınırı buna bakar). `sql_key`: boşlukları ve sondaki `;`'yi önemsemeyen key (cache, tekrar) |
| `harness/tools/submit.py` | Adım 7 | `run`: small model'in ve large model'in `submit`'i; iki kapı sırayla: hatasız çalışıyor mu, large model doğru buluyor mu. `fail`: geçmeyen kapının notu döner ve bir hak düşer; 2. seferde handoff (son not handoff mesajında kalır). `runs_without_error`: pre-check, ana sorgu olarak (200 sn) hatasız çalışıyor mu; geçen SQL `context.submitted_sql` olur (fallback adayı). `large_model_review`: her cevabı large model kontrol eder (`CHECK_ANSWER`; ayrı context: adım 1'in memory örnekleri olmadan bağlamı, SQL ve small model'e yönelik notsuz sonuç, `format_result(hint=False)`); cevabı JSON: `{"reason", "correct"}`, `read_review` okur (okunamazsa onay sayılmaz); small model'in cevabı yanlışsa handoff (gerekçe small model'in konuşmasında kalır), large model'in kendi cevabı yanlışsa gerekçesiyle `REVIEWER_NOTE` döner ve final check hakkından düşer; small model'in cevabına verilen her karar `context.large_model_checks`'e yazılır. Large model'in API'si cevap vermezse cevap kabul edilir (`large_model_error`) |
| `harness/guards.py` | Her adım | `read_tool_call`: bozuk çıktının reddi. `extract_sql`: modelin düz metin cevabındaki SQL (base). `clean_sql`: SQL'in etrafındaki ```sql işaretleri (kapanıştan sonraki metinle birlikte) ve baştaki `--` ya da `/* */` yorumları atılır; base de bunu kullanır. `earlier_calls`: çağıranın (small model ya da large model) kendi çağrısını tekrarı (3. tekrarda handoff). `compress`: modele giden mesajların sıkıştırılmış kopyası (konuşmanın kendisi, experience log için, tam kalır); `is_encodable`: UTF-8'e çevrilemeyen argument'lı çağrı reddedilir |
| `db/sqlite_db.py` | Adım 5, 6 | `execute`, `explain` (aşağıda) |
| `db/sqlite_schema.py` | Adım 1 | `schema`, `profile`, `descriptions` (aşağıda). Başka bir veritabanına geçince bu iki dosyanın aynı fonksiyonlarla bir eşi yazılır |
| `config.py` | | Tüm sabitler (aşağıdaki tablo) |
| `run.py` | | Tek bir soruyu çalıştırır; her adımı olduğu anda yazar (terminalde renkli: small model mavi, large model turkuaz, ret kırmızı, kabul yeşil; `answer_question(show_step=...)`): `python run.py --db <sqlite yolu> "soru" [--evidence "..."]` |
| `evaluate.py` | | BIRD dev'i çalıştırır, BIRD kuralıyla puanlar (`run_gold`: gold SQL soru başına bir kez, 200 sn; `is_correct`), experience log satırına split, `question_id` ve cevabın doğru olup olmadığını ekletir, large model'in kontrol ettiği her SQL'i de puanlar (`large_model_checks`), sonucu yazar: `python evaluate.py --name <deney> [--limit n] [--no-handoff] [--no-memory] [--large-model-agent]` → `results/<deney>.jsonl` |
| `baseline.py` | | Base: tool'suz tek SQL (temperature 0), agentic sistemle karşılaştırmak için; API hatası olan soru `error` ile yanlış sayılır, koşu sürer: `python baseline.py --name <deney> [--model <model>] [--limit n]` → `results/<deney>.jsonl` |
| `report.py` | | Bir deneyin özeti (`summary`, evaluate.py sonunda yazar; large model kontrolünün isabeti de); birden çok sonuç dosyası için tek satırlık tablo: `python report.py results/<deney>*.jsonl` |
| `requirements.txt` | | Bağımlılıklar; her yeni paket kullanıcıya sorularak eklenir |
| `tests/` | | Testler (API gerekmez). Test için küçük bir SQLite dosyası kod içinde oluşturulur |
| `data/` | | Veri setleri ve hazırlanmış dosyalar; kod değil. `data/bird/dev/` (değerlendirme), `data/bird/train/train.json` (yalnızca soru–SQL çiftleri; memory'ye bir kez eklenir), `data/prepared/<db_id>/` (column profile'ları ve değer index'i; her veritabanı için bir kez üretilir) |
| `models/` | | Yerel model dosyaları; kod değil, git'e girmez. `models/Qwen3.5-0.8B/` (small model; `mlx_lm.server` buradan yükler), `models/Qwen3-Embedding-0.6B/` (embedding modeli; memory kullanır) |
| `results/` | | Deney sonuçları (aşağıda) |

## Tool'lar

Agent her turda tek bir tool call yapar. Tool call'lar Qwen'in kendi tool-call biçimiyle yazılır. Her çağrı budget'tan bir düşer; reddedilen ve biçimi bozuk çağrılar da.

| Tool | Argument'lar | Agent'a giden | Akıştaki yeri |
|---|---|---|---|
| `search_values` | `query` | Kelimeyi içeren ya da ona benzer yazılan en ilgili 5 değer (3 harften kısa kelimede tam eşleşme): `tablo.sütun = 'değer'` | Adım 3 |
| `execute_sql` | `sql` | Gerçek sonuç (en fazla 20 satır; kırpıldıysa "hepsini görmeden submit edebilirsin" notu; boşsa ya da yalnızca 0/NULL ise `search_values` hatırlatması) ya da pre-check notu | Adım 4–6 |
| `submit` | `sql` | Cevap return edilir ya da final check notu | Adım 7 |

- **`search_values`:** Metin sütunlarının farklı değerlerinden kurulmuş bir SQLite FTS5 index'inde arar. Index trigram'lıdır (kelimenin bir parçası da eşleşir); adaylar `difflib` ile yazım benzerliğine göre sıralanır, böylece "Los Angles" araması "Los Angeles"ı bulur. Trigram 3 harften kısa metni arayamaz; kısa metin (ör. "UK") büyük/küçük harf farkı gözetmeden tam eşleşmeyle aranır. Index her veritabanı için bir kez kurulur ve `data/prepared/<db_id>/values.sqlite`'ta saklanır.

## `db/sqlite_db.py` ve `db/sqlite_schema.py` fonksiyonları

| Function | Return |
|---|---|
| `execute(db_path, sql, timeout_seconds)` | `{"ok", "error", "timed_out", "columns", "rows", "row_count", "result_key"}`. `rows` en fazla 100 satır; `row_count` gerçek satır sayısı. `result_key` bütün satırlardan hesaplanır (aşağıda). Hata olursa `ok=False` ve `error` dolu |
| `explain(db_path, sql)` | `{"ok", "error", "plan"}`: `plan`, `EXPLAIN QUERY PLAN` satırları. Sözdizimi hatası, eksik tablo/sütun ya da ikinci bir komut varsa `ok=False` ve `error` dolu. Bulunamayan "çift tırnaklı" ad metin sayılmaz, hata verir |
| `schema(db_path)` | Tablo listesi: her biri `{"name", "columns", "foreign_keys"}`. Sütun: `{"name", "type", "primary_key"}`; foreign key: `{"column", "ref_table", "ref_column"}` |
| `profile(db_path, table)` | `{"table", "row_count", "columns"}`. Her sütun için: tip, NULL oranı, farklı değer sayısı, en sık 10 değer (en fazla 10 farklı değer varsa hepsi); sayısal değerlerin min ve max'ı |
| `descriptions(db_path)` | `{tablo: {sütun: açıklama}}`, BIRD'ün `database_description/<tablo>.csv` dosyalarından |

- **Salt okuma** iki katmanlıdır: veritabanı `mode=ro` ile açılır ve yalnızca `SELECT` / `WITH` ile başlayan sorgular kabul edilir.
- **Zaman aşımı:** keşif ve deneme sorguları (`execute_sql`) 50 saniye; ana sorgular (submit edilen SQL, puanlamada gold ve cevap) 200 saniye.
- **Result key:** Bütün satırlar alınır, tekrarlar atılır, satırlar sıralanır ve bunun hash'i alınır. Satır sırası önemsizdir, sütun sırası önemlidir; bu BIRD'ün resmi karşılaştırma kuralıdır. Puanlama yalnızca bu anahtarı kullanır.

## Agent loop

`agent/loop.py`'nin özü (sadeleştirilmiş). Her dal tek bir dosyaya gider:

```python
def run_steps(context):                                              # bir budget boyunca döngü
    context.calls_left = config.MAX_TOOL_CALLS                      # small model de large model de 10
    while context.calls_left > 0:
        step = next_step(context)                                   # adım 2
        context.calls_left -= 1
        outcome = take_step(step, context)                          # adım 3–7
        if outcome == "accepted":
            return context.answer(sql, "ok")
        if outcome == "stopped" or early_handoff(context):         # takıldı → adım 8
            return None
        add_budget_note(context)
    return None                                                     # budget bitti → adım 8


def take_step(step, context):                                       # tek bir tool call
    earlier = guards.earlier_calls(step, context)
    if step["error"]:                                               # tool call okunamadı: reddedilir
        result = step["error"]
    elif len(earlier) >= config.MAX_REPEATS:                        # kendi 3. tekrarı: takıldı
        return "stopped"
    elif earlier:                                                   # aynı çağrı: önceki sonuç döner
        result = guards.repeat_note(earlier)
    elif step["tool"] == "search_values":
        result = search_values.run(query, context)                  # adım 3
    elif step["tool"] == "execute_sql":
        result = execute_sql.run(sql, context)                      # adım 4–6
    else:
        outcome = submit.run(sql, context)                          # adım 7
        if outcome["done"]:
            return "accepted"
        if outcome["handoff"]:
            return "stopped"                                        # ör. final check 2 kez geçmedi
        result = outcome["note"]                                    # kontrolün notu → adım 2
    context.add(step, result)
    return None
```

## `config.py` sabitleri

| Sabit | Değer | Akıştaki yeri |
|---|---|---|
| Tool-call budget | Small model 10, handoff'tan sonra large model de 10. Reddedilen istekler de sayılır | Adım 2, 8 |
| Kalan budget | Her sonucun altında yazar; son 2 hakta "submit et" hatırlatması da eklenir (`BUDGET_WARNING`) | Adım 2 |
| Tekrar sınırı | Aynı çağrı 3. kez tekrarlanırsa handoff (`MAX_REPEATS`); small model ve large model yalnızca kendi çağrılarıyla karşılaştırılır. `submit` tekrar sayılmaz | Adım 2, 8 |
| İlerleme sınırı | Small model ilk 6 tool call'ında dolu sonuç veren bir SQL çalıştıramadıysa (`PROGRESS_CALLS`; tek satırı yalnızca 0/NULL olan sonuç dolu sayılmaz) ya da arka arkaya 5 çağrısı boşa gittiyse (`WASTED_CALLS`: okunamadı, tekrarlandı ya da pre-check'te reddedildi; boşa gitmeyen bir çağrı sayacı sıfırlar) handoff | Adım 2, 8 |
| Memory | En fazla 3 benzer çözülmüş soru (`MEMORY_EXAMPLES`), benzerlik en az 0.7 (`MEMORY_MIN_SIMILARITY`: BIRD dev soruları arasında 0.7'nin altı çoğunlukla alakasız, üstü aynı tabloları paylaşıyor); `MEMORY = True`, `evaluate.py --no-memory` ile `False` (ne okunur ne yazılır) | Adım 1 |
| Search sonuç sayısı | 5 | Adım 3 |
| Değer index'i | 100 karakterden uzun metinler index'e girmez; bir aramada index'ten en fazla 200 aday benzerlikle sıralanır | Adım 3 |
| Benzer yazım eşiği | `difflib` benzerliği en az 0.8 | Adım 3 |
| Başlangıç bağlamı | Bütün şema ve column profile'ları; BIRD dev'de en fazla ~12K token | Adım 1 |
| Profildeki değerler | Metin sütunlarında en sık 10 değer (en fazla 10 farklı değer varsa hepsi), en fazla 40 karakter; farklı değer sayısı dolu satırların en az %90'ı olan sütunlarda yalnızca 3 (`PROFILE_UNIQUE_RATIO`, `PROFILE_UNIQUE_VALUES`); değerlerinin çoğu 40 karakterden uzun serbest metinde hiç (`is_long_text`); sütun açıklamasını tekrar eden "value description" yazılmaz; sayısal sütunlarda yalnızca min ve max | Adım 1 |
| Zaman aşımı / satır sınırı | Keşif 50 saniye (`EXPLORE_TIMEOUT_SECONDS`), ana sorgu 200 saniye (`ANSWER_TIMEOUT_SECONDS`) / 100 satır; 1 milyondan çok farklı satır dönen sorgu hata sayılır (`MAX_TOTAL_ROWS`; tekrarlar sayılmaz) | Adım 6, 7 |
| Agent'a gösterilen sonuç | En fazla 20 satır, hücre başına en fazla 100 karakter | Adım 6 |
| Bağlam sınırı | 32K token; aşılırsa en eski observation'lar tek satıra indirilir | Her adım |
| Final check tekrarı | 2 kez geçmezse handoff (`FINAL_CHECK_TRIES`) | Adım 7, 8 |
| Handoff (ablation) | `HANDOFF = True`; `evaluate.py --no-handoff` ile `False`: large model yalnızca kontrol eder, small model'in reddedilen cevabının gerekçesi small model'e döner, erken handoff yok | Adım 7, 8 |
| Small model ve large model üretimi | Temperature 0 (en olası cevap); son çağrı reddedildiyse ya da tekrarsa sıradaki adım temperature 0.7 ile örneklenir (`RETRY_TEMPERATURE`); top_p 0.8; thinking modu kapalı | Adım 2, 8 |
| Model isteği | Cevap en fazla 1024 token; bir isteğin toplam süresi en fazla 300 saniye (`LLM_TIMEOUT_SECONDS`; cevap parça parça okunur, süre dolunca kesilip yeniden denenir); API'ye aynı anda en fazla 4 istek (`API_PARALLEL`); geçici API hatasında (408, 429, 5xx) 8 deneme, bekleme 5 sn'den başlayıp ikiye katlanır; 401/402'de (key ya da kredi) koşu durur | |
| Değerlendirmede paralellik | Aynı anda 8 soru (`EVAL_WORKERS`; yerel sunucu istekleri batch'ler). API'de 4 | |
| Modeller | Small model yerel `mlx_lm.server`'daki `Qwen/Qwen3.5-0.8B` (`SMALL_MODEL = "models/Qwen3.5-0.8B"`, sunucuya verilen klasör). Large model OpenRouter API'sindeki `qwen/qwen3.5-9b`; bf16 sunan sağlayıcılardan biri (`LARGE_MODEL_PROVIDERS`: DeepInfra, PrimeIntellect, Parasail), biri yoğunsa sıradakine geçilir; key `.env`'de. Large model'i de yerelde çalıştırmak ya da small model'i API'ye almak `config.py`'deki yorumda. Hedef yerel modeller: small model `Qwen3.5-4B` (`mlx-community/Qwen3.5-4B-bf16`), large model `Qwen3.6-27B` (4-bit) | |
| Örneklem | `--limit n`: soruların seed 0 ile seçilmiş sabit bir örneklemi, veri setindeki sırayla (`SAMPLE_SEED`). Aynı n hep aynı soruları seçer | |

## Kayıt biçimleri

**`results/<deney>.jsonl`** (her deney için bir dosya; tekrar koşular ayrı adlarla):
- İlk satır deneyin kendisidir: deney adı, veri seti (`bird`), `--limit`, soru sayısı, kodun git commit'i (`code`: commit ve commit edilmemiş değişikliklerin hash'i, yoksa boş), bütün `config.py` değerleri ve prompt metinleri. `baseline.py`'nin dosyasında ise model, temperature ve prompt.
- Sonraki her satır bir sorudur: `question_id`, `db_id`, `sql` (cevap), `label`, `answered_by` (`small_model` / `large_model`), `error_message` (cevap yoksa nedeni; `no_answer`'da `answered_by` boştur), `correct`, `tool_calls`, `executions` (gerçek çalıştırma sayısı), `handoff_reason` (small model'in döngüsü neden durdu; handoff kapalıyken yalnızca durma nedeni), `large_model_stop_reason` (large model'in döngüsü neden durdu), `large_model_checks` (small model'in submit ettiği her SQL için large model'in kararı `approved`, gerekçesi `reason` ve SQL'in gerçekten doğru olup olmadığı `correct`), `large_model_error` (large model'in API'sine ulaşılamadıysa), `steps` (her tool call ve observation; `by` alanı `small_model` mı `large_model` mı), `memory_examples` (bağlama eklenen benzer soruların metni), `prompt_tokens`, `completion_tokens`, `cost`, `retries` (modele giden isteklerin yeniden deneme sayısı), `seconds`. Gold SQL hata verirse `gold_error`, model cevap vermezse `error` da yazılır.

**`experience/log.jsonl`** (experience log; ileride small model'in eğitim verisi, kayıtlar birikir; `agent/loop.py` her soru bitince yazar): her satır bir soru: zaman, split (`use` kullanımda, `dev` değerlendirmede; `correct` yalnızca `dev`'de dolu), `run` (değerlendirmede koşunun adı ve başlama zamanı), veri seti, `question_id`, `db_id`, soru, evidence, gold SQL, cevap SQL'i, `label`, `correct`, `answered_by`, `handoff_reason`, `large_model_stop_reason`, `large_model_error`, model adları, `handoff` (`config.HANDOFF`), `messages` (small model'in gördüğü konuşmanın tamamı: sistem prompt'u, adım 1'in bağlamı, her tool call ve observation) ve `large_model_messages` (handoff olduysa large model'in sıfırdan başlayan konuşması, yoksa boş). Eğitime yalnızca `split = train` satırları girer.


## Yazım sırası

Sistem küçük aşamalarla yazılır: her aşama tek bir parça ekler, `pytest tests/` ve tek bir gerçek soruyla (`run.py`) denenir, kullanıcı onaylayınca sonrakine geçilir. Kullanıcıya 2–3 cümleyle ne yapıldığı ve nasıl denendiği anlatılır.

Akışın 8 adımı tamam. Sıradaki aşamalar:
1. **Agent eğitimi:** experience log'la; yöntem açık (SFT, distillation ya da RL, biri ya da birleşimi); yalnızca train kayıtlarıyla.
2. **Yerel modeller:** makale rakamları için small model (Qwen3.5-4B) ve large model yerelde.

## Diyagram

Akış görseli `docs/diyagram/akis_diyagrami.py` ile üretilir; kullanımı dosyanın başında yazar. Akış değişirse görsel ve [AGENTIC_FLOW.md](AGENTIC_FLOW.md) birlikte güncellenir.
