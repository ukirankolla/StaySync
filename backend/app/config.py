import re
import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_ADMIN_PASSWORD = "admin123"  # published in old docs: must never protect a real admin account
WEAK_JWT_SECRETS = {"", "change-me-in-production", "change-me-to-a-long-random-string", "secret", "changeme"}


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
    cors_origins: str = "http://localhost:5173,http://localhost:3000,https://staysync.vercel.app,https://stay-sync-omega.vercel.app"
    # Vercel preview/production URLs of this project only (not every *.vercel.app site).
    cors_origin_regex: str = r"^https://stay-?sync[a-z0-9-]*\.vercel\.app$"
    # Secure by default: anything other than an explicit "development" is treated as production.
    # Local development sets ENV=development in backend/.env (see .env.example).
    env: str = "production"
    # Absolute base URL of this API, set in production so uploaded photos resolve
    # from any host (e.g. https://backend.up.railway.app).
    public_base_url: str = ""
    # Create the admin (and, in development only, demo data) on boot when the database is empty.
    seed_on_start: bool = False
    # Drop all tables and bootstrap on boot. Ignored in production unless allow_seed_reset is also true,
    # so a forgotten flag can never wipe the live database on a restart.
    seed_reset: bool = False
    allow_seed_reset: bool = False
    jwt_secret_is_ephemeral: bool = False

    # Owner/admin login. Created on boot when seed_on_start/seed_reset is on and
    # the admin account does not exist yet. Configure via env vars in production.
    admin_email: str = "admin@staysync.dev"
    admin_password: str = "admin123"

    # SMTP for email OTP delivery. Leave smtp_host empty to print OTPs to console (dev).
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    mail_from: str = "StaySync <no-reply@staysync.local>"
    smtp_use_tls: bool = True

    # HTTPS email API (Brevo) — preferred over SMTP because Railway only allows
    # outbound web traffic (443) on Free/Hobby plans; SMTP ports are blocked.
    brevo_api_key: str = ""

    # Upload storage. "local" writes to ./uploads on disk; "supabase" uploads to
    # Supabase Storage. Set supabase_url + supabase_service_key to enable supabase.
    storage_backend: str = "local"
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_storage_bucket: str = "staysync"

    # Origins used by the Android / iOS app shells (Capacitor). Always allowed, so setting
    # CORS_ORIGINS in production can never lock the store apps out.
    native_app_origins: tuple[str, ...] = ("https://localhost", "capacitor://localhost", "http://localhost")

    @property
    def dev_mode(self) -> bool:
        """True only for an explicit local-development setup (OTP codes may be shown on screen)."""
        return self.env.strip().lower() in {"development", "dev", "local", "test", "testing"}

    @property
    def is_production(self) -> bool:
        return not self.dev_mode

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        return origins + [o for o in self.native_app_origins if o not in origins]

    @property
    def sender_name(self) -> str:
        name, _email = parse_mail_from(self.mail_from, self.smtp_user)
        return name

    @property
    def sender_email(self) -> str:
        _name, email = parse_mail_from(self.mail_from, self.smtp_user)
        return email


def parse_mail_from(value: str, fallback_email: str) -> tuple[str, str]:
    """Split a 'Name <email>' (or mangled 'Name email') string into (name, email)."""
    email = ""
    name = ""
    m = re.search(r"<([^<>]+)>", value)
    if m:
        email = m.group(1).strip()
        name = value[: m.start()].replace("<", "").replace(">", "").strip()
    else:
        tokens = value.split()
        for tok in tokens:
            if "@" in tok:
                email = tok.strip("<>(),;")
                name = " ".join(t for t in tokens if "@" not in t).strip()
                break
    if not email:
        email = fallback_email or ""
    if not name:
        name = "StaySync"
    return name or "StaySync", email


settings = Settings()

if settings.is_production and (settings.jwt_secret in WEAK_JWT_SECRETS or len(settings.jwt_secret) < 16):
    # A guessable signing key lets anyone forge admin tokens. Use a random per-process key instead of
    # booting with it (sessions end on restart until a real JWT_SECRET is configured).
    settings.jwt_secret = secrets.token_urlsafe(48)
    settings.jwt_secret_is_ephemeral = True
    print("[StaySync] WARNING: JWT_SECRET is missing or weak. Using a temporary random key; "
          "users will be signed out on every restart. Set a long random JWT_SECRET.", flush=True)
