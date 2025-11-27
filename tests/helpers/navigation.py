from playwright.sync_api import Page


def navigate_to_services(page: Page):
    """Navigate to services page."""
    services_link = page.get_by_role("link", name="Usługi")
    services_link.wait_for(state="visible")
    services_link.click()
    page.wait_for_load_state("networkidle")


def select_first_service(page: Page):
    """Select the first service from the list."""
    first_service_link = page.get_by_role("link", name="Zobacz terminy").first
    first_service_link.wait_for(state="visible")
    first_service_link.click()
    page.wait_for_load_state("networkidle")


def navigate_to_my_bookings(page: Page):
    """Navigate to 'My Reservations' page."""
    my_bookings_link = page.get_by_role("link", name="Moje rezerwacje")
    my_bookings_link.wait_for(state="visible")
    my_bookings_link.click()
    page.wait_for_load_state("networkidle")
