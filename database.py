# database.py
# Handles all SQLite database operations for NIDAN.ai

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "nidan.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


# ─────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            email       TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Chat history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email  TEXT NOT NULL,
            query       TEXT NOT NULL,
            response    TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email)
        )
    """)

    # Image analysis history table (with image_data blob)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_history (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email      TEXT NOT NULL,
            filename        TEXT,
            modality        TEXT,
            mean_intensity  REAL,
            edge_density    REAL,
            ai_feedback     TEXT,
            ai_vision       TEXT,
            image_data      TEXT,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email)
        )
    """)

    # Add image_data column if upgrading from old DB
    try:
        cursor.execute("ALTER TABLE image_history ADD COLUMN image_data TEXT")
    except Exception:
        pass

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────

def save_chat(user_email: str, query: str, response: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_email, query, response) VALUES (?, ?, ?)",
        (user_email, query, response)
    )
    conn.commit()
    conn.close()


def get_chat_history(user_email: str) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, query, response, created_at FROM chat_history WHERE user_email = ? ORDER BY created_at DESC",
        (user_email,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_chat(record_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# IMAGE ANALYSIS HISTORY
# ─────────────────────────────────────────────

def save_image_analysis(user_email: str, filename: str, modality: str,
                         mean_intensity: float, edge_density: float,
                         ai_feedback: str, ai_vision: str,
                         image_data: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO image_history
           (user_email, filename, modality, mean_intensity, edge_density,
            ai_feedback, ai_vision, image_data)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_email, filename, modality, mean_intensity,
         edge_density, ai_feedback, ai_vision, image_data)
    )
    conn.commit()
    conn.close()


def get_image_history(user_email: str) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, filename, modality, mean_intensity, edge_density,
                  ai_feedback, ai_vision, image_data, created_at
           FROM image_history WHERE user_email = ? ORDER BY created_at DESC""",
        (user_email,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_image_analysis(record_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM image_history WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# CLEAR ALL
# ─────────────────────────────────────────────

def clear_all_history(user_email: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE user_email = ?", (user_email,))
    cursor.execute("DELETE FROM image_history WHERE user_email = ?", (user_email,))
    conn.commit()
    conn.close()


init_db()