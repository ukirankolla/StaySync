"""Sample ("demo") profiles use reserved example.com addresses, which can never belong to a real person."""


def is_demo_email(email: str | None) -> bool:
    return bool(email) and email.lower().endswith("@example.com")


DEMO_PREFIX = "Demo reply: "


def demo_reply(peer_name: str, text: str, city: str | None, n: int) -> str:
    """Clearly labelled sample reply so a demo conversation works. Not a real person; not AI-generated."""
    t = (text or "").lower()
    first = (peer_name or "").split(" ")[0] or "there"
    if any(w in t for w in ("rent", "budget", "price", "cost")):
        body = f"Budget-wise I'm flexible within my range. Let's compare what we each can pay{f' in {city}' if city else ''}."
    elif any(w in t for w in ("visit", "see", "view", "meet", "flat", "room")):
        body = "I'd be happy to view a place together this weekend. Which area works for you?"
    elif any(w in t for w in ("sleep", "wake", "clean", "smok", "drink", "veg", "habit", "routine")):
        body = "Our lifestyle answers looked close, so that's a good sign. What matters most to you in a roommate?"
    elif any(w in t for w in ("hi", "hello", "hey")) and len(t) < 40:
        body = f"Hi! This is {first}. Nice to connect. What are you looking for in a flat?"
    else:
        body = ["Thanks for reaching out! Tell me a bit more about your routine.",
                "Sounds good. When are you planning to move in?",
                "Great. Shall we shortlist a few areas and compare?"][n % 3]
    return f"{DEMO_PREFIX}{body} (Sample message from a demo profile; no real person is replying.)"
