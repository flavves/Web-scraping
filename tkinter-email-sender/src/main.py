import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
from email_sender import EmailSender
from ui.app_ui import AppUI

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Email Sender")
        
        self.config_file = 'config.json'
        self.smtp_server = ""
        self.smtp_port = ""
        self.email_address = ""
        self.email_password = ""
        
        self.load_config()
        
        self.ui = AppUI(self.root, self.smtp_server, self.smtp_port, self.email_address, self.email_password)
        self.ui.save_button.config(command=self.save_config)
        self.ui.select_excel_button.config(command=self.select_excel_file)
        self.ui.select_images_button.config(command=self.select_image_files)
        self.ui.send_email_button.config(command=self.send_bulk_emails)

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.smtp_server = config.get('smtp_server', '')
                self.smtp_port = config.get('smtp_port', '')
                self.email_address = config.get('email_address', '')
                self.email_password = config.get('email_password', '')

    def save_config(self):
        self.smtp_server = self.ui.smtp_entry.get()
        self.smtp_port = self.ui.port_entry.get()
        self.email_address = self.ui.email_entry.get()
        self.email_password = self.ui.password_entry.get()
        
        config = {
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'email_address': self.email_address,
            'email_password': self.email_password
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
        
        messagebox.showinfo("Info", "Configuration saved successfully!")

    def select_excel_file(self):
        excel_file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if excel_file:
            self.ui.excel_path.set(excel_file)

    def select_image_files(self):
        image_files = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg")])
        if image_files:
            self.ui.image_paths.set(", ".join(image_files))

    def send_bulk_emails(self):
        excel_file = self.ui.excel_path.get()
        image_paths = self.ui.image_paths.get().split(", ")
        
        email_sender = EmailSender(self.smtp_server, self.smtp_port, self.email_address, self.email_password)
        subject_template = "Hello, Special Offer!"
        body_template = "<html><body><p>Dear {company},</p><p>Your special offer is attached.</p>{images}</body></html>"
        
        attachments = []  # Add any attachments if needed
        email_sender.send_bulk_emails(excel_file, subject_template, body_template, attachments, image_paths)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()