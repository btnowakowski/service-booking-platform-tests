# service_booking_platform_tests

## Raport testów E2E - Github Actions, Github Pages, Allure

Aktualny raport: [zobacz tutaj](https://btnowakowski.github.io/service-booking-platfrom-tests/)

## Uruchamianie testów lokalnie

Domyślnie testy odpalają się przeciwko lokalnej instancji (`http://127.0.0.1:8000`).

1. Uruchom aplikację lokalnie ([Skorzystaj z README w repozytorium aplikacji](https://github.com/btnowakowski/mvc_projekt_semestralny)).
2. Uruchom testy i otwórz raport za pomocą poleceń:

```bash
pytest
allure generate allure-results -o allure-report --clean
allure serve allure-results
```
