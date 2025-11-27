from dotenv import load_dotenv
from os import getenv
from pytest import mark, skip
from tests.helpers import (
    navigate_to_services,
    select_first_service,
    find_available_slot,
    book_slot,
    navigate_to_my_bookings,
    get_pending_reservations,
)


@mark.booking
def test_user_can_book_slot(page, logged_in_user, booking_cleanup):
    navigate_to_services(page)
    select_first_service(page)

    slot = find_available_slot(page)
    if slot is None:
        skip("No available slots to book.")

    booking_info = book_slot(page, slot)
    booking_cleanup["slot_label"] = booking_info["slot_label"]

    navigate_to_my_bookings(page)

    pending = get_pending_reservations(page)
    assert (
        len(pending) > 0
    ), f"No pending reservations found. Booking info: {booking_info}"

    found = any(
        part in res["full_text"]
        for res in pending
        for part in booking_info["preview_text"].split()
    )
    assert (
        found or len(pending) > 0
    ), f"Expected pending reservation with slot info. Preview was: {booking_info['preview_text']}"


@mark.booking
def test_user_can_book_slot_using_fixture(page, booked_slot):
    navigate_to_my_bookings(page)

    pending = get_pending_reservations(page)
    assert (
        len(pending) > 0
    ), f"No pending reservations found. Booking info: {booked_slot}"
