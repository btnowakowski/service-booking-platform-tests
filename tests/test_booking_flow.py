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
    # Saving service name for later verification
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

    while True:
        free_slots = page.locator(".fc-event:visible")
        if free_slots.count() > 0:
            break
        next_week_button = page.locator(".fc-next-button")
        next_week_button.click()
        page.wait_for_load_state("networkidle")

    free_slot = page.locator(".fc-event:visible").first
    free_slot.wait_for(state="visible")

    # Saving slot label for later verification
    slot_label = free_slot.inner_text().strip()[
        :5  # First 5 chars to identify the slot
    ]
    free_slot.click()
    booking_cleanup["slot_label"] = (
        free_slot.inner_text().strip()
    )  # Full label for cleanup
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
    # We are looking for a row that contains both the slot label and the status "Oczekująca"
    rows = page.locator(".res-card")
    rows.first.wait_for(state="visible")

    matched = page.locator(".res-card:visible")

    count = matched.count()  # Ensure the locator is evaluated

    # Cache inner_text() results to avoid redundant DOM queries
    cached_date_texts = [
        matched.locator(".res-meta").nth(i).inner_text() for i in range(count)
    ]
    cached_status_texts = [
        matched.locator(".res-badge").nth(i).inner_text() for i in range(count)
    ]
    """
    This dictionary maps timeslots (with their indices) to their statuses, 
    allowing for easier debugging and verification of reservations.
    """
    timeslots_with_status = {
        (
            i,
            " ".join(cached_date_texts[i].split(" ")[1:3]),
        ): cached_status_texts[i]
        for i in range(count)
    }

    assert (
        timeslots_with_status.__len__() == count
    ), f"Expected {count} unique reservations, but found {timeslots_with_status.__len__()}: {timeslots_with_status.__repr__()} - there might be duplicate timeslots."
    assert (
        matched.filter(has_text=slot_label).count() > 0
    ), f"Couldn't find the reservation for '{slot_label}' - found {timeslots_with_status.__repr__()}"
    assert (
        matched.filter(has_text="Oczekująca").count() > 0
    ), f"Couldn't find any reservation with pending status - found {timeslots_with_status.__repr__()}"
    assert (
        matched.filter(has_text="Oczekująca").filter(has_text=slot_label).count() > 0
    ), f"Couldn't find the reservation for '{slot_label}' with pending status. Found statuses with the timeslot: {timeslots_with_status.get(slot_label, 'None')}"
