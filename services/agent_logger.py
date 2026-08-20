import json
import logging
from sqlalchemy import text
from database import engine

logger = logging.getLogger("agent_logger")

def log_interaction(session_id: str, user_input: str, tool_calls: dict, ai_response: str, execution_status: str = "success", eval_score: float = None, critic_feedback: str = None):
    """
    Asynchronously logs agent interactions for 24/7 continuous training and self-reflection.
    """
    query = text("""
        INSERT INTO agent_eval_logs (session_id, user_input, tool_calls, ai_response, execution_status, eval_score, critic_feedback)
        VALUES (:session_id, :user_input, :tool_calls, :ai_response, :execution_status, :eval_score, :critic_feedback)
    """)
    
    try:
        with engine.connect() as conn:
            conn.execute(query, {
                "session_id": session_id or "default_session",
                "user_input": user_input,
                "tool_calls": json.dumps(tool_calls) if tool_calls else None,
                "ai_response": ai_response,
                "execution_status": execution_status,
                "eval_score": eval_score,
                "critic_feedback": critic_feedback
            })
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to log interaction to agent_eval_logs: {e}")

