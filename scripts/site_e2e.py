"""Exercise the static PlatformPulse website in a real headless Chrome browser."""
from __future__ import annotations

from pathlib import Path
import tempfile
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import Select, WebDriverWait

DOWNLOAD_DIR = Path(tempfile.gettempdir()) / "platformpulse-site-downloads"


def _options() -> webdriver.ChromeOptions:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for path in DOWNLOAD_DIR.glob("*"):
        if path.is_file():
            path.unlink()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1600,1200")
    options.add_argument("--disable-extensions")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
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


def _click_tab(driver: webdriver.Chrome, wait: WebDriverWait, tab_id: str, panel_id: str) -> None:
    tab = wait.until(conditions.element_to_be_clickable((By.ID, tab_id)))
    driver.execute_script("arguments[0].click();", tab)
    panel = wait.until(conditions.visibility_of_element_located((By.ID, panel_id)))
    assert panel.get_attribute("hidden") is None


def _set_range(driver: webdriver.Chrome, element_id: str, value: int) -> None:
    element = driver.find_element(By.ID, element_id)
    driver.execute_script(
        "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles:true}));",
        element,
        value,
    )


def _set_text(driver: webdriver.Chrome, element_id: str, value: str) -> None:
    element = driver.find_element(By.ID, element_id)
    driver.execute_script(
        "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles:true}));",
        element,
        value,
    )


def _wait_for_download(filename: str) -> Path:
    deadline = time.monotonic() + 15
    expected = DOWNLOAD_DIR / filename
    while time.monotonic() < deadline:
        if expected.exists() and not (DOWNLOAD_DIR / f"{filename}.crdownload").exists():
            return expected
        time.sleep(0.25)
    raise AssertionError(f"Expected download was not created: {filename}")


def _assert_no_browser_errors(driver: webdriver.Chrome) -> None:
    ignored_fragments = ("favicon.ico",)
    severe = [
        entry["message"]
        for entry in driver.get_log("browser")
        if entry.get("level") == "SEVERE"
        and not any(fragment in entry.get("message", "") for fragment in ignored_fragments)
    ]
    if severe:
        raise AssertionError("Browser console errors: " + " | ".join(severe))


def main() -> None:
    driver = webdriver.Chrome(options=_options())
    wait = WebDriverWait(driver, 20)
    try:
        driver.get("http://127.0.0.1:8080")
        wait.until(conditions.title_contains("PlatformPulse"))
        wait.until(lambda browser: browser.find_element(By.CSS_SELECTOR, "[data-counter='82']").text == "82")

        _click_tab(driver, wait, "tab-discovery", "panel-discovery")
        Select(driver.find_element(By.ID, "persona")).select_by_value("platform")
        wait.until(
            conditions.text_to_be_present_in_element(
                (By.ID, "persona-insight-title"), "Platform fragmentation and support toil"
            )
        )
        journey_values = [int(item.get_attribute("value")) for item in driver.find_elements(By.CSS_SELECTOR, "#journey-bars progress")]
        assert journey_values == [54, 65, 78, 84, 71]

        _click_tab(driver, wait, "tab-golden", "panel-golden")
        _set_text(driver, "service-name", "catalog_api<script>")
        _set_text(driver, "team-name", "marketplace:platform/unsafe")
        preview = driver.find_element(By.ID, "manifest-preview").text
        assert "<script>" not in preview
        assert "owner: marketplaceplatformunsafe" in preview
        submit = driver.find_element(By.CSS_SELECTOR, "#manifest-form button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", submit)
        wait.until(conditions.text_to_be_present_in_element((By.ID, "manifest-status"), "Downloaded"))
        _wait_for_download("catalog-api-script-service-catalog.yaml")

        _click_tab(driver, wait, "tab-experiment", "panel-experiment")
        _set_range(driver, "control-rate", 45)
        _set_range(driver, "treatment-rate", 70)
        _set_range(driver, "sample-size", 400)
        wait.until(conditions.text_to_be_present_in_element((By.ID, "absolute-uplift"), "25.0 pts"))
        assert driver.find_element(By.ID, "control-bar").get_attribute("value") == "45"
        assert driver.find_element(By.ID, "treatment-bar").get_attribute("value") == "70"

        _click_tab(driver, wait, "tab-governance", "panel-governance")
        for checkbox in driver.find_elements(By.CSS_SELECTOR, "#governance-controls input[type='checkbox']"):
            if not checkbox.is_selected():
                driver.execute_script("arguments[0].click();", checkbox)
        wait.until(conditions.text_to_be_present_in_element((By.ID, "governance-score"), "100"))
        assert driver.find_element(By.ID, "score-ring").get_attribute("value") == "100"

        _assert_no_browser_errors(driver)
        driver.save_screenshot("site-e2e-success.png")
        print("PASS: static visual website tabs, discovery, generator, download, experiment and governance")
    except (AssertionError, TimeoutException, WebDriverException) as exc:
        driver.save_screenshot("site-e2e-failure.png")
        try:
            _assert_no_browser_errors(driver)
        except AssertionError as console_exc:
            raise AssertionError("Static website browser validation failed") from console_exc
        raise AssertionError("Static website browser validation failed") from exc
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
