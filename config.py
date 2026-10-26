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

# Modeller. Policy yerel mlx_lm.server'daki küçük Qwen3.5-0.8B'dir (komut CLAUDE.md'de);
# teacher OpenRouter API'sindeki Qwen3.5-9B'dir (handoff'tan sonra, adım 8; key .env'de). Teacher'ı da yerelde
# çalıştırmak için: TEACHER_MODEL = POLICY_MODEL, TEACHER_URL = LLM_URL, TEACHER_PROVIDERS = None.
# Policy'yi de API'ye almak için: LLM_URL = TEACHER_URL, POLICY_MODEL = "qwen/qwen3.5-9b", POLICY_PROVIDERS = TEACHER_PROVIDERS,
# SEND_SEED = True, EVAL_WORKERS = 4. Makale rakamları sonda yerel Qwen3.5-4B ile alınır.
LLM_URL = "http://127.0.0.1:8080/v1"  # policy modelinin adresi
TEACHER_URL = "https://openrouter.ai/api/v1"  # teacher modelinin adresi
LLM_API_KEY_NAME = "OPENROUTER_API_KEY"  # key .env dosyasında durur; yalnızca https adreslerine gönderilir
POLICY_MODEL = "Qwen/Qwen3.5-0.8B"
TEACHER_MODEL = "qwen/qwen3.5-9b"  # handoff'tan sonra (adım 8)
POLICY_PROVIDERS = None  # yerel sunucuda None
# API'de model yalnızca bunlardan birinde, bf16 çalışır; biri yoğunsa (429) sıradakine geçilir
TEACHER_PROVIDERS = ["deepinfra", "primeintellect", "parasail"]
SEND_SEED = False  # yerel sunucu seed'li istekleri batch'e almaz, tek tek çalıştırır
TOKENIZER_MODEL = "Qwen/Qwen3.5-9B"  # 16K bağlam sınırı asıl model (Qwen) için sayılır; yalnızca tokenizer indirilir
POLICY_TEMPERATURE = 0  # policy ve teacher her adımda en olası cevabı seçer (0.8B'de tek SQL: 0'da 5/25, 0.7'de 3/25)
POLICY_TOP_P = 0.8
RETRY_TEMPERATURE = 0.7  # son çağrı reddedildiyse ya da tekrarsa sıradaki adım bununla örneklenir (0'da aynısı gelir)
MAX_NEW_TOKENS = 1024
LLM_TIMEOUT_SECONDS = 300
LLM_RETRIES = 8  # geçici hatada bekleme 5, 10, 20, ... 320 sn

# Agent loop (adım 2)
MAX_TOOL_CALLS = 10  # agent'ın tool-call budget'ı (teacher bunun yarısını alır); reddedilen ve bozuk çağrılar da sayılır
BUDGET_WARNING = 2  # kalan budget her sonucun altında yazar; bu kadar kalınca "submit et" hatırlatması da eklenir
MAX_REPEATS = 3  # aynı çağrı bu kadar kez tekrarlanırsa agent takılmış sayılır: handoff
PROGRESS_CALLS = 4  # agent ilk bu kadar tool call'ında dolu sonuç veren bir SQL çalıştıramadıysa: handoff

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
QUERY_TIMEOUT_SECONDS = 30
MAX_RESULT_ROWS = 100

# Final check (adım 7)
FINAL_CHECK_TRIES = 2  # 2 kez geçmezse handoff

# Experience log (soru bittikten sonra): ileride agent'ın eğitim verisi
EXPERIENCE_LOG = PROJECT_DIR / "experience" / "log.jsonl"

# Başlangıç bağlamı ve column profile (adım 1)
CONTEXT_MAX_TOKENS = 16000
SCHEMA_SELECT_TEMPERATURE = 0  # sınır aşılınca tabloları seçen model; aynı soru hep aynı seçimi alsın
PROFILE_TOP_VALUES = 10  # metin sütunlarında en sık 10 değer (en fazla 10 farklı değer varsa hepsi); diğerlerini agent search_values ile bulur
PROFILE_VALUE_MAX_CHARS = 40
