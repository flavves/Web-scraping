from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import json
import pickle
class SeleniumTools:
    def __init__(self, headless=False, wait_time=60):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        # Ağ trafiğini yakalamak için performans loglarını aç
        self.caps = webdriver.DesiredCapabilities.CHROME
        self.caps["goog:loggingPrefs"] = {"performance": "ALL"}
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})  # ✅ Yeni yöntem

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, wait_time)
    
    
    def get_network_logs(self):
        """Tarayıcıdan yapılan ağ isteklerini alır ve detaylı bir şekilde yazdırır."""
        logs = self.driver.get_log("performance")
        
        request_details = {}  # İstekleri requestId ile eşleştirmek için
        
        for log in logs:
            try:
                log_data = json.loads(log["message"])["message"]

                # Gönderilen İstekleri (Request) Yakalama
                if log_data["method"] == "Network.requestWillBeSent":
                    request_id = log_data["params"]["requestId"]
                    url = log_data["params"]["request"]["url"]
                    method = log_data["params"]["request"]["method"]
                    headers = log_data["params"]["request"].get("headers", {})
                    post_data = log_data["params"]["request"].get("postData", "")

                    request_details[request_id] = {
                        "url": url,
                        "method": method,
                        "headers": headers,
                        "payload": post_data
                    }

                    print(f"\n🔹 [Request] {method} {url}")
                    print(f"   Headers: {json.dumps(headers, indent=2)}")
                    if post_data:
                        print(f"   Payload: {post_data}")

                # Gelen Yanıtları (Response) Yakalama
                if log_data["method"] == "Network.responseReceived":
                    request_id = log_data["params"]["requestId"]
                    url = log_data["params"]["response"]["url"]
                    status = log_data["params"]["response"]["status"]
                    headers = log_data["params"]["response"].get("headers", {})

                    print(f"\n🔸 [Response] {url} - Status: {status}")
                    print(f"   Headers: {json.dumps(headers, indent=2)}")

                    # Eğer istek detayları bulunursa, birlikte yazdıralım
                    if request_id in request_details:
                        req = request_details[request_id]
                        print(f"\n✅ [Full Transaction] {req['method']} {req['url']}")
                        print(f"   Request Headers: {json.dumps(req['headers'], indent=2)}")
                        if req['payload']:
                            print(f"   Request Payload: {req['payload']}")
                        print(f"   Response Headers: {json.dumps(headers, indent=2)}")

                    # RESPONSE BODY'Yİ ÇEKME (istek ID'si üzerinden)
                    response_body = self.get_response_body(request_id)
                    if response_body:
                        print(f"   📥 Response Body: {json.dumps(response_body, indent=2)}")

            except Exception as e:
                print(f"Error parsing network log: {e}")

    def get_response_body(self, request_id):
        """
        Belirtilen request_id için yanıt gövdesini alır.
        """
        try:
            response = self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
            body = response.get("body", "")
            if response.get("base64Encoded", False):  # Eğer body Base64 ile encode edilmişse
                import base64
                body = base64.b64decode(body).decode("utf-8")
            
            try:
                return json.loads(body)  # JSON formatında döndür
            except json.JSONDecodeError:
                return body  # Eğer JSON değilse, direkt string olarak döndür

        except Exception as e:
            print(f"❌ Response body alınamadı: {e}")
            return None

    
               
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
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
    
    def get_text_by_xpath(self, xpath):
        try:
            element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return element.text
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

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
                time.sleep(1)
                element.send_keys(Keys.RETURN)
            print(f"Text '{text}' sent to element with name '{name}' successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def click_element_by_class_name(self, class_name):
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
            element.click()
            print(f"Element with class name '{class_name}' clicked successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def send_keys_by_class_name(self, class_name, text, return_key=False):
        try:
            element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
            element.send_keys(text)
            
            if return_key:
                time.sleep(1)
                element.send_keys(text, Keys.RETURN)
            print(f"Text '{text}' sent to element with class name '{class_name}' successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def open_url(self, url):
        self.driver.get(url)

    def quit(self):
        self.driver.quit()
        
    def save_cookies(self, file_path):
        with open(file_path, "wb") as file:
            pickle.dump(self.driver.get_cookies(), file)
        file.close()
    
    def refresh(self):
        self.driver.refresh()
    
    def load_cookies(self, file_path):
        with open(file_path, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                self.driver.add_cookie(cookie)