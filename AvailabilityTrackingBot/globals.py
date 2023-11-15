import sys
import json
import os


working_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

if len(sys.argv) == 0:
    config_file_name = "default.json"
else:
    config_file_name = sys.argv[1]

with open(working_dir + "\\configs\\" + config_file_name, "r") as f:
    data = json.load(f)

target_url = data.get("target_url", None)
licence_no = data.get("licence_no", None)
test_date = data.get("test_date", None)
post_code = data.get("post_code", None)
test_centre_names = data.get("test_centre_names", None)
user_title = data.get("user_title", None)
first_names = data.get("first_names", None)
surname = data.get("surname", None)
address_line_1 = data.get("address_line_1", None)
town = data.get("town", None)
post_code_full = data.get("post_code_full", None)
email = data.get("email", None)
contact_number = data.get("contact_number", None)
card_number = data.get("card_number", None)
expiry_month = data.get("expiry_month", None)
expiry_year = data.get("expiry_year", None)
card_holder_name = data.get("card_holder_name", None)
security_code = data.get("security_code", None)
payment_address_same = data.get("payment_address_same", None)
should_wait_on_confirm_page = data.get("should_wait_on_confirm_page", None)
captcha_sound_loop = data.get("captcha_sound_loop", None)
available_booking_sound = data.get("available_booking_sound", None)
final_step_loop = data.get("final_step_loop", None)
error_loop = data.get("error_loop", None)
paused_sound_loop = data.get("paused_sound_loop", None)
waiting_loop = data.get("waiting_loop", None)
form_delay_range_1 = data.get("form_delay_range_1", None)
form_delay_range_2 = data.get("form_delay_range_2", None)
search_delay_range_1 = data.get("search_delay_range_1", None)
search_delay_range_2 = data.get("search_delay_range_2", None)
submit_delay_range_1 = data.get("submit_delay_range_1", None)
submit_delay_range_2 = data.get("submit_delay_range_2", None)
page_load_delay_range_1 = data.get("page_load_delay_range_1", None)
page_load_delay_range_2 = data.get("page_load_delay_range_2", None)
retries = data.get("retries", None)
is_incognito = data.get("is_incognito", None)
should_pause_on_start = data.get("should_pause_on_start", None)
manual_restart = data.get("manual_restart", None)
max_repeat_captcha_checks = data.get("max_repeat_captcha_checks", None)
# Check error-content captcha & repeats this check for "max_repeat_captcha_checks" times, negative for indefinite checks

test_centre = data.get("test_centre", None)
current_test_date = data.get("current_test_date", None)
earliest_desired_rebook_date = data.get("earliest_desired_rebook_date", None)
# To get any available earliest_desired_rebook_date, set this to null in the config setting
test_ref_no = data.get("test_ref_no", None)

use_days_after_today = data.get("use_days_after_today", None)
no_days_after_today = data.get("no_days_after_today", None)

captcha_code_1, captcha_code_2, captcha_code_3, captcha_code_4 = "1.00", "1.01", "1.02", "1.03"
kill_thread = False
kill_modal_thread = False  # Unused
step_four_btn: any  # Unused
step_four_postcode_form: any  # Unused
step_four_header: any  # Unused
