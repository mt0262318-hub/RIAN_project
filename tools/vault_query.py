import logging
from sqlalchemy import text
from database import engine

logger = logging.getLogger("vault_query")

def search_cloud_vault(keyword: str = "", category: str = None) -> list:
    """
    Search and retrieve file pointers and summaries from the Telegram Cloud Vault registry.
    """
    query_str = "SELECT file_name, category, telegram_file_id, file_size_kb, summary, created_at FROM vault_registry WHERE 1=1"
    params = {}

    if keyword:
        query_str += " AND (file_name ILIKE :keyword OR summary ILIKE :keyword)"
        params["keyword"] = f"%{keyword}%"

    if category:
        query_str += " AND category = :category"
        params["category"] = category

    query_str += " ORDER BY created_at DESC LIMIT 10;"

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query_str), params)
            records = [dict(row._mapping) for row in result]
            return records
    except Exception as e:
        logger.error(f"Error querying cloud vault: {e}")
        return []

if __name__ == "__main__":
    results = search_cloud_vault()
    print(f"✅ Cloud Vault Search Tool initialized. Total matching files: {len(results)}")
