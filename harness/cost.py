"""Cost simulation (aşama 32; adım 2 ve 5). SQLite'ta sorgular ucuz olduğu için SIMULATE_COST açıkken:
her tool call BIRD-Interact'teki gibi bird-coin harcar, "budget az" kalan bird-coin'e bakar ve sorgunun tahmini
maliyeti SIMULATED_ROW_COST ile çarpılır (pahalı sorgu yolu, adım 6, SQLite'ta da denenebilsin).
Kapalıyken budget tool call sayısıdır ve maliyet estimate_cost'un kendisidir."""

import config
from db import sqlite_db


def start_coins(ambiguity):
    """Başlangıç bird-coin'i: 6 + her belirsizlik için bir ask_user maliyeti + kullanıcının sabrı."""
    count = 0
    if ambiguity:
        count = len(ambiguity["user_query_ambiguity"].get("critical_ambiguity", []))
        count += len(ambiguity["knowledge_ambiguity"])
    return config.BIRD_COIN_START + count * config.BIRD_COINS["ask_user"] + config.USER_PATIENCE


def spend(step, context):
    if config.SIMULATE_COST:
        context.coins_left -= config.BIRD_COIN_BAD_CALL if step["error"] else config.BIRD_COINS[step["tool"]]


def budget_left(context):
    if context.calls >= context.budget_end:
        return False
    return not config.SIMULATE_COST or context.coins_left > 0


def budget_low(context):
    """Kalan budget başlangıcın LOW_BUDGET_SHARE'inin altında mı (tool call ya da bird-coin)."""
    if config.SIMULATE_COST:
        return context.coins_left < config.LOW_BUDGET_SHARE * context.coins
    return context.budget_end - context.calls < config.LOW_BUDGET_SHARE * config.MAX_TOOL_CALLS


def query_cost(db_path, sql):
    """Tahmini taranacak satır sayısı; SQL hatalıysa None."""
    rows = sqlite_db.estimate_cost(db_path, sql)
    if rows is None or not config.SIMULATE_COST:
        return rows
    return rows * config.SIMULATED_ROW_COST
