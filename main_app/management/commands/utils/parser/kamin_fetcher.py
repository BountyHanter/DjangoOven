"""Загрузчик kamin.ru с параметрами, проверенными в runner_test.py."""

import fcntl
import logging
import os
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings

from main_app.management.commands.utils.parser.runner_test import fetch_html_playwright
from main_app.management.commands.utils.parser.schemas import FetchResult


logger = logging.getLogger("main_app.management.commands.parser")
KAMIN_DOMAINS = frozenset({"kamin.ru", "www.kamin.ru"})


def fetch_kamin(url: str) -> FetchResult:
    """Загружает товар, сохраняя профиль между запусками контейнера."""
    target = urlparse(url)
    if target.scheme not in {"http", "https"} or target.hostname not in KAMIN_DOMAINS:
        return FetchResult(status_code=400, error_text="unsupported_kamin_url")

    profile_dir = Path(settings.BASE_DIR) / "logs" / "parser_profiles" / "kamin"
    # Совпадает с рабочим тестом; отключается после исправления сертификата сайта.
    ignore_https_errors = os.getenv("KAMIN_IGNORE_HTTPS_ERRORS", "True").strip().lower() in {
        "true", "1", "yes", "y",
    }

    try:
        profile_dir.mkdir(parents=True, exist_ok=True)
        # Chrome не допускает одновременного открытия одного профиля.
        # Lock находится рядом с профилем и освобождается при закрытии файла.
        with (profile_dir.parent / "kamin.lock").open("a") as profile_lock:
            try:
                fcntl.flock(profile_lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                logger.warning("Профиль kamin.ru занят другим запуском: %s", url)
                return FetchResult(status_code=503, error_text="kamin_profile_busy")

            return fetch_html_playwright(
                url,
                headless=False,
                virtual_display=True,
                channel="chrome",
                reduce_automation_signals=True,
                wait_timeout_ms=120_000,
                profile_dir=profile_dir,
                ignore_https_errors=ignore_https_errors,
            )
    except OSError as exc:
        logger.error("Ошибка профиля kamin.ru для URL %s: %s", url, exc)
        return FetchResult(status_code=503, error_text=f"kamin_profile_error: {exc}")
