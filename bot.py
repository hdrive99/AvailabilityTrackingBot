from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc
import time


def sleep_while_browser_alive(browser):
    continue_app = True
    while continue_app:
        try:
            _ = browser.window_handles
            time.sleep(1)
        except:
            continue_app = False


class Chrome(uc.Chrome):
    # Override exit to not restart service or start() and remove sleep
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.service.stop()


target_url = "https://example.com/"

options = uc.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--start-maximized")
options.add_argument("--incognito")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#                     "Chrome/111.0.0.0 Safari/537.36")

with Chrome(options=options, version_main=111) as driver:
    driver.get(target_url)
    input("Press enter to continue execution when page is ready...")
    driver.save_screenshot("screenshot1.png")

    print("Now capturing element...")
    element = WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(by=By.TAG_NAME, value="a"))
    print("Element captured. Element is: " + element.text)
    assert element.text == "More information..."

    # Quit the browser instance
    sleep_while_browser_alive(driver)
    print("Killing process...")
    # driver.__exit__()

print("Killed process.")
