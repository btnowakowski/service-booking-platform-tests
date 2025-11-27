import os
from pytest import mark, skip


@mark.admin
def test_admin_panel_loads(admin_page):
    """Admin login and panel load verification - prerequisite for other tests"""
    assert admin_page.url.endswith("/admin-panel/"), "Admin panel URL not correct"
    assert admin_page.locator(".stat-dot").count() > 0, "Admin panel content not loaded"


@mark.admin
def test_admin_panel_navigate_to_dashboard(admin_page):
    """Verify admin can navigate to dashboard"""
    admin_nav = admin_page.locator("a", has_text="Panel admina")
    if admin_nav.is_visible():
        admin_nav.click()
        admin_page.wait_for_load_state("networkidle")
    assert admin_page.url.endswith("/admin-panel/"), "Admin panel URL not correct"


@mark.admin
def test_admin_panel_stat_cards_visible(admin_page):
    """Verify all stat cards are visible
    datatestid attributes to check for future reference:
    [datatestid=stats-approved]
    [datatestid=stats-canceled]
    [datatestid=stats-pending]
    [datatestid=stats-all]
    """

    stat_cards = admin_page.locator(".stat-card")
    assert stat_cards.count() >= 4, "Should have at least 4 stat cards"

    expected_labels = ["Wszystkie", "Potwierdzone", "Anulowane", "Oczekujące"]
    for label in expected_labels:
        card = stat_cards.filter(has_text=label).first
        assert card.is_visible(), f"Card '{label}' not visible"


@mark.admin
def test_admin_panel_reservation_numbers_are_numeric(admin_page):
    """Verify reservation numbers are valid"""

    stat_cards = admin_page.locator(".stat-card")

    for i in range(stat_cards.count()):
        count_element = stat_cards.nth(i).locator(".fs-4")
        count_text = count_element.inner_text()
        try:
            count = int(count_text)
            assert count >= 0, f"Reservation count should not be negative: {count}"
        except ValueError:
            raise AssertionError(f"Value '{count_text}' is not a number")


@mark.admin
def test_admin_panel_stat_dots_visible(admin_page):
    """Verify status indicators are visible"""

    stat_dots = admin_page.locator(".stat-dot")
    assert stat_dots.count() >= 1, "Should have status indicators (.stat-dot)"

    for i in range(stat_dots.count()):
        dot = stat_dots.nth(i)
        assert dot.is_visible(), f"Status indicator #{i} is not visible"


@mark.admin
def test_admin_panel_pending_reservations_list(admin_page):
    """Verify pending reservations list structure"""

    pending_list = admin_page.locator(
        "ul.mb-0, [data-testid='pending-reservations-list']"
    ).first

    if not pending_list.is_visible():
        skip("Pending reservations list not visible")

    reservation_items = pending_list.locator("li.py-2")

    if reservation_items.count() == 0:
        assert (
            admin_page.locator("[data-testid='no-pending-reservations']").is_visible()
            or admin_page.locator("text=Brak oczekujących rezerwacji").is_visible()
        ), "Expected 'Brak oczekujących rezerwacji.' message"
        skip("No pending reservations available")

    # Check first reservation item structure
    first_item = reservation_items.first

    # Verify user and service name
    user_service = first_item.locator(".fw-semibold")
    assert user_service.is_visible(), "User and service name not visible"
    assert "→" in user_service.inner_text(), "Should contain arrow separator"

    # Verify timestamp
    timestamp = first_item.locator(".text-muted-2.small")
    assert timestamp.is_visible(), "Timestamp not visible"

    # Verify action buttons
    approve_button = first_item.locator("a.btn-success")
    reject_button = first_item.locator("a.btn-outline-danger")
    assert approve_button.is_visible(), "Approve button not visible"
    assert reject_button.is_visible(), "Reject button not visible"


@mark.admin
def test_admin_can_create_service(admin_with_test_service):
    """Verify admin can create a test service"""
    # Service creation is handled by fixture, just verify it exists
    assert admin_with_test_service.locator(
        "h3", has_text="Test Service"
    ).is_visible(), "Test service not found"


@mark.admin
def test_admin_can_create_slots(admin_with_test_slots):
    """Verify admin can create test slots"""
    # Slots creation is handled by fixture
    admin_with_test_slots.goto("/admin-panel/slots/")
    admin_with_test_slots.wait_for_load_state("networkidle")

    # Verify slots exist
    slots = admin_with_test_slots.locator(".slot-item, [data-testid='slot'], tr")
    assert slots.count() > 0, "No slots found"
