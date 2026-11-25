"""Durable book history with a separate SQLite database per operating mode."""

import sqlite3


class Store:
    def __init__(self, folder, mode):
        folder.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(folder / f"{mode}.sqlite3")
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
          PRAGMA journal_mode=WAL;
          CREATE TABLE IF NOT EXISTS shifts(id INTEGER PRIMARY KEY, started TEXT DEFAULT CURRENT_TIMESTAMP);
          INSERT INTO shifts(id) SELECT 1 WHERE NOT EXISTS(SELECT 1 FROM shifts);
          CREATE TABLE IF NOT EXISTS jobs(
            id TEXT PRIMARY KEY, shift INTEGER, status TEXT, verdict TEXT, label TEXT, confidence REAL,
            reason TEXT, model_hash TEXT, image BLOB, raw BLOB, actual_route TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
          CREATE TABLE IF NOT EXISTS samples(id INTEGER PRIMARY KEY, book TEXT, truth TEXT, split TEXT,
            label TEXT, confidence REAL, model_hash TEXT, image BLOB, raw BLOB);
        """)
        fields = {r["name"] for r in self.db.execute("PRAGMA table_info(jobs)")}
        with self.db:
            for name, kind in (("policy", "TEXT"), ("stop_reason", "TEXT"), ("inference_ms", "REAL")):
                if name not in fields:
                    self.db.execute(f"ALTER TABLE jobs ADD COLUMN {name} {kind}")
            self.db.execute("UPDATE jobs SET status='UNCONFIRMED',stop_reason='PC_RESTART' WHERE status IN ('WAIT_AI','DECIDED')")
        columns = {row["name"] for row in self.db.execute("PRAGMA table_info(samples)")}
        if "provenance" not in columns:
            with self.db:
                self.db.execute("ALTER TABLE samples ADD COLUMN provenance TEXT")

    def begin(self, key, policy=None):
        with self.db:
            cur = self.db.execute(
                "INSERT OR IGNORE INTO jobs(id,policy,shift,status) SELECT ?,?,max(id),'WAIT_AI' FROM shifts",
                (key, policy),
            )
        return cur.rowcount == 1

    def inspection_issue(self, key, reason):
        with self.db:
            self.db.execute("UPDATE jobs SET reason=? WHERE id=? AND status='WAIT_AI'", (reason, key))

    def decision(self, key, r):
        with self.db:
            return (
                self.db.execute(
                    """UPDATE jobs SET verdict=?,label=?,confidence=?,reason=?,model_hash=?,inference_ms=?,
              image=?,raw=?,status='DECIDED' WHERE id=? AND status='WAIT_AI'""",
                    (
                        r.verdict,
                        r.label,
                        r.confidence,
                        r.reason,
                        r.model_hash,
                        getattr(r, "inference_ms", None),
                        r.image,
                        r.raw,
                        key,
                    ),
                ).rowcount
                == 1
            )

    def finish(self, key, state, reason):
        with self.db:
            self.db.execute(
                """UPDATE jobs SET status=?,stop_reason=?,reason=coalesce(nullif(reason,''),?)
                WHERE id=? AND status IN ('WAIT_AI','DECIDED')""",
                (state, reason, reason, key),
            )

    def summary(self):
        row = self.db.execute("""SELECT count(CASE WHEN verdict='OK' THEN 1 END) ok,
          count(CASE WHEN verdict='NG' THEN 1 END) ng FROM jobs WHERE shift=(SELECT max(id) FROM shifts)""").fetchone()
        recent = self.db.execute(self.job_query + " WHERE shift=(SELECT max(id) FROM shifts) ORDER BY rowid DESC LIMIT 8").fetchall()
        return dict(ok=row["ok"], ng=row["ng"], total=sum(row)), [dict(r) for r in recent]

    job_query = """SELECT id,shift,status,verdict,label,confidence,reason,stop_reason,policy,inference_ms,
                   coalesce(length(image),0)>0 AS has_image,strftime('%Y-%m-%dT%H:%M:%SZ',created) AS created FROM jobs"""

    def job(self, key):
        row = self.db.execute(self.job_query + " WHERE id=?", (key,)).fetchone()
        return dict(row) if row else None

    def shift(self):
        with self.db:
            self.db.execute("INSERT INTO shifts DEFAULT VALUES")

    def sample(self, book, truth, split, r, provenance=None):
        if self.db.execute(
            "SELECT 1 FROM samples WHERE book=? AND (split<>? OR truth<>?)",
            (book, split, truth),
        ).fetchone():
            raise ValueError("Cuốn này đã thuộc tập khác hoặc có nhãn khác")
        with self.db:
            self.db.execute(
                """INSERT INTO samples(book,truth,split,label,confidence,model_hash,image,raw,provenance)
                VALUES(?,?,?,?,?,?,?,?,?)""",
                (
                    book,
                    truth,
                    split,
                    r.label,
                    r.confidence,
                    r.model_hash,
                    r.image,
                    r.raw,
                    provenance,
                ),
            )
