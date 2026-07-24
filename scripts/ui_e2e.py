"""Exercise every PlatformPulse view in a real headless browser."""
from __future__ import annotations

from dataclasses import dataclass

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait


@dataclass(frozen=True)
class View:
    navigation: str
    heading: str


VIEWS = (
    View("Executive Overview", "Product outcome overview"),
    View("Developer Discovery", "Developer Experience Discovery"),
    View("Golden Path Generator", "Secure Self-Service Golden Path"),
    View("Service Catalogue", "Internal Service Catalogue"),
    View("Platform Metrics", "Developer Platform Metrics"),
    View("Experiment Lab", "A/B Experiment Lab"),
    View("Roadmap & Decisions", "Feedback-to-Roadmap Workflow"),
    View("AI Governance & Security", "AI Governance & Cybersecurity Control Centre"),
    View("Reliability", "Platform Reliability & Operational Action"),
)


def _options() -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1600,1200")
    options.add_argument("--disable-extensions")
    return options


def _assert_no_streamlit_error(driver: webdriver.Chrome) -> None:
    errors = driver.find_elements(By.CSS_SELECTOR, '[data-testid="stException"]')
    if errors:
        raise AssertionError("Streamlit exception rendered: " + " | ".join(error.text for error in errors))


def main() -> None:
    driver = webdriver.Chrome(options=_options())
    wait = WebDriverWait(driver, 30)
    try:
        driver.get("http://127.0.0.1:8501")
        wait.until(conditions.presence_of_element_located((By.XPATH, "//*[normalize-space()='PlatformPulse']")))
        for view in VIEWS:
            target = wait.until(
                conditions.presence_of_element_located(
                    (By.XPATH, f"//*[normalize-space()={view.navigation!r}]")
                )
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
            driver.execute_script("arguments[0].click();", target)
            wait.until(
                conditions.presence_of_element_located(
                    (By.XPATH, f"//*[self::h1 or self::h2 or self::h3][contains(normalize-space(.), {view.heading!r})]")
                )
            )
            _assert_no_streamlit_error(driver)
            print(f"PASS: {view.navigation}")
    except TimeoutException as exc:
        driver.save_screenshot("ui-e2e-failure.png")
        raise AssertionError("Timed out while navigating PlatformPulse") from exc
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
