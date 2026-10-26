# Predict – Gate – Settle (PGS)

Agentic Text-to-SQL sistemi. ICML'e makale olarak gidecek ve ders projesi olarak sunulacak. Sunumu yapacak kullanıcı her parçayı zahmetsizce anlayabilmeli.

Küçük bir policy agent soruyu tool'larla çözer: değer arar, SQL dener, sonuca bakar, düzeltir. Cevap, agent'ın en son çalıştırdığı SQL'dir (`submit` argümansız) ve bir final check'ten geçer. Agent ilerleyemez ya da takılırsa iş büyük bir teacher modele devredilir (handoff).

**Durum:** Akış 8 adımdır (AGENTIC_FLOW.md): 1 başlangıç bağlamı, 2 agent'ın kararı, 3 `search_values`, 4–6 `execute_sql` (pre-check ve gerçek çalıştırma; agent SQL'i ` ```sql ` bloğunda yazarsa o da çalıştırılır), 7 `submit` → final check, 8 handoff. Sistem bilerek sade tutuluyor (kullanıcı kararı): candidate seçimi, confidence gate, `ask_user`, Mini-Interact, world model, forecast ve user simulator yok; gerekirse sonra eklenir. Agent (policy) ileride kesin eğitilecek (SFT → on-policy distillation → RL; kullanıcı kararı); bunun için her soru, nereden çalıştırılırsa çalıştırılsın (kullanım dahil), bütün konuşmasıyla `experience/log.jsonl`'a yazılır (`agent/loop.py` `write_experience`). Testler API'siz geçiyor. Policy yerel Qwen3.5-0.8B, teacher API'deki Qwen3.5-9B (kullanıcı kararı; API kotası ve bütçe sınırlı). Karşılaştırmanın base'i `baseline.py`'dir (tool'suz tek SQL). Dosyalar ve görevleri KOD_YAPISI.md "Dosya haritası"nda.

**Deneyler (kullanıcı kararı):** Uzun ölçüm yapılmaz: bir test için 10 soru yeter (`--limit 10`); kullanıcı istemedikçe büyük ölçüm alınmaz, kod değişikliğinin doğruluğu testlerle ve tek bir gerçek soruyla (`run.py`) gösterilir.

**Modeller:** Policy yerel `mlx_lm.server`'daki `Qwen/Qwen3.5-0.8B`; teacher OpenRouter'daki `qwen/qwen3.5-9b`, bf16 sunan sağlayıcılardan biri (`TEACHER_PROVIDERS`: DeepInfra, PrimeIntellect, Parasail; DeepInfra tek başına sık sık 429 `engine_overloaded` veriyor). Yerel sunucu aynı anda gelen istekleri tek batch'te üretir; seed'li istekler batch'e girmediği için seed gönderilmez (`SEND_SEED`). Policy ve teacher temperature 0 ile çalışır; son çağrı reddedildiyse ya da tekrarsa sıradaki adım 0.7 ile örneklenir. Teacher'ı da yerelde çalıştırmak ya da policy'yi API'ye almak `config.py`'deki yorumdadır. Ücretsiz `nvidia/nemotron-3.5-lightning:free` denendi: çok yavaş, kullanılmıyor. Makale rakamları en sonda yerel Qwen3.5-4B ile alınır (aşama 35).

BIRD dev `data/bird/dev/` altında; column profile'ları `data/prepared/<db_id>/` altında. `evaluate.py` soruları aynı anda 8 tane çalıştırır (`EVAL_WORKERS`; API'de 4, 8'de sağlayıcı 429 hatası verdi). Kod küçük aşamalarla yazılır ve her aşamadan sonra kullanıcının onayı beklenir. Son ölçümler (BIRD'den sabit 20 soru `--limit 20`, seed 0): 0.8B base 4/20 (`results/base08_seed0.jsonl`), 9B base 13/20, $0.012 (`results/base9b_seed0.jsonl`). Güncel kodla agentic sistemin ölçümü henüz alınmadı. Önceki sürümlerden öğrenilenler: 0.8B'nin tavanı düşük (8 SQL'den en az birinin doğru olduğu soru 25'te 6); agent keşif sorgusuyla başlayınca ilk SQL'i 20'de 0 doğruydu (tek SQL 4), bu yüzden prompt önce cevabı yazdırır; tool'suz denemede SQL'i JSON argument'ı yerine ` ```sql ` bloğunda yazmak ilk SQL'i 2/20'den 4/20'ye çıkardı, ama tool listesinde SQL tool'u olmayınca 0.8B var olmayan tool'lar uyduruyor, bu yüzden `execute_sql` tool'u kalır ve blok da kabul edilir; candidate'li sürüm 0.8B + 9B teacher'da 13/20 almıştı (candidate'ler yanlış 0.8B cevaplarını reddedip 9B'ye yönlendiriyordu). Temperature kararı: 0.8B tek SQL 0'da 5/25, 0.7'de 3/25 (`results/base08_t0_25_seed0.jsonl`, `results/base08_t07_25_seed0.jsonl`). Yerel sunucuda 8 soru paralel çalışırken uzun süre açık kalan sunucu bir kez GPU belleğini doldurdu (`Insufficient Memory`); sunucuyu yeniden başlatmak çözdü. Ölçüm çıktısı bir boruya (`| grep`) verilmez: boruyu okuyan süreç kapanırsa evaluate.py ilerleme satırında çöker; çıktı doğrudan dosyaya yazılır. Depo: github.com/OnurAlp-Guvercin/foresql (push'u kullanıcı yapar; `.gitignore` `.env` ve `data/`'yı dışarıda bırakır).

## Dokümanlar

- [docs/AGENTIC_FLOW.md](docs/AGENTIC_FLOW.md): akış (8 adım), terim sözlüğü, tasarım kararları. **Bir adımı kodlamadan önce o adımı oku.**
- [docs/KOD_YAPISI.md](docs/KOD_YAPISI.md): kod kuralları, dosya haritası, tool'lar, sabitler, kayıt biçimleri, yazım sırası (aşağıda içeri aktarılıyor).
- [docs/ARASTIRMA.md](docs/ARASTIRMA.md): literatür. Veri setleri 8. bölümde, hiperparametreler ve ödüller 9. bölümde; gerektiğinde oku.
- `docs/en/` (AGENTIC_FLOW.md, CODE_STRUCTURE.md, RESEARCH.md) ve `README.md`: hoca ve okuyucular için İngilizce çeviriler; asıl dokümanlar Türkçedir. Türkçe bir doküman değişirse İngilizcesi de aynı değişiklikle güncellenir. İngilizce akış görseli `docs/diyagram/flow_diagram_en.py` → `docs/PGS_flow_EN.png`; Türkçe görsel değişirse o da değişir.

@docs/KOD_YAPISI.md

## Komutlar

| Komut | Ne yapar |
|---|---|
| `uv venv --python 3.12 && source .venv/bin/activate` | Sanal ortam: Python 3.12.13, SQLite 3.53.1, FTS5 trigram var (doğrulandı). Sistemdeki Python 3.14 kullanılmaz |
| `uv pip install -r requirements.txt` | Bağımlılıklar |
| `python run.py --db <sqlite yolu> "soru" [--evidence "..."]` | Tek bir soruyu çalıştırır: agent'ın her adımını, cevabı ve cevabın gerçek sonucunu yazar |
| `python evaluate.py --name <deney> --seed 0 [--limit n]` | BIRD dev'i (`--limit n`: soruların sabit bir örneklemi; aynı n hep aynı soruları seçer) çalıştırıp puanlar, `results/<deney>_seed<n>.jsonl`'a yazar; doğruluk, süre ve maliyeti özetler |
| `python baseline.py --name <deney> [--model <model>] [--limit n]` | Base: aynı sorularda tool'suz tek SQL (temperature 0); agentic sistemle karşılaştırmak için. Teacher modeli verilirse API'ye gider |
| `python -m harness.prepare <sqlite yolu> "soru" ["evidence"]` | Bir sorunun başlangıç bağlamını (adım 1) yazdırır |
| `mlx_lm.server --model Qwen/Qwen3.5-0.8B --port 8080 --chat-template-args '{"enable_thinking":false}'` | Yerel model sunucusu (policy buraya gider; teacher OpenRouter API'sine). Sonda `mlx-community/Qwen3.5-4B-bf16` ile çalıştırılır. Kullanıcı ayrı bir terminalde başlatır. Model ilk seferde indirilir (0.8B ~1.7 GB, 4B ~9 GB); Xet takılırsa önce `HF_HUB_DISABLE_XET=1 hf download <model>` |
| `python report.py results/<deney>_*.jsonl` | Birden çok sonuç dosyasını (ör. seed'ler) tek tabloda özetler |
| `python -m agent.llm "soru"` | Modele tek bir soru sorar; cevabı, sağlayıcıyı ve hızı yazar |
| `pytest tests/` | Testler (`pytest.ini` proje kökünü import yoluna ekler). `test_api_answers` API'ye gerçek bir istek atar; atlamak için `--deselect tests/test_llm.py::test_api_answers` |
| `python3 docs/diyagram/akis_diyagrami.py` | Akış görselinin HTML'ini üretir; PNG'ye çevirme komutu dosyanın başında. İngilizcesi `docs/diyagram/flow_diagram_en.py` |

## En önemli kural: az kod, kolay okunur

- Az kodla çok iş, ama önce okunabilirlik. Kısa ama anlaşılmaz kod yazılmaz.
- Aşırı mühendislik yapılmaz (ayrıntılar KOD_YAPISI.md "Kurallar").
- Yeni bağımlılık eklemeden önce kullanıcıya sor. Standart kütüphane ya da tek bir yaygın paket yetiyorsa onu kullan.
- Bir parçayı yazdıktan sonra kullanıcıya 2–3 cümleyle ne yaptığını ve nasıl denendiğini anlat.

## Araştırma kuralları (ICML)

- **Her deney tekrar üretilebilir olmalı:** config değerleri, seed ve model adları sonuç dosyasına yazılır. Sonuçlar `results/` altında, her deney ve seed için tek bir JSONL dosyasındadır.
- **Makaledeki her rakam gerçekten çalıştırılmış bir deneyden gelir.** Literatür rakamı ya da tahmin, sonuç olarak yazılmaz.
- **Ablation'lar:** Bir parçanın katkısı ölçülmek istendiğinde o parçayı kapatan bir flag eklenir; şu an her parça hep açıktır.
- **Karşılaştırmalar** en az 3 seed ile yapılır.

## Dikkat

- **Makine Apple Silicon, 48 GB RAM, CUDA yok.** CUDA isteyen düz vLLM çalışmaz (Apple Silicon için ayrı bir vllm-metal eklentisi var, denenmedi). Yerel modeller `mlx-lm` 0.32.2 ile çalışır (ölçüm, Qwen3.5-4B bf16: ~25 token/sn, 16K bağlamı okuma ~24 sn, bellek ~12 GB). Bu hızla tam BIRD deneyleri günler sürebileceği için geliştirmede API kullanılır.
- **Son cevap her zaman gerçekten çalıştırılır** (final check).
- **`data/`** büyük veri setleri içindir (BIRD, SynSQL-2.5M); kod buraya konmaz.
- **`.env`** gizli değerler içerir (`OPENROUTER_API_KEY`); içeriği okunmaz, yazdırılmaz. Key'i yalnızca `agent/llm.py` çalışırken okur.

## Doküman kuralları

- Dokümanlar Türkçe yazılır, ama projeye özgü teknik terimler İngilizce kalır (policy agent, harness, final check, handoff...). Sözlük AGENTIC_FLOW.md "Terimler" bölümünde; yeni bir terim gerekirse önce oraya eklenir.
- Dosya adlarına ve içeriklere sürüm numarası (v1, v2) yazılmaz.
- Akış değişirse AGENTIC_FLOW.md ve görsel birlikte güncellenir. Görseldeki adım numaraları dokümanla eşleşmelidir.
- Kullanıcıya yapılan açıklamalar kısa ve basit olur, gerektiğinde örnekle anlatılır. Kısaltma ve jargon kullanılırsa açıklanır.
