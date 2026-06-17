"""SQLite persistence layer for translation history."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "translations.db"


@dataclass(frozen=True)
class TranslationRecord:
    original_text: str
    source_language: str
    target_language: str
    translated_text: str


@contextmanager
def get_connection(db_path: Path = DATABASE_PATH) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT NOT NULL,
                source_language TEXT NOT NULL,
                target_language TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_translation(record: TranslationRecord) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO translations (
                original_text,
                source_language,
                target_language,
                translated_text
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                record.original_text,
                record.source_language,
                record.target_language,
                record.translated_text,
            ),
        )


def fetch_history(search_query: str | None = None) -> pd.DataFrame:
    initialize_database()
    base_query = """
        SELECT
            id,
            original_text AS "Original Text",
            source_language AS "Source Language",
            target_language AS "Target Language",
            translated_text AS "Translated Text",
            timestamp AS "Timestamp"
        FROM translations
    """
    params: tuple[str, ...] = ()

    if search_query:
        base_query += """
            WHERE original_text LIKE ?
               OR translated_text LIKE ?
               OR source_language LIKE ?
               OR target_language LIKE ?
        """
        like_query = f"%{search_query}%"
        params = (like_query, like_query, like_query, like_query)

    base_query += " ORDER BY timestamp DESC, id DESC"

    with get_connection() as connection:
        return pd.read_sql_query(base_query, connection, params=params)


def get_statistics() -> dict[str, int]:
    initialize_database()
    with get_connection() as connection:
        total_translations = connection.execute(
            "SELECT COUNT(*) FROM translations"
        ).fetchone()[0]
        unique_source_languages = connection.execute(
            "SELECT COUNT(DISTINCT source_language) FROM translations"
        ).fetchone()[0]
        unique_target_languages = connection.execute(
            "SELECT COUNT(DISTINCT target_language) FROM translations"
        ).fetchone()[0]
        total_characters = connection.execute(
            "SELECT COALESCE(SUM(LENGTH(original_text)), 0) FROM translations"
        ).fetchone()[0]

    return {
        "total_translations": total_translations,
        "unique_source_languages": unique_source_languages,
        "unique_target_languages": unique_target_languages,
        "total_characters": total_characters,
    }


def clear_history() -> None:
    initialize_database()
    with get_connection() as connection:
        connection.execute("DELETE FROM translations")
