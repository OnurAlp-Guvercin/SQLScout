"""Gold temizliği (eğitimden önce, bir kez): train ve val (BIRD dev) sorularının gold SQL'i çalıştırılır. Hata veren,
zaman aşımına uğrayan ya da boş (yalnızca 0/NULL) dönen sorular silinir ve json dosyasının üzerine yazılır. Train'in
question_id'si yoktur; dosyadaki sırası question_id olur. Temiz dosyada yeniden çalıştırılırsa bir şey değişmez.
Kullanım: python -m training.clean_bird"""

import json
from concurrent.futures import ThreadPoolExecutor

import config
import evaluate
from db import sqlite_db
from harness.tools.execute_sql import has_rows


def gold_works(question, split):
    """Gold SQL hatasız çalışıp dolu bir sonuç veriyor mu?"""
    db_path = evaluate.database_path(question["db_id"], split)
    result = sqlite_db.execute(db_path, question["SQL"], config.ANSWER_TIMEOUT_SECONDS)
    return has_rows(result)


def clean(split):
    path = evaluate.bird_dir(split) / f"{split}.json"
    questions = json.loads(path.read_text())
    for number, question in enumerate(questions):
        question.setdefault("question_id", number)
    with ThreadPoolExecutor(config.EVAL_WORKERS) as pool:
        works = list(pool.map(lambda question: gold_works(question, split), questions))
    kept = [question for question, ok in zip(questions, works) if ok]
    path.write_text(json.dumps(kept, indent=4, ensure_ascii=False))
    print(f"{split}: {len(questions)} soru, {len(questions) - len(kept)} silindi, {len(kept)} kaldı")


if __name__ == "__main__":
    for split in ["train", "dev"]:
        clean(split)
