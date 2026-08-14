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
    cors_origins: str = "http://localhost:5173,http://localhost:3000,https://staysync.vercel.app"
    env: str = "development"
    # Absolute base URL of this API, set in production so uploaded photos resolve
    # from any host (e.g. https://backend.up.railway.app).
    public_base_url: str = ""
    # Seed demo data on boot when the database is empty (used on first deploy).
    seed_on_start: bool = False

    # SMTP for email OTP delivery. Leave smtp_host empty to print OTPs to console (dev).
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    mail_from: str = "StaySync <no-reply@staysync.local>"
    smtp_use_tls: bool = True

    # Upload storage. "local" writes to ./uploads on disk; "supabase" uploads to
    # Supabase Storage. Set supabase_url + supabase_service_key to enable supabase.
    storage_backend: str = "local"
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_storage_bucket: str = "staysync"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
