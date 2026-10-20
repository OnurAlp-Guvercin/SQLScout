# Predict – Gate – Settle (PGS)

Agentic Text-to-SQL sistemi. ICML'e makale olarak gidecek ve ders projesi olarak sunulacak. Sunumu yapacak kullanıcı her parçayı zahmetsizce anlayabilmeli.

Küçük bir policy agent (Qwen3.5-4B) soruyu tool'larla çözer; soru belirsizse kullanıcıya sorar (`ask_user`). Her SQL'i çalıştırmadan önce sonucunu tahmin eder (agent forecast). World model yalnızca pahalı sorgularda devreye girer; ilk sürümde eğitilmemiş bir LLM'dir ve prompt'la world model gibi davranır (placeholder). Agent takılırsa iş teacher'a (Qwen3.6-27B, 4-bit) devredilir (handoff).

**Durum:** Aşama 1–33 yazıldı (Phase 1 ve Phase 2; aşama 34 Phase 3 ve eğitim yapılmayacak, kullanıcı kararı). Testler API'siz geçiyor. Phase 2: Mini-Interact (`data/mini_interact/`, 300 belirsiz SELECT görevi) `evaluate.py --dataset mini_interact` ile çalışır; kendi iki adımlı user simulator'ü ve bird-coin'li cost simulation (`--simulate-cost`) var. Mini-Interact'in doğru SQL'leri açık dosyada yok: kullanıcı bird.bench25@gmail.com'a "[mini-interact GT&Test Cases]" konulu e-posta atıp gelen dosyayı `data/mini_interact/mini_interact_gold.jsonl` olarak koyarsa puanlanır; o zamana kadar Mini-Interact soruları puanlanmaz. Ölçümler yerel Qwen3.5-0.8B ile alınacak (kullanıcı kararı); bu model çok zayıf olduğu için rakamlar yalnızca akışın çalıştığını gösterir. Dosyalar ve görevleri KOD_YAPISI.md "Dosya haritası"nda. Eski API ölçümleri (50 soru, Qwen3.5-9B, seed 0): aşama 5 %64, aşama 6 %60, aşama 7 %58 (seed 1/2: aşama 5 %66/62, aşama 6 %64/66). 50 soruda 1–3 soruluk fark şanstır.

**Modeller:** Şu an bütün model çağrıları (policy, candidate'ler, teacher, user simulator, world model) yerel `mlx_lm.server`'daki `Qwen/Qwen3.5-0.8B`'ye gider; yalnızca akışın çalıştığını görmek içindir, az istekle denenir (kullanıcı kararı). Sunucu aynı anda gelen istekleri tek batch'te üretir; seed'li istekler batch'e girmediği için seed gönderilmez (`SEND_SEED`). Ölçümler için API'ye dönüş `config.py`'deki yorumda yazan birkaç satırdır: policy ve world model `qwen/qwen3.5-9b` (DeepInfra, bf16; 50 soruluk ölçüm ~$0.05–0.4), teacher ve simulator `qwen/qwen3.6-27b`. Ücretsiz `nvidia/nemotron-3.5-lightning:free` denendi: çok yavaş, kullanılmıyor. Makale rakamları en sonda yerel Qwen3.5-4B ile alınır (aşama 35).

**Eğitim yokmuş gibi çalışılır.** World model ve policy eğitimi (aşama 36–43) isteğe bağlıdır; agentic süreç uçtan uca oturunca kullanıcı karar verir.

**Açık karar (aşama 26–27'den önce kullanıcıya sorulacak):** ARASTIRMA.md "world model, calibration kontrolünden geçmeden kullanılmaz" diyor; placeholder ise aşama 27'de bu kontrol olmadan karar vermeye başlıyor. Öneri: aşama 26'daki ölçümde tahminler yeterince isabetli değilse aşama 27'de prediction gate eşiği yükseltilir. Aşama 26'nın ölçümü dev verisiyle yapıldığı için yalnızca bakmak içindir; eşik dev'e göre ayarlanmaz.

BIRD dev `data/bird/dev/` altında; column profile'ları `data/prepared/<db_id>/` altında. `evaluate.py` soruları aynı anda 8 tane çalıştırır (`EVAL_WORKERS`; API'de 4, 8'de sağlayıcı 429 hatası verdi). Proje bir git deposu değil. Kod küçük aşamalarla yazılır ve her aşamadan sonra kullanıcının onayı beklenir. Bilinen çelişki: AGENTIC_FLOW.md database memory için "sorular veri setindeki sırayla çalıştırılır" diyor, `evaluate.py` ise soruları aynı anda 4 tane çalıştırıyor; memory açıkken kayıtların sırası çalıştırmadan çalıştırmaya değişebilir (karar kullanıcıda). Yapılan ölçüm (yerel Qwen3.5-0.8B, BIRD'den 50 soru, tam sistem): seed 0/1/2 doğruluk %4/%0/%6 (`results/asama29_tam_seed*.jsonl`); kullanıcı bunun ardından durulmasını istedi. Sıradaki iş (kullanıcı onaylayınca): yerel sunucu başlatılır, ablation'lar (seed 0, her flag tek tek): `python evaluate.py --name asama29_off_<flag> --seed 0 --subset --off USE_<FLAG>`; tablo: `python report.py results/asama29_*.jsonl`. Mini-Interact ölçümü (aşama 33) ve world model eşik ölçümü kullanıcı istemedikçe yapılmaz. Ölçüm çıktısı bir boruya (`| grep`) verilmez: boruyu okuyan süreç kapanırsa evaluate.py ilerleme satırında çöker; çıktı doğrudan dosyaya yazılır. Depo: github.com/OnurAlp-Guvercin/foresql (push'u kullanıcı yapar; `.gitignore` `.env` ve `data/`'yı dışarıda bırakır).

## Dokümanlar

- [docs/AGENTIC_FLOW.md](docs/AGENTIC_FLOW.md): akış (11 adım), terim sözlüğü, tasarım kararları. **Bir adımı kodlamadan önce o adımı oku.**
- [docs/KOD_YAPISI.md](docs/KOD_YAPISI.md): kod kuralları, dosya haritası, tool'lar, sabitler ve flag'ler, kayıt biçimleri, yazım sırası (aşağıda içeri aktarılıyor).
- [docs/ARASTIRMA.md](docs/ARASTIRMA.md): literatür. Veri setleri 8. bölümde, hiperparametreler ve ödüller 9. bölümde; gerektiğinde oku.
- `docs/en/` (AGENTIC_FLOW.md, CODE_STRUCTURE.md, RESEARCH.md) ve `README.md`: hoca ve okuyucular için İngilizce çeviriler; asıl dokümanlar Türkçedir. Türkçe bir doküman değişirse İngilizcesi de aynı değişiklikle güncellenir. İngilizce akış görseli `docs/diyagram/flow_diagram_en.py` → `docs/PGS_flow_EN.png`; Türkçe görsel değişirse o da değişir.

@docs/KOD_YAPISI.md

## Komutlar

| Komut | Ne yapar |
|---|---|
| `uv venv --python 3.12 && source .venv/bin/activate` | Sanal ortam: Python 3.12.13, SQLite 3.53.1, FTS5 trigram var (doğrulandı). Sistemdeki Python 3.14 kullanılmaz |
| `uv pip install -r requirements.txt` | Bağımlılıklar |
| `python run.py --db <sqlite yolu> "soru" [--evidence "..."]` | Tek bir soruyu çalıştırır: agent'ın her adımını, cevabı ve cevabın gerçek sonucunu yazar |
| `python evaluate.py --name <deney> --seed 0 [--dataset bird\|mini_interact] [--subset] [--limit n] [--off USE_...] [--simulate-cost]` | Bir veri setini (`--subset`: BIRD'den sabit 50 soru; `--limit n`: ilk n soru; `--off`: ablation; `--simulate-cost`: bird-coin, Phase 2) çalıştırıp puanlar, `results/<deney>_seed<n>.jsonl`'a yazar; doğruluk, süre ve maliyeti özetler |
| `python -m harness.prepare <sqlite yolu> "soru" ["evidence"]` | Bir sorunun başlangıç bağlamını (adım 1) yazdırır |
| `mlx_lm.server --model Qwen/Qwen3.5-0.8B --port 8080 --chat-template-args '{"enable_thinking":false}'` | Yerel model sunucusu (şu an bütün model çağrıları buraya gider). Sonda `mlx-community/Qwen3.5-4B-bf16` ile çalıştırılır. Kullanıcı ayrı bir terminalde başlatır. Model ilk seferde indirilir (0.8B ~1.7 GB, 4B ~9 GB); Xet takılırsa önce `HF_HUB_DISABLE_XET=1 hf download <model>` |
| `python -m world_model.predict [n]` | World model'in ölçümü (aşama 26, 33): experience log'un son n gerçek çalıştırması için tahmin; type/shape tuttu mu, her eşikte trusted denenlerin kaçı doğru |
| `python report.py results/<deney>_*.jsonl` | Birden çok sonuç dosyasını (seed'ler, ablation'lar) tek tabloda özetler |
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
- **Ablation'lar:** tasarım kararları KOD_YAPISI.md'deki ablation flag'leriyle açılıp kapatılır (agent forecast, candidate'ler, handoff, database memory, `ask_user`, world model).
- **Karşılaştırmalar** en az 3 seed ile yapılır.

## Dikkat

- **Makine Apple Silicon, 48 GB RAM, CUDA yok.** CUDA isteyen düz vLLM çalışmaz (Apple Silicon için ayrı bir vllm-metal eklentisi var, denenmedi). Yerel modeller `mlx-lm` 0.32.2 ile çalışır (ölçüm, Qwen3.5-4B bf16: ~25 token/sn, 16K bağlamı okuma ~24 sn, bellek ~12 GB). Bu hızla tam BIRD deneyleri günler sürebileceği için geliştirmede API kullanılır. Büyük RL eğitimleri bu makineye sığmayabilir; gerekiyorsa kullanıcıya sorulur.
- **Son cevap her zaman gerçekten çalıştırılır.** World model'in prediction'ı asla cevap ya da reward olarak kullanılmaz.
- **`data/`** büyük veri setleri içindir (BIRD, SynSQL-2.5M); kod buraya konmaz.
- **`.env`** gizli değerler içerir (`OPENROUTER_API_KEY`); içeriği okunmaz, yazdırılmaz. Anahtarı yalnızca `agent/llm.py` çalışırken okur.

## Doküman kuralları

- Dokümanlar Türkçe yazılır, ama projeye özgü teknik terimler İngilizce kalır (policy agent, world model, harness, gate, candidate, consensus, handoff, experience log...). Sözlük AGENTIC_FLOW.md "Terimler" bölümünde; yeni bir terim gerekirse önce oraya eklenir.
- Dosya adlarına ve içeriklere sürüm numarası (v1, v2) yazılmaz.
- Akış değişirse AGENTIC_FLOW.md ve görsel birlikte güncellenir. Görseldeki adım numaraları dokümanla eşleşmelidir.
- Kullanıcıya yapılan açıklamalar kısa ve basit olur, gerektiğinde örnekle anlatılır. Kısaltma ve jargon kullanılırsa açıklanır.
