from SeleniumTools import SeleniumTools
from CsvReader import CsvReader
from dotenv import load_dotenv
import os
import time
import pandas as pd
# .env dosyasını yükle
load_dotenv()

# .env dosyasından kullanıcı adı ve şifreyi al
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

csvReader = CsvReader("/Users/batuhanokmen/Documents/yazilim/bionluk/Apollo/Web-scraping/files/Companies.csv")
data = csvReader.read_csv()
companies = csvReader.get_companies()
companies= companies[0:10]
print(companies)


def login():

    print(f"Kullanıcı Adı: {username}, Şifre: {password}")
    selenium_tools.send_keys_by_name("email", username)
    time.sleep(5)
    selenium_tools.send_keys_by_name("password", password, return_key=True)
    time.sleep(5)

def click_companies():
    selenium_tools.click_element_by_xpath("//a[@id='side-nav-companies']")
    time.sleep(5)

def click_textBox():
    # girdi kutusunu aç
    selenium_tools.click_element_by_xpath("(//div[contains(@class, 'zp-accordion-header')])[2]")
    time.sleep(5)
    selenium_tools.click_element_by_class_name("zp-select-main")
    time.sleep(5)
    
def click_people():
    selenium_tools.click_element_by_id("people")
    time.sleep(5)
    
def write_company_name(company_name):
    for i in company_name:
        print(i)      
        selenium_tools.send_keys_by_class_name("Select-input", i)
        time.sleep(0.5)
    selenium_tools.send_keys_by_class_name("Select-input", "", return_key=True)
    time.sleep(5)

def click_company(company_name):
    selenium_tools.click_element_by_xpath("//a[span[text()='" + company_name + "']]")
    time.sleep(5)

def collect_mails():
    mails=[]
    for i in range(5):
        try:
            #bu sırayla erişim verilmemiş mail adreslerini açıyor. burada 5 tane açıksa hiç tıklama yapılsın ilerde
            selenium_tools.click_element_by_xpath("//button[contains(@class, 'zp-button') and div[text()='Access email']]")
            time.sleep(2)
            #"//span[contains(text(),'Verified')]/ancestor::div/following-sibling::div//span"
            #bununla mail adresini almamız gerekiyor
            mail=selenium_tools.get_text_by_xpath("//span[contains(text(),'Verified')]/ancestor::div/following-sibling::div//span")
            print(mail)
            mails.append(mail)
            time.sleep(2)
            selenium_tools.click_element_by_xpath("//img[contains(@src, 'copy.svg')]")
        except:pass
    print("All Mails -> ",mails)
    return mails

def saveToExcel(company, mails):
    file_path = "/Users/batuhanokmen/Documents/yazilim/bionluk/Apollo/Web-scraping/files/Emails.xlsx"
    
    # Check if the file exists
    if os.path.exists(file_path):
        # Load existing data
        df = pd.read_excel(file_path)
    else:
        # Create a new DataFrame if the file does not exist
        df = pd.DataFrame(columns=["Şirket", "Mail"])
    
    # Append new data
    for mail in mails:
        df = df.append({"Şirket": company, "Mail": mail}, ignore_index=True)
    
    # Save the DataFrame to Excel
    df.to_excel(file_path, index=False)

if __name__ == "__main__":
    selenium_tools = SeleniumTools(headless=False)
    selenium_tools.open_url("https://app.apollo.io/#/login")  # Açmak istediğiniz web sayfasının URL'sini buraya yazın
    # Burada kullanıcı adı ve şifreyi kullanabilirsiniz
    login()
    for company in companies:
        selenium_tools.open_url("https://app.apollo.io/#/companies")
        #companies tıkla
        click_companies()
        click_textBox()
        write_company_name(company)
        click_company(company)
        click_people()
        mails=collect_mails()
        