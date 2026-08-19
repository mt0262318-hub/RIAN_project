from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_api_key: str
    groq_model: str = "openai/gpt-oss-120b"
    chroma_dir: str = "./rian_memory"
    embeddings_model: str = "all-MiniLM-L6-v2"
    cpu_alert_threshold: int = 85
    ram_alert_threshold: int = 85
    monitor_interval_seconds: int = 10
    app_name: str = "R.I.A.N."

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()