import os
import subprocess
import pkg_resources
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet
from tkinter import Tk, messagebox, filedialog, Entry, Button, Label

# Ensure required packages are installed
required_packages = ['pycryptodomex', 'pillow', 'cryptography', 'tk']
for package in required_packages:
    try:
        pkg_resources.get_distribution(package)
    except pkg_resources.DistributionNotFound:
        print(f"{package} is not installed. Installing...")
        subprocess.check_call(['pip', 'install', package])

# Function to encrypt the folder
def encrypt_folder():
    folder_path = folderpath_entry.get()
    if folder_path == '':
        messagebox.showerror("Error", "Please select a folder to encrypt.")
        return
    if not os.path.exists(folder_path):
        messagebox.showerror("Error", "The selected folder does not exist.")
        return

    key = Fernet.generate_key()
    fernet = Fernet(key)

    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as file:
                file_data = file.read()
            encrypted_data = fernet.encrypt(file_data)
            with open(filepath, 'wb') as file:
                file.write(encrypted_data)

    send_encryption_key(key)
    messagebox.showinfo("Info", "Folder encrypted successfully.")

# Function to send the encryption key via email
def send_encryption_key(key):
    sender_email = 'your_email@example.com'
    receiver_email = 'receiver_email@example.com'
    subject = 'The Key for Encrypted Folder'
    message = f'The Key for Encrypted Folder: {key.decode()}'
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    username = "your_email@example.com"
    password = "your_password"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(username, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()

# Function to decrypt the folder
def decrypt_folder():
    folder_path = folderpath_entry.get()
    if folder_path == '':
        messagebox.showerror("Error", "Please select a folder to decrypt.")
        return
    if not os.path.exists(folder_path):
        messagebox.showerror("Error", "The selected folder does not exist.")
        return

    key = get_decryption_key()  # Implement a way to retrieve the key
    fernet = Fernet(key)

    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as file:
                encrypted_data = file.read()
            decrypted_data = fernet.decrypt(encrypted_data)
            with open(filepath, 'wb') as file:
                file.write(decrypted_data)

    messagebox.showinfo("Info", "Folder decrypted successfully.")

# Function to retrieve the decryption key
def get_decryption_key():
    # Implement the logic to retrieve the key, e.g., from a file or input dialog
    key = b'your_key'  # Replace with actual key retrieval logic
    return key

# Setup the GUI
root = Tk()
root.title("Folder Encryptor/Decryptor")

Label(root, text="Folder Path:").grid(row=0, column=0, padx=10, pady=10)
folderpath_entry = Entry(root, width=50)
folderpath_entry.grid(row=0, column=1, padx=10, pady=10)

Button(root, text="Encrypt Folder", command=encrypt_folder).grid(row=1, column=0, padx=10, pady=10)
Button(root, text="Decrypt Folder", command=decrypt_folder).grid(row=1, column=1, padx=10, pady=10)

root.mainloop()
