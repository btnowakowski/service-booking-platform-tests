import pytest
from tests.helpers.navigation import navigate_to_services, select_first_service
from tests.helpers.booking import find_available_slot, book_slot


@pytest.fixture
def booking_cleanup(page):
    """Cleanup: cancel pending reservations after test."""
    cleanup_data = {}
    yield cleanup_data
    try:
        pending = page.locator(".res-card").filter(has_text="Oczekująca")
        if pending.count() == 0:
            return
        cancel_btn = pending.first.locator("a.btn-outline-danger")
        if cancel_btn.is_visible():
            cancel_btn.click()
            page.wait_for_load_state("networkidle")
    except Exception:
        pass


@pytest.fixture
def booked_slot(page, logged_in_user, booking_cleanup):
    """Fixture: prepare a booked slot. Returns dict with booking info."""
    navigate_to_services(page)
    select_first_service(page)

    slot = find_available_slot(page)
    if slot is None:
        pytest.skip("No available slots to book.")

    booking_info = book_slot(page, slot)
    booking_cleanup["slot_label"] = booking_info["slot_label"]

    return booking_info
