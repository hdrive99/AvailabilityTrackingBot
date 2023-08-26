from helpers import *
from logging.handlers import RotatingFileHandler
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from datetime import datetime as dt
import undetected_chromedriver as uc
import winsound
import time
import traceback
import threading
import contextlib
import logging


# Set trace, main_thread, and logger globally
if not sys.gettrace():
    sys.settrace(lambda *args: None)

main_thread = threading.current_thread()

file_time = time.strftime("%Y.%m.%d - %H.%M.%S")
logger = logging.getLogger("Rotating Log")
logger.root.setLevel(logging.NOTSET)
path = working_dir + "/logs"
if not os.path.exists(path):
    os.makedirs(path)
screenshots_path = working_dir + "/screenshots"
if not os.path.exists(screenshots_path):
    os.makedirs(screenshots_path)
file_handler = RotatingFileHandler(path + "/" + file_time + "-debug.log", maxBytes=1000000, backupCount=10)
file_handler.namer = namer
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class Chrome(uc.Chrome):
    # Override exit to not restart service or start() and remove sleep
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.service.stop()


class RetryOnException(Exception):
    def __init__(self, passed_error, passed_code, passed_message, passed_browser):
        self.passed_error = passed_error
        self.passed_code = passed_code
        self.passed_message = passed_message
        self.passed_browser = passed_browser


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


def pause_if_captcha_page_watcher(browser):
    global kill_thread

    while True:
        if kill_thread:
            return
        time.sleep(1)
        logger.debug(captcha_code_1 + " - Checking if captcha page...")
        if is_el_found_by_xpath("Captcha iframe", captcha_code_1, "//iframe[@id='main-iframe']", browser, 1):
            with thread_paused(main_thread):
                logger.debug(captcha_code_2 + " - Pausing main thread...")
                logger.debug(captcha_code_2 + " - On captcha page. Waiting to leave this page to continue execution...")
                play_song(captcha_code_2, captcha_sound_loop, winsound.SND_ASYNC + winsound.SND_LOOP)
                time.sleep(5)  # Sleep while captcha is solved

                page_check_count = 0
                is_on_captcha_page = False  # initialize boolean
                logger.debug(captcha_code_2 + " - Checking if captcha page...")
                while is_el_found_by_xpath("Captcha iframe", captcha_code_1, "//iframe[@id='main-iframe']", browser,
                                           1, 0.5):
                    logger.debug(captcha_code_3 + "a - Still on captcha page. Page check count: " +
                                 str(page_check_count) + ". Waiting to leave this page to continue execution...")
                    if page_check_count != max_repeat_captcha_checks:
                        page_check_count += 1
                        logger.debug(captcha_code_3 + "b - Continuing to check if on captcha page...")
                        time.sleep(1)
                    else:
                        page_check_count += 1
                        logger.debug(captcha_code_3 + "c - Stopped checks after " + str(page_check_count) +
                                     " page checks. Likely still on captcha page. Continuing execution...")
                        is_on_captcha_page = True
                        break
                stop_song(captcha_code_4)
                resume_message = "Likely still on captcha page" if is_on_captcha_page else "Not on captcha page"
                logger.debug(captcha_code_4 + " - " + resume_message + ". Resuming main thread...")
        else:
            logger.debug(captcha_code_1 + " - Not on captcha page. Continuing execution...")


# Unused as it wasn't working
def pause_if_modal_watcher(browser):
    global kill_modal_thread
    global step_four_btn
    global step_four_postcode_form
    global step_four_header

    while True:
        if kill_modal_thread:
            return
        time.sleep(1)
        logger.debug("4.30 - Checking if modal page...")
        # Check if on limit modal screen & if page title as expected (for modal watcher)
        if is_el_found_by_xpath("Limit Modal Window Shown", "4.31",
                                "//div[@class='underlay' and @style='display: block;']", browser
                                ) and "Test centre" in execute_with_retry(retries, try_get_title, "4.32", browser):
            with thread_paused(main_thread):
                logger.debug("4.33 - Pausing main thread...")
                logger.debug("4.33 - Sleeping to cool-down Max Searches Per Hour. User shouldn't touch the page...")
                play_song("4.33", waiting_loop, winsound.SND_ASYNC + winsound.SND_LOOP)
                logger.debug("4.33 - Checking if timeout modal...")

                # Exit modal screen
                step_four_ok_modal_btn = execute_with_retry(
                    retries, get_el_by_xpath_else_quit, "Limit Modal Ok Btn", "4.33.2",
                    "//div[@class='underlay' and @style='display: block;']"
                    "/section/div/div[@class='dialog-wrapper-inner']/div/a", browser)

                time.sleep(3)  # Modal appeared, wait for a bit
                execute_with_retry(
                    retries, click_el_else_quit, "Limit Modal Ok Btn", step_four_ok_modal_btn, "4.33.3", browser)
                time.sleep(3)  # Modal closed, wait for a bit

                # Refresh target elements
                step_four_btn = execute_with_retry(
                    retries, get_el_by_attribute_else_quit, "testCentreSubmit", "4.33.4", By.NAME, browser)

                execute_with_retry(retries, verify_submit_btn_el_else_quit, step_four_btn, "4.33.5", browser)

                step_four_postcode_form = execute_with_retry(
                    retries, get_el_by_attribute_else_quit, "testCentreName", "4.33.6", By.NAME, browser)

                step_four_header = execute_with_retry(
                    retries, get_el_by_attribute_else_quit, "page-header", "4.33.7", By.CLASS_NAME, browser)

                # Prevent inactivity for 10-15 minutes to pass the Search Limit cool-down
                logger.debug("4.33.8 - Scroll to top before preventing inactivity...")
                execute_with_retry(
                    retries, try_move_to_el_else_quit, "Page Header Submit Btn", step_four_header, "4.33.9", browser)

                sleep_time = 900
                while sleep_time > 0:
                    a = get_random_delay_or_median(30, 60)
                    time.sleep(a)
                    execute_with_retry(
                        retries, try_move_to_el_else_quit,
                        "Page Header Submit Btn (area)", step_four_header, "4.34.0", browser)

                    b = get_random_delay_or_median(30, 60)
                    time.sleep(b)
                    execute_with_retry(
                        retries, click_el_else_quit, "Postcode Input", step_four_postcode_form, "4.34.1", browser)

                    sleep_time -= (a + b)
                    logger.debug("4.34.2 - Slept for " + str(a + b) + " sec. Sleep time left: " + str(sleep_time) +
                                 " sec.")

                stop_song("4.35.0")
                logger.debug("4.35.1 - Awakened from sleep, expecting Max Searches Per Hour to have passed")
                time.sleep(1)
        else:
            logger.debug("4.32 - Not on timeout modal. Continuing execution...")


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


def wait_for_search_cooldown(code):
    logger.debug(code + " - Restarting app after an interval...")
    time.sleep(1800)


def handle_err_and_quit(error, code, message, browser):
    try_screenshot(code, message, browser)
    logger.debug(code + " - " + type(error).__name__ + ": " + message)
    logger.error(code + " - " + traceback.format_exc())
    play_song("999X", error_loop, winsound.SND_ASYNC + winsound.SND_LOOP)
    while manual_restart:
        time.sleep(1)  # Don't actually quit browser to keep song playing
    close_and_kill(browser)


def close_and_kill(browser):
    global kill_thread
    global kill_modal_thread  # Unused
    logger.debug("Killing process...")
    kill_thread = True
    kill_modal_thread = True  # Unused
    browser.quit()
    raise Fragile.Break


def try_screenshot(code, message, browser):
    try:
        logger.debug(code + "S - Now taking screenshot... (for msg): " + message)
        browser.save_screenshot(working_dir + "/screenshots/" + time.strftime("%Y.%m.%d - %H.%M.%S - ") + code + ".png")
        logger.debug(code + "S1 - Screenshot captured for msg: " + message)
    except Exception as exc:
        log_err(exc, code + "S2", "Failed to take screenshot for msg: " + message)


def log_err(error, code, message):
    logger.debug(code + " - " + type(error).__name__ + ": " + message)
    logger.error(code + " - " + traceback.format_exc())


def play_song(code, sound_track, params=winsound.SND_ASYNC):
    logger.debug(code + "a - Music has started...")
    try:
        fullPath: str = fr"{working_dir}\sounds\{sound_track}.wav".replace("\\", "/")
        winsound.PlaySound(fullPath, params)
    except Exception as exc:
        log_err(exc, code + "b", "Attempted to play sound but failed. Exiting thread...")


def stop_song(code):
    logger.debug(code + "a - Told the music thread to stop...")
    try:
        winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception as exc:
        log_err(exc, code + "b", "Failed to stop the music")


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


# Does not retry on timeout as we only want to check once. Retry only if a different exception is raised.
def is_el_found_by_attribute_single_check(name, code, by_attr, browser):
    try:
        logger.debug(code + " - Now capturing element by " + str(by_attr) + "...")
        browser.find_element(by=by_attr, value=name)
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


def try_get_title(code, browser):
    try:
        logger.debug(code + " - Now getting page title...")
        get_title = browser.title.strip()
        logger.debug(code + "a - Successfully got page title")
        return get_title
    except Exception as exc:
        raise RetryOnException(exc, code + "b", "Failed to get page title", browser)


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
        WebDriverWait(browser, timeout, polling).until(lambda d: d.find_element(by=by_attr, value=name))
        logger.debug(code + "a - Element captured by " + str(by_attr) + ". Element is: " + name)
        return True
    except TimeoutException as exc:
        log_err(exc, code + "b", "Element was not found by " + str(by_attr))
        return False
    except Exception as exc:
        raise RetryOnException(exc, code + "c", "Failed to capture element by " + str(by_attr), browser)


# Does not retry on timeout as we only want to check once. Retry only if a different exception is raised.
def is_el_found_by_xpath(name, code, xpath, browser, timeout=5, polling=0.5):
    try:
        logger.debug(code + " - Now capturing element (having xpath: '" + xpath + "')...")
        WebDriverWait(browser, timeout, polling).until(lambda d: d.find_element("xpath", xpath))
        logger.debug(code + "a - Captured element (having xpath: '" + xpath + "'). Element is: " + name)
        return True
    except TimeoutException as exc:
        log_err(exc, code + "b", "Element (having xpath: '" + xpath + "') was not found")
        return False
    except Exception as exc:
        raise RetryOnException(exc, code + "c", "Failed to capture element (having xpath: '" + xpath + "')", browser)


def get_el_by_xpath_else_quit(name, code, xpath, browser, timeout=5, polling=0.5):
    try:
        logger.debug(code + " - Now capturing element (having xpath: '" + xpath + "')...")
        element = WebDriverWait(browser, timeout, polling).until(lambda d: d.find_element("xpath", xpath))
        logger.debug(code + "a - Captured element (having xpath: '" + xpath + "'). Element is: " + name)
        return element
    except TimeoutException as exc:
        raise RetryOnException(exc, code + "b", "Element (having xpath: '" + xpath + "') was not found", browser)
    except Exception as exc:
        raise RetryOnException(exc, code + "c", "Failed to capture element (having xpath: '" + xpath + "')", browser)


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


def try_move_to_el_else_quit(name, element, code, browser):
    try:
        logger.debug(code + " - Now moving to element " + name + "...")
        browser.execute_script("arguments[0].scrollIntoView(true);", element)
        logger.debug(code + "a - Moved to element " + name + " successfully")
    except Exception as exc:
        raise RetryOnException(exc, code + "b", "Failed to move to element " + name, browser)


def try_execute_script(script, code, browser):
    try:
        logger.debug(code + " - Now executing script: " + script + "...")
        browser.execute_script(script)
        logger.debug(code + "a - Executed script successfully")
    except Exception as exc:
        log_err(exc, code + "b", "Failed to execute script")
        pass

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


# TODO: Fix: This currently assumes there will only be 1 cancellation at any time, selecting the 1st & ignoring the rest
# So if 1st cancellation is not later than earliest_desired_rebook_date, but 2nd is, then we miss the 2nd rebook chance
def verify_attribute_href_date_is_earlier(booked_date_string, earliest_desired_rebook_date_str, element, code, browser):
    try:
        if earliest_desired_rebook_date_str != None:
            earliest_desired_rebook_date_str = dt.strptime(earliest_desired_rebook_date_str, "%Y-%m-%d")
            logger.debug(code + " - Now verifying if element's attribute for date is earlier... "
                                "(but later than: " + str(earliest_desired_rebook_date_str) + ")")
        else:
            logger.debug(code + " - Now verifying if element's attribute for date is earlier...")
        booked_date_string = dt.strptime(booked_date_string, "%Y-%m-%d")
        href = element.get_attribute("href")
        new_date = dt.strptime(href[-10:], "%Y-%m-%d")
        logger.debug(
            code + " - Comparing booked date " + str(booked_date_string) + " with new date " + str(new_date) + "...")
        if new_date >= booked_date_string:
            logger.debug(code + "b - New date is equal to or later than the booked date")
            return False

        logger.debug(code + "a - New date is earlier than the booked date")
        if earliest_desired_rebook_date_str == None:
            return True

        if new_date >= earliest_desired_rebook_date_str:
            logger.debug(code + "c - New date is later than or is on the earliest desired rebooking date!!! Booking...")
            return True
        else:
            logger.debug(code + "d - New date is earlier than the earliest desired rebooking date. Ignoring...")
            return False
    except Exception as exc:
        raise RetryOnException(exc, code + "c", "Failed to verify if element's attribute for date is earlier", browser)


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
