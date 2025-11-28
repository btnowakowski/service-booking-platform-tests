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


## Running tests locally

By default set to run on (`http://127.0.0.1:8000`).

1. Get the app to run locally ([Use README of the Booking Platform](https://github.com/btnowakowski/service-booking-platform)).
2. Run tests and generate your report using:

```bash
pytest
allure generate allure-results -o allure-report --clean
allure serve allure-results
```
