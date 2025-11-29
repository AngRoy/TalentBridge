from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AIRTABLE_API_KEY: str
    AIRTABLE_BASE_ID: str
    AIRTABLE_JOBS_TABLE: str = "Jobs"
    AIRTABLE_APPS_TABLE: str = "Applications"

    # Optional AI key (can be empty)
    OPENAI_API_KEY: str | None = None

    # OTP secret (for demo only)
    OTP_SECRET: str = "change_me_in_prod"

    # Pydantic v2 style config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
