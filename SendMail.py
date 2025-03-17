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
load_dotenv()

base_path = os.path.dirname(os.path.abspath(__file__))
print(f"Base Path: {base_path}")
# Loglama ayarları
#logging.basicConfig(filename='email_sender.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Log dosyasının günlük olarak sıfırlanması
log_handler = TimedRotatingFileHandler(
    filename='email_sender.log',  # Log dosya adı
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





class EmailSender:
    def __init__(self, smtp_server, smtp_port, email_address, email_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_address = email_address
        self.email_password = email_password

    def read_excel(self, file_path):
        try:
            return pd.read_excel(file_path)
        except FileNotFoundError:
            logging.error(f"Dosya bulunamadı: {file_path}")
            return None
        except Exception as e:
            logging.error(f"Excel okuma hatası: {e}")
            return None

    def send_email(self, to_email, subject, body, attachments=[], image_paths=[]):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
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

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.sendmail(self.email_address, to_email, msg.as_string())
            server.quit()

            logging.info(f"E-posta gönderildi: {to_email}")
        except smtplib.SMTPAuthenticationError:
            logging.error("SMTP kimlik doğrulama hatası. Şifrenizi kontrol edin.")
        except Exception as e:
            logging.error(f"E-posta gönderme hatası: {e}")

    def send_bulk_emails(self, excel_file, subject_template, body_template, attachments=[], image_paths=[]):
        logging.info("Toplu mail gönderme başladı.")
        data = self.read_excel(excel_file)
        if data is None:
            return

        for index, row in data.iterrows():
            to_email = row['Mail']
            company_name = row['Şirket']
            logging.info(f"Gönderilecek e-posta: {to_email}, Şirket: {company_name}")

            subject = subject_template.replace("{company}", company_name)
            body = body_template.replace("{company}", company_name)
            logging.debug(f"Konu: {subject}, Gövde: {body}, Ekler: {attachments}")

            self.send_email(to_email, subject, body, attachments, image_paths)
            logging.info("Mail gönderildi.")

            delay = random.randint(180, 300)
            logging.info(f"Bekleniyor: {delay} saniye...")
            time.sleep(delay)

# Kullanım Örneği
# Load configuration from config.json
with open(base_path+'/config.json', 'r') as config_file:
    config = json.load(config_file)

smtp_server = config["smtp_server"]
smtp_port = config["smtp_port"]
email_address = config["email_address"]
email_password = config["email_password"]

email_sender = EmailSender(smtp_server, smtp_port, email_address, email_password)

excel_path = base_path+"/files/Emails.xlsx"
subject_template = "Merhaba {company}, Özel Teklifimiz Var!"

body_template = """
<html>
    <body>
        <p>Sayın {company} Yetkilisi,</p>
        <p>Size özel teklifimizi ekte bulabilirsiniz.</p>
        {images}
    </body>
</html>
"""

attachments = [base_path+"/files/exPdf/py copy.pdf",
               base_path+"/files/exPdf/py.pdf"]

image_paths = [base_path+"/files/exPdf/fognoise.jpg",
               base_path+"/files/exPdf/AspectRatio.jpg"]

image_html = ''.join([f'<img src="cid:{os.path.basename(image)}">' for image in image_paths])
body_template = body_template.replace("{images}", image_html)

email_sender.send_bulk_emails(excel_path, subject_template, body_template, attachments, image_paths)