import socket

from fastapi import APIRouter

from ..config import settings

router = APIRouter(tags=["debug"])


def _try_connect(host: str, port: int, family: int | None = None, timeout: float = 10) -> str:
    try:
        if family is None:
            sock = socket.create_connection((host, port), timeout=timeout)
        else:
            infos = socket.getaddrinfo(host, port, family=family, type=socket.SOCK_STREAM)
            sock = socket.socket(infos[0][0], infos[0][1])
            sock.settimeout(timeout)
            sock.connect(infos[0][4])
        sock.close()
        return "CONNECTED"
    except Exception as exc:  # noqa: BLE001
        return f"{type(exc).__name__}: {exc}"


@router.get("/debug/network")
def debug_network():
    try:
        addrinfo = socket.getaddrinfo(settings.smtp_host or "smtp.gmail.com", settings.smtp_port or 587)
        addrinfo = [(a[0].name, a[4]) for a in addrinfo[:8]]
    except Exception as exc:  # noqa: BLE001
        addrinfo = f"getaddrinfo error: {type(exc).__name__}: {exc}"

    host = settings.smtp_host or "smtp.gmail.com"
    port = settings.smtp_port or 587
    return {
        "smtp_host": settings.smtp_host,
        "smtp_port": settings.smtp_port,
        "smtp_user": settings.smtp_user,
        "mail_from": settings.mail_from,
        "env": settings.env,
        "addrinfo": addrinfo,
        "connect_default": _try_connect(host, port),
        "connect_ipv4": _try_connect(host, port, family=socket.AF_INET),
        "connect_ipv6": _try_connect(host, port, family=socket.AF_INET6),
        "connect_443_google": _try_connect("www.google.com", 443),
    }
