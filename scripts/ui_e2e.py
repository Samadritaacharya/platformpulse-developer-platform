"""Exercise every PlatformPulse view and the golden-path workflow in Chrome."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
import zipfile

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait

DOWNLOAD_DIR = Path("/tmp/platformpulse-ui-downloads")


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
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1600,1200")
    options.add_argument("--disable-extensions")
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(DOWNLOAD_DIR),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )
    return options


def _assert_no_streamlit_error(driver: webdriver.Chrome) -> None:
    errors = driver.find_elements(By.CSS_SELECTOR, '[data-testid="stException"]')
    if errors:
        raise AssertionError("Streamlit exception rendered: " + " | ".join(error.text for error in errors))


def _button(driver: webdriver.Chrome, wait: WebDriverWait, label: str):
    xpath = f"//button[normalize-space(.)={label!r} or .//*[normalize-space()={label!r}]]"
    element = wait.until(conditions.presence_of_element_located((By.XPATH, xpath)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    return element


def _test_golden_path(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    build = _button(driver, wait, "Build secure starter")
    driver.execute_script("arguments[0].click();", build)
    wait.until(
        conditions.presence_of_element_located(
            (By.XPATH, "//*[contains(normalize-space(.), 'Secure starter generated for catalog-insights-api')]")
        )
    )
    download = _button(driver, wait, "Download secure starter ZIP")
    driver.execute_script("arguments[0].click();", download)
    deadline = time.monotonic() + 20
    archive_path: Path | None = None
    while time.monotonic() < deadline:
        completed = [path for path in DOWNLOAD_DIR.glob("*.zip") if not path.name.endswith(".crdownload")]
        if completed:
            archive_path = completed[0]
            break
        time.sleep(.5)
    if archive_path is None:
        raise AssertionError("Secure starter ZIP was not downloaded")
    with zipfile.ZipFile(archive_path) as archive:
        names = set(archive.namelist())
        required = {
            "catalog-insights-api/app/main.py",
            "catalog-insights-api/tests/test_health.py",
            "catalog-insights-api/Dockerfile",
            "catalog-insights-api/kubernetes/deployment.yaml",
            "catalog-insights-api/service-catalog.yaml",
        }
        missing = required.difference(names)
        if missing:
            raise AssertionError(f"Downloaded starter is missing: {sorted(missing)}")
    print("PASS: Golden Path form, generation, download and archive validation")


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
            if view.navigation == "Golden Path Generator":
                _test_golden_path(driver, wait)
                _assert_no_streamlit_error(driver)
    except (TimeoutException, AssertionError, zipfile.BadZipFile) as exc:
        driver.save_screenshot("ui-e2e-failure.png")
        raise AssertionError("Browser end-to-end validation failed") from exc
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
