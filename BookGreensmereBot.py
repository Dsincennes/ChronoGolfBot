from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
from datetime import timedelta
import time
import yaml


class BookGreensmereBot:

    def __init__(self):
        with open('GreensmereInfo.yaml', 'r') as file:
            config = yaml.safe_load(file)
            self.username = config['username']
            self.password = config['password']
            self.clock = config['clock']
            self.guest = config['guests']

        # Create instance of chrome and open
        service = Service(r"C:\chromedriver.exe")
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get('https://www.chronogolf.ca/login#/reservations')
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)

    def login(self):
        # Login
        self.driver.find_element(By.NAME, 'email').send_keys(self.username)

        # Enter Password
        self.driver.find_element(By.XPATH, '//*[@id="sessionPassword"]').send_keys(self.password, Keys.RETURN)

    def load_page(self):
        # Wait page to load

        self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR,
                                                        'body > div.site-body > ui-view > div > div.dashboard > '
                                                        'div.dashboard-body.ng-scope > div > div.dashboard-body-header > '
                                                        'div:nth-child(2) > button')))

    def new_booking(self):
        # Click New Booking
        self.driver.find_element(By.CLASS_NAME, 'fl-button').click()

        # Book Tee Sheet
        time.sleep(1)
        self.driver.find_element(By.XPATH,
                                 '/html/body/div[2]/ui-view/div/div[2]/div[2]/div/div/affiliations-line/div/div[2]/div/button[1]').click()

        # Get current day then add 7 days
        current_date = datetime.now()
        next_week = datetime(current_date.year, current_date.month, current_date.day) + timedelta(days=7)
        future_day_to_book = next_week.strftime('%d')

        # Open calendar
        self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'datepicker-popdown')))
        self.driver.find_element(By.CLASS_NAME, 'datepicker-popdown').click()

        # Click future day to book
        future_day_element = self.driver.find_elements(By.XPATH, f"//span[contains(text(), '{future_day_to_book}')]")[0]
        future_day_element.click()

        # Scroll down within Calendar to find time
        time.sleep(3)
        inner_window = self.driver.find_element(By.CLASS_NAME, 'teesheet-body-item')
        ActionChains(self.driver).move_to_element(inner_window).click().perform()

        element_found = False

        while not element_found:
            ActionChains(self.driver).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
            self.driver.implicitly_wait(1)

            try:
                target_element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{self.clock}')]")
                target_element.find_element(By.XPATH,
                                            f"//div[contains(text(), '{self.clock}')]/following-sibling::div//div[@percent='100']").click()
                element_found = True
                break
            except:
                pass

        self.wait.until(ec.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Continue')]")))
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]").click()

        self.wait.until(
            ec.presence_of_element_located((By.XPATH, "(//span[@class='tab-label tab-label-ellipsis ng-binding'])[2]")))

        # Add 3 guests
        def add_guests(guest_to_add, index):
            self.driver.find_element(By.XPATH,
                                     f"(//span[@class='tab-label tab-label-ellipsis ng-binding'])[{index}]").click()
            time.sleep(2)
            self.driver.find_element(By.CLASS_NAME, 'ui-select-search').send_keys(f'{guest_to_add}')
            time.sleep(5)
            self.driver.find_element(By.CLASS_NAME, 'ui-select-search').send_keys('', Keys.RETURN)
            time.sleep(2)
            self.driver.find_element(By.XPATH, "//button[contains(text(), 'Add to reservation')]").click()
            time.sleep(2)

        for idx, guest in enumerate(self.guest, start=2):
            add_guests(guest, idx)

    def confirm_reserve(self):
        # Check box, and reserve
        self.driver.find_element(By.CLASS_NAME, 'fl-checkbox-input').send_keys(Keys.SPACE)
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Confirm Reservation')]").click()
