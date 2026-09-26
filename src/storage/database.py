import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../tennis_bot.db")

def get_connection():
    """Cria e retorna uma conexão com a base de dados SQLite."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa a tabela de controlo de alertas enviados se ela não existir."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(match_id, alert_type)
        )
    """)
    conn.commit()
    conn.close()
    print("[BASE DE DADOS] Tabela 'sent_alerts' inicializada com sucesso.")

def alert_was_sent(match_id, alert_type):
    """Verifica se um determinado tipo de alerta já foi enviado para um jogo específico."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM sent_alerts WHERE match_id = ? AND alert_type = ?",
        (match_id, alert_type)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_alert_as_sent(match_id, alert_type, details=""):
    """Regista na base de dados que um alerta foi enviado para evitar repetições."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO sent_alerts (match_id, alert_type, details) VALUES (?, ?, ?)",
            (match_id, alert_type, details)
        )
        conn.commit()
    except Exception as e:
        print(f"[ERRO BD] Falha ao registar alerta enviado: {e}")
    finally:
        conn.close()