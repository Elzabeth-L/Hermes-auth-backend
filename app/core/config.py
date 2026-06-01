from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_uri: str = Field(default="<COSMOS_DB_MONGO_URI_PLACEHOLDER>", alias="MONGODB_URI")
    database_name: str = Field(default="hermes_auth", alias="DATABASE_NAME")
    jwt_secret: str = Field(default="<JWT_SECRET>", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=60, alias="JWT_EXPIRE_MINUTES")
    admin_email: str = Field(default="admin@hermes.com", alias="ADMIN_EMAIL")
    admin_password: str = Field(default="<ADMIN_PASSWORD>", alias="ADMIN_PASSWORD")
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")
    customer_service_url: str = Field(
        default="http://hermes-customer-backend",
        alias="CUSTOMER_SERVICE_URL",
    )
    customer_service_timeout_seconds: float = Field(
        default=10.0,
        alias="CUSTOMER_SERVICE_TIMEOUT_SECONDS",
    )
    mongodb_server_selection_timeout_ms: int = Field(
        default=5000,
        alias="MONGODB_SERVER_SELECTION_TIMEOUT_MS",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
