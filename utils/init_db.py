import sqlite3
import os
from pathlib import Path


def create_db_from_sql(sql_path) -> bool:
    with open(sql_path, encoding='utf-8') as f:
        script = f.read()
    p = Path(sql_path)
    name = p.stem
    parent = p.parents[0]
    if os.path.isfile(f"{parent}/{name}.sqlite"):
        return False
    db = sqlite3.connect(f"{parent}/{name}.sqlite")
    cur = db.cursor()
    cur.executescript(script)
    db.commit()
    return True


def init_notepaper_db():
    create_db_from_sql("data/note_paper.sql")
    create_db_from_sql("blueprints/data/share_id.sql")


if __name__ == '__main__':
    create_db_from_sql("../data/note_paper.sql")
