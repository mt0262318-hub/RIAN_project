import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

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
