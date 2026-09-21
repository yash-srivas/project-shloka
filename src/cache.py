"""
Caching Layer for 7-Step Shloka Analysis.
Uses SQLite for zero-setup local persistence, structured to cleanly migrate to PostgreSQL later.
Prevents redundant LLM calls when a shloka is reopened or demonstrated.
"""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from src.config import CACHE_DB_PATH
from src.schemas import StepOutput, RetrievalResult

class ShlokaCache:
    """SQLite-backed cache for shloka step analysis results."""

    def __init__(self, db_path: Path = CACHE_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shloka_steps_cache (
                    shloka_id TEXT NOT NULL,
                    step_number INTEGER NOT NULL,
                    step_name_sa TEXT,
                    step_name_en TEXT,
                    output TEXT NOT NULL,
                    model TEXT NOT NULL,
                    retrieval_metadata TEXT,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (shloka_id, step_number, model)
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_shloka_id 
                ON shloka_steps_cache (shloka_id)
            """)
            conn.commit()

    def get_step_output(self, shloka_id: str, step_number: int, model: str = "default") -> Optional[StepOutput]:
        """Fetch cached output for a specific step and model."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT step_number, step_name_sa, step_name_en, output, model, retrieval_metadata
                FROM shloka_steps_cache
                WHERE shloka_id = ? AND step_number = ? AND (model = ? OR model = 'default')
                ORDER BY updated_at DESC
                LIMIT 1
            """, (shloka_id, step_number, model))
            row = cursor.fetchone()
            if not row:
                return None

            retrieved = []
            if row["retrieval_metadata"]:
                try:
                    contexts_data = json.loads(row["retrieval_metadata"])
                    retrieved = [RetrievalResult(**c) for c in contexts_data]
                except Exception:
                    retrieved = []

            return StepOutput(
                step_number=row["step_number"],
                step_name_sanskrit=row["step_name_sa"] or f"Step {row['step_number']}",
                step_name_english=row["step_name_en"] or f"Step {row['step_number']}",
                output=row["output"],
                retrieved_contexts=retrieved,
                model=row["model"]
            )

    def set_step_output(
        self,
        shloka_id: str,
        step_number: int,
        step_name_sa: str,
        step_name_en: str,
        output: str,
        model: str = "default",
        retrieved_contexts: List[RetrievalResult] = None
    ):
        """Save or update step output in cache."""
        retrieved_contexts = retrieved_contexts or []
        metadata_json = json.dumps([c.model_dump() for c in retrieved_contexts], ensure_ascii=False)
        now_iso = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO shloka_steps_cache 
                (shloka_id, step_number, step_name_sa, step_name_en, output, model, retrieval_metadata, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(shloka_id, step_number, model) DO UPDATE SET
                    output = excluded.output,
                    step_name_sa = excluded.step_name_sa,
                    step_name_en = excluded.step_name_en,
                    retrieval_metadata = excluded.retrieval_metadata,
                    updated_at = excluded.updated_at
            """, (shloka_id, step_number, step_name_sa, step_name_en, output, model, metadata_json, now_iso))
            conn.commit()

    def get_all_steps(self, shloka_id: str, model: str = "default") -> Dict[int, StepOutput]:
        """Fetch all cached steps (1-7) for a shloka."""
        results = {}
        for step_num in range(1, 8):
            cached = self.get_step_output(shloka_id, step_num, model)
            if cached:
                results[step_num] = cached
        return results

    def clear_cache(self, shloka_id: Optional[str] = None):
        """Clear cache for a specific shloka or everything."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if shloka_id:
                cursor.execute("DELETE FROM shloka_steps_cache WHERE shloka_id = ?", (shloka_id,))
            else:
                cursor.execute("DELETE FROM shloka_steps_cache")
            conn.commit()
