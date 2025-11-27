import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import allure

load_dotenv()

# Rejestracja fixture'ów z podkatalogów
pytest_plugins = [
    "tests.fixtures.auth",
    "tests.fixtures.booking",
    "tests.fixtures.admin",
]

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
ARTIFACTS_DIR = Path("artifacts")
SCREENSHOTS_DIR = ARTIFACTS_DIR / "screenshots"
VIDEOS_DIR = ARTIFACTS_DIR / "videos"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def setup_timezone():
    os.environ["TZ"] = "Europe/Warsaw"


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("BASE_URL", DEFAULT_BASE_URL).rstrip("/")


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture(autouse=True)
def clear_browser_storage(page):
    yield
    page.context.clear_cookies()


@pytest.fixture
def page(browser, base_url, request):
    ctx = browser.new_context(
        timezone_id="Europe/Warsaw",
        base_url=base_url,
        record_video_dir=str(VIDEOS_DIR),
        record_video_size={"width": 1280, "height": 720},
    )
    page = ctx.new_page()
    yield page

    test_name = request.node.name
    rep = getattr(request.node, "rep_call", None)
    failed = rep is not None and rep.failed
    video = getattr(page, "video", None)

    if failed:
        screenshot_path = SCREENSHOTS_DIR / f"{test_name}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        with open(screenshot_path, "rb") as f:
            allure.attach(
                f.read(), name=f"{test_name} - screenshot", attachment_type="image/png"
            )

    ctx.close()

    if video is not None:
        try:
            video_path = video.path()
        except Exception:
            video_path = None
        if video_path and failed:
            with open(video_path, "rb") as f:
                allure.attach(
                    f.read(), name=f"{test_name} - video", attachment_type="video/webm"
                )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(scope="session", autouse=True)
def guard_against_unintentional_prod(base_url):
    if base_url.startswith("https://") or "accommodations" in base_url:
        allow = os.getenv("ALLOW_PROD_TESTS") == "1"
        if not allow:
            pytest.exit("Production tests are blocked.", returncode=1)
