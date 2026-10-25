import fcntl
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from main_app.management.commands.parser import get_fetcher
from main_app.management.commands.utils.parser import kamin_fetcher
from main_app.management.commands.utils.parser.runner_test import fetch_html, fetch_html_playwright
from main_app.management.commands.utils.parser.schemas import FetchResult, PriceResult


@pytest.mark.parametrize("url", [
    "https://kamin.ru/katalog/product/#options",
    "https://www.kamin.ru/katalog/product/",
    "https://KAMIN.RU/katalog/product/",
    "http://kamin.ru/katalog/product/",
])
def test_parser_routes_kamin_to_its_fetcher(url):
    assert get_fetcher(url) is kamin_fetcher.fetch_kamin


@pytest.mark.parametrize("url, expected", [
    ("https://prometall.ru/product", fetch_html_playwright),
    ("https://www.prometall.ru/product", fetch_html_playwright),
    ("https://saunaru.com/product", fetch_html_playwright),
    ("https://nkamin.ru/product", fetch_html),
    ("https://astov.ru/product", fetch_html),
    ("https://kamin.ru.example.com/product", fetch_html),
    ("https://example.com/?url=https://kamin.ru/", fetch_html),
])
def test_parser_keeps_other_sites_routing(url, expected):
    assert get_fetcher(url) is expected


@pytest.fixture
def kamin_browser(tmp_path, monkeypatch):
    monkeypatch.setattr(kamin_fetcher, "settings", SimpleNamespace(BASE_DIR=tmp_path))
    monkeypatch.delenv("KAMIN_IGNORE_HTTPS_ERRORS", raising=False)
    browser = Mock(return_value=FetchResult(status_code=200, data=PriceResult(price=130000)))
    monkeypatch.setattr(kamin_fetcher, "fetch_html_playwright", browser)
    return browser, tmp_path / "logs" / "parser_profiles" / "kamin"


def test_kamin_uses_verified_browser_settings_and_persistent_profile(kamin_browser):
    browser, profile_dir = kamin_browser
    url = "https://kamin.ru/katalog/product/#options"

    result = kamin_fetcher.fetch_kamin(url)

    assert result is browser.return_value
    assert profile_dir.is_dir()
    browser.assert_called_once_with(
        url,
        headless=False,
        virtual_display=True,
        channel="chrome",
        reduce_automation_signals=True,
        wait_timeout_ms=120_000,
        profile_dir=profile_dir,
        ignore_https_errors=True,
    )


def test_kamin_can_enable_certificate_verification(kamin_browser, monkeypatch):
    browser, _ = kamin_browser
    monkeypatch.setenv("KAMIN_IGNORE_HTTPS_ERRORS", "False")

    kamin_fetcher.fetch_kamin("https://kamin.ru/katalog/product/")

    assert browser.call_args.kwargs["ignore_https_errors"] is False


@pytest.mark.parametrize("url", [
    "https://example.com/product/",
    "https://kamin.ru.example.com/product/",
    "https://example.com/?url=https://kamin.ru/",
    "file:///kamin.ru/product/",
])
def test_kamin_rejects_other_sites_before_launching_browser(kamin_browser, url):
    browser, profile_dir = kamin_browser

    result = kamin_fetcher.fetch_kamin(url)

    assert result.status_code == 400
    assert result.data is None
    browser.assert_not_called()
    assert not profile_dir.exists()


def test_kamin_does_not_open_a_profile_in_use(kamin_browser):
    browser, profile_dir = kamin_browser
    profile_dir.parent.mkdir(parents=True)
    with (profile_dir.parent / "kamin.lock").open("a") as profile_lock:
        fcntl.flock(profile_lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

        result = kamin_fetcher.fetch_kamin("https://kamin.ru/katalog/product/")

    assert result.status_code == 503
    assert result.error_text == "kamin_profile_busy"
    assert result.data is None
    browser.assert_not_called()


def test_kamin_releases_the_profile_after_a_failed_load(kamin_browser):
    browser, profile_dir = kamin_browser
    failure = FetchResult(error_text="browser_check_timeout")
    success = FetchResult(status_code=200, data=PriceResult(price=130000))
    browser.side_effect = [failure, success]
    url = "https://kamin.ru/katalog/product/"

    assert kamin_fetcher.fetch_kamin(url) is failure
    assert kamin_fetcher.fetch_kamin(url) is success
    assert browser.call_count == 2
    assert browser.call_args.kwargs["profile_dir"] == profile_dir


def test_kamin_reports_unavailable_profile_directory(kamin_browser, monkeypatch, tmp_path):
    browser, _ = kamin_browser
    invalid_base = tmp_path / "file_instead_of_directory"
    invalid_base.write_text("test")
    monkeypatch.setattr(kamin_fetcher, "settings", SimpleNamespace(BASE_DIR=invalid_base))

    result = kamin_fetcher.fetch_kamin("https://kamin.ru/katalog/product/")

    assert result.status_code == 503
    assert result.error_text.startswith("kamin_profile_error:")
    assert result.data is None
    browser.assert_not_called()
