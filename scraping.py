from SeleniumTools import SeleniumTools
from CsvReader import CsvReader
from dotenv import load_dotenv
import os
import time
import pandas as pd
import json
import threading
class ApolloScraper:
    def __init__(self):
        load_dotenv()
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        print(f"Base Path: {self.base_path}")
        
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        
        self.username = config["username"]
        self.password = config["password"]
        self.csv_reader = CsvReader(self.base_path+"/files/Companies.csv")
        self.companies = self.csv_reader.get_companies()
        self.selenium_tools = SeleniumTools(headless=False)
      
    def login(self):
        print(f"Kullanıcı Adı: {self.username}, Şifre: {self.password}")
        self.selenium_tools.send_keys_by_name("email", self.username)
        time.sleep(5)
        self.selenium_tools.send_keys_by_name("password", self.password, return_key=True)
        time.sleep(5)
    
    def click_companies(self):
        self.selenium_tools.click_element_by_xpath("//a[@id='side-nav-companies']")
        time.sleep(5)
    
    def click_textBox(self):
        self.selenium_tools.click_element_by_xpath("(//div[contains(@class, 'zp-accordion-header')])[2]")
        time.sleep(5)
        self.selenium_tools.click_element_by_class_name("zp-select-main")
        time.sleep(5)
    
    def click_people(self):
        self.selenium_tools.click_element_by_id("people")
        time.sleep(5)
    
    def write_company_name(self, company_name):
        for i in company_name:
            print(i)
            self.selenium_tools.send_keys_by_class_name("Select-input", i)
            time.sleep(0.5)
        self.selenium_tools.send_keys_by_class_name("Select-input", "", return_key=True)
        time.sleep(5)
    
    def click_company(self, company_name):
        res = self.selenium_tools.click_element_by_xpath("//a[span[text()='" + company_name + "']]")
        if not res:
            self.selenium_tools.click_element_by_xpath('//*[@id="table-row-0"]/div[1]/div[2]')
        time.sleep(5)
    
    def save_to_excel(self, company, mails, names):
        file_path = self.base_path+"/files/Emails.xlsx"
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
        else:
            df = pd.DataFrame(columns=["Şirket", "Mail", "Çalışan Adı"])
        new_data = pd.DataFrame([{ "Şirket": company, "Mail": mail, "Çalışan Adı": name} for mail, name in zip(mails, names)])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(file_path, index=False)
    
    def collect_mails(self, company, mails, names):
        for _ in range(5):
            try:
                self.selenium_tools.click_element_by_xpath("//button[contains(@class, 'zp-button') and div[text()='Access email']]")
                time.sleep(1)
                mail = self.selenium_tools.get_text_by_xpath("//span[contains(text(),'Verified')]/ancestor::div/following-sibling::div//span")
                print("Toplanan Mail ->", mail)
                mails.append(mail)
                time.sleep(1)
                self.selenium_tools.click_element_by_xpath("//img[contains(@src, 'copy.svg')]")
                time.sleep(1)
                try:
                    sonuclar = self.selenium_tools.get_network_logs()
                    for sonuc in sonuclar:
                        try:
                            if "contact_emails" in sonuc["contacts"][0] and sonuc["contacts"][0]["contact_emails"]:
                                email_alt = sonuc["contacts"][0]["contact_emails"][0]["email"]
                                name = sonuc["contacts"][0]["name"]
                                names.append(name)
                                print(email_alt, name)
                        except:
                            pass
                except:
                    names.append("")
            except:
                names.append("")
        print("Collected Mails -> ", mails, " Collected Names -> ", names)
        self.save_to_excel(company, mails, names)
    
    def delete_before_searches(self):
        try:
            self.selenium_tools.click_element_by_xpath("//div[contains(@class, 'zp-badge')]")
        except:
            pass
    
    def run(self):
        self.selenium_tools.open_url("https://app.apollo.io/#/login")
        self.login()
        print("Giriş yapıldı")
        mails_counter = 0
        company_counter = 0
        last_company = None
        try:
            with open(self.base_path+"/files/last_company.txt", "r") as file:
                last_company = file.read().strip()
        except FileNotFoundError:
            pass
        start_index = self.companies.index(last_company) + 1 if last_company in self.companies else 0
        for company in self.companies[start_index:]:
            with open(self.base_path+"/files/last_company.txt", "w") as file:
                file.write(company)
            print("Şirketler tıklanıyor")
            self.click_companies()
            if company_counter != 0:
                print("onceki sirket siliniyor")
                self.delete_before_searches()
            print("Textbox tıklanıyor")
            self.click_textBox()
            print("Şirket aranıyor ->", company)
            self.write_company_name(company)
            print("Şirkete tıklanıyor")
            self.click_company(company)
            print("People tıklanıyor")
            self.click_people()
            mails, names = [], []
            print("Mail toplanıyor")
            self.collect_mails(company, mails, names)
            mails_counter += len(mails)
            company_counter += 1
            print(f"Toplam şirket sayısı -> {company_counter} / {len(self.companies)}, Toplam mail sayısı -> {mails_counter}")
        print("Toplanan mail sayısı ->", mails_counter)
        self.selenium_tools.quit()
        print("Program sonlandı")

if __name__ == "__main__":
    scraper = ApolloScraper()
    scraper.run()
