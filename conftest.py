import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import allure

load_dotenv()

DEFAULT_BASE_URL = "http://127.0.0.1:8000"

ARTIFACTS_DIR = Path("artifacts")
SCREENSHOTS_DIR = ARTIFACTS_DIR / "screenshots"
VIDEOS_DIR = ARTIFACTS_DIR / "videos"

SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def setup_timezone():
    """Ustaw strefę czasową dla testów."""
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


@pytest.fixture
def page(browser, base_url, request):
    """
    Every test gets a fresh browser context and page.
    Records video and takes screenshot on failure.
    """
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

    # Screenshot when test failed
    if failed:
        screenshot_path = SCREENSHOTS_DIR / f"{test_name}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)

        with open(screenshot_path, "rb") as f:
            allure.attach(
                f.read(),
                name=f"{test_name} - screenshot",
                attachment_type="image/png",
            )

    # Close context to finalize video
    ctx.close()

    # Attach video when test failed
    if video is not None:
        try:
            video_path = video.path()
        except Exception:
            video_path = None

        if video_path and failed:
            with open(video_path, "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"{test_name} - video",
                    attachment_type="video/webm",
                )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture
def booking_cleanup(page, request):
    cleanup_data = {"slot_label": None}
    yield cleanup_data
    label = cleanup_data.get("slot_label")
    debug_log = []
    if not label:
        allure.attach(
            "No slot_label set, skipping cleanup",
            name="cleanup_log",
            attachment_type="text/plain",
        )
        return
    SHORT = 3000
    try:
        matched = page.locator(".res-card")
        current_count = matched.count()
        if current_count == 0:
            allure.attach(
                "No cards found, returning",
                name="cleanup_log",
                attachment_type="text/plain",
            )
            return
        booking_to_cancel = matched.filter(has_text="Oczekująca")
        before_count = booking_to_cancel.count()
        if before_count == 0:
            allure.attach(
                "No pending bookings found",
                name="cleanup_log",
                attachment_type="text/plain",
            )
            return
        first_pending = booking_to_cancel.first
        try:
            cancel_button = first_pending.locator("a.btn-outline-danger")
            cancel_button.wait_for(state="visible", timeout=SHORT)
            with page.expect_navigation(wait_until="networkidle", timeout=SHORT):
                cancel_button.click(timeout=SHORT)

            # Make sure page is loaded
            page.wait_for_load_state("networkidle")
            # Hard reload to avoid caching issues
            matched_after = page.locator(".res-card").filter(has_text="Oczekująca")
            after_count = matched_after.count()
            if after_count == before_count:
                page.reload(wait_until="networkidle")
                matched_after = page.locator(".res-card").filter(has_text="Oczekująca")
                after_count = matched_after.count()

            # Retry a couple of times if count didn't change
            retries = 2
            while after_count == before_count and retries > 0:
                page.wait_for_timeout(500)
                matched_after = page.locator(".res-card").filter(has_text="Oczekująca")
                after_count = matched_after.count()
                retries -= 1

            # Final assertion to ensure cleanup worked
            assert (before_count == 0) or (
                after_count < before_count
            ), f"Cleanup failed: pending count not decreased (before={before_count}, after={after_count})"
        except Exception as e:
            debug_log.append(f"Error clicking cancel: {e}")
    except Exception as e:
        debug_log.append(f"Error during cleanup: {e}")
        import traceback

        debug_log.append(traceback.format_exc())
    if debug_log:
        allure.attach(
            "\n".join(debug_log), name="cleanup_log", attachment_type="text/plain"
        )


@pytest.fixture(scope="session", autouse=True)
def guard_against_unintentional_prod(base_url):
    """
    Safeguard to prevent running tests in production
    """
    if base_url.startswith("https://") or "accommodations" in base_url:
        allow = os.getenv("ALLOW_PROD_TESTS") == "1"
        if not allow:
            pytest.exit(
                "Testy na produkcji są zablokowane. ",
                returncode=1,
            )
