import tkinter as tk
from tkinter import messagebox
import os
base_path = os.path.dirname(os.path.abspath(__file__))
print(f"Base Path: {base_path}")
def on_submit():
    name = entry_name.get()
    age = entry_age.get()
    messagebox.showinfo("Bilgi", f"Ad: {name}\nYaş: {age}")

# Ana pencereyi oluştur
root = tk.Tk()
root.title("Basit Tkinter Arayüzü")
root.geometry("300x200")

# Etiketler ve Giriş Kutuları
label_name = tk.Label(root, text="Adınızı Girin:")
label_name.pack(pady=5)
entry_name = tk.Entry(root)
entry_name.pack(pady=5)

label_age = tk.Label(root, text="Yaşınızı Girin:")
label_age.pack(pady=5)
entry_age = tk.Entry(root)
entry_age.pack(pady=5)

# Gönder Butonu
submit_button = tk.Button(root, text="Gönder", command=on_submit)
submit_button.pack(pady=10)

# Pencereyi çalıştır
root.mainloop()
