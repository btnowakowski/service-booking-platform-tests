# service_booking_platform_tests

## Tech Stack
- Python
- Playwright
- Pytest
- Allure

## E2E Test Report - Github Actions, Github Pages, Allure

Latest Report: [Check it out](https://btnowakowski.github.io/service-booking-platform-tests/)

## Running tests locally

By default set to run on (`http://127.0.0.1:8000`).

1. Get the app to run locally ([Use README of the Booking Platform](https://github.com/btnowakowski/service-booking-platform)).
2. Run tests and generate your report using:

```bash
pytest
allure generate allure-results -o allure-report --clean
allure serve allure-results
```
