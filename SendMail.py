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

class EmailSender:
    def __init__(self, smtp_server, smtp_port, email_address, email_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_address = email_address
        self.email_password = email_password

    def read_excel(self, file_path):
        return pd.read_excel(file_path)

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

            print(f"E-posta gönderildi: {to_email}")
        except Exception as e:
            print(f"Hata: {e}")

    def send_bulk_emails(self, excel_file, subject_template, body_template, attachments=[], image_paths=[]):
        data = self.read_excel(excel_file)
        for index, row in data.iterrows():
            to_email = row['Email']
            company_name = row['Company']
            
            subject = subject_template.replace("{company}", company_name)
            body = body_template.replace("{company}", company_name)
            
            self.send_email(to_email, subject, body, attachments, image_paths)
            
            delay = random.randint(180, 300)  # 3-5 dakika rastgele bekleme
            print(f"Bekleniyor: {delay} saniye...\n")
            time.sleep(delay)

'''
# Kullanım Örneği
smtp_server = "smtp.gmail.com"
smtp_port = 587
email_address = "your_email@gmail.com"
email_password = "your_password"

email_sender = EmailSender(smtp_server, smtp_port, email_address, email_password)

excel_path = "emails.xlsx"  # E-posta adreslerinin bulunduğu Excel dosyası
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
attachments = ["brochure1.pdf", "brochure2.pdf"]
image_paths = ["offer_image1.jpg", "offer_image2.jpg"]  # E-posta içeriğine eklenecek görseller

# Generate image HTML tags
image_html = ''.join([f'<img src="cid:{os.path.basename(image)}">' for image in image_paths])
body_template = body_template.replace("{images}", image_html)

email_sender.send_bulk_emails(excel_path, subject_template, body_template, attachments, image_paths)
'''