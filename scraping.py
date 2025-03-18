from SeleniumTools import SeleniumTools
from FileReader import FileReader
from dotenv import load_dotenv
import os
import time
import pandas as pd
import json
import tkinter as tk
from tkinter import messagebox

import logging
from logging.handlers import TimedRotatingFileHandler
from tkinter import filedialog


# Log dosyasının günlük olarak sıfırlanması
log_handler = TimedRotatingFileHandler(
    filename='scraping.log',  # Log dosya adı
    when='midnight',              # Her gece yarısı yenile
    interval=1,                   # 1 gün aralıklarla
    backupCount=0,                # Eski logları tutma, sadece en günceli olsun
    encoding='utf-8'              # Türkçe karakter sorunlarını önlemek için
)

# Log formatını ayarla
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

# Logger oluştur
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
# DETAYLAR

BOT_STATUS = "Pasif"
BOT_DESCRIPTION = "Veri çekme işlemi başlatılmadı"
EXCELL_PATH = ""
MAIL_TEMPLATE = ""

# DETAYLAR




# .env dosyasını yükle
load_dotenv()
base_path = os.path.dirname(os.path.abspath(__file__))
print(f"Base Path: {base_path}")
logger.info(f"Base Path: {base_path}")
# .env dosyasından kullanıcı adı ve şifreyi al

with open(base_path+'/config.json', 'r') as config_file:
    config = json.load(config_file)

username = config["username"]
password = config["password"]

csvReader = FileReader(base_path+"/files/Companies.csv")
data = csvReader.read_file()
companies = csvReader.get_companies()
#companies= companies[0:10]
#print(companies)
logger.info(f"Şirketler -> {companies}")

def login():
    print(f"Kullanıcı Adı: {username}, Şifre: {password}")
    logger.info(f"Kullanıcı Adı: {username}, Şifre: {password}")
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
    res=selenium_tools.click_element_by_xpath("//a[span[text()='" + company_name + "']]")
    if res==False:
        selenium_tools.click_element_by_xpath('//*[@id="table-row-0"]/div[1]/div[2]')
    time.sleep(5)


def saveToExcel(company, mails, names):
        file_path = base_path+"/files/Emails.xlsx"
        
        # Check if the file exists
        if os.path.exists(file_path):
            # Load existing data
            df = pd.read_excel(file_path)
        else:
            # Create a new DataFrame if the file does not exist
            df = pd.DataFrame(columns=["Şirket", "Mail", "Çalışan Adı"])
        
        # Append new data
        new_data = pd.DataFrame([{"Şirket": company, "Mail": mail, "Çalışan Adı": name} for mail, name in zip(mails, names)])
        df = pd.concat([df, new_data], ignore_index=True)
        
        # Save the DataFrame to Excel
        df.to_excel(file_path, index=False)



def collect_mails(company,mails,names):
    for i in range(5):
        try:
            #bu sırayla erişim verilmemiş mail adreslerini açıyor. burada 5 tane açıksa hiç tıklama yapılsın ilerde
            selenium_tools.click_element_by_xpath("//button[contains(@class, 'zp-button') and div[text()='Access email']]")
            time.sleep(1)
            mail=selenium_tools.get_text_by_xpath("//span[contains(text(),'Verified')]/ancestor::div/following-sibling::div//span")
            print("Toplanan Mail ->",mail)
            logger.info(f"Toplanan Mail -> {mail}")
            mails.append(mail)
            time.sleep(1)
            selenium_tools.click_element_by_xpath("//img[contains(@src, 'copy.svg')]")
            time.sleep(1)
            try:
                #get name
                sonuclar=selenium_tools.get_network_logs()
                for sonuc in sonuclar:
                    try:
                        if "contact_emails" in sonuc["contacts"][0] and sonuc["contacts"][0]["contact_emails"]:
                            email_alt = sonuc["contacts"][0]["contact_emails"][0]["email"]
                            name = sonuc["contacts"][0]["name"]
                            names.append(name)
                            print(email_alt,name)  # Çıktı: jani@janakiram.com
                    except:
                        pass
            except:
                names.append("")
        except:
            names.append("")

    print("Collected Mails -> ",mails," Collected Names -> ",names)
    logger.info(f"Collected Mails -> {mails}, Collected Names -> {names}")
    saveToExcel(company, mails, names)


def delete_before_searches():
    try:
        selenium_tools.click_element_by_xpath("//div[contains(@class, 'zp-badge')]")
    except:
        pass
    
def start():
    global selenium_tools,BOT_STATUS,BOT_DESCRIPTION
    selenium_tools = SeleniumTools(headless=False)
    selenium_tools.open_url("https://app.apollo.io/#/login")  # Açmak istediğiniz web sayfasının URL'sini buraya yazın
    # Burada kullanıcı adı ve şifreyi kullanabilirsiniz
    login()
    print("Giriş yapıldı")
    logger.info("Giriş yapıldı")
    BOT_STATUS = "Aktif | Veri çekme işlemi başladı"
    mailsCounter=0
    companyCounter=0
    # Son kaldığı şirketi txt dosyasından oku
    last_company = None
    try:
        with open(base_path+"/files/last_company.txt", "r") as file:
            last_company = file.read().strip()
    except FileNotFoundError:
        pass

    start_index = 0
    if last_company:
        try:
            start_index = companies.index(last_company) + 1
        except ValueError:
            pass
    counter = 0
    for company in companies[start_index:]:
        # Son kaldığı şirketi txt dosyasına kaydet
        with open(base_path+"/files/last_company.txt", "w") as file:
            file.write(company)
            print("Son kaldığı şirket kayıt tamamdır -> ", company)
            logger.info(f"Son kaldığı şirket kayıt tamamdır -> {company}")
        file.close()
        
        selenium_tools.open_url("https://app.apollo.io/#/companies")
        #companies tıkla
        print("Şirketler tıklanıyor")
        logger.info("Şirketler tıklanıyor")
        click_companies()
        if companyCounter != 0:
            print("onceki sirket siliniyor")
            logger.info("onceki sirket siliniyor")
            delete_before_searches()    
        print("Textbox tıklanıyor")
        logger.info("Textbox tıklanıyor")
        click_textBox()
        print("Şirket aranıyor -> ",company)
        logger.info(f"Şirket aranıyor -> {company}")
        write_company_name(company)
        print("Şirkete tıklanıyor")
        logger.info("Şirkete tıklanıyor")
        click_company(company)
        print("People tıklanıyor")
        logger.info("People tıklanıyor")
        click_people()
        mails=[]
        names=[]
        print("Mail toplanıyor")
        logger.info("Mail toplanıyor")
        collect_mails(company,mails,names)
        mailsCounter+=len(mails)
        companyCounter+=1
        print("________________________________________________________")
        logger.info("________________________________________________________")
        
        print("Toplam şirket sayısı -> ",companyCounter," / ",len(companies), "| Toplam mail sayısı -> ",mailsCounter)
        logger.info(f"Toplam şirket sayısı -> {companyCounter} / {len(companies)} | Toplam mail sayısı -> {mailsCounter}")
        BOT_DESCRIPTION = ("Şirketlerin %"+str(companyCounter/len(companies)*100)+"'si tamamlandı","Toplanan mail sayısı -> ",mailsCounter)+"\n"

        print("Şirketlerin %",companyCounter/len(companies)*100,"'si tamamlandı")
        logger.info(f"Şirketlerin %{companyCounter/len(companies)*100}'si tamamlandı")
        BOT_DESCRIPTION= "Şirketlerin %"+str(companyCounter/len(companies)*100)+"'si tamamlandı"
        
        print("________________________________________________________")      
        
    print("Toplanan mail sayısı -> ",mailsCounter)
    logger.info(f"Toplanan mail sayısı -> {mailsCounter}")
    selenium_tools.quit()
    print("Program sonlandı")
    logger.info("Program sonlandı")

def stop():
    global BOT_STATUS
    BOT_STATUS = "Pasif | Veri çekme işlemi durduruldu"
    print("Veri çekme işlemi durduruldu")
    logger.info("Veri çekme işlemi durduruldu")


def send_mail():
    global BOT_STATUS
    BOT_STATUS = "Aktif | Mail Gönderme işlemi başlatıldı"
    print("Mail Gönderme işlemi başlatılıyor")
    logger.info("Mail Gönderme işlemi başlatılıyor")

    print("Mail Gönderme işlemi tamamlandı")
    logger.info("Mail Gönderme işlemi tamamlandı")
    BOT_STATUS = "Pasif | Mail Gönderme işlemi tamamlandı"


def selectExcellPath():
    global EXCELL_PATH,BOT_STATUS
    file_path = filedialog.askopenfilename(
        title="Excel Dosyasını Seç",
        filetypes=[("Excel Dosyaları", "*.xlsx"), ("Tüm Dosyalar", "*.*")]
    )
    if file_path:
        print(f"Seçilen Excel Dosyası: {file_path}")
        logger.info(f"Seçilen Excel Dosyası: {file_path}")
        EXCELL_PATH = file_path
    else:
        print("Hiçbir dosya seçilmedi.")
        logger.info("Hiçbir dosya seçilmedi.")
        BOT_STATUS = "Pasif | Excell Seçilmedi"
        EXCELL_PATH = ""
    BOT_STATUS = "Aktif | Excell Seçildi"

def MailTemplate():
    global BOT_STATUS, MAIL_TEMPLATE
    file_path = filedialog.askopenfilename(
        title="Mail Şablon Dosyasını Seç",
        filetypes=[("Metin Dosyaları", "*.txt"), ("Tüm Dosyalar", "*.*")]
    )
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            MAIL_TEMPLATE = file.read()
        print("Mail Şablonu Yüklendi")
        logger.info("Mail Şablonu Yüklendi")
        BOT_STATUS = "Aktif | Mail Şablonu Yüklendi"
    else:
        print("Hiçbir dosya seçilmedi.")
        logger.info("Hiçbir dosya seçilmedi.")
        BOT_STATUS = "Pasif | Mail Şablonu Seçilmedi"

# Ana pencereyi oluştur
root = tk.Tk()
root.title("SMTP Ayarları")
root.geometry("900x600")

# Giriş kutularını global olarak tanımla
entry_smtp = tk.Entry(root)
entry_port = tk.Entry(root)
entry_mail = tk.Entry(root)
entry_pass = tk.Entry(root, show="*")  # Şifre gizli
entry_username = tk.Entry(root)
entry_passUsername = tk.Entry(root, show="*")  # Şifre gizli

def load_config():
    """Konfigürasyonu JSON dosyasından yükler ve giriş kutularına ekler."""
    config_path = os.path.join(base_path, 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            entry_smtp.delete(0, tk.END)
            entry_smtp.insert(0, config.get('smtp_server', ''))

            entry_port.delete(0, tk.END)
            entry_port.insert(0, config.get('smtp_port', ''))

            entry_mail.delete(0, tk.END)
            entry_mail.insert(0, config.get('email_address', ''))

            entry_pass.delete(0, tk.END)
            entry_pass.insert(0, config.get('email_password', ''))

            entry_username.delete(0, tk.END)
            entry_username.insert(0, config.get('username', ''))

            entry_passUsername.delete(0, tk.END)
            entry_passUsername.insert(0, config.get('password', ''))
    else:
        print("config.json dosyası bulunamadı.")

def save_config():
    """Giriş kutularındaki verileri JSON dosyasına kaydeder."""
    config = {
        'smtp_server': entry_smtp.get(),
        'smtp_port': entry_port.get(),
        'email_address': entry_mail.get(),
        'email_password': entry_pass.get(),
        'username': entry_username.get(),
        'password': entry_passUsername.get()
    }
    with open(base_path+'/config.json', 'w') as f:
        json.dump(config, f, indent=4)
    print("Ayarlar başarıyla kaydedildi.")

def toggle_password_visibility():
    """Şifreleri göster veya gizle"""
    if show_password_var.get():
        entry_pass.config(show="")  # Şifreleri göster
        entry_passUsername.config(show="")
    else:
        entry_pass.config(show="*")  # Şifreleri gizle
        entry_passUsername.config(show="*")

# Etiketler ve Giriş Kutuları
labels = ["SMTP Server:", "SMTP Port:", "E-Mail:", "Şifre:", "Kullanıcı Adı:", "Şifre:"]
entries = [entry_smtp, entry_port, entry_mail, entry_pass, entry_username, entry_passUsername]

for i, (label_text, entry) in enumerate(zip(labels, entries)):
    tk.Label(root, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky="e")
    entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")

# Şifreleri Göster Checkbox
show_password_var = tk.BooleanVar()
show_password_checkbox = tk.Checkbutton(root, text="Şifreleri Göster", variable=show_password_var, command=toggle_password_visibility)
show_password_checkbox.grid(row=6, column=0, columnspan=2, pady=5)

# Butonlar
tk.Button(root, text="Ayarları Kaydet", command=save_config).grid(row=7, column=0, columnspan=1, pady=5)
tk.Button(root, text="Ayarları Yükle", command=load_config).grid(row=7, column=1, columnspan=1, pady=5)
tk.Button(root, text="Excell Seç", command=selectExcellPath).grid(row=7, column=2, columnspan=1, pady=5)
tk.Button(root, text="Mail Şablonu Seç", command=MailTemplate).grid(row=7, column=15, columnspan=1, pady=5)

tk.Label(root, text="Apollo Veri Çek").grid(row=8, column=0, columnspan=1, pady=5)

tk.Button(root, text="Başla", command=start).grid(row=9, column=0, columnspan=1, pady=5)
tk.Button(root, text="Durdur", command=root.quit).grid(row=9, column=1, columnspan=1, pady=5)

tk.Label(root, text="Mail Gönder").grid(row=10, column=0, columnspan=1, pady=5)

tk.Button(root, text="Başla", command=start).grid(row=11, column=0, columnspan=1, pady=5)
tk.Button(root, text="Durdur", command=root.quit).grid(row=11, column=1, columnspan=1, pady=5)

tk.Label(root, text="Bot Durumu: ").grid(row=0, column=2, columnspan=10, pady=5)
tk.Label(root, text=BOT_STATUS).grid(row=0, column=13, columnspan=10, pady=5)

tk.Label(root, text="Son Durum: ").grid(row=1, column=2, columnspan=10, pady=5)
tk.Label(root, text=BOT_DESCRIPTION).grid(row=1, column=13, columnspan=10, pady=5)

# Pencereyi çalıştır
root.mainloop()