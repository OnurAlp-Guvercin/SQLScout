# Predict – Gate – Settle (PGS)

Agentic Text-to-SQL sistemi. ICML'e makale olarak gidecek ve ders projesi olarak sunulacak. Sunumu yapacak kullanıcı her parçayı zahmetsizce anlayabilmeli.

Küçük bir policy agent (Qwen3.5-4B) soruyu tool'larla çözer: değer arar, SQL dener, sonuca bakar; soru belirsizse kullanıcıya sorar (`ask_user`). Cevap, ayrı ayrı yazılmış SQL'lerin aynı sonucu verip vermediğine bakan bir gate'ten geçer. Agent takılırsa iş teacher'a (Qwen3.6-27B, 4-bit) devredilir (handoff).

**Durum:** Akışın 10 adımı yazıldı (Phase 1 ve Phase 2). Şu an hedef sade, çalışan bir base (kullanıcı kararı): world model, forecast ve user simulator yok. Agent (policy) ileride kesin eğitilecek (SFT → on-policy distillation → RL; kullanıcı kararı); bunun için her soru, nereden çalıştırılırsa çalıştırılsın (kullanım dahil), bütün konuşmasıyla `experience/log.jsonl`'a yazılır (`agent/loop.py` `write_experience`). Kod adım başına tek dosya olacak şekilde sadeleştirildi; eski hâlin yedeği `/tmp/pgs_backup/project_2026-10-25`'te. Testler API'siz geçiyor. Phase 2: Mini-Interact (`data/mini_interact/`, 300 belirsiz SELECT görevi) `evaluate.py --dataset mini_interact` ile çalışır. Mini-Interact'in doğru SQL'leri açık dosyada yok: kullanıcı bird.bench25@gmail.com'a "[mini-interact GT&Test Cases]" konulu e-posta atıp gelen dosyayı `data/mini_interact/mini_interact_gold.jsonl` olarak koyarsa puanlanır; o zamana kadar Mini-Interact soruları puanlanmaz. Policy yerel Qwen3.5-0.8B, teacher API'deki Qwen3.5-9B (kullanıcı kararı; API kotası ve bütçe sınırlı). Dosyalar ve görevleri KOD_YAPISI.md "Dosya haritası"nda. Eski API ölçümleri (50 soru, Qwen3.5-9B, eski kod; kayıt dosyaları temizlikte silindi): tool'suz tek SQL %62–66, yalnızca submit'li agent loop %60–66.

**`ask_user` ve deneyler (kullanıcı kararı):** User simulator yok. Agent `ask_user` çağırınca soru terminale gelir (`run.py`'de de `evaluate.py`'de de). Deneyi Claude yürütüyorsa soruyu, sorunun doğru SQL'ine (Mini-Interact'te belirsizlik notlarına) bakıp kullanıcı gibi tek cümleyle cevaplar: SQL'i, değerleri ya da sonucu söylemez; verdiği cevapları kullanıcıya raporlar. Kullanıcı kendisi çalıştırırsa cevabı o verir. `evaluate.py` cevap beklerken durur; Claude onu arka planda, stdin'i bir FIFO'dan okuyacak şekilde başlatır (`mkfifo /tmp/pgs_answers; python evaluate.py ... 0<>/tmp/pgs_answers > /tmp/pgs_eval.log`; `0<>` FIFO'yu açık tutar, her cevaptan sonra EOF gelmez; denendi), çıktıda `Agent asks:` görünce cevabı `echo "..." > /tmp/pgs_answers` ile yazar. Bir test için 10–20 soru yeter (`--limit 20`); yüzlerce soru çalıştırılmaz (kullanıcı kararı).

**Modeller:** Policy (ve onun candidate'leri) yerel `mlx_lm.server`'daki `Qwen/Qwen3.5-0.8B`; teacher OpenRouter'daki `qwen/qwen3.5-9b`, bf16 sunan sağlayıcılardan biri (`TEACHER_PROVIDERS`: DeepInfra, PrimeIntellect, Parasail; DeepInfra tek başına sık sık 429 `engine_overloaded` veriyor). Teacher'ın candidate'lerini teacher yazar. Yerel sunucu aynı anda gelen istekleri tek batch'te üretir; seed'li istekler batch'e girmediği için seed gönderilmez (`SEND_SEED`). Policy ve teacher temperature 0 ile çalışır; son çağrı reddedildiyse ya da tekrarsa sıradaki adım 0.7 ile örneklenir. Teacher'ı da yerelde çalıştırmak ya da policy'yi API'ye almak `config.py`'deki yorumdadır. Ücretsiz `nvidia/nemotron-3.5-lightning:free` denendi: çok yavaş, kullanılmıyor. Makale rakamları en sonda yerel Qwen3.5-4B ile alınır (aşama 35).

BIRD dev `data/bird/dev/` altında; column profile'ları `data/prepared/<db_id>/` altında. `evaluate.py` soruları aynı anda 8 tane çalıştırır (`EVAL_WORKERS`; API'de 4, 8'de sağlayıcı 429 hatası verdi). Kod küçük aşamalarla yazılır ve her aşamadan sonra kullanıcının onayı beklenir. Son ölçümler (güncel kod, BIRD'den sabit 20 soru `--limit 20`, seed 0): 0.8B tool'suz tek SQL 3/20 (`results/base08_20_seed0.jsonl`); 9B tool'suz tek SQL 13/20, $0.012 (`results/base9b_20_seed0.jsonl`); yalnızca 0.8B'li sistem (teacher da 0.8B) 3/20 (`results/agent08_only_seed0.jsonl`); tam sistem, 0.8B agent + 9B teacher 13/20, $0.13, 20 sorunun 19'u handoff (`results/full_9bteacher_fix_seed0.jsonl`); agent ve teacher 9B 14/20, $0.19 (`results/agent9b_seed0.jsonl`). Bulgular: (1) 0.8B'nin bilgisi tavan: 8 candidate'in en az birinin doğru olduğu soru 25'te yalnızca 6 (pass@8), tek SQL 5/25; agent loop ya da gate modelin yazamadığı SQL'i yaratamaz. (2) 0.8B + 9B sistemin kazancı tamamen teacher'dan; aynı 20 soruda 9B'nin tek SQL'ine eşit, 10 kat maliyetle. (3) Agentic yapı 9B'ye +1 soru kattı (14 vs 13), 20 soruda gürültü düzeyinde. Base'in 0.8B SQL'lerinin çoğu (25'te 16) çalışmıyor (yanlış sütun/alias); hata notu bu yüzden sorgudaki tabloların gerçek sütunlarını gösterir. Temperature kararı: 0.8B tek SQL 0'da 5/25, 0.7'de 3/25 (`results/base08_t0_25_seed0.jsonl`, `results/base08_t07_25_seed0.jsonl`). Base ölçümleri `harness/tools/submit.py` `write_sql` ile adım 1'in bağlamında, temperature 0'da alındı. Sıradaki iş kullanıcının kararına bağlı: büyük kazanç beklenen yer belirsiz sorular (Mini-Interact, `ask_user`); bunun için doğru SQL dosyası gerekiyor. Yerel sunucuda 8 soru paralel çalışırken uzun süre açık kalan sunucu bir kez GPU belleğini doldurdu (`Insufficient Memory`); sunucuyu yeniden başlatmak çözdü. Mini-Interact ölçümü kullanıcı istemedikçe yapılmaz. Ölçüm çıktısı bir boruya (`| grep`) verilmez: boruyu okuyan süreç kapanırsa evaluate.py ilerleme satırında çöker; çıktı doğrudan dosyaya yazılır. Depo: github.com/OnurAlp-Guvercin/foresql (push'u kullanıcı yapar; `.gitignore` `.env` ve `data/`'yı dışarıda bırakır).

## Dokümanlar

- [docs/AGENTIC_FLOW.md](docs/AGENTIC_FLOW.md): akış (10 adım), terim sözlüğü, tasarım kararları. **Bir adımı kodlamadan önce o adımı oku.**
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
| `python evaluate.py --name <deney> --seed 0 [--dataset bird\|mini_interact] [--limit n]` | Bir veri setini (`--limit n`: soruların sabit bir örneklemi; aynı n hep aynı soruları seçer) çalıştırıp puanlar, `results/<deney>_seed<n>.jsonl`'a yazar; doğruluk, süre ve maliyeti özetler |
| `python -m harness.prepare <sqlite yolu> "soru" ["evidence"]` | Bir sorunun başlangıç bağlamını (adım 1) yazdırır |
| `mlx_lm.server --model Qwen/Qwen3.5-0.8B --port 8080 --chat-template-args '{"enable_thinking":false}'` | Yerel model sunucusu (şu an bütün model çağrıları buraya gider). Sonda `mlx-community/Qwen3.5-4B-bf16` ile çalıştırılır. Kullanıcı ayrı bir terminalde başlatır. Model ilk seferde indirilir (0.8B ~1.7 GB, 4B ~9 GB); Xet takılırsa önce `HF_HUB_DISABLE_XET=1 hf download <model>` |
| `python report.py results/<deney>_*.jsonl` | Birden çok sonuç dosyasını (ör. seed'ler) tek tabloda özetler |
| `hf download birdsql/mini-interact --repo-type dataset --local-dir data/mini_interact` | Mini-Interact verisi (139 MB; indirildi) |
| `python -m agent.llm "soru"` | Modele tek bir soru sorar; cevabı, sağlayıcıyı ve hızı yazar |
| `pytest tests/` | Testler (`pytest.ini` proje kökünü import yoluna ekler). `test_api_answers` API'ye gerçek bir istek atar; atlamak için `--deselect tests/test_llm.py::test_api_answers` |
| `python3 docs/diyagram/akis_diyagrami.py` | Akış görselinin HTML'ini üretir; PNG'ye çevirme komutu dosyanın başında |

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

- Dokümanlar Türkçe yazılır, ama projeye özgü teknik terimler İngilizce kalır (policy agent, harness, gate, candidate, consensus, handoff...). Sözlük AGENTIC_FLOW.md "Terimler" bölümünde; yeni bir terim gerekirse önce oraya eklenir.
- Dosya adlarına ve içeriklere sürüm numarası (v1, v2) yazılmaz.
- Akış değişirse AGENTIC_FLOW.md ve görsel birlikte güncellenir. Görseldeki adım numaraları dokümanla eşleşmelidir.
- Kullanıcıya yapılan açıklamalar kısa ve basit olur, gerektiğinde örnekle anlatılır. Kısaltma ve jargon kullanılırsa açıklanır.
