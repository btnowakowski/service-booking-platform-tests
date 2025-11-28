# service_booking_platform_tests

## Tech Stack
- Python
- Playwright
- Pytest
- Allure

## E2E Test Report - Github Actions, Github Pages, Allure

Latest Report: [Check it out](https://btnowakowski.github.io/service-booking-platform-tests/)

The report will generate screenshots and reproduction videos in case of failure i.e.
<img width="1837" height="895" alt="image" src="https://github.com/user-attachments/assets/9476a584-3473-4ef5-954b-9585ecc0255c" />
## Project Structure

```text
tests/
  data/
    admin.py       # selectors & expected content for admin panel
    auth.py        # UI labels and selectors for auth flow
    booking.py     # booking-related UI data
    pages.py       # homepage expectations (title, headings, nav)
    services.py    # test service data
    users.py       # UserCredentials + generate_test_user()
  fixtures/
    admin.py       # admin_page, admin_page_with_test_service, admin_page_with_test_slots
    auth.py        # auth-related fixtures
    booking.py     # booked_slot_info and related booking setup
  helpers/
    admin.py       # admin panel actions and queries
    auth.py        # register_user, login_user, logout_user, is_user_logged_in
    booking.py     # get_pending_reservations and related helpers
    home.py        # homepage-specific helpers
    navigation.py  # navigation helpers (e.g. navigate_to_my_bookings)
  test_admin_panel.py
  test_auth.py
  test_booking_flow.py
  test_smoke_home.py

conftest.py         # Playwright setup, global fixtures, Allure hooks, safety guard
pytest.ini          # pytest configuration and markers
requirements.txt    # test dependencies
.github/workflows/
  main.yml          # CI pipeline: run tests + publish Allure report
```

## What is covered

This suite currently covers:

- **Homepage smoke check**  
  - `tests/test_smoke_home.py`  
  - Verifies that the homepage loads correctly, title matches expectation and key navigation elements are visible.

- **User authentication**  
  - `tests/test_auth.py`  
  - Marked with `@pytest.mark.registration`  
  - Scenarios:
    - New user can register and is automatically logged in.
    - User can log out and log back in with the same credentials.

- **Booking flow (user side)**  
  - `tests/test_booking_flow.py`  
  - Marked with `@pytest.mark.booking`  
  - Scenarios:
    - User can book a slot.
    - Booked slot appears in the list of pending reservations (`navigate_to_my_bookings` + verification in `get_pending_reservations`).

- **Admin panel**  
  - `tests/test_admin_panel.py`  
  - Marked with `@pytest.mark.admin` (for admin-specific scenarios)  
  - Scenarios:
    - Admin panel structure and statistics cards.
    - Pending reservations list (structure and content).
    - Creating services and verifying that a test service appears.
    - Creating slots for a service and verifying they appear in the admin UI.  

These tests use shared helpers and test data abstractions to keep scenarios readable and maintainable.  

## Running tests locally

By default set to run on (`http://127.0.0.1:8000`).  

1. Get the app to run locally ([Use README of the Booking Platform](https://github.com/btnowakowski/service-booking-platform)).
2. Install dependencies
```bash
pip install -r requirements.txt
```  
3. Run tests and generate your report using:

```bash
pytest
allure generate allure-results -o allure-report --clean
allure serve allure-results
```
## Usage examples  

@pytest.mark.registration – tests that create new user accounts.  

@pytest.mark.booking – tests verifying booking flows.  

@pytest.mark.admin – tests that operate in the admin panel.  

You can easily run a subset of tests by marker, for example:  
```bash
pytest -m admin
pytest -m registration
pytest -m booking
```
