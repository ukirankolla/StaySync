from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "StaySync API"
    api_prefix: str = "/api"
    database_url: str = "sqlite:///./staysync.db"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    otp_expire_minutes: int = 10
    otp_secret_salt: str = "staysync-otp"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    env: str = "development"

    # SMTP for email OTP delivery. Leave smtp_host empty to print OTPs to console (dev).
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    mail_from: str = "StaySync <no-reply@staysync.local>"
    smtp_use_tls: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
