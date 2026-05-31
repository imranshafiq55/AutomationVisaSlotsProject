import random
import sys
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import winsound

class UsVisaScheduling:
    ofc_post_city_list = []
    year_numbers = ""
    month_numbers = ""
    dates_filter_list = []
    city_dropdown_wait_time = 5
    # Retry Logic 
    def retry(self, func, retries=3, delay=2, *args, **kwargs):
        last_exception = None

        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                print(f"[Retry {attempt+1}/{retries}] Failed: {str(e)}")
                time.sleep(delay)

        print("All retries failed.")
        raise last_exception
    
    def safe_switch_window(self, driver, prefer_index=0):
        try:
            handles = driver.window_handles
            print("Available window handles:", handles)
            if len(handles) > prefer_index:
                driver.switch_to.window(handles[prefer_index])
                print(f"Switched to tab index {prefer_index}")
            else:
                driver.switch_to.window(handles[0])
                print("Only one tab exists, staying in main tab")
            print(driver.current_url)
        except Exception as expt:
            print("switching window handles Exception : " + str(expt))
            raise expt
    
    def wait_for_page_ready(self, driver, group_members_path):
        max_attempts = 60
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            current_title = driver.title.lower()
            current_url = driver.current_url.lower()

            # ✅ OFC Page is ready
            if self.isElementPresent(driver, group_members_path):
                print("✅ OFC Page Ready!")
                time.sleep(random.uniform(1.0, 2.0))
                return True

            # 🕐 State 1: Waiting Queue — URL is /en-US/ with image-section
            elif current_url == "https://www.usvisascheduling.com/en-us/" or \
                self.isElementPresent(driver, "//div[@id='image-section']"):
                print(f"⏳ [QUEUE] Waiting room active... ({attempt * 10}s elapsed)")
                time.sleep(10)

            # 🤖 State 2: Tick/Checkbox Verification — URL is root URL
            elif "just a moment" in current_title or \
                self.isElementPresent(driver, "//label[contains(@class,'cb-lb')]"):
                print(f"🤖 [CLOUDFLARE TURNSTILE] Checkbox verification detected...")
                checkbox_clicked = self.click_verification_checkbox(driver)
                if checkbox_clicked:
                    print("✅ Checkbox clicked! Waiting for redirect...")
                    time.sleep(5)
                else:
                    print("⚠️ Could not auto-click checkbox, waiting 5s...")
                    time.sleep(5)
            
            # ❌ State 3: Cloudflare 524 Timeout
            elif "524" in current_title or \
                self.isElementPresent(driver, "//*[contains(text(),'timeout occurred')]"):
                print(f"❌ [524 ERROR] Timeout error, waiting to retry... ({attempt * 10}s elapsed)")
                time.sleep(15)
                print("🔄 Refreshing page after 524...")
                driver.refresh()
                time.sleep(5)

            # ❓ Unknown state
            else:
                print(f"⚠️ [UNKNOWN] Title: {driver.title} URL: {driver.current_url} ({attempt * 10}s elapsed)")
                time.sleep(10)

        print("❌ Gave up waiting for page to be ready.")
        return False
    
    def click_verification_checkbox(self, driver):
        checkbox_xpaths = [
            "//label[contains(@class,'cb-lb')]//input[@type='checkbox']",
            "//label[contains(@class,'cb-lb')]",
            "//input[@type='checkbox']",
            "//iframe[contains(@src,'challenges.cloudflare.com')]",
        ]
        
        # First try direct click on checkbox
        for xpath in checkbox_xpaths:
            try:
                # Try switching to iframe first if cloudflare iframe exists
                iframes = driver.find_elements(By.XPATH, "//iframe")
                for iframe in iframes:
                    try:
                        driver.switch_to.frame(iframe)
                        checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox']")
                        if checkbox.is_displayed():
                            driver.execute_script("arguments[0].click();", checkbox)
                            print("✅ Checkbox clicked inside iframe!")
                            driver.switch_to.default_content()
                            return True
                    except:
                        driver.switch_to.default_content()
                        continue
                
                # Try direct click without iframe
                element = driver.find_element(By.XPATH, xpath)
                if element.is_displayed():
                    driver.execute_script("arguments[0].click();", element)
                    print(f"✅ Clicked verification element: {xpath}")
                    return True
            except:
                continue
        
        return False
    
    def ofc_post(self):
        print("0: CHENNAI VAC")
        print("1: HYDERABAD VAC")
        print("2: KOLKATA VAC")
        print("3: MUMBAI VAC")
        print("4: NEW DELHI VAC")
        try:
            self.ofc_post_city = input("Please Select OFC Post. Enter numbers separated by commas: ")
            print("You entered:", self.ofc_post_city)
            self.ofc_post_city = self.ofc_post_city.split(",")
            for ofc_post in self.ofc_post_city:
                if ofc_post == '0':
                    print("Selected OFC Post: CHENNAI VAC")
                    self.ofc_post_city_list.append("CHENNAI VAC")
                elif ofc_post == '1':
                    print("Selected OFC Post: HYDERABAD VAC")
                    self.ofc_post_city_list.append("HYDERABAD VAC")
                elif ofc_post == '2':
                    print("Selected OFC Post: KOLKATA VAC")
                    self.ofc_post_city_list.append("KOLKATA VAC")
                elif ofc_post == '3':
                    print("Selected OFC Post: MUMBAI VAC")
                    self.ofc_post_city_list.append("MUMBAI VAC")
                elif ofc_post == '4':
                    print("Selected OFC Post: NEW DELHI VAC")
                    self.ofc_post_city_list.append("NEW DELHI VAC")
                else:
                    print("Please Select Valid OFC Post")
        except Exception as e:
            print("Exception Occurred in ofc_post method: " + str(e))

    def select_months(self):
        user_years = input("Please Select Years. Enter Years separated by commas Like:- 2024,2025: ")
        self.year_numbers = user_years.split(',')
        for year in self.year_numbers:
            print("0: JAN")
            print("1: FEB")
            print("2: MAR")
            print("3: APR")
            print("4: MAY")
            print("5: JUN")
            print("6: JUL")
            print("7: AUG")
            print("8: SEP")
            print("9: OCT")
            print("10: NOV")
            print("11: DEC")
            try:
                user_months = input('Please Select Months for Year: ' + str(year) + '. Enter numbers separated by commas Like:- 0,1: ')
                self.month_numbers = user_months.split(',')
                for num in self.month_numbers:
                    filter_dates = input('Please Enter Date for Month: ' + str(num) + ' Like: 1-10 : ')
                    self.dates_filter_list.append(year + "|" + num + "|" + filter_dates)

            except Exception as ex:
                print("Exception Occurred in select_months method: " + str(ex))
            city_dropdown_wait_input = input("Please Provide City Dropdown Waiting Time Like 5: ")
            self.city_dropdown_wait_time = int(city_dropdown_wait_input)

    def us_visa_sch_nav(self):
        try:

            inner_start_time = float(input("Please Enter Start Time of wait between Every Loop like: 1.1 :"))
            inner_end_time = float(input("Please Enter End Time of wait between Every Loop like: 10.9 :"))
            outer_start_time = float(input("Please Enter Start Time of wait After Every Loop like: 1.1 :"))
            outer_end_time = float(input("Please Enter End Time of wait After Every Loop like: 12.9 :"))

            # pause_duration = random.uniform(15.1, 45.9)  # Pause for 30 seconds
            # pause_duration = random.uniform(15.1, 120.9)  # Pause for 30 seconds
            # pause_duration = random.uniform(15.1, 60.9)  # Pause for 30 seconds
            # # bot_run_interval = random.randint(8 * 60, 12 * 60)  # 8-12 minutes
            # # bot_run_interval = random.uniform(1 * 60, 5 * 60)  # 8-12 minutes
            # # bot_run_interval = random.uniform(1 * 60, 8 * 60)  # 8-12 minutes
            # bot_run_interval = random.uniform(3 * 60, 8 * 60)  # 8-12 minutes
            # start_time = time.time()

            bot_run_interval_start_time = int(input("Please Enter Start Time of Bot Run Interval like 3: "))
            bot_run_interval_end_time = int(input("Please Enter End Time of Bot Run Interval like 15: "))
            bot_run_interval = random.uniform(bot_run_interval_start_time * 60, bot_run_interval_end_time * 60)  # 8-12 minutes
            pause_duration_start_time = float(input("Please Enter Start Time of pause duration like 3.1: "))
            pause_duration_end_time = float(input("Please Enter End Time of pause duration like 120.9: "))
            pause_duration = random.uniform(pause_duration_start_time, pause_duration_end_time)  # Pause for 30 seconds

            

            # Define the URL
            url = "https://www.usvisascheduling.com/"
            #url = "https://www.usvisascheduling.com/en-US/ofc-schedule/"
            proxy = input("Please Enter Proxy Like: 5.59.250.12:6710: ")

            # def get_random_proxy():
            #     return random.choice(proxies)

            # Initialize Chrome WebDriver options
            options = uc.ChromeOptions()
            # options = Options()
            # proxy = get_random_proxy()
            # print("Current Proxy: " + str(proxy))
            options = self.getChromeOptions(options, proxy)
            #options = self.getChromeOptions(options, "")
            # Initialize Chrome WebDriver with options
            # driver = uc.Chrome(options=options, version_main=144)
            #driver = uc.Chrome(options=options)
            driver = uc.Chrome(options=options, version_main=148)
            # driver = uc.Chrome(service=Service(), options=options)
            # Navigate to the website using WebDriver
            driver.get(url)

            # driver.maximize_window()

            navigate_to_ofc = input("Please Hit Enter After Navigating to the OFC POST: ")
            try:
                self.safe_switch_window(driver, prefer_index=1)
                driver.execute_script("window.alert = function() {};")

            except Exception as expt:
                print("switching window handles Exception : " + str(expt))
                return

            slot_not_found = True
            group_members_path = "//h2[text()='Group Members']"
            
            #waiting room logic
            waiting_room_path = "//div[@id='image-section']"
            print("Waiting room XPath set: " + waiting_room_path)

            ofc_post_city_select_dropdown_path = "//select[@id='post_select']"
            ofc_post_city_calendar_date_picker = '//div[contains(@class,"hasDatepicker")]'
            ofc_post_city_calendar_date_picker_year = "//select[@class='ui-datepicker-year']"
            ofc_post_city_calendar_date_picker_month = "//select[@class='ui-datepicker-month']"

            start_time = time.time()
            counter = 1
            print("Slot finding start")
            while slot_not_found:
                print("Loop in")
                for post_city in self.ofc_post_city_list:
                    print("Counter: " + str(counter))

                    # ✅ FIX 3: Detect waiting room and wait it out
                    if self.isElementPresent(driver, waiting_room_path):
                        print("⏳ Waiting Room Detected. Waiting for it to clear...")
                        wait_counter = 0
                        while self.isElementPresent(driver, waiting_room_path):
                            wait_counter += 1
                            print(f"Still in waiting room... ({wait_counter * 10} seconds elapsed)")
                            time.sleep(10)
                            if wait_counter > 60:  # max wait 10 minutes
                                print("Waited too long. Refreshing page...")
                                driver.refresh()
                                time.sleep(5)
                                break
                        print("✅ Waiting Room Cleared! Resuming bot...")
                        time.sleep(3)  # small buffer after waiting room clears

                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    if elapsed_time >= bot_run_interval:
                        #removed the blank dropdown selection during pause
                        #self.select_dropdown(driver, ofc_post_city_select_dropdown_path, "")
                        #self.retry(self.select_dropdown, 3, 2, driver, ofc_post_city_select_dropdown_path, post_city)
                        # self.clear_browser_cache(driver)
                        print("Pausing for '" + str(pause_duration) + "' Seconds after every '" + str(bot_run_interval_start_time) + "' to '" + str(bot_run_interval_end_time) + "' Minutes...")
                        time.sleep(pause_duration)
                        bot_run_interval = random.uniform(bot_run_interval_start_time * 60, bot_run_interval_end_time * 60)
                        pause_duration = random.uniform(pause_duration_start_time, pause_duration_end_time)
                        start_time = time.time()  # Pause the bot for in between 15 seconds to 45 seconds
                        # bot_run_interval = random.randint(8 * 60, 12 * 60)  # 8-12 minutes
                        # bot_run_interval = random.uniform(1 * 60, 8 * 60)  # 8-12 minutes
                        # bot_run_interval = random.uniform(3 * 60, 8 * 60)  # 8-12 minutes
                        bot_run_interval = random.uniform(bot_run_interval_start_time * 60, bot_run_interval_end_time * 60)  # 8-12 minutes
                        pause_duration = random.uniform(pause_duration_start_time, pause_duration_end_time)  # Pause for 30 seconds
                        start_time = time.time()  # Reset the start time

                    # ✅ Wait for page to be ready (handles queue, cloudflare, 524 automatically)
                    page_ready = self.wait_for_page_ready(driver, group_members_path)

                    if page_ready:
                        if self.isElementPresent(driver, ofc_post_city_select_dropdown_path):

                            if len(self.ofc_post_city_list) == 1:
                                self.select_dropdown(driver, ofc_post_city_select_dropdown_path, "")
                                time.sleep(random.uniform(1.5, 3.0))

                            self.retry(self.select_dropdown, 3, 2, driver, ofc_post_city_select_dropdown_path, post_city)

                            #Check this solution for calendar loading.
                            # ✅ Use ActionChains to simulate real human click on dropdown option
                            try:
                                from selenium.webdriver.common.action_chains import ActionChains
                                from selenium.webdriver.support.select import Select

                                dropdown = driver.find_element(By.XPATH, ofc_post_city_select_dropdown_path)

                                # Scroll into view
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown)
                                time.sleep(random.uniform(0.5, 1.0))

                                # Move mouse to dropdown naturally
                                action = ActionChains(driver)
                                action.move_to_element(dropdown)
                                action.pause(random.uniform(0.3, 0.7))
                                action.click()
                                action.perform()
                                time.sleep(random.uniform(0.3, 0.6))

                                # Now select the option
                                select = Select(dropdown)
                                select.select_by_visible_text(post_city)
                                time.sleep(random.uniform(0.5, 1.0))

                                print("✅ Human-like selection done")

                            except Exception as e:
                                print("Selection failed: " + str(e))
                                self.retry(self.select_dropdown, 3, 2, driver, ofc_post_city_select_dropdown_path, post_city)
                            no_slots_avail_path = "//div[not(contains(@style,'none'))]/div[text()='No Slots Available']"
                            # ✅ Retry calendar load up to 3 times
                            calendar_loaded = False
                            for cal_attempt in range(3):
                                self.wait_for_any_element_to_be_visible(driver, ofc_post_city_calendar_date_picker, no_slots_avail_path, 60)
                                time.sleep(random.uniform(0.5, 1))
                                
                                if self.isElementPresent(driver, ofc_post_city_calendar_date_picker):
                                    print(f"✅ Calendar loaded on attempt {cal_attempt + 1}")
                                    calendar_loaded = True
                                    break
                                elif self.isElementPresent(driver, no_slots_avail_path):
                                    print(f"❌ No Slots Available on attempt {cal_attempt + 1}")
                                    calendar_loaded = True
                                    break
                                else:
                                    print(f"⚠️ Calendar not loaded yet, retrying... attempt {cal_attempt + 1}")
                                    # Re-fire the selection
                                    try:
                                        dropdown = driver.find_element(By.XPATH, ofc_post_city_select_dropdown_path)
                                        option_xpath = f"//select[@id='post_select']/option[text()='{post_city}']"
                                        option = driver.find_element(By.XPATH, option_xpath)
                                        driver.execute_script("arguments[0].selected = true;", option)
                                        driver.execute_script("""
                                                var el = arguments[0];
                                                var event = new Event('change', { bubbles: true, cancelable: true });
                                                el.dispatchEvent(event);
                                            """, dropdown)
                                        print(f"🔄 Re-fired selection event attempt {cal_attempt + 1}")
                                    except Exception as e:
                                        print(f"Re-fire failed: {str(e)}")

                            if self.isElementPresent(driver, ofc_post_city_calendar_date_picker):
                                for year in self.year_numbers:
                                    self.wait_for_element_to_visible(driver, ofc_post_city_calendar_date_picker_year, 3)
                                    if not self.isElementPresent(driver, ofc_post_city_calendar_date_picker_year + "/option[@value='" + year + "' and @selected]"):
                                        self.select_dropdown(driver, ofc_post_city_calendar_date_picker_year, year, True)

                                    months = [o.split("|")[1] for o in self.dates_filter_list if o.__contains__(str(year))]
                                    for num in months:
                                        if self.isElementPresent(driver, ofc_post_city_calendar_date_picker_month):
                                            if not self.isElementPresent(driver, ofc_post_city_calendar_date_picker_month + "/option[@value='" + num + "' and @selected]"):
                                                self.select_dropdown(driver, ofc_post_city_calendar_date_picker_month, num, True)
                                                time.sleep(random.uniform(0.2, 0.4))

                                            self.handle_calendar(driver, num, post_city, "first", year)
                                            if str(int(num) + 1) in months:
                                                self.handle_calendar(driver, str(int(num) + 1), post_city, "last", year)
                            else:
                                print("Date Picker Not Found For City: ", post_city)
                        else:
                            print("First City Dropdown not Found")
                    else:
                        print("⚠️ Page never became ready — skipping this iteration")

                    counter = counter + 1

                    time.sleep(random.uniform(inner_start_time, inner_end_time))  # Wait between 1 and 3 seconds
                if len(self.ofc_post_city_list) == 1:
                    time.sleep(random.uniform(outer_start_time, outer_end_time))  # Wait between 1 and 3 seconds
                if len(self.ofc_post_city_list) == 2:
                    time.sleep(random.uniform(6.1, 15.9))  # Wait between 1 and 3 seconds
                if len(self.ofc_post_city_list) == 3:
                    time.sleep(random.uniform(7.1, 20.9))  # Wait between 1 and 3 seconds
                if len(self.ofc_post_city_list) == 4:
                    time.sleep(random.uniform(8.1, 25.9))  # Wait between 1 and 3 seconds
                if len(self.ofc_post_city_list) == 5:
                    time.sleep(random.uniform(9.1, 30.9))  # Wait between 1 and 3 seconds
        except Exception as exp:
            print("Exception Occurred in us_visa_sch_nav method: " + str(exp))

    def select_dropdown(self, driver, locator, city, value=False):
        try:
            # Find the dropdown element
            dropdown = driver.find_element(By.XPATH, locator)

            # Initialize the Select object
            select = Select(dropdown)

            if value == True:
                # Select the option by value
                select.select_by_value(city)
            else:
                # Select the option by visible text
                select.select_by_visible_text(city)
        except Exception as exc:
            # print("Exception Occurred in select_dropdown method: " + str(exc))
            print("select_dropdown not found : " + str(city))

    def isElementPresent(self, driver, locator):
        try:
            element = driver.find_element(By.XPATH, locator)
            if element.is_displayed():
                return True
            else:
                print("Element is not present or not visible" + str(locator))
                return False
        except Exception as expt:
            # print("Exception Occurred in isElementPresent: ", str(expt))
            # print("Element not Found in isElementPresent" + str(locator))
            return False

    def ClickElement(self, driver, XPath):
        try:
            driver.find_element(By.XPATH, XPath).click()
        except Exception as exption:
            print("XPath Not Found to Click: " + str(XPath))
            # print("Exception Occurred in ClickElement method: " + str(exption))

    def ClickElementWithJS(self, driver, XPath):
        try:
            element = driver.find_element(By.XPATH, XPath)
            driver.execute_script("arguments[0].click();", element)
        except Exception as exption:
            print("XPath Not Clicked with JS: " + str(XPath))
            # print("Exception Occurred in ClickElement method: " + str(exption))

    def clickingElement_whileClicked(self, driver, locator, locaType=By.XPATH, wait_time=0.0):
        try:
            element = driver.find_element(locaType, locator)
            if element not in [None, False, ""]:
                i = 1
                while (self.isElementPresent(driver, locator)) is True:
                    self.ClickElement(driver, locator)
                    time.sleep(random.uniform(0.3, 0.5))  # Wait between 1 and 3 seconds
                    i += 1
                    if i > 5:
                        break
        except Exception as ex:
            print("Locator Not Found to Click while Clicked: " + str(locator))

    def wait_for_element_to_visible(self, driver, locator, wait_time):
        try:
            # Wait for 3 seconds until finding the element
            wait = WebDriverWait(driver, wait_time, poll_frequency=0.1)
            element = wait.until(EC.visibility_of_element_located((By.XPATH, locator)))
        except Exception as ex:
            print("Locator Not Found " + str(locator) + " in time " + str(wait_time))
            # print("Exception Occurred in wait_for_element_to_visible: " + str(ex))

    def wait_for_element_to_invisible(self, driver, locator, wait_time):
        try:
            # Wait for 3 seconds until finding the element
            wait = WebDriverWait(driver, wait_time)
            element = wait.until(EC.invisibility_of_element_located((By.XPATH, locator)))
        except Exception as expt:
            print("Locator Not Invisible " + str(locator) + " in time " + str(wait_time))
            # print("Exception Occurred in wait_for_element_to_visible: " + str(expt))

    def wait_for_any_element_to_be_visible(self, driver, locator1, locator2, wait_time):
        try:
            wait = WebDriverWait(driver, wait_time, poll_frequency=0.1)
            element = wait.until(lambda d: d.find_element(By.XPATH, locator1).is_displayed() or d.find_element(By.XPATH, locator2).is_displayed())
        except Exception as ex:
            print(f"Neither locator '{locator1}' nor '{locator2}' became visible in time {wait_time}")

    def getChromeOptions(self, chrome_options, proxy):
        # chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-websecurity')

        # For Disabling Popups
        chrome_options.add_argument('--disable-popup-blocking')
        # For Disabling Notification
        chrome_options.add_argument('--disable-notifications')
        # For Saving Login Session. Remove this when handling this to client
        #chrome_options.add_argument(r"--user-data-dir=F:\chrome_profile")
        chrome_options.add_argument(r"--user-data-dir=./chrome_profile")
        #chrome_options.add_argument(r"--user-data-dir=./visa_profile")
        
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        # Below statements comment due to circumstances that slots aren't booking verified by me also.
        # prefs = {
        #     "profile.default_content_setting_values.notifications": 2,  # Disable notifications
        #     "profile.default_content_setting_values.popups": 2  # Disable popups
        # }
        # chrome_options.add_experimental_option("prefs", prefs)

        # chrome_options.add_argument("--disable-session-crashed-bubble")
        chrome_options.add_argument('--disable-infobars')
        # chrome_options.add_argument('--disable-browser-side-navigation')

        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors=yes')
        # chrome_options.add_argument('--headless')

        # This is causing break when click on Schedule Appointment.
        # chrome_options.add_argument('--single-process')

        # Trying solution for disabling popups
        # chrome_options.add_argument('--window-size=1080x900')
        chrome_options.add_argument('--window-size=1920x1080')

        # chrome_options.add_argument("--mute-audio")

        # Anti-bot and automation detection bypass
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        # Custom user agent
        # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        # Set Chrome WebDriver options to disable images
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # options.add_experimental_option("prefs", prefs)
        
        if proxy != "":
            chrome_options.add_argument(f'--proxy-server=http://{proxy}')
       
        return chrome_options

    def getElementAttributeText(self, driver, locator, attributeName, locaType=By.XPATH, returnBlankStr=True):

        try:
            element = driver.find_element(locaType, locator)
            if element not in [None, False, ""]:
                AttrTxt = element.get_attribute(str(attributeName))
                return AttrTxt
        except:
            print(str("getElementAttributeText Not Found with Locator :: " + locator + "and Locator Type = " + locaType))

        if returnBlankStr == True:
            return ""
        else:
            return None

    def getElementText(self, driver, locator, locaType=By.XPATH, returnBlankStr=True):

        gettext = driver.find_element(locaType, locator)
        if gettext not in [None, False, ""]:
            try:
                textfecth = gettext.text
                if textfecth != "":
                    return "" + textfecth
            except Exception as ex:
                print("")
            return self.getElementAttributeText(driver, locator, "textContent", returnBlankStr=returnBlankStr)
        if returnBlankStr == True:
            return ""
        else:
            return None

    def getElements(self, driver, locator, locaType=By.XPATH):
        elements_list = None
        try:
            elements_list = driver.find_elements(locaType, locator)
        except Exception as ex:
            print("getElements: Elements Not Found. locator:" + str(locator))
        return elements_list

    def AlertBox_accept(self, driver, wait_after_accept=False, wait_time=0.5, wait_after_accept_time=1):
        str_text = ""
        try:
            # alert = WebDriverWait(driver, wait_time).until(EC.alert_is_present(), 'Timed out waiting for alert confirmation popup to appear.')
            alert = WebDriverWait(driver, wait_time).until(EC.alert_is_present())

            str_text = str(alert.text)
            alert.accept()
            # print("alert accepted")
            print("Alert Box Found & Accepted.")

            if wait_after_accept == True:
                time.sleep(random.uniform(0.1, wait_after_accept_time))  # Wait between 1 and 3 seconds

        except Exception as ex:
            # Log(LogType.ERROR, str("AlertBox_accept: No alert found. Error: " + str(ex)))

            # print("No alert found. Error: "+str(ex))
            print(end='')

        return str_text

    def handle_calendar(self, driver, num, post_city, calendar, year):
        date_picker_green = f"//div[contains(@class,'ui-datepicker-group-{calendar}')]//tr/td[contains(@class,'greenday')]"
        if self.isElementPresent(driver, date_picker_green):
            filter_date = [o.split("|")[2] for o in self.dates_filter_list if o.split("|")[0] == year and o.split("|")[1] == num]
            filter_date = filter_date[0].split("-")
            filter_start_date = int(filter_date[0])
            filter_end_date = int(filter_date[1])
            all_dates = list(range(filter_start_date, filter_end_date + 1))
            # random.shuffle(all_dates)  # Randomize the order of dates
            # for i in range(filter_start_date, filter_end_date + 1):
            # for i in range(filter_end_date, filter_start_date - 1, -1):
            # Loop through the shuffled dates
            for i in all_dates:
                date_picker_green_day = f"//div[contains(@class,'ui-datepicker-group-{calendar}')]//tr/td[contains(@class,'greenday')]/a[text()='" + str(i) + "']"
                if self.isElementPresent(driver, date_picker_green_day):
                    print("Slot Found For Month: ", num)
                    # ✅ Early alert when green day detected
                    try:
                        import winsound
                        winsound.Beep(1500, 1000)  # shorter beep when green day found
                    except:
                        print("🔔 GREEN DAY DETECTED!")
                    self.ClickElement(driver, date_picker_green_day)
                    # driver.execute_script("window.alert = function() {};")  # Override alert to prevent any alert popup
                    # time.sleep(random.uniform(0.2, 0.5))  # Wait between 1 and 3 seconds
                    slot_times_path = "//input[@name='schedule-entries']"
                    allocations_path = "//input[@name='schedule-entries']/parent::label/ancestor::td/following-sibling::td[2]"
                    allocations_error_path = "//div[contains(@class,'alert-danger')]"
                    # self.wait_for_element_to_visible(driver, allocations_path, 20)
                    # self.wait_for_any_element_to_be_visible(driver, allocations_path, allocations_error_path, 30)
                    self.wait_for_any_element_to_be_visible(driver, allocations_path, allocations_error_path, 60)
                    # time.sleep(random.uniform(3, 4))  # Wait between 1 and 3 seconds
                    time.sleep(random.uniform(0.5, 1))  # Wait between 1 and 3 seconds
                    # driver.execute_script("window.alert = function() {};")  # Override alert to prevent any alert popup
                    if self.isElementPresent(driver, slot_times_path):
                        slot_times = self.getElements(driver, slot_times_path)
                        allocations = self.getListofText(driver, allocations_path, By.XPATH)
                        print("All Available Allocations: " + str(allocations))
                        if allocations:
                            allocations = [int(x) for x in allocations if x]
                            allocations.sort(reverse=True)
                            allocations = [str(x) for x in allocations if x]
                        else:
                            allocations = []
                        # Initialize a dictionary to keep track of processed allocations
                        allocation_counts = {}
                        for allocation in allocations:
                            print("Current Allocation: " + str(allocation))
                            if allocation not in allocation_counts:
                                allocation_counts[allocation] = 1
                            else:
                                allocation_counts[allocation] += 1

                            # Get the count of processed allocations for the current value
                            count = allocation_counts[allocation]
                            # Construct XPath for the current allocation based on its count
                            allocation_xpath = "(" + allocations_path + "[.=" + str(allocation) + "])[" + str(count) + "]"
                            if self.isElementPresent(driver, allocation_xpath + "/preceding-sibling::td[2]//input"):
                                # self.ClickElement(driver, allocation_xpath + "/preceding-sibling::td[2]//input")
                                # self.ScrolltoView(driver, allocation_xpath + "/preceding-sibling::td[2]//input", By.XPATH, Pos_Center=True)
                                # time.sleep(random.uniform(0.2, 0.3))  # Wait between 1 and 3 seconds
                                self.ClickElementWithJS(driver, allocation_xpath + "/preceding-sibling::td[2]//input")
                                # driver.execute_script("window.alert = function() {};")  # Override alert to prevent any alert popup

                                submit_btn_not_disabled_path = '//input[@type="submit" and not (@disabled)]'
                                self.wait_for_element_to_visible(driver, submit_btn_not_disabled_path, 5)
                                # time.sleep(random.uniform(0.2, 0.3))  # Wait between 1 and 3 seconds
                                # driver.execute_script("window.alert = function() {};")  # Override alert to prevent any alert popup

                                if self.isElementPresent(driver, submit_btn_not_disabled_path):
                                    print("Submit Button Found")
                                    slot_date_path = allocation_xpath + "/preceding-sibling::td[2]"
                                    slot_time_path = allocation_xpath + "/preceding-sibling::td[1]"
                                    slot_date = self.getElementText(driver, slot_date_path)
                                    slot_time = self.getElementText(driver, slot_time_path)
                                    # self.ClickElement(driver, submit_btn_not_disabled_path)
                                    # self.ScrolltoView(driver, submit_btn_not_disabled_path, By.XPATH, Pos_Center=True)
                                    # time.sleep(random.uniform(0.2, 0.3))  # Wait between 1 and 3 seconds
                                    # self.ClickElementWithJS(driver, submit_btn_not_disabled_path)
                                    # time.sleep(random.uniform(0.3, 0.5))  # Wait between 1 and 3 seconds
                                    self.ClickElementWithJS(driver, submit_btn_not_disabled_path)
                                    print("✅ Submit button clicked!")
                                    # time.sleep(random.uniform(0.3, 0.5))  # Wait between 1 and 3 seconds
                                    # driver.execute_script("window.alert = function() {};")  # Override alert to prevent any alert popup

                                    # self.ClickElementWithJS(driver, submit_btn_not_disabled_path)
                                    ofc_post_label = "//label[text()='OFC Post']"
                                    slot_no_longer_avail_path = "//div[.='The selected appointment time is no longer available, please select another appointment time.']"
                                    if len(slot_times) > 1:
                                        self.wait_for_element_to_visible(driver, slot_no_longer_avail_path, 40)
                                        # driver.execute_script("window.alert = function() {};")  # Override alert to prevent any alert popup
                                    else:
                                        self.wait_for_element_to_visible(driver, slot_no_longer_avail_path, 60)
                                        # driver.execute_script("window.alert = function() {};")  # Override alert to prevent any alert popup

                                    if not self.isElementPresent(driver, ofc_post_label):
                                        # driver.execute_script("window.alert = function() {};")  # Override alert to prevent any alert popup

                                        print("Slot City: " + post_city)
                                        print("Slot Date: " + str(slot_date))
                                        print("Slot Time: " + str(slot_time))
                                        print("Slot Allocation: " + allocation)
                                        try:
                                            import winsound
                                            winsound.Beep(1000, 3000)  # beep at 1000Hz for 3 seconds
                                        except:
                                            print("🔔 SLOT FOUND ALERT!")

                                        waitforinput = input("Clicked on Submit Button Successfully, OFC Page Navigates to Next Page Successfully. Do you want continue the program ? Yes/No.")
                                        # driver.execute_script("window.alert = function() {};")  # Override alert to prevent any alert popup

                                        if waitforinput.lower() == 'no':
                                            slot_not_found = False
                                            sys.exit()
                                        else:
                                            print("Program is Continue.")
                                            # driver.execute_script("window.alert = function() {};")  # Override alert to prevent any alert popup

                                    else:
                                        print("It seems like Submit Button is Clicked but OFC Page Doesn't Navigates to the Next Page So Program is Continue & Looking Forward for any other Slot Time or Green Day to Catch.")
                                        # driver.execute_script("window.alert = function() {};")  # Override alert to prevent any alert popup

    def getListofText(self, driver, locator, locatorType):

        elements = self.getElements(driver, locator, locatorType)
        elemsList = []
        try:
            for element in elements:
                if element is not None:
                    elemsList.append(element.text)
        except Exception as ex:
            # print("getListofText error: " + str(ex))
            # Log(LogType.ERROR, str("Something Went wrong can't find text in element"))
            print("List of Text Not Found")

        return elemsList

    def getElement(self, driver, locator, locaType=By.XPATH):
        element = False
        try:
            elements_list = self.getElements(driver, locator, locaType)

            if elements_list is not None and len(elements_list) > 0:
                element = elements_list[0]

            if element is not None and element != False:
                return element
            else:
                print(str("Element Not Found with Locator :: " + locator + "and Locator Type = XPath"))
                return False

        except Exception as ex:
            print(str("Element Not Found with Locator :: " + locator + "and Locator Type = XPath, Error:" + str(ex)))
            element = False
        return element

    def ScrolltoView(self, driver, locator, locaType, Pos_Center=False):

        try:
            element = self.getElement(driver, locator, locaType)
            if element not in [False, None, ""]:
                Params = ""
                if Pos_Center == True:
                    Params = "{block: 'center'}"
                driver.execute_script("arguments[0].scrollIntoView(" + str(Params) + ");", element)
            else:
                print(str("Element Not Found " + locator))

        except Exception as ex:
            print(str("ScrolltoView: Error: " + str(ex)))

    def clear_browser_cache(self, driver):
        try:
            print("Clearing Browser Cache, Session, & Cookies before Pause")
            driver.delete_all_cookies()
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
        except Exception as clear_exc:
            print(f"Error clearing browser Cache, Session, & Cookies: {clear_exc}")


obj_class_us_visa = UsVisaScheduling()
obj_class_us_visa.ofc_post()
obj_class_us_visa.select_months()
obj_class_us_visa.us_visa_sch_nav()

