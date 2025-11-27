import os
import pytest
from tests.helpers.auth import login_user


@pytest.fixture
def logged_in_user(page):
    """Fixture: logged in test user."""
    username = os.getenv("TEST_USER_EMAIL")
    password = os.getenv("TEST_USER_PASSWORD")
    if not username or not password:
        pytest.skip("Missing TEST_USER_EMAIL / TEST_USER_PASSWORD in env")
    login_user(page, username, password)
    return {"username": username, "page": page}
