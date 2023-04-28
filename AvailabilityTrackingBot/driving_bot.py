from core import *
from selenium.webdriver.common.by import By
import winsound
import undetected_chromedriver as uc
import time
import os
import glob
import threading


options = uc.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--start-maximized")
if is_incognito:
    options.add_argument("--incognito")  # Toggle this when Error 15 appears
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#                     "Chrome/111.0.0.0 Safari/537.36")

with Fragile(Chrome(options=options, version_main=111)) as driver:
    execute_with_retry(retries, try_get_url, target_url, "0.00", driver)

    if should_pause_on_start:
        play_song("0.01", paused_sound_loop, winsound.SND_ASYNC + winsound.SND_LOOP)
        input("Paused. Press enter to continue when the page is ready (Step 1)...")
        stop_song("0.02")

    # Step 1 Page
    captcha_code_1, captcha_code_2, captcha_code_3, captcha_code_4 = "1.00", "1.01", "1.02", "1.03"
    kill_thread = False
    watcher = threading.Thread(target=pause_if_captcha_page_watcher, args=(driver,))
    watcher.start()
    # Wait for sub-thread to check page
    if not should_pause_on_start:
        time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    execute_with_retry(retries, quit_if_title_mismatch, "Type of test", "1.10", "1.11", driver)

    step_one_btn = execute_with_retry(retries, get_el_by_attribute_else_quit, "testTypeCar", "1.20", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_one_btn, "1.21", driver)

    time.sleep(get_random_delay_or_median(submit_delay_range_1, submit_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_one_btn, "1.22", driver)

    # Step 2 Page
    set_captcha_codes("2.00", "2.01", "2.02", "2.03")
    time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    execute_with_retry(retries, quit_if_title_mismatch, "Licence details", "2.10", "2.11", driver)

    step_two_licence_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "driverLicenceNumber", "2.20", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Licence Input", step_two_licence_form, "2.21", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit, "Licence Input", step_two_licence_form, licence_no, "2.22", driver)

    step_two_special_needs_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "special-needs-none", "2.30", By.ID, driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, click_el_else_quit, "Special Needs Radio Btn", step_two_special_needs_form, "2.31", driver)

    step_two_btn = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "drivingLicenceSubmit", "2.40", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_two_btn, "2.41", driver)

    time.sleep(get_random_delay_or_median(submit_delay_range_1, submit_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_two_btn, "2.42", driver)

    # Step 3 Page
    set_captcha_codes("3.00", "3.01", "3.02", "3.03")
    time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    execute_with_retry(retries, quit_if_title_mismatch, "Test date", "3.10", "3.11", driver)

    step_three_date_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "preferredTestDate", "3.20", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Test Date Input", step_three_date_form, "3.21", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit, "Test Date Input", step_three_date_form, test_date, "3.22", driver)

    step_three_btn = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "drivingLicenceSubmit", "3.30", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_three_btn, "3.31", driver)

    time.sleep(get_random_delay_or_median(submit_delay_range_1, submit_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_three_btn, "3.32", driver)

    # Step 4 Page
    set_captcha_codes("4.00", "4.01", "4.02", "4.03")
    time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    execute_with_retry(retries, quit_if_title_mismatch, "Test centre", "4.10", "4.11", driver)

    step_four_postcode_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "testCentreName", "4.20", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Postcode Input", step_four_postcode_form, "4.21", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit, "Postcode Input", step_four_postcode_form, post_code, "4.22", driver)

    # Step 4.3 - Postcode Search & Loop
    # # Check if modal exists, if so wait 10-15 minutes before clicking submit btn --- doesn't work
    # kill_modal_thread = False
    # modal_watcher = threading.Thread(target=pause_if_modal_watcher, args=(driver,))
    # modal_watcher.start()

    keep_searching_centres = True
    while keep_searching_centres:
        time.sleep(get_random_delay_or_median(search_delay_range_1, search_delay_range_2))

        # Refresh postcode_form element target upon driver.refresh() each iteration
        step_four_postcode_form = execute_with_retry(
            retries, get_el_by_attribute_else_quit, "testCentreName", "4.20", By.NAME, driver)

        step_four_btn = execute_with_retry(
            retries, get_el_by_attribute_else_quit, "testCentreSubmit", "4.40", By.NAME, driver)

        execute_with_retry(retries, verify_submit_btn_el_else_quit, step_four_btn, "4.41", driver)

        # Try to navigate to the button by moving to page header
        step_four_header = execute_with_retry(
            retries, get_el_by_attribute_else_quit, "page-header", "4.42", By.CLASS_NAME, driver)

        execute_with_retry(
            retries, try_move_to_el_else_quit, "Page Header Submit Btn", step_four_header, "4.43", driver)

        execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_four_btn, "4.50", driver)
        # Wait at least x seconds before checking the search results
        time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

        search_results_exist = execute_with_retry(
            retries, is_el_found_by_attribute, "test-centre-content", "4.60", By.CLASS_NAME, driver, 25, 2.5)

        if search_results_exist:
            for i in test_centre_names:
                logger.debug("4.61 - Searching for an available booking at " + i + "...")
                step_four_test_el = execute_with_retry(
                    retries, get_el_by_tag_and_text_sibling_else_quit,
                    "Test Centre " + i + " Status Link", "4.62", "h4", i, "h5", driver)

                if execute_with_retry(
                        retries, is_el_text_matching,
                        "Test Centre " + i + " Status Message", step_four_test_el, "available", "4.63", driver):
                    play_song("4.63" + "M", available_booking_sound)
                    logger.debug("4.63a - Found an available booking at " + i + "!!!")
                    execute_with_retry(
                        retries, try_move_to_el_else_quit, "Booking Link", step_four_test_el, "4.64", driver)
                    execute_with_retry(retries, click_el_else_quit, "Booking Link", step_four_test_el, "4.65", driver)
                    keep_searching_centres = False
                    break
                else:
                    logger.debug("4.63 - Did not find an available booking at " + i + ".")
                    pass
        if keep_searching_centres:
            logger.debug("4.64 - The current URL is: " + driver.current_url + " --- Refreshing the browser...")
            driver.refresh()
            time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    # Step 5 Page
    set_captcha_codes("5.00", "5.01", "5.02", "5.03")
    time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))
    kill_modal_thread = True  # Unused

    execute_with_retry(
        retries, quit_if_title_mismatch, "Test date / time — test times available", "5.10", "5.11", driver)

    step_five_calendar_btn = execute_with_retry(
        retries, get_el_by_xpath_else_quit,
        "Calendar Btn", "5.20", "//td[@class='BookingCalendar-date--bookable ']", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Calendar Btn", step_five_calendar_btn, "5.21", driver)
    time.sleep(1)  # Wait briefly for radio buttons to load

    step_five_timeslot_btn = execute_with_retry(
        retries, get_el_by_xpath_else_quit,
        "Time Slot Btn", "5.30", "//li[@class='SlotPicker-day is-active']/label", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Time Slot Btn", step_five_timeslot_btn, "5.31", driver)

    step_five_submit_btn = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "chooseSlotSubmit", "5.40", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_five_submit_btn, "5.41", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_five_submit_btn, "5.42", driver)

    on_modal_screen = execute_with_retry(
        retries, get_el_by_xpath_else_quit,
        "Modal Window Visible", "5.50", "//div[@class='underlay-wrapper' and @style='display: block;']", driver, 25, 3)

    # Wait briefly on modal screen to try and avoid being kicked off (unneeded?)
    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    step_five_timeslot_modal_btn = execute_with_retry(
        retries, get_el_by_xpath_else_quit, "Time Continue Btn", "5.51",
        "//div[@class='underlay-wrapper']/div/section/div/div[@class='dialog-wrapper-inner']/div/button", driver)

    execute_with_retry(
        retries, click_el_else_quit, "Time Continue Btn", step_five_timeslot_modal_btn, "5.52", driver)

    # Step 6 Page
    set_captcha_codes("6.00", "6.01", "6.02", "6.03")
    time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    execute_with_retry(retries, quit_if_title_mismatch, "Your details", "6.10", "6.11", driver)

    step_six_title_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "details-suffix", "6.20.0", By.ID, driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Title Input", step_six_title_form, "6.20.1", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, try_select_dropdown_text_else_quit, "Title Input", step_six_title_form, user_title, "6.20.2", driver)

    step_six_first_name_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "firstName", "6.21.0", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "First Names Input", step_six_first_name_form, "6.21.1", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit,
        "First Names Input", step_six_first_name_form, first_names, "6.21.2", driver)

    step_six_surname_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "surname", "6.22.0", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Surname Input", step_six_surname_form, "6.22.1", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit, "Surname Input", step_six_surname_form, surname, "6.22.2", driver)

    step_six_address_line_1_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "addressLine1", "6.23.0", By.NAME, driver)

    execute_with_retry(
        retries, click_el_else_quit, "Address Line 1 Input", step_six_address_line_1_form, "6.23.1", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Address Line 1 Input", step_six_address_line_1_form, address_line_1, "6.23.2", driver)

    step_six_town_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "town", "6.24.0", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Town Input", step_six_town_form, "6.24.1", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit, "Town Input", step_six_town_form, town, "6.24.2", driver)

    step_six_postcode_full_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "postcode", "6.25.0", By.NAME, driver)

    execute_with_retry(
        retries, click_el_else_quit, "Postcode Full Input", step_six_postcode_full_form, "6.25.1", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Postcode Full Input", step_six_postcode_full_form, post_code_full, "6.25.2", driver)

    step_six_email_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "emailAddress", "6.26.0", By.NAME, driver)

    execute_with_retry(retries, click_el_else_quit, "Email Input", step_six_email_form, "6.26.1", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit, "Email Input", step_six_email_form, email, "6.26.2", driver)

    step_six_confirm_email_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "confirmEmailAddress", "6.27.0", By.NAME, driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, click_el_else_quit, "Confirm Email Input", step_six_confirm_email_form, "6.27.1", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Confirm Email Input", step_six_confirm_email_form, email, "6.27.2", driver)

    step_six_contact_number_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "contactNumber", "6.28.0", By.NAME, driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, click_el_else_quit, "Contact Number Input", step_six_contact_number_form, "6.28.1", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Contact Number Input", step_six_contact_number_form, contact_number, "6.28.2", driver)

    step_six_submit_btn = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "detailsSubmit", "6.30", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_six_submit_btn, "6.31", driver)

    time.sleep(get_random_delay_or_median(submit_delay_range_1, submit_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_six_submit_btn, "6.32", driver)

    # Step 7
    set_captcha_codes("7.00", "7.01", "7.02", "7.03")
    time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    execute_with_retry(retries, quit_if_title_mismatch, "Card details", "7.10", "7.11", driver)

    step_seven_card_number_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "cardNumber", "7.20", By.NAME, driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Card Number Input", step_seven_card_number_form, "7.21", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Card Number Input", step_seven_card_number_form, card_number, "7.22", driver)

    step_seven_expiry_month_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "expiresOnMonth", "7.30", By.NAME, driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Expiry Month Input", step_seven_expiry_month_form, "7.31", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, try_select_dropdown_text_else_quit,
        "Expiry Month Input", step_seven_expiry_month_form, expiry_month, "7.32", driver)

    step_seven_expiry_year_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "expiresOnYear", "7.40", By.NAME, driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Expiry Year Input", step_seven_expiry_year_form, "7.41", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, try_select_dropdown_text_else_quit,
        "Expiry Year Input", step_seven_expiry_year_form, expiry_year, "7.42", driver)

    step_seven_card_holder_name_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "cardHolderName", "7.50", By.NAME, driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, click_el_else_quit, "Card Holder Name Input", step_seven_card_holder_name_form, "7.51", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Card Holder Name Input", step_seven_card_holder_name_form, card_holder_name, "7.52", driver)

    step_seven_security_code_form = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "securityCode", "7.60", By.NAME, driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, click_el_else_quit, "Security Code Input", step_seven_security_code_form, "7.61", driver)

    time.sleep(get_random_delay_or_median(form_delay_range_1, form_delay_range_2))
    execute_with_retry(
        retries, fill_text_input_else_quit,
        "Security Code Input", step_seven_security_code_form, security_code, "7.62", driver)

    step_seven_submit_btn = execute_with_retry(
        retries, get_el_by_attribute_else_quit, "paymentSubmit", "7.70", By.NAME, driver)

    execute_with_retry(retries, verify_submit_btn_el_else_quit, step_seven_submit_btn, "7.71", driver)

    time.sleep(get_random_delay_or_median(submit_delay_range_1, submit_delay_range_2))
    execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_seven_submit_btn, "7.72", driver)

    # Step 8
    set_captcha_codes("8.00", "8.01", "8.02", "8.03")
    time.sleep(get_random_delay_or_median(page_load_delay_range_1, page_load_delay_range_2))

    execute_with_retry(retries, quit_if_title_mismatch, "Confirm & pay", "8.10", "8.11", driver)

    play_song("8.12M", final_step_loop, winsound.SND_ASYNC + winsound.SND_LOOP)

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
        logger.debug("8.3 - Proceeding past confirm page...")

        step_eight_submit_btn = execute_with_retry(
            retries, get_el_by_attribute_else_quit, "confirm-button", "8.30", By.ID, driver)

        execute_with_retry(retries, verify_submit_btn_el_else_quit, step_eight_submit_btn, "8.31", driver)

        time.sleep(get_random_delay_or_median(submit_delay_range_1, submit_delay_range_2))
        execute_with_retry(retries, click_el_else_quit, "Submit Btn", step_eight_submit_btn, "8.32", driver)

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

file_handler.close()
files = glob.glob(working_dir + "/logs/*")
for f in files:
    if not os.path.getsize(f):
        os.remove(f)

if not manual_restart:
    restart_program(logger)
