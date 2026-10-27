# Predict – Gate – Settle (PGS)

Agentic Text-to-SQL sistemi. ICML'e makale olarak gidecek ve ders projesi olarak sunulacak. Sunumu yapacak kullanıcı her parçayı zahmetsizce anlayabilmeli.

Küçük bir policy agent soruyu tool'larla çözer: değer arar, SQL dener, sonuca bakar, düzeltir. Cevap olarak seçtiği SQL'i `submit` eder; cevap bir final check'ten geçer. Agent ilerleyemez ya da takılırsa iş büyük bir teacher modele devredilir (handoff).

**Durum:** Akışın 8 adımı tamam (AGENTIC_FLOW.md). Sıradaki aşama agent'ın eğitimi: SFT → on-policy distillation → RL (kullanıcı kararı). Eğitim verisi experience log'dur: her soru, nereden çalıştırılırsa çalıştırılsın, bütün konuşmasıyla `experience/log.jsonl`'a yazılır (`agent/loop.py` `write_experience`); eğitime yalnızca `split = train` kayıtları girer. Karşılaştırmanın base'i `baseline.py`'dir (tool'suz tek SQL). Dosyaların görevleri KOD_YAPISI.md "Dosya haritası"nda.

**Modeller (kullanıcı kararı):** Policy yerel `mlx_lm.server`'daki `Qwen/Qwen3.5-0.8B`; teacher OpenRouter'daki `qwen/qwen3.5-9b`, bf16 sunan sağlayıcılardan biri (`TEACHER_PROVIDERS`; biri yoğunsa sıradakine geçilir). İkisinde de thinking kapalı (açıkken doğruluk düşüyor) ve temperature 0; son çağrı reddedildiyse ya da tekrarsa sıradaki adım 0.7 ile örneklenir. API kotası ve bütçe sınırlı. Teacher'ı yerelde çalıştırmak ya da policy'yi API'ye almak `config.py`'deki yorumda. Makale rakamları en sonda yerel Qwen3.5-4B ile alınır.

**Deneyler (kullanıcı kararı):** Bir test için 10 soru yeter (`--limit 10`); kullanıcı istemedikçe büyük ölçüm alınmaz. Kod değişikliğinin doğruluğu testlerle ve tek bir gerçek soruyla (`run.py`) gösterilir. `evaluate.py` soruları aynı anda 8 tane çalıştırır (`EVAL_WORKERS`; API'de 4). Ölçüm çıktısı bir boruya (`| grep`) verilmez, doğrudan dosyaya yazılır: boruyu okuyan süreç kapanırsa evaluate.py çöker.

BIRD dev `data/bird/dev/` altında; column profile'ları ve değer index'i `data/prepared/<db_id>/` altında (ilk çalıştırmada kurulur). Kod küçük aşamalarla yazılır ve her aşamadan sonra kullanıcının onayı beklenir. Depo: github.com/OnurAlp-Guvercin/foresql (push'u kullanıcı yapar; `.gitignore` `.env`, `data/` ve `experience/`'ı dışarıda bırakır).

## Dokümanlar

- [docs/AGENTIC_FLOW.md](docs/AGENTIC_FLOW.md): akış (8 adım), terim sözlüğü, tasarım kararları. **Bir adımı kodlamadan önce o adımı oku.**
- [docs/KOD_YAPISI.md](docs/KOD_YAPISI.md): kod kuralları, dosya haritası, tool'lar, sabitler, kayıt biçimleri (aşağıda içeri aktarılıyor).
- [docs/ARASTIRMA.md](docs/ARASTIRMA.md): literatür. Veri setleri 8. bölümde, hiperparametreler ve ödüller 9. bölümde; gerektiğinde oku.
- `docs/en/` ve `README.md`: hoca ve okuyucular için İngilizce çeviriler; asıl dokümanlar Türkçedir. Türkçe bir doküman değişirse İngilizcesi de aynı değişiklikle güncellenir. İngilizce akış görseli `docs/diyagram/flow_diagram_en.py` → `docs/PGS_flow_EN.png`; Türkçe görsel değişirse o da değişir.

@docs/KOD_YAPISI.md

## Komutlar

| Komut | Ne yapar |
|---|---|
| `uv venv --python 3.12 && source .venv/bin/activate` | Sanal ortam (Python 3.12, SQLite FTS5 trigram ile). Sistemdeki Python 3.14 kullanılmaz |
| `uv pip install -r requirements.txt` | Bağımlılıklar |
| `mlx_lm.server --model Qwen/Qwen3.5-0.8B --port 8080 --chat-template-args '{"enable_thinking":false}'` | Yerel model sunucusu (policy buraya gider; teacher OpenRouter API'sine). Kullanıcı ayrı bir terminalde başlatır. Model ilk seferde indirilir; Xet takılırsa önce `HF_HUB_DISABLE_XET=1 hf download <model>` |
| `python run.py --db <sqlite yolu> "soru" [--evidence "..."]` | Tek bir soruyu çalıştırır: agent'ın her adımını, cevabı ve cevabın gerçek sonucunu yazar |
| `python evaluate.py --name <deney> [--limit n]` | BIRD dev'i (`--limit n`: soruların sabit bir örneklemi) çalıştırıp puanlar, `results/<deney>.jsonl`'a yazar; doğruluk, süre ve maliyeti özetler |
| `python baseline.py --name <deney> [--model <model>] [--limit n]` | Base: aynı sorularda tool'suz tek SQL. Teacher modeli verilirse API'ye gider |
| `python report.py results/<deney>*.jsonl` | Birden çok sonuç dosyasını (ör. tekrar koşular) tek tabloda özetler |
| `python -m harness.prepare <sqlite yolu> "soru" ["evidence"]` | Bir sorunun başlangıç bağlamını (adım 1) yazdırır |
| `python -m agent.llm "soru"` | Modele tek bir soru sorar; cevabı, sağlayıcıyı ve hızı yazar |
| `pytest tests/` | Testler. `test_api_answers` API'ye gerçek bir istek atar; atlamak için `--deselect tests/test_llm.py::test_api_answers` |
| `python3 docs/diyagram/akis_diyagrami.py` | Akış görselinin HTML'ini üretir; PNG'ye çevirme komutu dosyanın başında. İngilizcesi `docs/diyagram/flow_diagram_en.py` |

## En önemli kural: az kod, kolay okunur

- Az kodla çok iş, ama önce okunabilirlik. Kısa ama anlaşılmaz kod yazılmaz.
- Aşırı mühendislik yapılmaz (ayrıntılar KOD_YAPISI.md "Kurallar").
- Yeni bağımlılık eklemeden önce kullanıcıya sor. Standart kütüphane ya da tek bir yaygın paket yetiyorsa onu kullan.
- Bir parçayı yazdıktan sonra kullanıcıya 2–3 cümleyle ne yaptığını ve nasıl denendiğini anlat.

## Araştırma kuralları (ICML)

- **Her deney tekrar üretilebilir olmalı:** config değerleri ve model adları sonuç dosyasına yazılır. Sonuçlar `results/` altında, her deney (koşu) için tek bir JSONL dosyasındadır.
- **Makaledeki her rakam gerçekten çalıştırılmış bir deneyden gelir.** Literatür rakamı ya da tahmin, sonuç olarak yazılmaz.
- **Ablation'lar:** Bir parçanın katkısı ölçülmek istendiğinde o parçayı kapatan bir flag eklenir; şu an her parça hep açıktır.
- **Karşılaştırmalar** en az 3 tekrar koşuyla yapılır (her koşu ayrı bir `--name`).

## Dikkat

- **Makine Apple Silicon, 48 GB RAM, CUDA yok.** Yerel modeller `mlx-lm` ile çalışır (Qwen3.5-4B bf16: ~25 token/sn, bellek ~12 GB). Bu hızla tam BIRD deneyleri günler sürebileceği için geliştirmede teacher API'de çalışır. Uzun paralel koşularda yerel sunucu GPU belleğini doldurabilir (`Insufficient Memory`); sunucuyu yeniden başlatmak çözer.
- **Son cevap her zaman gerçekten çalıştırılır** (final check).
- **`data/`** büyük veri setleri içindir (BIRD); kod buraya konmaz.
- **`.env`** gizli değerler içerir (`OPENROUTER_API_KEY`); içeriği okunmaz, yazdırılmaz. Key'i yalnızca `agent/llm.py` çalışırken okur.

## Doküman kuralları

- Dokümanlar Türkçe yazılır, ama projeye özgü teknik terimler İngilizce kalır (policy agent, harness, final check, handoff...). Sözlük AGENTIC_FLOW.md "Terimler" bölümünde; yeni bir terim gerekirse önce oraya eklenir.
- Dokümanlar yalnızca bugünkü durumu anlatır; geçmiş denemeler ve kaldırılan parçalar yazılmaz. Dosya adlarına ve içeriklere sürüm numarası (v1, v2) yazılmaz.
- Akış değişirse AGENTIC_FLOW.md ve görsel birlikte güncellenir. Görseldeki adım numaraları dokümanla eşleşmelidir.
- Kullanıcıya yapılan açıklamalar kısa ve basit olur, gerektiğinde örnekle anlatılır. Kısaltma ve jargon kullanılırsa açıklanır.
