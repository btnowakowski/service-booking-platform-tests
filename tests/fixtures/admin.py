import os
from datetime import datetime, timedelta
import pytest


@pytest.fixture
def admin_page(page, base_url):
    """Login to admin panel."""
    page.goto(f"{base_url}/admin-panel/")
    page.wait_for_load_state("domcontentloaded", timeout=15000)

    current_url = page.url

    if "/admin-panel/" in current_url:
        page.wait_for_load_state("networkidle")
        stat_cards = page.locator(".stat-card")
        if stat_cards.count() > 0:
            return page

    login_form = page.locator("input[name='username']").first

    if login_form.is_visible():
        try:
            page.fill("input[name='username']", os.getenv("ADMIN_EMAIL"))
            page.fill("input[type='password']", os.getenv("ADMIN_PASSWORD"))
            page.get_by_role("button", name="Zaloguj").click()
            page.wait_for_url("**/admin-panel/**", timeout=15000)
            page.wait_for_load_state("networkidle")
        except Exception:
            page.screenshot(path="debug_admin_login_failed.png")
            raise

    return page


@pytest.fixture
def admin_with_test_service(admin_page):
    """Ensure a test service exists."""
    admin_page.goto(admin_page.url + "services/")
    test_service = admin_page.locator("h3", has_text="Test Service").first

    if not test_service.is_visible():
        admin_page.get_by_role("link", name="Dodaj usługę").click()
        admin_page.wait_for_load_state("networkidle")
        admin_page.fill("#id_name", "Test Service")
        admin_page.fill("#id_description", "Service for testing purposes")
        admin_page.fill("#id_price", "50")
        admin_page.fill("#id_slot_duration", "90")
        admin_page.get_by_role("button", name="Zapisz").click()

    return admin_page


@pytest.fixture
def admin_with_test_slots(admin_with_test_service):
    """Admin page with at least two slots in Test Service."""
    admin_page = admin_with_test_service
    admin_page.get_by_role("link", name="Dashboard").first.click()
    admin_page.get_by_role("link", name="Terminy").first.click()

    slots = admin_page.locator("td", has_text="Test Service")
    while slots.count() < 2:
        add_slot_btn = admin_page.get_by_role("link", name="+ Dodaj termin")
        add_slot_btn.click()
        admin_page.wait_for_load_state("networkidle")

        tomorrow = datetime.now() + timedelta(days=1)
        options = admin_page.eval_on_selector_all(
            "#id_service_select option", "opts => opts.map(o => o.value)"
        )
        last_value = options[-1]
        admin_page.select_option("#id_service_select", value=last_value)
        admin_page.fill("#id_slot_date", tomorrow.strftime("%Y-%m-%d"))
        admin_page.wait_for_timeout(500)
        admin_page.select_option("#id_slots_select", index=2)
        admin_page.get_by_role("button", name="Zapisz").click()
        admin_page.wait_for_load_state("networkidle")

    return admin_page
