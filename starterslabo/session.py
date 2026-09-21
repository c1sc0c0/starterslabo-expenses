"""Browser session helpers for mijn.starterslabo.be."""

import os
import sys

from dotenv import load_dotenv
from playwright.sync_api import Browser, Page, Playwright

LOGIN_URL = "https://mijn.starterslabo.be/login.aspx"


def load_credentials() -> tuple[str, str]:
    load_dotenv()
    email = os.environ.get("STARTERSLABO_EMAIL")
    password = os.environ.get("STARTERSLABO_PASSWORD")
    if not email or not password:
        print(
            "Missing STARTERSLABO_EMAIL or STARTERSLABO_PASSWORD. "
            "Copy .env.example to .env and fill in your credentials.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return email, password


def is_headed() -> bool:
    return os.environ.get("HEADED", "").lower() in ("1", "true", "yes")


def new_page(playwright: Playwright) -> tuple[Browser, Page]:
    browser = playwright.chromium.launch(headless=not is_headed())
    return browser, browser.new_page()


def login(page: Page, email: str, password: str) -> None:
    page.goto(LOGIN_URL, wait_until="domcontentloaded")
    page.fill("#InputUsername", email)
    page.fill("#InputPassword", password)
    page.click("#BtnSubmit")
    page.wait_for_url(lambda url: "login.aspx" not in url.lower(), timeout=30_000)
    if "login.aspx" in page.url.lower():
        raise RuntimeError(f"Login failed; still on {page.url}")
