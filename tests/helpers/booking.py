from playwright.sync_api import Page


def find_available_slot(page: Page, max_weeks: int = 5):
    """Find first available slot in calendar. Returns locator or None."""
    calendar = page.locator("#calendar")
    if not calendar.is_visible():
        placeholder = page.locator("#calendar-placeholder")
        if placeholder.get_by_text("Brak terminów w tym tygodniu").is_visible():
            return None
        raise AssertionError("Neither calendar nor 'no slots' placeholder is visible.")

    calendar.wait_for(state="visible")

    for _ in range(max_weeks):
        free_slots = page.locator(".fc-event:visible")
        if free_slots.count() > 0:
            return free_slots.first
        next_week_button = page.locator(".fc-next-button")
        next_week_button.click()
        page.wait_for_timeout(500)

    return None


def book_slot(page: Page, slot_locator) -> dict:
    """Book the selected slot. Returns dict with booking info."""
    slot_locator.wait_for(state="visible")
    slot_id = slot_locator.get_attribute("data-eventid")
    slot_text = slot_locator.inner_text().strip()

    slot_locator.click()
    page.wait_for_timeout(300)

    slot_preview = page.locator("#slot-preview")
    slot_preview.wait_for(state="visible")
    slot_preview_text = slot_preview.inner_text().strip()

    book_button = page.get_by_role("button", name="Rezerwuj termin")
    book_button.wait_for(state="visible")
    book_button.click()
    page.wait_for_load_state("networkidle")

    return {
        "slot_id": slot_id,
        "slot_text": slot_text,
        "slot_label": slot_id or slot_text,
        "preview_text": slot_preview_text,
    }


def get_reservations(page: Page) -> list[dict]:
    """Get list of reservations from 'My Reservations' page."""
    rows = page.locator(".res-card")
    if rows.count() == 0:
        return []
    rows.first.wait_for(state="visible")

    matched = page.locator(".res-card:visible")
    count = matched.count()

    reservations = []
    for i in range(count):
        res_meta = matched.locator(".res-meta").nth(i).inner_text()
        res_badge = matched.locator(".res-badge").nth(i).inner_text()
        reservations.append(
            {
                "index": i,
                "meta": res_meta,
                "status": res_badge,
                "full_text": matched.nth(i).inner_text(),
            }
        )
    return reservations


def get_pending_reservations(page: Page) -> list[dict]:
    """Get only pending reservations."""
    reservations = get_reservations(page)
    return [r for r in reservations if "Oczekująca" in r["status"]]
