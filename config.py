"""Projedeki bütün sabitler. Sayılar yalnızca burada durur.
Her değerin anlamı KOD_YAPISI.md "config.py sabitleri" tablosunda; yeni parça geldikçe dosya büyür."""

from pathlib import Path

# Yollar
PROJECT_DIR = Path(__file__).parent
BIRD_DEV_DIR = PROJECT_DIR / "data" / "bird" / "dev"
PREPARED_DIR = PROJECT_DIR / "data" / "prepared"
RESULTS_DIR = PROJECT_DIR / "results"

# Değerlendirme
SAMPLE_SEED = 0  # --limit n: soruların bu seed'le seçilmiş sabit bir örneklemi
EVAL_WORKERS = 8  # aynı anda çalışan soru sayısı; yerel sunucu bunları batch'ler. API'de 4 (8'de 429 hatası verdi)

# Modeller. Small model yerel mlx_lm.server'daki küçük Qwen3.5-0.8B'dir (komut CLAUDE.md'de);
# large model OpenRouter API'sindeki Qwen3.5-9B'dir (handoff'tan sonra, adım 8; key .env'de). Large model'i de yerelde
# çalıştırmak için: büyük modeli ikinci bir mlx_lm.server'da başka bir port'ta aç; LARGE_MODEL_URL = "http://127.0.0.1:8081/v1",
# LARGE_MODEL = o modelin adı, LARGE_MODEL_PROVIDERS = None (large model small model'le aynı model olmamalı).
# Small model'i de API'ye almak için: SMALL_MODEL_URL = LARGE_MODEL_URL, SMALL_MODEL = "qwen/qwen3.5-9b", SMALL_MODEL_PROVIDERS = LARGE_MODEL_PROVIDERS,
# EVAL_WORKERS = 4 ve HANDOFF = False (evaluate.py --large-model-agent hepsini yapar): small model large model'le aynı model olunca kendine devretmesin,
# large model yalnızca cevabı kontrol etsin. Makale rakamları sonda yerel Qwen3.5-4B ile alınır.
SMALL_MODEL_URL = "http://127.0.0.1:8080/v1"  # small model'in adresi
LARGE_MODEL_URL = "https://openrouter.ai/api/v1"  # large model'in adresi
LLM_API_KEY_NAME = "OPENROUTER_API_KEY"  # key .env dosyasında durur; yalnızca https adreslerine gönderilir
SMALL_MODEL = "models/Qwen3.5-0.8B"  # proje kökündeki klasör; mlx_lm.server'a --model ile verilen yolla aynı olmalı
LARGE_MODEL = "qwen/qwen3.5-9b"  # handoff'tan sonra (adım 8)
SMALL_MODEL_PROVIDERS = None  # yerel sunucuda None
# API'de model yalnızca bunlardan birinde, bf16 çalışır; biri yoğunsa (429) sıradakine geçilir
LARGE_MODEL_PROVIDERS = ["deepinfra", "primeintellect", "parasail"]
TOKENIZER = "models/Qwen3.5-0.8B/tokenizer.json"  # konuşmanın token'ları (CONVERSATION_MAX_TOKENS) bununla sayılır; Qwen3.5-9B'ninkiyle aynı dosya
TEMPERATURE = 0  # small model ve large model her adımda en olası cevabı seçer
TOP_P = 0.8
RETRY_TEMPERATURE = 0.7  # son çağrı reddedildiyse ya da tekrarsa sıradaki adım bununla örneklenir (0'da aynısı gelir)
MAX_NEW_TOKENS = 1024
LLM_TIMEOUT_SECONDS = 300  # bir isteğin toplam süresi; geçerse kesilip yeniden denenir
API_PARALLEL = 4  # API'ye aynı anda giden en fazla istek (sağlayıcılar yoğunken kuyruk ve zaman aşımı azalır)
LLM_RETRIES = 8  # geçici hatada bekleme 5, 10, 20, ... 320 sn

# Agent loop (adım 2)
MAX_TOOL_CALLS = 10  # small model'in ve handoff'tan sonra large model'in tool-call budget'ı; reddedilen ve bozuk çağrılar da sayılır
BUDGET_WARNING = 2  # kalan budget her sonucun altında yazar; bu kadar kalınca "submit et" hatırlatması da eklenir
MAX_REPEATS = 3  # aynı çağrı bu kadar kez tekrarlanırsa agent takılmış sayılır: handoff
PROGRESS_CALLS = 6  # small model ilk bu kadar tool call'ında dolu sonuç veren bir SQL çalıştıramadıysa: handoff
WASTED_CALLS = 5  # small model arka arkaya bu kadar çağrıyı boşa harcadıysa (okunamadı, tekrar, ret): handoff

# Guardrail'ler (her adım)
SHOWN_ROWS = 20  # agent'ın gördüğü en fazla satır
SHOWN_CELL_CHARS = 100  # agent'ın gördüğü hücre başına en fazla karakter
CONVERSATION_MAX_TOKENS = 32000  # aşılırsa en eski observation'lar tek satıra iner

# Search (adım 3)
SEARCH_RESULTS = 5
SEARCH_SIMILARITY = 0.8  # difflib benzerliği
SEARCH_CANDIDATES = 200  # FTS5 index'ten benzerlik sıralamasına giden en fazla değer
INDEX_VALUE_MAX_CHARS = 100  # bundan uzun metinler (ör. yorum gövdeleri) değer index'ine girmez

# Veritabanı: gerçek çalıştırma (adım 6)
EXPLORE_TIMEOUT_SECONDS = 50  # execute_sql: keşif ve deneme sorguları
ANSWER_TIMEOUT_SECONDS = 200  # ana sorgular: submit edilen SQL (final check) ve puanlamadaki gold ile cevap
MAX_RESULT_ROWS = 100
MAX_TOTAL_ROWS = 1_000_000  # bundan çok satır dönen sorgu hata sayılır (belleği korur); BIRD dev'in en büyük gold'u ~278 bin

# Final check (adım 7)
FINAL_CHECK_TRIES = 2  # 2 kez geçmezse handoff

# Handoff (adım 8)
HANDOFF = True  # ablation (evaluate.py --no-handoff): False ise large model yalnızca cevabı kontrol eder, hiç devralmaz

# Experience log (soru bittikten sonra): ileride agent'ın eğitim verisi
EXPERIENCE_LOG = PROJECT_DIR / "experience" / "log.jsonl"

# Memory (adım 1): daha önce doğru çözülmüş en benzer sorular bağlama eklenir
MEMORY = True  # ablation (evaluate.py --no-memory): False ise bellek ne okunur ne yazılır
MEMORY_DB = PROJECT_DIR / "experience" / "memory.sqlite"
EMBEDDING_MODEL = "models/Qwen3-Embedding-0.6B"  # proje kökündeki klasör
MEMORY_EXAMPLES = 3  # bağlama eklenen en fazla örnek
MEMORY_MIN_SIMILARITY = 0.7  # BIRD dev soruları arasında 0.7 altı çoğunlukla alakasız, üstü aynı tabloları paylaşıyor

# Column profile (adım 1)
PROFILE_TOP_VALUES = 10  # metin sütunlarında en sık 10 değer (en fazla 10 farklı değer varsa hepsi); diğerlerini agent search_values ile bulur
PROFILE_VALUE_MAX_CHARS = 40
PROFILE_UNIQUE_RATIO = 0.9  # farklı değer sayısı dolu satırların en az bu oranıysa sütun neredeyse tekil (ID, isim)
PROFILE_UNIQUE_VALUES = 3  # neredeyse tekil metin sütunlarında gösterilen örnek değer sayısı (token tasarrufu)
