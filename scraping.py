from SeleniumTools import SeleniumTools
from CsvReader import CsvReader
from dotenv import load_dotenv
import os

# .env dosyasını yükle
load_dotenv()

# .env dosyasından kullanıcı adı ve şifreyi al
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")


if __name__ == "__main__":
    selenium_tools = SeleniumTools(headless=False)
    selenium_tools.open_url("https://app.apollo.io/#/login")  # Açmak istediğiniz web sayfasının URL'sini buraya yazın
    # Burada kullanıcı adı ve şifreyi kullanabilirsiniz
    print(f"Kullanıcı Adı: {username}, Şifre: {password}")
    selenium_tools.send_keys_by_name("email", username)
    selenium_tools.send_keys_by_name("password", password, return_key=True)
    while 1:
        #tuşa basana kadar bekle
        pass
    #selenium_tools.quit()