import psycopg2
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback construction if individual vars are used in .env
if not DATABASE_URL:
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_pass = os.getenv("POSTGRES_PASSWORD", "")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "postgres")
    DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

queries = """
-- 1. Vault File Tracking Table
CREATE TABLE IF NOT EXISTS vault_registry (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    telegram_file_id TEXT,
    telegram_message_id BIGINT,
    file_size_kb FLOAT,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 24/7 Continuous Training & Evaluation Logs
CREATE TABLE IF NOT EXISTS agent_eval_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100),
    user_input TEXT NOT NULL,
    tool_calls JSONB,
    ai_response TEXT NOT NULL,
    execution_status VARCHAR(20) DEFAULT 'success',
    eval_score FLOAT,
    critic_feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(queries)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Step 1 Success: vault_registry & agent_eval_logs tables created successfully!")
except Exception as e:
    print(f"❌ Error during Step 1 setup: {e}")
