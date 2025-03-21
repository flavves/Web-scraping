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
import random
import threading
import smtplib
import time
import random
import pandas as pd
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import logging
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
import json
import threading
stop_event = threading.Event()
stop_event_mail = threading.Event()
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
global selenium_tools,BOT_STATUS,BOT_DESCRIPTION,MAIL_TEMPLATE,EXCELL_PATH,PDF_PATHS,MAIL_TEMPLATE_SUBJECT,MAIL_TEMPLATE_BODY,JPG_PATHS

BOT_STATUS = "Pasif"
BOT_DESCRIPTION = "Veri çekme işlemi başlatılmadı"
EXCELL_PATH = ""
MAIL_TEMPLATE = ""
MAIL_TEMPLATE_SUBJECT = ""
MAIL_TEMPLATE_BODY = ""
PDF_PATHS = []
JPG_PATHS = []
companies = []


# Ana pencereyi oluştur
root = tk.Tk()
root.title("Apollo Otomasyon")
root.geometry("1080x600")
# DETAYLAR
bot_status_var = tk.StringVar()
bot_description_var = tk.StringVar()



# .env dosyasını yükle
load_dotenv()
base_path = os.path.dirname(os.path.abspath(__file__))
print(f"Base Path: {base_path}")
logger.info(f"Base Path: {base_path}")
# .env dosyasından kullanıcı adı ve şifreyi al

config_path = 'config.json'
if not os.path.exists(config_path):
    default_config = {
        'smtp_server': '',
        'smtp_port': '',
        'email_address': '',
        'email_password': '',
        'username': '',
        'password': ''
    }
    with open(config_path, 'w') as config_file:
        json.dump(default_config, config_file, indent=4)
        print("config.json dosyası oluşturuldu.")
        logger.info("config.json dosyası oluşturuldu.")

with open(config_path, 'r') as config_file:
    config = json.load(config_file)

username = config["username"]
password = config["password"]



def login():
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    username = config["username"]
    password = config["password"]


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
        global selenium_tools,BOT_STATUS,BOT_DESCRIPTION,MAIL_TEMPLATE_SUBJECT,EXCELL_PATH,MAIL_TEMPLATE_BODY

        file_path = "Emails.xlsx"
        
        if(len(mails)==0):
            print("Mail toplanamadı db kaydı yapılamadı")
            logger.info("Mail toplanamadı db kaydı yapılamadı")
            return -1
        # Check if the file exists
        if os.path.exists(file_path):
            # Load existing data
            df = pd.read_excel(file_path)
        else:
            # Create a new DataFrame if the file does not exist
            df = pd.DataFrame(columns=["Şirket", "Mail", "Çalışan Adı"])
        print("Dataframe -> ",df)
        logger.info(f"Dataframe -> {df}")
        # Append new data
        new_data = pd.DataFrame([{"Şirket": company, "Mail": mail, "Çalışan Adı": name} for mail, name in zip(mails, names)])
        df = pd.concat([df, new_data], ignore_index=True)
        
        # Save the DataFrame to Excel
        df.to_excel(file_path, index=False)
        print("Kaydedilen Dataframe OK -> ",df," -> ",file_path)
        logger.info(f"Kaydedilen Dataframe OK -> {df} -> {file_path}")

        return 1



def collect_mails(company,mails,names):
    for i in range(4):
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
    if(len(names)==0):
            print("Mail toplanamadı")
            logger.info("Mail toplanamadı")
            BOT_STATUS = "Pasif | Mail toplanamadı"
            BOT_DESCRIPTION = "Mail toplanamadı"
            update_status()
            return -1
    res=saveToExcel(company, mails, names)
    try:
        if res==-1:
            print("Mail toplanamadı")
            logger.info("Mail toplanamadı")
            BOT_STATUS = "Pasif | Mail toplanamadı"
            BOT_DESCRIPTION = "Mail toplanamadı"
            update_status()
            return -1
        else:
            print("Mail toplandı")
            logger.info("Mail toplandı")
            return 1
    except:
        print("Mail toplanamadı")
        logger.info("Mail toplanamadı")
        return -1


def delete_before_searches():
    try:
        selenium_tools.click_element_by_xpath("//div[contains(@class, 'zp-badge')]")
    except:
        pass
    
def start():
    global selenium_tools,BOT_STATUS,BOT_DESCRIPTION,MAIL_TEMPLATE,EXCELL_PATH,MAIL_TEMPLATE_SUBJECT,MAIL_TEMPLATE_BODY

    stop_event.clear()

    csvReader = FileReader(EXCELL_PATH)
    data = csvReader.read_file()
    companies = csvReader.get_companies()
    #companies= companies[0:10]
    #print(companies)
    logger.info(f"Şirketler -> {companies}")

    selenium_tools = SeleniumTools(headless=False)
    selenium_tools.open_url("https://app.apollo.io/#/login")  # Açmak istediğiniz web sayfasının URL'sini buraya yazın
    # Burada kullanıcı adı ve şifreyi kullanabilirsiniz
    login()
    print("Giriş yapıldı")
    logger.info("Giriş yapıldı")
    BOT_STATUS = "Aktif | Veri çekme işlemi başladı"
    BOT_DESCRIPTION = "Veri çekme işlemi başladı"
    update_status()
    mailsCounter=0
    companyCounter=0
    # Son kaldığı şirketi txt dosyasından oku
    last_company = None
    try:
        with open("last_company.txt", "r") as file:
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
        if stop_event.is_set():
            BOT_STATUS = "Pasif | Bot kullanıcı tarafından durduruldu"
            BOT_DESCRIPTION = "Bot kullanıcı tarafından durduruldu"
            update_status()
            break  # Döngüden çık
        # Son kaldığı şirketi txt dosyasına kaydet
        with open("last_company.txt", "w") as file:
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
        res=collect_mails(company,mails,names)
        if res==-1:
            logger.info("Mail toplanamadı program durduruldu kredi kontrol edilsin")
            BOT_STATUS = "Pasif | Mail toplanamadı program durduruldu kredi kontrol edilsin"
            BOT_DESCRIPTION = "Mail toplanamadı program durduruldu kredi kontrol edilsin"
            update_status()
            break

        mailsCounter+=len(mails)
        companyCounter+=1
        print("________________________________________________________")
        logger.info("________________________________________________________")
        
        print("Toplam şirket sayısı -> ",companyCounter," / ",len(companies), "| Toplam mail sayısı -> ",mailsCounter)
        BOT_DESCRIPTION = f"Toplam şirket sayısı -> {companyCounter} / {len(companies)} | Toplam mail sayısı -> {mailsCounter}"
        logger.info(f"Toplam şirket sayısı -> {companyCounter} / {len(companies)} | Toplam mail sayısı -> {mailsCounter}")
        BOT_DESCRIPTION += f"Şirketlerin %{companyCounter/len(companies)*100:.2f}'si tamamlandı \nToplanan mail sayısı -> {mailsCounter}"

        print("Şirketlerin %",companyCounter/len(companies)*100,"'si tamamlandı")
        logger.info(f"Şirketlerin %{companyCounter/len(companies)*100}'si tamamlandı")
        BOT_DESCRIPTION += f"Şirketlerin %{companyCounter / len(companies) * 100:.2f}'si tamamlandı"
        update_status()
        
        print("________________________________________________________")      

        delay = random.randint(180, 300)
        #delay = random.randint(10, 15)

        logging.info(f"Bekleniyor: {delay} saniye...")
        BOT_DESCRIPTION += f"Bekleniyor: {delay} saniye..."
        time.sleep(delay)
        
    print("Toplanan mail sayısı -> ",mailsCounter)
    logger.info(f"Toplanan mail sayısı -> {mailsCounter}")
    selenium_tools.quit()
    print("Program sonlandı")
    logger.info("Program sonlandı")

def start_thread():
    print("Veri çekme işlemi başlatılıyor")
    logging.info("Veri çekme işlemi başlatılıyor")
    thread = threading.Thread(target=start, daemon=True)
    thread.start()
    print("Veri çekme işlemi başlatıldı")
    logging.info("Veri çekme işlemi başlatıldı")


def stop():
    global BOT_STATUS
    BOT_STATUS = "Pasif | Veri çekme işlemi durduruldu"
    update_status()
    print("Veri çekme işlemi durduruldu")
    logger.info("Veri çekme işlemi durduruldu")
    stop_event.set()



def update_status():
    global BOT_STATUS, BOT_DESCRIPTION

    #print("Bot Durumu: ", BOT_STATUS)
    #print("Son Durum: ", BOT_DESCRIPTION)

    logger.info(f"Bot Durumu: {BOT_STATUS}")
    logger.info(f"Son Durum: {BOT_DESCRIPTION}")

    try:
        bot_status_var.set(BOT_STATUS)
        bot_description_var.set(BOT_DESCRIPTION)
    except:
        try:
            root.after(0, lambda: bot_status_var.set(BOT_STATUS))
            root.after(0, lambda: bot_description_var.set(BOT_DESCRIPTION))
        except:
            pass



def selectExcellPath():
    global EXCELL_PATH,BOT_STATUS,BOT_DESCRIPTION
    file_path = filedialog.askopenfilename(
        title="Excel Dosyasını Seç",
        filetypes=[("Excel Dosyaları", "*.xlsx"), ("Tüm Dosyalar", "*.*")]
    )
    if file_path:
        print(f"Seçilen Excel Dosyası: {file_path}")
        logger.info(f"Seçilen Excel Dosyası: {file_path}")
        EXCELL_PATH = file_path
        
        BOT_STATUS = "Aktif | Excell Seçildi"
        BOT_DESCRIPTION = "Excel Dosyası Seçildi"
        update_status()
        
    else:
        print("Hiçbir dosya seçilmedi.")
        logger.info("Hiçbir dosya seçilmedi.")
        BOT_STATUS = "Pasif | Excell Seçilmedi"
        BOT_DESCRIPTION = "Excell Seçilmedi"
        EXCELL_PATH = ""
        update_status()
    update_status()

def MailTemplateSubject():
    global BOT_STATUS, MAIL_TEMPLATE,BOT_DESCRIPTION,MAIL_TEMPLATE_SUBJECT,MAIL_TEMPLATE_BODY
    file_path = filedialog.askopenfilename(
        title="Mail Başlık Dosyasını Seç",
        filetypes=[("Metin Dosyaları", "*.txt"), ("Tüm Dosyalar", "*.*")]
    )
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            MAIL_TEMPLATE_SUBJECT = file.read()
        print("Mail Şablonu Yüklendi")
        logger.info("Mail Şablonu Yüklendi")
        BOT_STATUS = "Aktif | Mail Şablonu Yüklendi"
        BOT_DESCRIPTION = "Mail Şablonu Yüklendi"
        update_status()
    else:
        print("Hiçbir dosya seçilmedi.")
        logger.info("Hiçbir dosya seçilmedi.")
        BOT_STATUS = "Pasif | Mail Şablonu Seçilmedi"
        BOT_DESCRIPTION = "Mail Şablonu Seçilmedi"
        update_status()

        

def MailTemplateBody():
    global BOT_STATUS, MAIL_TEMPLATE,BOT_DESCRIPTION,MAIL_TEMPLATE_BODY
    file_path = filedialog.askopenfilename(
        title="Mail Şablon Dosyasını Seç",
        filetypes=[("Metin Dosyaları", "*.txt"), ("Tüm Dosyalar", "*.*")]
    )
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            MAIL_TEMPLATE_BODY = file.read()
        print("Mail Şablonu Yüklendi")
        logger.info("Mail Şablonu Yüklendi")
        BOT_STATUS = "Aktif | Mail Şablonu Yüklendi"
        BOT_DESCRIPTION = "Mail Şablonu Yüklendi"
        update_status()
    else:
        print("Hiçbir dosya seçilmedi.")
        logger.info("Hiçbir dosya seçilmedi.")
        BOT_STATUS = "Pasif | Mail Şablonu Seçilmedi"
        BOT_DESCRIPTION = "Mail Şablonu Seçilmedi"
        update_status()

def selectJPGPaths():
    global BOT_STATUS, MAIL_TEMPLATE,BOT_DESCRIPTION,JPG_PATHS
    file_paths = filedialog.askopenfilenames(
        title="JPG Dosyalarını Seç",
        filetypes=[("JPG Dosyaları", "*.jpg"), ("Tüm Dosyalar", "*.*")]
    )
    if file_paths:
        print("Seçilen JPG Dosyaları:")
        for path in file_paths:
            print(path)
        JPG_PATHS = file_paths
        print("JPG Dosyaları Seçildi")
        logger.info("JPG Dosyaları Seçildi")
        BOT_STATUS = "Aktif | JPG Dosyaları Seçildi"
        BOT_DESCRIPTION = "JPG Dosyaları Seçildi"
        update_status()
    else:
        print("Hiçbir dosya seçilmedi.")
        JPG_PATHS = []
        logger.info("Hiçbir dosya seçilmedi.")
        BOT_STATUS = "Pasif | JPG Dosyaları Seçilmedi"
        BOT_DESCRIPTION = "JPG Dosyaları Seçilmedi"
        update_status()

def selectPDFPaths():
    global PDF_PATHS,BOT_STATUS,BOT_DESCRIPTION
    file_paths = filedialog.askopenfilenames(
        title="PDF Dosyalarını Seç",
        filetypes=[("PDF Dosyaları", "*.pdf"), ("Tüm Dosyalar", "*.*")]
    )
    if file_paths:
        print("Seçilen PDF Dosyaları:")
        for path in file_paths:
            print(path)
        PDF_PATHS = file_paths
        print("PDF Dosyaları Seçildi")
        logger.info("PDF Dosyaları Seçildi")
        BOT_STATUS = "Aktif | PDF Dosyaları Seçildi"
        BOT_DESCRIPTION = "PDF Dosyaları Seçildi"
        update_status()
    else:
        print("Hiçbir dosya seçilmedi.")
        PDF_PATHS = []
        logger.info("Hiçbir dosya seçilmedi.")
        BOT_STATUS = "Pasif | PDF Dosyaları Seçilmedi"
        BOT_DESCRIPTION = "PDF Dosyaları Seçilmedi"
        update_status()

def send_mail():
    global PDF_PATHS,JPG_PATHS,MAIL_TEMPLATE_SUBJECT,MAIL_TEMPLATE_BODY,EXCELL_PATH,BOT_DESCRIPTION,BOT_STATUS
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    smtp_server = config["smtp_server"]
    smtp_port = config["smtp_port"]
    email_address = config["email_address"]
    email_password = config["email_password"]

    #############################################3
    def read_excel(file_path):
        try:
            return pd.read_excel(file_path)
        except FileNotFoundError:
            logging.error(f"Dosya bulunamadı: {file_path}")
            return None
        except Exception as e:
            logging.error(f"Excel okuma hatası: {e}")
            return None

    def send_email(to_email, subject, body, attachments=[], image_paths=[]):
        try:
            msg = MIMEMultipart()
            msg['From'] = email_address
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            for image_path in image_paths:
                with open(image_path, 'rb') as img:
                    mime_image = MIMEImage(img.read())
                    mime_image.add_header('Content-ID', f'<{os.path.basename(image_path)}>')
                    msg.attach(mime_image)

            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                with open(attachment, 'rb') as file:
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment)}')
                msg.attach(part)

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_address, email_password)
            server.sendmail(email_address, to_email, msg.as_string())
            server.quit()

            logging.info(f"E-posta gönderildi: {to_email}")
        except smtplib.SMTPAuthenticationError:
            logging.error("SMTP kimlik doğrulama hatası. Şifrenizi kontrol edin.")
        except Exception as e:
            logging.error(f"E-posta gönderme hatası: {e}")

    def send_bulk_emails(excel_file, subject_template, body_template, attachments=[], image_paths=[]):
        global BOT_STATUS, BOT_DESCRIPTION
        stop_event_mail.clear()
        logging.info("Toplu mail gönderme başladı.")
        data = read_excel(excel_file)
        if data is None:
            return

        # Son gönderilen maili txt dosyasından oku
        last_email = None
        try:
            with open("last_mailsender.txt", "r") as file:
                last_email = file.read().strip()
        except FileNotFoundError:
            pass

        start_index = 0
        if last_email:
            try:
                start_index = data[data['Mail'] == last_email].index[0] + 1
            except IndexError:
                logging.warning("Son gönderilen mail bulunamadı, baştan başlanacak.")

        for index, row in data.iloc[start_index:].iterrows():
            if stop_event_mail.is_set():
                BOT_STATUS = "Pasif | Bot kullanıcı tarafından durduruldu"
                BOT_DESCRIPTION = "Bot kullanıcı tarafından durduruldu"
                update_status()
                break  # Döngüden çık

            to_email = row['Mail']
            company_name = row['Şirket']
            name = row['Çalışan Adı']
            logging.info(f"Gönderilecek e-posta: {to_email}, Şirket: {company_name}, Çalışan Adı: {name}")

            subject = subject_template.replace("{company}", company_name)
            subject = subject.replace("{name}", name)

            body = body_template.replace("{company}", company_name)
            body = body.replace("{name}", name)
            logging.info(f"Konu: {subject}, Gövde: {body}, Ekler: {attachments}")

            send_email(to_email, subject, body, attachments, image_paths)
            logging.info("Mail gönderildi.")

            # Son gönderilen maili txt dosyasına kaydet
            with open("last_mailsender.txt", "w") as file:
                file.write(to_email)
                logging.info(f"Son gönderilen mail kaydedildi: {to_email}")

            delay = random.randint(180, 520)
            logging.info(f"Bekleniyor: {delay} saniye...")
            print(f"Bekleniyor: {delay} saniye...")
            time.sleep(delay)
            print("Mail Gönderildi")

        logging.info("Toplu mail gönderme tamamlandı.")


    ##############################################


    excel_path = "Emails.xlsx"
    subject_template = MAIL_TEMPLATE_SUBJECT

    body_template = MAIL_TEMPLATE_BODY

    attachments = PDF_PATHS

    image_paths = JPG_PATHS

    image_html = ''.join([f'<img src="cid:{os.path.basename(image)}">' for image in image_paths])
    body_template = body_template.replace("{images}", image_html)
    logger.info("Mail Gönderme işlemi başlatıldı")
    BOT_STATUS = "Aktif | Mail Gönderme işlemi başlatıldı"
    BOT_DESCRIPTION = "Mail Gönderme işlemi başlatıldı"
    update_status()

    send_bulk_emails(excel_path, subject_template, body_template, attachments, image_paths)
    print("Mail Gönderme işlemi tamamlandı")
    logger.info("Mail Gönderme işlemi tamamlandı")
    BOT_STATUS = "Pasif | Mail Gönderme işlemi tamamlandı"
    BOT_DESCRIPTION = "Mail Gönderme işlemi tamamlandı"
    update_status()

def mail_stop():
    global BOT_STATUS
    BOT_STATUS = "Pasif | Mail GÖnderme işlemi durduruldu"
    update_status()
    print(" Mail GÖnderme işlemi durduruldu")
    logger.info(" Mail GÖnderme işlemi durduruldu")
    stop_event_mail.set()

def send_mail_thread():
    print("Mail Gönderme başlatılıyor")
    logging.info("Mail Gönderme başlatılıyor")
    thread = threading.Thread(target=send_mail, daemon=True)
    thread.start()
    print("Mail Gönderme başlatıldı")
    logging.info("Mail Gönderme başlatıldı")


# Giriş kutularını global olarak tanımla
entry_smtp = tk.Entry(root)
entry_port = tk.Entry(root)
entry_mail = tk.Entry(root)
entry_pass = tk.Entry(root, show="*")  # Şifre gizli
entry_username = tk.Entry(root)
entry_passUsername = tk.Entry(root, show="*")  # Şifre gizli

def load_config():
    """Konfigürasyonu JSON dosyasından yükler ve giriş kutularına ekler."""
    config_path = os.path.join('config.json')
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
    with open('config.json', 'w') as f:
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
tk.Button(root, text="Mail Konu Şablonu Seç", command=MailTemplateSubject).grid(row=7, column=15, columnspan=1, pady=5)
tk.Button(root, text="Mail Mesaj Şablonu Seç", command=MailTemplateBody).grid(row=7, column=16, columnspan=1, pady=5)
tk.Button(root, text="PDF Dosyalarını Seç", command=selectPDFPaths).grid(row=7, column=17, columnspan=1, pady=5)
tk.Button(root, text="JPG Dosyalarını Seç", command=selectJPGPaths).grid(row=7, column=18, columnspan=1, pady=5)

tk.Label(root, text="Apollo Veri Çek").grid(row=8, column=0, columnspan=1, pady=5)

tk.Button(root, text="Başla", command=start_thread).grid(row=9, column=0, columnspan=1, pady=5)
tk.Button(root, text="Durdur", command=stop).grid(row=9, column=1, columnspan=1, pady=5)

tk.Label(root, text="Mail Gönder").grid(row=10, column=0, columnspan=1, pady=5)

tk.Button(root, text="Başla", command=send_mail_thread).grid(row=11, column=0, columnspan=1, pady=5)
tk.Button(root, text="Durdur", command=mail_stop).grid(row=11, column=1, columnspan=1, pady=5)

tk.Label(root, text="Bot Durumu: ").grid(row=0, column=2, columnspan=10, pady=5)
tk.Label(root, textvariable=bot_status_var).grid(row=0, column=13, columnspan=10, pady=5)

tk.Label(root, text="Son Durum: ").grid(row=1, column=2, columnspan=10, pady=5)
tk.Label(root, textvariable=bot_description_var).grid(row=1, column=13, columnspan=10, pady=5)

# Pencereyi çalıştır
root.mainloop()
