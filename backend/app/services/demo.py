"""Sample ("demo") profiles use reserved example.com addresses, which can never belong to a real person."""


def is_demo_email(email: str | None) -> bool:
    return bool(email) and email.lower().endswith("@example.com")
