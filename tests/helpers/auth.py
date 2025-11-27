from playwright.sync_api import Page


def login_user(page: Page, username: str, password: str):
    """Log in user via login form."""
    page.goto("/")
    page.wait_for_load_state("networkidle")
    page.get_by_role("link", name="Zaloguj").click()
    page.wait_for_load_state("networkidle")
    page.locator("input[name='username']").fill(username)
    page.get_by_label("Hasło").fill(password)
    page.get_by_role("button", name="Zaloguj").click()
    page.wait_for_load_state("networkidle")
