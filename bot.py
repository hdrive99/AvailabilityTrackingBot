from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import winsound
import undetected_chromedriver as uc
import random
import time
import os
import glob
import traceback
import threading
import contextlib
import sys
import logging
from logging.handlers import RotatingFileHandler

if not sys.gettrace():
    sys.settrace(lambda *args: None)


def _thread_frames(thread):
    for thread_id, frame in sys._current_frames().items():
        if thread_id == thread.ident:
            break
    else:
        raise ValueError("No thread found")
    # walk up to the root
    while frame:
        yield frame
        frame = frame.f_back


@contextlib.contextmanager
def thread_paused(thread):
    """Context manager that pauses a thread for its duration"""
    # signal for the thread to wait on
    e = threading.Event()

    for frame in _thread_frames(thread):
        # attach a new temporary trace handler that pauses the thread

        def new(frame, event, arg, old=frame.f_trace):
            e.wait()

            # call the old one, to keep debuggers working
            if old is not None:
                return old(frame, event, arg)

        frame.f_trace = new

    try:
        yield
    finally:
        # wake the other thread
        e.set()


def sleep_while_browser_alive(code, browser):
    logger.debug(code + " - Continuously checking if browser is alive...")
    continue_app = True
    while continue_app:
        try:
            _ = browser.window_handles
            time.sleep(1)
        except Exception as exc:
            log_err(exc, code + "a", "Browser is no longer alive")
            continue_app = False


class Chrome(uc.Chrome):
    # Override exit to not restart service or start() and remove sleep
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.service.stop()


def namer(name):
    return name.replace(".log", "") + ".log"


class Fragile(object):
    class Break(Exception):
        """Break out of the with statement"""

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value.__enter__()

    def __exit__(self, etype, value, traceback):
        error = self.value.__exit__(etype, value, traceback)
        if etype == self.Break:
            return True
        return error


def close_and_kill(browser):
    global kill_thread
    logger.debug("Killing process...")
    kill_thread = True
    browser.quit()
    raise Fragile.Break


def try_screenshot(code, message, browser):
    try:
        logger.debug(code + "S - Now taking screenshot... (for msg): " + message)
        browser.save_screenshot("screenshots/" + time.strftime("%Y.%m.%d - %H.%M.%S - ") + code + ".png")
        logger.debug(code + "S1 - Screenshot captured for msg: " + message)
    except Exception as exc:
        log_err(exc, code + "S2", "Failed to take screenshot for msg: " + message)


def log_err(error, code, message):
    logger.debug(code + " - " + type(error).__name__ + ": " + message)
    logger.error(code + " - " + traceback.format_exc())


def handle_err_and_quit(error, code, message, browser):
    try_screenshot(code, message, browser)
    logger.debug(code + " - " + type(error).__name__ + ": " + message)
    logger.error(code + " - " + traceback.format_exc())
    close_and_kill(browser)


def pause_if_captcha_page_watcher(browser):
    global kill_thread

    while True:
        if kill_thread:
            return
        time.sleep(1)
        logger.debug(captcha_code_1 + " - Checking if captcha page...")
        if is_el_found_by_attribute_single_check("iframe", captcha_code_1, By.TAG_NAME, browser):
            with thread_paused(main_thread):
                logger.debug(captcha_code_2 + " - Pausing main thread...")
                logger.debug(captcha_code_2 + "a - On captcha page. Waiting for user to continue execution...")
                play_song(captcha_code_2 + "M", captcha_sound_loop, winsound.SND_ASYNC|winsound.SND_LOOP)
                input("Press enter to continue execution when page is ready...")
                logger.debug(captcha_code_3 + " - Continuing execution...")
                stop_song(captcha_code_3 + "M")

                page_check_count = 0
                is_on_captcha_page = False  # initialize boolean
                while is_el_found_by_attribute_single_check("error-content", captcha_code_1, By.CLASS_NAME, browser):
                    page_check_count += 1
                    logger.debug(captcha_code_3 + "a - On captcha page again. Page check count: " +
                                 str(page_check_count) + ". Waiting for user to continue execution...")
                    play_song(captcha_code_2 + "M", captcha_sound_loop, winsound.SND_ASYNC|winsound.SND_LOOP)
                    input("Press enter to continue execution when page is ready...")
                    stop_song(captcha_code_3 + "M")
                    if page_check_count != 3:
                        logger.debug(captcha_code_3 + "b - Continuing execution...")
                        time.sleep(1)
                    else:
                        logger.debug(captcha_code_3 + "c - Stopped checks after " + str(page_check_count) +
                                     " page checks. Likely still on captcha page. Continuing execution...")
                        is_on_captcha_page = True
                        break
                resume_message = "Likely still on captcha page" if is_on_captcha_page else "Not on captcha page"
                logger.debug(captcha_code_3 + "* - " + resume_message + ". Resuming main thread...")
        else:
            logger.debug(captcha_code_2 + "b - Not on captcha page. Continuing execution...")


def set_captcha_codes(code1, code2, code3):
    global captcha_code_1, captcha_code_2, captcha_code_3
    captcha_code_1 = code1
    captcha_code_2 = code2
    captcha_code_3 = code3


def is_el_found_by_attribute_single_check(name, code, by_attr, browser):
    try:
        logger.debug(code + " - Now capturing element by " + str(by_attr) + "...")
        element = browser.find_element(by=by_attr, value=name)
        logger.debug(code + "a - Element captured by " + str(by_attr) + ". Element is: " + name)
        return True
    except NoSuchElementException as exc:
        logger.error(code + "b" + " - " + type(exc).__name__ + ": " + "Element was not found by " + str(by_attr))
        return False
    except Exception as exc:
        handle_err_and_quit(exc, code + "c", "Failed to capture element by " + str(by_attr), browser)


def try_get_url(url, code, browser):
    try:
        logger.debug(code + " - Now reaching target URL...")
        browser.get(url)
        logger.debug(code + "a - Successfully reached target URL")
    except Exception as exc:
        raise RetryOnException(exc, code + "b", "Failed to reach target URL", browser)


def quit_if_title_mismatch(title, code1, code2, browser):
    try:
        logger.debug(code1 + " - Now getting page title...")
        get_title = browser.title.strip()
        logger.debug(code1 + "a - Successfully got page title")
    except Exception as exc:
        raise RetryOnException(exc, code1 + "b", "Failed to get page title", browser)

    try:
        logger.debug(code2 + " - Now checking if page title matches...")
        if get_title == title:
            logger.debug(code2 + "a - Title is as expected")
        else:
            raise ValueError()
    except ValueError as exc:
        raise RetryOnException(exc, code2 + "b", "Title not as expected. Expected: " +
                               title + " || Actual: " + get_title, browser)
    except Exception as exc:
        raise RetryOnException(exc, code2 + "c", "Failed to check if page title matches", browser)


# Does not retry on timeout as we only want to check once. Retry only if a different exception is raised.
def is_el_found_by_attribute(name, code, by_attr, browser, timeout=5, polling=0.5):
    try:
        logger.debug(code + " - Now capturing element by " + str(by_attr) + "...")
        element = WebDriverWait(browser, timeout, polling).until(lambda d: d.find_element(by=by_attr, value=name))
        logger.debug(code + "a - Element captured by " + str(by_attr) + ". Element is: " + name)
        return True
    except TimeoutException as exc:
        log_err(exc, code + "b", "Element was not found by " + str(by_attr))
        return False
    except Exception as exc:
        raise RetryOnException(exc, code + "c", "Failed to capture element by " + str(by_attr), browser)


def get_el_by_attribute_else_quit(name, code, by_attr, browser, timeout=5, polling=0.5):
    try:
        logger.debug(code + " - Now capturing element by " + str(by_attr) + "...")
        element = WebDriverWait(browser, timeout, polling).until(lambda d: d.find_element(by=by_attr, value=name))
        logger.debug(code + "a - Element captured by " + str(by_attr) + ". Element is: " + name)
        return element
    except TimeoutException as exc:
        raise RetryOnException(exc, code + "b", "Element was not found by " + str(by_attr), browser)
    except Exception as exc:
        raise RetryOnException(exc, code + "c", "Failed to capture element by " + str(by_attr), browser)


def get_el_by_tag_and_text_else_quit(name, code, tag, text, browser, timeout=5, polling=0.5):
    try:
        logger.debug(code + " - Now capturing " + tag + " element (text: '" + text + "')...")
        element = WebDriverWait(browser, timeout, polling).until(
            lambda d: d.find_element("xpath", "//" + tag + "[text()='" + text + "']"))
        logger.debug(code + "a - Captured " + tag + " element (text: '" + text + "'). Element is: " + name)
        return element
    except TimeoutException as exc:
        raise RetryOnException(exc, code + "b", "The " + tag + " element (text: '" + text + "') was not found", browser)
    except Exception as exc:
        raise RetryOnException(exc, code + "c", "Failed to capture " + tag + " element (text: '" + text + "')", browser)


def get_el_by_tag_and_text_sibling_else_quit(name, code, tag, text, tag_target, browser, timeout=5, polling=0.5):
    try:
        logger.debug(code + " - Now capturing " + tag + " element's sibling (having text: '" + text + "')...")
        element = WebDriverWait(browser, timeout, polling).until(
            lambda d: d.find_element("xpath", "//" + tag + "[text()='" + text + "']/following-sibling::" + tag_target))
        logger.debug(
            code + "a - Captured " + tag + " element's sibling (having text: '" + text + "'). Element is: " + name)
        return element
    except TimeoutException as exc:
        raise RetryOnException(
            exc, code + "b", "The " + tag + " element's sibling (having text: '" + text + "') was not found", browser)
    except Exception as exc:
        raise RetryOnException(
            exc, code + "c", "Failed to capture " + tag + " element's sibling (having text: '" + text + "')", browser)


def get_el_by_xpath_else_quit(name, code, xpath, browser, timeout=5, polling=0.5):
    try:
        logger.debug(code + " - Now capturing element (having xpath: '" + xpath + "')...")
        element = WebDriverWait(browser, timeout, polling).until(
            lambda d: d.find_element("xpath", xpath))
        logger.debug(
            code + "a - Captured element (having xpath: '" + xpath + "'). Element is: " + name)
        return element
    except TimeoutException as exc:
        raise RetryOnException(
            exc, code + "b", "Element (having xpath: '" + xpath + "') was not found", browser)
    except Exception as exc:
        raise RetryOnException(
            exc, code + "c", "Failed to capture element (having xpath: '" + xpath + "')", browser)


def try_move_to_el_else_quit(name, element, code, browser):
    try:
        logger.debug(code + " - Now moving to element " + name + "...")
        actions = ActionChains(browser)
        actions.move_to_element(element).perform()
        logger.debug(code + "a - Moved to element " + name + " successfully")
    except Exception as exc:
        raise RetryOnException(exc, code + "b", "Failed to move to element " + name, browser)


def is_el_text_matching(name, element, text_to_match, code, browser):
    try:
        logger.debug(code + " - Now checking if element " + name + " has text that matches '" + text_to_match + "'...")
        if text_to_match in element.text:
            logger.debug(code + "a - Confirmed that element " + name + " has matching text!!!")
            return True
        else:
            logger.debug(code + "b - Element " + name + " does not have matching text")
            return False
    except Exception as exc:
        raise RetryOnException(exc, code + "c", "Failed to check if element " + name + " has matching text", browser)


def verify_submit_btn_el_else_quit(element, code, browser):
    try:
        logger.debug(code + " - Now verifying submit btn element...")
        if "button" in element.get_attribute("class") and element.get_attribute("type") == "submit":
            logger.debug(code + "a - Element is submit btn as expected")
        else:
            raise ValueError()
    except ValueError as exc:
        raise RetryOnException(exc, code + "b", "Element is not submit btn as expected.", browser)
    except Exception as exc:
        raise RetryOnException(exc, code + "c", "Failed to verify submit btn element", browser)


def click_el_else_quit(name, element, code, browser):
    try:
        logger.debug(code + " - Now clicking on " + name + " element...")
        element.click()
        logger.debug(code + "a - Successfully clicked on " + name + " element")
    except Exception as exc:
        raise RetryOnException(exc, code + "b", "Failed to click on " + name + " element", browser)


def fill_text_input_else_quit(name, element, txt_input, code, browser):
    try:
        logger.debug(code + " - Now filling in " + name + " text field...")
        element.send_keys(txt_input)
        logger.debug(code + "a - Successfully clicked on " + name + " element")
    except Exception as exc:
        raise RetryOnException(exc, code + "b", "Failed to fill in " + name + " text field", browser)


def try_select_dropdown_text_else_quit(name, element, text, code, browser):
    try:
        logger.debug(code + " - Now selecting dropdown text option '" + text + "' in '" + name + "' dropdown...")
        select = Select(element)
        select.select_by_visible_text(text)
        logger.debug(code + "a - Successfully selected '" + text + "' in '" + name + "' dropdown")
    except Exception as exc:
        raise RetryOnException(exc, code + "b", "Failed to select '" + text + "' in '" + name + "' dropdown", browser)


def get_random_delay(time_range_1, time_range_2):
    return random.randint(time_range_1, time_range_2)


def stop_song(code):
    logger.debug(code + "a - Told the music thread to stop...")
    try:
        winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception as exc:
        log_err(exc, code + "b", "Failed to stop the music")


def play_song(code, sound_track, params=winsound.SND_ASYNC):
    logger.debug(code + "a - Music has started...")
    try:
        fullPath:str = fr"{os.getcwd()}\sounds\{sound_track}.wav".replace("\\", "/")
        winsound.PlaySound(fullPath, params)
    except Exception as exc:
        log_err(exc, code + "b", "Attempted to play sound but failed. Exiting thread...")


def execute_with_retry(retry_count, fun, *args, **kwargs):
    try:
        result = fun(*args, **kwargs)
        return result
    except RetryOnException as exc:
        logger.debug("444 - Entered retry block for function " + fun.__name__ + "() due to an exception")
        time.sleep(3)
        if retry_count > 0:
            retry_count -= 1
            try_screenshot(exc.passed_code, exc.passed_message, exc.passed_browser)
            log_err(exc.passed_error, exc.passed_code, exc.passed_message)
            logger.debug(
                "444a - Now retrying last function " + fun.__name__ + "(). Retries remaining afterwards: " + str(
                    retry_count))
            execute_with_retry(retry_count, fun, *args, **kwargs)
        else:
            logger.debug("444b - No retries left on last function " + fun.__name__ + "() executed. Quitting...")
            handle_err_and_quit(exc.passed_error, exc.passed_code, exc.passed_message, exc.passed_browser)


class RetryOnException(Exception):
    def __init__(self, passed_error, passed_code, passed_message, passed_browser):
        self.passed_error = passed_error
        self.passed_code = passed_code
        self.passed_message = passed_message
        self.passed_browser = passed_browser


file_time = time.strftime("%Y.%m.%d - %H.%M.%S")
logger = logging.getLogger("Rotating Log")
logger.root.setLevel(logging.NOTSET)
handler = RotatingFileHandler("logs/" + file_time + "-debug.log", maxBytes=1000000, backupCount=10)
handler.namer = namer
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

target_url = "https://driverpracticaltest.dvsa.gov.uk/application"
licence_no = "MORGA657054SM9IJ"
test_date = "01/05/23"
post_code = "BT29"
test_centre_names = ["Girvan", "Newton Stewart", "Stranraer"]
user_title = "Mr"
first_names = "Bob"
surname = "Banton"
address_line_1 = "12 Cleveland Road"
town = "London"
post_code_full = "SW13 0AA"
email = "abcdefg@hijk.com"
contact_number = "07874928592"
card_number = "4485324135825867"
expiry_month = "06"
expiry_year = "23"
card_holder_name = "Mr Bob Banton"
security_code = "644"
payment_address_same = True
should_wait_on_confirm_page = True
captcha_sound_loop = "captcha_sound_loop.wav"
available_booking_sound = "available_booking_sound.wav"
final_step_loop = "final_step_loop.wav"


options = uc.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--start-maximized")
options.add_argument("--incognito")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#                     "Chrome/111.0.0.0 Safari/537.36")

with Fragile(Chrome(options=options, version_main=111)) as driver:
    main_thread = threading.current_thread()

    delay_range_1 = 6
    delay_range_2 = 9
    retries = 3
    execute_with_retry(retries, try_get_url, target_url, "0.00", driver)

    # Step 1 Page
    captcha_code_1, captcha_code_2, captcha_code_3 = "1.00", "1.01", "1.02"
    kill_thread = False
    watcher = threading.Thread(target=pause_if_captcha_page_watcher, args=(driver,))
    watcher.start()
    time.sleep(get_random_delay(delay_range_1, delay_range_2))  # Wait for sub-thread to check page

    execute_with_retry(retries, quit_if_title_mismatch, "Type of test", "1.10", "1.11", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_one_btn = execute_with_retry(retries, get_el_by_attribute_else_quit, "testTypeCar", "1.20", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_one_btn, "1.21", driver)

    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_one_btn, "1.22", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    # Step 2 Page
    set_captcha_codes("2.00", "2.01", "2.02")

    execute_with_retry(retries, quit_if_title_mismatch, "Licence details", "2.10", "2.11", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_two_licence_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "driverLicenceNumber", "2.20", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Licence Input", step_two_licence_form, "2.21", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, fill_text_input_else_quit, "Licence Input", step_two_licence_form, licence_no, "2.22", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_two_special_needs_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "special-needs-none", "2.30", By.ID, driver)

    execute_with_retry(
        retries, click_el_else_quit, "Special Needs Radio Btn", step_two_special_needs_form, "2.31", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_two_btn = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "drivingLicenceSubmit", "2.40", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_two_btn, "2.41", driver)

    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_two_btn, "2.42", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    # Step 3 Page
    set_captcha_codes("3.00", "3.01", "3.02")

    execute_with_retry(retries, quit_if_title_mismatch, "Test date", "3.10", "3.11", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_three_date_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "preferredTestDate", "3.20", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Test Date Input", step_three_date_form, "3.21", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, fill_text_input_else_quit, "Test Date Input", step_three_date_form, test_date, "3.22", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_three_btn = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "drivingLicenceSubmit", "3.30", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_three_btn, "3.31", driver)

    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_three_btn, "3.32", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    # Step 4 Page
    set_captcha_codes("4.00", "4.01", "4.02")

    execute_with_retry(retries, quit_if_title_mismatch, "Test centre", "4.10", "4.11", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_four_postcode_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "testCentreName", "4.20", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Postcode Input", step_four_postcode_form, "4.21", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, fill_text_input_else_quit, "Postcode Input", step_four_postcode_form, post_code, "4.22", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    # Step 4.3 - Postcode Search & Loop
    keep_searching_centres = True
    while keep_searching_centres:
        step_four_btn = execute_with_retry(
            retries, get_el_by_attribute_else_quit, "testCentreSubmit", "4.30", By.NAME, driver)

        execute_with_retry(retries, verify_submit_btn_el_else_quit, step_four_btn, "4.31", driver)

        execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_four_btn, "4.32", driver)
        time.sleep(get_random_delay(delay_range_1, delay_range_2))

        search_results_exist = execute_with_retry(
            retries, is_el_found_by_attribute, "test-centre-content", "4.40", By.CLASS_NAME, driver, 25, 2.5)

        if search_results_exist:
            for i in test_centre_names:
                logger.debug("4.41 - Searching for an available booking at " + i + "...")
                step_four_test_el = execute_with_retry(
                    retries, get_el_by_tag_and_text_sibling_else_quit,
                    "Test Centre " + i + " Status Link", "4.42", "h4", i, "h5", driver)

                if execute_with_retry(
                        retries, is_el_text_matching,
                        "Test Centre " + i + " Status Message", step_four_test_el, "available", "4.43", driver):
                    play_song("4.43" + "M", available_booking_sound, winsound.SND_ASYNC)
                    logger.debug("4.43a - Found an available booking at " + i + "!!!")
                    execute_with_retry(retries, click_el_else_quit, "Booking Link", step_four_test_el, "4.44", driver)
                    keep_searching_centres = False
                    break
                else:
                    logger.debug("4.43b - Did not find an available booking at " + i + ".")
                    pass
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    # Step 5 Page
    set_captcha_codes("5.00", "5.01", "5.02")

    execute_with_retry(
        retries, quit_if_title_mismatch, "Test date / time — test times available", "5.10", "5.11", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_five_calendar_btn = execute_with_retry(
        retries, get_el_by_xpath_else_quit,
        "Calendar Btn", "5.20", "//td[@class='BookingCalendar-date--bookable ']", driver)

    execute_with_retry(retries, click_el_else_quit, "Calendar Btn", step_five_calendar_btn, "5.21", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_five_timeslot_btn = execute_with_retry(
        retries, get_el_by_xpath_else_quit,
        "Time Slot Btn", "5.30", "//li[@class='SlotPicker-day is-active']/label", driver)

    execute_with_retry(retries, click_el_else_quit, "Time Slot Btn", step_five_timeslot_btn, "5.31", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_five_submit_btn = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "chooseSlotSubmit", "5.40", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_five_submit_btn, "5.41", driver)

    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_five_submit_btn, "5.42", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    on_modal_screen = execute_with_retry(
        retries, get_el_by_xpath_else_quit,
        "Modal Window Visible", "5.50", "//div[@class='underlay-wrapper' and @style='display: block;']", driver, 25, 3)

    if on_modal_screen:
        time.sleep(3)  # Wait on this step to try and avoid being kicked off
        step_five_timeslot_modal_btn = execute_with_retry(
            retries, get_el_by_xpath_else_quit, "Time Continue Btn", "5.51",
            "//div[@class='underlay-wrapper']/div/section/div/div[@class='dialog-wrapper-inner']/div/button", driver)

        execute_with_retry(
            retries, click_el_else_quit, "Time Continue Btn", step_five_timeslot_modal_btn, "5.52", driver)
        time.sleep(get_random_delay(delay_range_1, delay_range_2))

    # Step 6 Page
    set_captcha_codes("6.00", "6.01", "6.02")

    execute_with_retry(retries, quit_if_title_mismatch, "Your details", "6.10", "6.11", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_six_title_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "details-suffix", "6.20.0", By.ID, driver)

    execute_with_retry(retries, click_el_else_quit, "Title Input", step_six_title_form, "6.20.1", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, try_select_dropdown_text_else_quit, "Title Input", step_six_title_form, user_title, "6.20.2", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_six_first_name_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "firstName", "6.21.0", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "First Names Input", step_six_first_name_form, "6.21.1", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, fill_text_input_else_quit,
        "First Names Input", step_six_first_name_form, first_names, "6.21.2", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_six_surname_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "surname", "6.22.0", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Surname Input", step_six_surname_form, "6.22.1", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, fill_text_input_else_quit, "Surname Input", step_six_surname_form, surname, "6.22.2", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_six_address_line_1_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "addressLine1", "6.23.0", By.NAME, driver)

    execute_with_retry(
        retries, click_el_else_quit, "Address Line 1 Input", step_six_address_line_1_form, "6.23.1", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Address Line 1 Input", step_six_address_line_1_form, address_line_1, "6.23.2", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_six_town_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "town", "6.24.0", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Town Input", step_six_town_form, "6.24.1", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, fill_text_input_else_quit, "Town Input", step_six_town_form, town, "6.24.2", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_six_postcode_full_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "postcode", "6.25.0", By.NAME, driver)

    execute_with_retry(
        retries, click_el_else_quit, "Postcode Full Input", step_six_postcode_full_form, "6.25.1", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Postcode Full Input", step_six_postcode_full_form, post_code_full, "6.25.2", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_six_email_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "emailAddress", "6.26.0", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Email Input", step_six_email_form, "6.26.1", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, fill_text_input_else_quit, "Email Input", step_six_email_form, email, "6.26.2", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_six_confirm_email_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "confirmEmailAddress", "6.27.0", By.NAME, driver)

    execute_with_retry(
        retries, click_el_else_quit, "Confirm Email Input", step_six_confirm_email_form, "6.27.1", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Confirm Email Input", step_six_confirm_email_form, email, "6.27.2", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_six_contact_number_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "contactNumber", "6.28.0", By.NAME, driver)

    execute_with_retry(
        retries, click_el_else_quit, "Contact Number Input", step_six_contact_number_form, "6.28.1", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Contact Number Input", step_six_contact_number_form, contact_number, "6.28.2", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_six_submit_btn = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "detailsSubmit", "6.30", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_six_submit_btn, "6.31", driver)

    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_six_submit_btn, "6.32", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    # Step 7
    set_captcha_codes("7.00", "7.01", "7.02")

    execute_with_retry(retries, quit_if_title_mismatch, "Card details", "7.10", "7.11", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_seven_card_number_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "cardNumber", "7.20", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Card Number Input", step_seven_card_number_form, "7.21", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Card Number Input", step_seven_card_number_form, card_number, "7.22", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_seven_expiry_month_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "expiresOnMonth", "7.30", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Expiry Month Input", step_seven_expiry_month_form, "7.31", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, try_select_dropdown_text_else_quit,
        "Expiry Month Input", step_seven_expiry_month_form, expiry_month, "7.32", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_seven_expiry_year_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "expiresOnYear", "7.40", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Expiry Year Input", step_seven_expiry_year_form, "7.41", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, try_select_dropdown_text_else_quit,
        "Expiry Year Input", step_seven_expiry_year_form, expiry_year, "7.42", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_seven_card_holder_name_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "cardHolderName", "7.50", By.NAME, driver)

    execute_with_retry(
        retries, click_el_else_quit, "Card Holder Name Input", step_seven_card_holder_name_form, "7.51", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Card Holder Name Input", step_seven_card_holder_name_form, card_holder_name, "7.52", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_seven_security_code_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "securityCode", "7.60", By.NAME, driver)

    execute_with_retry(
        retries, click_el_else_quit, "Security Code Input", step_seven_security_code_form, "7.61", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Security Code Input", step_seven_security_code_form, security_code, "7.62", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    step_seven_submit_btn = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "paymentSubmit", "7.70", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_seven_submit_btn, "7.71", driver)

    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_seven_submit_btn, "7.72", driver)
    time.sleep(get_random_delay(delay_range_1, delay_range_2))

    # Step 8
    set_captcha_codes("8.00", "8.01", "8.02")

    execute_with_retry(retries, quit_if_title_mismatch, "Confirm & pay", "8.10", "8.11", driver)

    play_song("8.12M", final_step_loop, winsound.SND_ASYNC|winsound.SND_LOOP)

    if should_wait_on_confirm_page:
        while True:
            try:
                logger.debug("8.20a - Waiting on confirm page indefinitely...")
            except Exception as ex:
                log_err(ex, "8.20b", "Error while waiting on confirm page for user indefinitely. Waiting until "
                                      "browser dies...")
                # Quit the browser instance if browser dies
                stop_song("8.21M")
                sleep_while_browser_alive("999", driver)
                logger.debug("Killing process...")
                kill_thread = True
                raise Fragile.Break
            time.sleep(300)
    else:
        time.sleep(5)  # Wait for the page to load
        logger.debug("8.3 - Proceeding past confirm page...")

        step_eight_submit_btn = execute_with_retry(
            retries, get_el_by_attribute_else_quit, "confirm-button", "8.30", By.ID, driver)

        execute_with_retry(retries, verify_submit_btn_el_else_quit, step_eight_submit_btn, "8.31", driver)

        execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_eight_submit_btn, "8.32", driver)
        time.sleep(get_random_delay(delay_range_1, delay_range_2))

        while True:
            try:
                logger.debug("8.40a - Waiting for user to manually perform transaction...")
            except Exception as ex:
                log_err(ex, "8.40b", "Error while waiting for user to manually perform transaction. Waiting until "
                                      "browser dies...")
                # Quit the browser instance if browser dies
                stop_song("8.41M")
                sleep_while_browser_alive("999", driver)
                logger.debug("Killing process...")
                kill_thread = True
                raise Fragile.Break
            time.sleep(300)

logger.debug("Killed process.")

handler.close()
files = glob.glob('logs/*')
for f in files:
    if not os.path.getsize(f):
        os.remove(f)
