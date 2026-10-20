"""Projedeki bütün sabitler ve ablation flag'leri. Sayılar yalnızca burada durur.
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
SUBSET_SIZE = 50
SUBSET_SEED = 0
EVAL_WORKERS = 8  # aynı anda çalışan soru sayısı; yerel sunucu bunları batch'ler. API'de 4 (8'de 429 hatası verdi)

# Modeller. Şimdi hepsi yerel mlx_lm.server'daki küçük Qwen3.5-0.8B'dir (yalnızca çalıştığını görmek için; komut
# CLAUDE.md'de). OpenRouter API'sine dönmek için: LLM_URL = "https://openrouter.ai/api/v1", POLICY_MODEL ve
# WORLD_MODEL = "qwen/qwen3.5-9b", TEACHER_MODEL ve SIMULATOR_MODEL = "qwen/qwen3.6-27b", POLICY_PROVIDER = "deepinfra",
# SEND_SEED = True, EVAL_WORKERS = 4. Makale rakamları sonda yerel Qwen3.5-4B ile alınır.
LLM_URL = "http://127.0.0.1:8080/v1"
LLM_API_KEY_NAME = "OPENROUTER_API_KEY"  # anahtar .env dosyasında durur; yerel sunucuda gerekmez
POLICY_MODEL = "Qwen/Qwen3.5-0.8B"
TEACHER_MODEL = "Qwen/Qwen3.5-0.8B"  # handoff'tan sonra (adım 11)
SIMULATOR_MODEL = "Qwen/Qwen3.5-0.8B"  # değerlendirmede ask_user'ı cevaplar (adım 3)
WORLD_MODEL = "Qwen/Qwen3.5-0.8B"  # placeholder world model (adım 6, 8)
POLICY_PROVIDER = None  # API'de policy modelini bf16 çalıştıran sağlayıcıya sabitler ("deepinfra")
SEND_SEED = False  # yerel sunucu seed'li istekleri batch'e almaz, tek tek çalıştırır
TOKENIZER_MODEL = "Qwen/Qwen3.5-9B"  # 16K bağlam sınırı asıl model (Qwen) için sayılır; yalnızca tokenizer indirilir
POLICY_TEMPERATURE = 0.7
POLICY_TOP_P = 0.8
MAX_NEW_TOKENS = 1024
LLM_TIMEOUT_SECONDS = 300
LLM_RETRIES = 8  # geçici hatada bekleme 5, 10, 20, ... 320 sn

# Agent loop (adım 2)
MAX_TOOL_CALLS = 10  # tool-call budget; reddedilen ve bozuk çağrılar da sayılır

# Guardrail'ler (her adım)
SHOWN_ROWS = 20  # agent'ın gördüğü en fazla satır
SHOWN_CELL_CHARS = 100  # agent'ın gördüğü hücre başına en fazla karakter
CONVERSATION_MAX_TOKENS = 32000  # aşılırsa en eski observation'lar tek satıra iner

# Search (adım 3) ve adım 1'deki değer eşleşmesi
SEARCH_RESULTS = 5
SEARCH_SIMILARITY = 0.8  # difflib benzerliği
SEARCH_CANDIDATES = 200  # FTS5 index'ten benzerlik sıralamasına giden en fazla değer
SEARCH_DESCRIPTION_MAX_CHARS = 200  # search_schema'da sütun açıklaması bundan uzunsa kırpılır
INDEX_VALUE_MAX_CHARS = 100  # bundan uzun metinler (ör. yorum gövdeleri) değer index'ine girmez
CONTEXT_VALUE_MATCHES = 2  # adım 1: sorudaki her kelime grubu için en iyi 2 değer
CONTEXT_PHRASE_WORDS = 3  # adım 1: en fazla 3 kelimelik gruplar aranır
CONTEXT_MIN_WORD_CHARS = 4  # adım 1: bundan kısa tek kelimeler aranmaz ("Los" → 'Loss' gürültüsü)
CONTEXT_WORD_SIMILARITY = 0.9  # adım 1: tek kelimelerde daha sıkı eşik ("schools" → 'Schooler' gürültüsü)

# Agent forecast (adım 4, 7)
ROW_RANGES = ["0", "1", "2-10", "11-100", "100+"]

# Veritabanı: gerçek çalıştırma (adım 7)
QUERY_TIMEOUT_SECONDS = 30
MAX_RESULT_ROWS = 100
EXPERIENCE_LOG = PROJECT_DIR / "experience" / "log.jsonl"

# Candidate'ler (adım 8)
FIRST_EXTRA_CANDIDATES = 2  # önce 2 ek candidate; hepsi agent'ın sonucunu verirse durulur
TOTAL_CANDIDATES = 8  # ayrışırlarsa agent'ın SQL'i dahil 8'e tamamlanır
CANDIDATE_TEMPERATURE = 0.8

# Confidence gate (adım 9): en kalabalık gruptaki candidate sayısı, hep 8 üzerinden
HIGH_MIN = 6  # ≥6/8 high (3/3 de high)
MEDIUM_MIN = 4  # 4–5/8 medium, ≤3/8 low
MAX_MEDIUM_NOTES = 1  # ikinci medium'da handoff
MEDIUM_NOTE_GROUPS = 2
MEDIUM_NOTE_ROWS = 3

# Final check (adım 10)
FINAL_CHECK_TRIES = 2  # 2 kez geçmezse handoff

# Handoff ve ask_user (adım 11, 3)
MAX_ASK_USER = 5  # soru başına, agent ve teacher toplam

# Database memory (adım 1)
MEMORY_DIR = PROJECT_DIR / "experience" / "memory"  # evaluate.py her deney ve seed için boş bir alt klasör açar
MEMORY_RECORDS = 3

# World model (adım 5, 6, 8)
EXPENSIVE_ROWS = 1_000_000  # estimate_cost bundan fazlaysa sorgu pahalıdır
LOW_BUDGET_SHARE = 0.25  # kalan budget başlangıcın %25'inin altındaysa "budget az"
PREDICTION_GATE = 0.9  # result type ve shape confidence'ı en az bu kadarsa trusted
AUDIT_SHARE = 0.05  # trusted prediction'ların %5'i yine de çalıştırılır
GATE_CHOICES = [0.5, 0.7, 0.8, 0.9, 0.95]  # aşama 33: world_model.predict ölçümünün denediği eşikler

# Cost simulation (aşama 32). Bird-coin maliyetleri BIRD-Interact'teki gibi: execute 1, ask 2, submit 3, bozuk çağrı 0.2;
# search'ler onların get_column_meaning'i gibi 0.5. Başlangıç: 6 + 2 × belirsizlik sayısı + kullanıcının sabrı.
BIRD_COINS = {"search_schema": 0.5, "search_values": 0.5, "ask_user": 2, "execute_sql": 1, "submit": 3, "handoff": 0}
BIRD_COIN_BAD_CALL = 0.2
BIRD_COIN_START = 6
USER_PATIENCE = 6
SIMULATED_ROW_COST = 1000  # her taranan satır 1000 satır sayılır; böylece SQLite'ta da "pahalı" sorgular olur

# Ablation flag'leri. Henüz yazılmamış parçalar kapalıymış gibi davranır.
USE_AGENT_FORECAST = True
USE_CANDIDATES = True
USE_HANDOFF = True
USE_ASK_USER = True
USE_DB_MEMORY = True
USE_WORLD_MODEL = True
SIMULATE_COST = False  # açıkken budget bird-coin'dir ve sorgu maliyeti SIMULATED_ROW_COST ile çarpılır

# Başlangıç bağlamı ve column profile (adım 1)
CONTEXT_MAX_TOKENS = 16000
PROFILE_TOP_VALUES = 5
PROFILE_ALL_VALUES_MAX = 30
PROFILE_VALUE_MAX_CHARS = 40
