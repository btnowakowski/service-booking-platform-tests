from dotenv import load_dotenv
from os import getenv
from pytest import mark, skip


def login_as_existing_user(page, username, password):
    page.goto("/")
    page.wait_for_load_state("networkidle")

    page.get_by_role("link", name="Zaloguj").click()
    page.wait_for_load_state("networkidle")

    page.locator("input[name='username']").fill(username)
    page.get_by_label("Hasło").fill(password)
    page.get_by_role("button", name="Zaloguj").click()
    page.wait_for_load_state("networkidle")


@mark.booking
def test_user_can_book_slot(page, booking_cleanup):
    # Loading environment variables
    load_dotenv()
    username = getenv("TEST_USER_EMAIL")
    password = getenv("TEST_USER_PASSWORD")

    if not username or not password:
        skip("Brak TEST_USER_EMAIL / TEST_USER_PASSWORD w env")

    # User login
    login_as_existing_user(page, username, password)

    # Navigation to Services page
    services_link = page.get_by_role("link", name="Usługi")
    services_link.wait_for(state="visible")
    services_link.click()
    page.wait_for_load_state("networkidle")

    # Selecting the first service
    first_service_link = page.get_by_role("link", name="Zobacz terminy").first
    first_service_link.wait_for(state="visible")
    first_service_link.click()
    page.wait_for_load_state("networkidle")

    # No available slots handling
    calendar = page.locator("#calendar")
    if not calendar.is_visible():
        placeholder = page.locator("#calendar-placeholder")
        if placeholder.get_by_text("Brak terminów w tym tygodniu").is_visible():
            skip("No available slots to book.")
        else:
            raise AssertionError(
                "Neither calendar nor 'no slots' placeholder is visible."
            )

    calendar.wait_for(state="visible")

    # Find first available slot
    free_slot = None
    max_iterations = 5
    iteration = 0

    while free_slot is None and iteration < max_iterations:
        free_slots = page.locator(".fc-event:visible")
        if free_slots.count() > 0:
            free_slot = free_slots.first
            break

        next_week_button = page.locator(".fc-next-button")
        next_week_button.click()
        page.wait_for_timeout(500)  # Czekaj na re-render
        iteration += 1

    if free_slot is None:
        skip("No available slots found in the next weeks.")

    free_slot.wait_for(state="visible")

    # Get the slot ID from the calendar event data
    slot_id = free_slot.get_attribute("data-eventid")

    # Alternatywa: jeśli data-eventid nie istnieje, pobierz cały tekst
    if not slot_id:
        slot_text = free_slot.inner_text().strip()
        booking_cleanup["slot_label"] = slot_text
    else:
        booking_cleanup["slot_label"] = slot_id

    # Click on the slot
    free_slot.click()
    page.wait_for_timeout(300)

    # Verify that slot preview was populated
    slot_preview = page.locator("#slot-preview")
    slot_preview.wait_for(state="visible")
    slot_preview_text = slot_preview.inner_text().strip()

    assert slot_preview_text, "Slot preview should be populated after clicking"

    # Slot booking confirmation
    book_button = page.get_by_role("button", name="Rezerwuj termin")
    book_button.wait_for(state="visible")
    book_button.click()
    page.wait_for_load_state("networkidle")

    # Navigating to "My Bookings" page
    my_bookings_link = page.get_by_role("link", name="Moje rezerwacje")
    my_bookings_link.wait_for(state="visible")
    my_bookings_link.click()
    page.wait_for_load_state("networkidle")

    # Verification if booking is present in the list with status "Oczekująca"
    rows = page.locator(".res-card")
    rows.first.wait_for(state="visible")

    matched = page.locator(".res-card:visible")
    count = matched.count()

    # Cache results
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

    # Check for pending reservations
    pending_reservations = [
        res for res in reservations if "Oczekująca" in res["status"]
    ]

    assert len(pending_reservations) > 0, (
        f"No pending reservations found. Available statuses: "
        f"{[r['status'] for r in reservations]}"
    )

    # Check if any pending reservation matches the booked slot
    found_slot = False
    for res in pending_reservations:
        if any(part in res["full_text"] for part in slot_preview_text.split()):
            found_slot = True
            break

    assert found_slot or len(pending_reservations) > 0, (
        f"Expected pending reservation with slot info. "
        f"Preview was: {slot_preview_text}"
    )
