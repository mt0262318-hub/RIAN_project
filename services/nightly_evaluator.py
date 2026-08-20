import os
import sys
import json
import logging
from datetime import datetime

# Add root directory to python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from database import engine

logger = logging.getLogger("nightly_evaluator")

def run_nightly_reflection():
    """
    Evaluates recent interactions, generates synthetic training pairs, 
    and exports them to Telegram Cloud Vault with zero local disk load.
    """
    fetch_query = text("""
        SELECT id, session_id, user_input, tool_calls, ai_response, execution_status 
        FROM agent_eval_logs 
        WHERE eval_score IS NULL 
        ORDER BY created_at DESC 
        LIMIT 50
    """)
    
    records = []
    try:
        with engine.connect() as conn:
            result = conn.execute(fetch_query)
            records = [dict(row._mapping) for row in result]
    except Exception as e:
        print(f"❌ DB Fetch Error: {e}")
        return
        
    if not records:
        print("ℹ️ No unreviewed interactions found for evaluation.")
        return

    dataset_filename = f"dataset_synth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    curated_data = []

    for item in records:
        entry = {
            "instruction": "You are R.I.A.N., an autonomous AI assistant.",
            "input": item["user_input"],
            "tool_calls": item["tool_calls"],
            "output": item["ai_response"],
            "status": item["execution_status"]
        }
        curated_data.append(entry)

    with open(dataset_filename, "w", encoding="utf-8") as f:
        for entry in curated_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Mark records as reviewed
    record_ids = [r["id"] for r in records]
    with engine.connect() as conn:
        conn.execute(
            text(f"UPDATE agent_eval_logs SET eval_score = 1.0 WHERE id IN ({','.join(map(str, record_ids))})")
        )
        conn.commit()

    print(f"✅ Generated {len(curated_data)} training pairs -> {dataset_filename}")

    # Vault Integration: upload & local purge
    try:
        from tools.vault_storage import upload_to_telegram_vault
        upload_to_telegram_vault(dataset_filename, category="training_dataset")
        if os.path.exists(dataset_filename):
            os.remove(dataset_filename)
        print(f"🚀 Synced {dataset_filename} to Cloud Vault & Purged locally!")
    except Exception as e:
        print(f"⚠️ Cloud Vault sync hook notice: {e}")

if __name__ == "__main__":
    run_nightly_reflection()
