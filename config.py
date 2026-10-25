"""Projedeki bütün sabitler. Sayılar yalnızca burada durur.
Her değerin anlamı KOD_YAPISI.md "config.py sabitleri" tablosunda; yeni parça geldikçe dosya büyür."""

from pathlib import Path

# Yollar
PROJECT_DIR = Path(__file__).parent
BIRD_DEV_DIR = PROJECT_DIR / "data" / "bird" / "dev"
MINI_INTERACT_DIR = PROJECT_DIR / "data" / "mini_interact"  # Phase 2 (aşama 30)
MINI_INTERACT_GOLD = MINI_INTERACT_DIR / "mini_interact_gold.jsonl"  # e-postayla istenen doğru SQL'ler
PREPARED_DIR = PROJECT_DIR / "data" / "prepared"
RESULTS_DIR = PROJECT_DIR / "results"

# Değerlendirme
SAMPLE_SEED = 0  # --limit n: soruların bu seed'le seçilmiş sabit bir örneklemi
EVAL_WORKERS = 8  # aynı anda çalışan soru sayısı; yerel sunucu bunları batch'ler. API'de 4 (8'de 429 hatası verdi)

# Modeller. Şimdi hepsi yerel mlx_lm.server'daki küçük Qwen3.5-0.8B'dir (yalnızca çalıştığını görmek için; komut
# CLAUDE.md'de). OpenRouter API'sine dönmek için: LLM_URL = "https://openrouter.ai/api/v1",
# POLICY_MODEL = "qwen/qwen3.5-9b", TEACHER_MODEL = "qwen/qwen3.6-27b", POLICY_PROVIDER = "deepinfra",
# SEND_SEED = True, EVAL_WORKERS = 4. Makale rakamları sonda yerel Qwen3.5-4B ile alınır.
LLM_URL = "http://127.0.0.1:8080/v1"
LLM_API_KEY_NAME = "OPENROUTER_API_KEY"  # key .env dosyasında durur; yerel sunucuda gerekmez
POLICY_MODEL = "Qwen/Qwen3.5-0.8B"
TEACHER_MODEL = "Qwen/Qwen3.5-0.8B"  # handoff'tan sonra (adım 10)
POLICY_PROVIDER = None  # API'de policy modelini bf16 çalıştıran sağlayıcıya sabitler ("deepinfra")
SEND_SEED = False  # yerel sunucu seed'li istekleri batch'e almaz, tek tek çalıştırır
TOKENIZER_MODEL = "Qwen/Qwen3.5-9B"  # 16K bağlam sınırı asıl model (Qwen) için sayılır; yalnızca tokenizer indirilir
POLICY_TEMPERATURE = 0.7
POLICY_TOP_P = 0.8
MAX_NEW_TOKENS = 1024
LLM_TIMEOUT_SECONDS = 300
LLM_RETRIES = 8  # geçici hatada bekleme 5, 10, 20, ... 320 sn

# Agent loop (adım 2)
MAX_TOOL_CALLS = 10  # agent'ın tool-call budget'ı (teacher bunun yarısını alır); reddedilen ve bozuk çağrılar da sayılır
BUDGET_WARNING = 2  # kalan budget her sonucun altında yazar; bu kadar kalınca "submit et" hatırlatması da eklenir
MAX_REPEATS = 3  # aynı çağrı bu kadar kez tekrarlanırsa agent takılmış sayılır: handoff

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

# Candidate'ler (adım 7)
FIRST_EXTRA_CANDIDATES = 2  # önce 2 ek candidate; hepsi agent'ın sonucunu verirse durulur
TOTAL_CANDIDATES = 8  # ayrışırlarsa agent'ın SQL'i dahil 8'e tamamlanır
CANDIDATE_TEMPERATURE = 0.8

# Confidence gate (adım 8): en kalabalık gruptaki candidate sayısı, hep 8 üzerinden
HIGH_MIN = 6  # ≥6/8 high (3/3 de high)
MEDIUM_MIN = 4  # 4–5/8 medium, ≤3/8 low
MAX_MEDIUM_NOTES = 1  # ikinci medium'da handoff
MEDIUM_NOTE_GROUPS = 2
MEDIUM_NOTE_ROWS = 3

# Final check (adım 9)
FINAL_CHECK_TRIES = 2  # 2 kez geçmezse handoff

# ask_user (adım 3)
MAX_ASK_USER = 5  # soru başına, agent ve teacher toplam

# Experience log (soru bittikten sonra): ileride agent'ın eğitim verisi
EXPERIENCE_LOG = PROJECT_DIR / "experience" / "log.jsonl"

# Database memory (adım 1)
MEMORY_DIR = PROJECT_DIR / "experience" / "memory"  # evaluate.py her deney ve seed için boş bir alt klasör açar
MEMORY_RECORDS = 3

# Başlangıç bağlamı ve column profile (adım 1)
CONTEXT_MAX_TOKENS = 16000
SCHEMA_SELECT_TEMPERATURE = 0  # sınır aşılınca tabloları seçen model; aynı soru hep aynı seçimi alsın
PROFILE_TOP_VALUES = 10  # metin sütunlarında en sık 10 değer (en fazla 10 farklı değer varsa hepsi); diğerlerini agent search_values ile bulur
PROFILE_VALUE_MAX_CHARS = 40
