from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "GatorSync"
    debug: bool = False
    database_url: str = "postgresql://gatorsync:gatorsync@localhost:5432/gatorsync"
    secret_key: str = "change-me-in-production"
    allowed_origins: str = "http://localhost:3000"

    model_config = {"env_file": ".env"}


settings = Settings()
