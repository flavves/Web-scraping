from tkinter import Tk, Label, Entry, Button, filedialog, messagebox
import json
import os

class AppUI:
    def __init__(self, master):
        self.master = master
        master.title("Email Sender Configuration")

        self.smtp_server_label = Label(master, text="SMTP Server:")
        self.smtp_server_label.grid(row=0, column=0)
        self.smtp_server_entry = Entry(master)
        self.smtp_server_entry.grid(row=0, column=1)

        self.smtp_port_label = Label(master, text="SMTP Port:")
        self.smtp_port_label.grid(row=1, column=0)
        self.smtp_port_entry = Entry(master)
        self.smtp_port_entry.grid(row=1, column=1)

        self.email_label = Label(master, text="Email Address:")
        self.email_label.grid(row=2, column=0)
        self.email_entry = Entry(master)
        self.email_entry.grid(row=2, column=1)

        self.password_label = Label(master, text="Email Password:")
        self.password_label.grid(row=3, column=0)
        self.password_entry = Entry(master, show='*')
        self.password_entry.grid(row=3, column=1)

        self.load_button = Button(master, text="Load Settings", command=self.load_settings)
        self.load_button.grid(row=4, column=0)

        self.save_button = Button(master, text="Save Settings", command=self.save_settings)
        self.save_button.grid(row=4, column=1)

        self.excel_button = Button(master, text="Select Excel File", command=self.select_excel_file)
        self.excel_button.grid(row=5, column=0)

        self.image_button = Button(master, text="Select Image Files", command=self.select_image_files)
        self.image_button.grid(row=5, column=1)

        self.excel_file_path = ""
        self.image_file_paths = []

    def load_settings(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.smtp_server_entry.delete(0, 'end')
                self.smtp_server_entry.insert(0, config.get('smtp_server', ''))
                self.smtp_port_entry.delete(0, 'end')
                self.smtp_port_entry.insert(0, config.get('smtp_port', ''))
                self.email_entry.delete(0, 'end')
                self.email_entry.insert(0, config.get('email_address', ''))
                self.password_entry.delete(0, 'end')
                self.password_entry.insert(0, config.get('email_password', ''))
            messagebox.showinfo("Info", "Settings loaded successfully.")
        else:
            messagebox.showwarning("Warning", "No configuration file found.")

    def save_settings(self):
        config = {
            'smtp_server': self.smtp_server_entry.get(),
            'smtp_port': self.smtp_port_entry.get(),
            'email_address': self.email_entry.get(),
            'email_password': self.password_entry.get()
        }
        with open('config.json', 'w') as f:
            json.dump(config, f)
        messagebox.showinfo("Info", "Settings saved successfully.")

    def select_excel_file(self):
        self.excel_file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if self.excel_file_path:
            messagebox.showinfo("Info", f"Selected Excel file: {self.excel_file_path}")

    def select_image_files(self):
        self.image_file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg")])
        if self.image_file_paths:
            messagebox.showinfo("Info", f"Selected image files: {', '.join(self.image_file_paths)}")

if __name__ == "__main__":
    root = Tk()
    app = AppUI(root)
    root.mainloop()