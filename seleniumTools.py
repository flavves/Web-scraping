from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
class SeleniumTools:
    def __init__(self, headless=False, wait_time=10):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, wait_time)

    def click_element_by_id(self, element_id):
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.ID, element_id)))
            element.click()
            print(f"Element with id '{element_id}' clicked successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def send_keys_by_id(self, element_id, text):
        try:
            element = self.wait.until(EC.presence_of_element_located((By.ID, element_id)))
            element.send_keys(text)
            print(f"Text '{text}' sent to element with id '{element_id}' successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def click_element_by_xpath(self, xpath):
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            element.click()
            print(f"Element with xpath '{xpath}' clicked successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def send_keys_by_xpath(self, xpath, text):
        try:
            element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            element.send_keys(text)
            print(f"Text '{text}' sent to element with xpath '{xpath}' successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def click_element_by_name(self, name):
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.NAME, name)))
            element.click()
            print(f"Element with name '{name}' clicked successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def send_keys_by_name(self, name, text, return_key=False):
        try:
            element = self.wait.until(EC.presence_of_element_located((By.NAME, name)))
            element.send_keys(text)
            if return_key:
                element.send_keys(Keys.RETURN)
            print(f"Text '{text}' sent to element with name '{name}' successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")


    def open_url(self, url):
        self.driver.get(url)

    def quit(self):
        self.driver.quit()
        
