from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def click_element_by_id(driver, element_id):
    try:
        element = driver.find_element(By.ID, element_id)
        element.click()
        print(f"Element with id '{element_id}' clicked successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Optional: Run Chrome in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get("https://www.example.com")  # Replace with the URL of the website you want to test

    element_id = "your_element_id"  # Replace with the actual id of the element you want to click
    click_element_by_id(driver, element_id)

    driver.quit()