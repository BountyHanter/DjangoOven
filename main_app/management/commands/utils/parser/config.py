from dataclasses import dataclass

@dataclass(frozen=True)
class HttpConfig:
    request_timeout: int = 25


@dataclass(frozen=True)
class DelayConfig:
    min_delay: float = 5.0
    max_delay: float = 7.0


@dataclass(frozen=True)
class AntiBlockConfig:
    max_403_streak: int = 5
    cooldown_seconds: int = 60
    post_cooldown_limit: int = 3


@dataclass(frozen=True)
class ParserConfig:
    task_limit: int | None = None
    delay: DelayConfig = DelayConfig()
    http: HttpConfig = HttpConfig()
    antiblock: AntiBlockConfig = AntiBlockConfig()


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

API_HEADERS = {
    "User-Agent": HEADERS["User-Agent"],
    "Accept": "application/json",
}

PLAYWRIGHT_DOMAINS = {
    "prometall.ru",
    "saunaru.com",
}