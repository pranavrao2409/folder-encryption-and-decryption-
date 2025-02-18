import os
from tkinter import *
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256
from Cryptodome.Random import get_random_bytes
from cryptography.fernet import Fernet, InvalidToken
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Setup logging
logging.basicConfig(filename='encrypt_decrypt.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Function to generate a key from the image
def generate_key_from_image(image_path):
    with open(image_path, 'rb') as file:
        image_data = file.read()

    # Hash the image data to produce a 256-bit key
    hasher = SHA256.new(image_data)
    return hasher.digest()

# Padding function for AES encryption
def pad(data):
    return data + (16 - len(data) % 16) * b'\x00'

# Unpadding function for AES decryption
def unpad(data):
    return data.rstrip(b'\x00')

# Encrypt the files in the folder
def encrypt_folder(key, folder_path):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'rb') as file:
                file_data = file.read()

            cipher = AES.new(key, AES.MODE_ECB)
            encrypted_data = cipher.encrypt(pad(file_data))

            encrypted_file_path = file_path + ".enc"
            with open(encrypted_file_path, 'wb') as file:
                file.write(encrypted_data)

            os.remove(file_path)  # Remove original file

    messagebox.showinfo("Success", "Folder encrypted successfully!")

# Decrypt the files in the folder
def decrypt_folder(key, folder_path):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".enc"):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'rb') as file:
                    encrypted_data = file.read()

                cipher = AES.new(key, AES.MODE_ECB)
                decrypted_data = unpad(cipher.decrypt(encrypted_data))

                decrypted_file_path = file_path.replace(".enc", "")
                with open(decrypted_file_path, 'wb') as file:
                    file.write(decrypted_data)

                os.remove(file_path)  # Remove encrypted file

    messagebox.showinfo("Success", "Folder decrypted successfully!")

# Select and display image
def select_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if not file_path:
        return

    global selected_image_path
    selected_image_path = file_path

    img = Image.open(file_path)
    img = img.resize((250, 250), Image.Resampling.LANCZOS)
    imgtk = ImageTk.PhotoImage(img)

    image_label.config(image=imgtk)
    image_label.image = imgtk

# Encrypt the folder using an image as a key
def encrypt_folder_with_image():
    if not selected_image_path:
        messagebox.showerror("Error", "Please select an image to use as the key")
        return

    folder_path = filedialog.askdirectory()
    if not folder_path:
        messagebox.showerror("Error", "Please select a folder to encrypt")
        return

    try:
        key = generate_key_from_image(selected_image_path)
        encrypt_folder(key, folder_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to encrypt folder: {str(e)}")

# Decrypt the folder using an image as a key
def decrypt_folder_with_image():
    if not selected_image_path:
        messagebox.showerror("Error", "Please select an image to use as the key")
        return

    folder_path = filedialog.askdirectory()
    if not folder_path:
        messagebox.showerror("Error", "Please select a folder to decrypt")
        return

    try:
        key = generate_key_from_image(selected_image_path)
        decrypt_folder(key, folder_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to decrypt folder: {str(e)}")

# Function to encrypt the folder using a computer-generated key
def encrypt_folder_with_generated_key():
    folder_path = filedialog.askdirectory()
    if not folder_path:
        messagebox.showerror("Error", "Please select a folder to encrypt")
        return

    try:
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
        messagebox.showinfo("Success", "Folder encrypted successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to encrypt folder: {str(e)}")

# Function to send the encryption key via email
def send_encryption_key(key):
    
    sender_email = 'jonnywalker01@gmail.com'
    receiver_email = 'pranavraopollukam@gmail.com'
    subject = 'The Key for Encrypted Folder'
    message = f'The Key for Encrypted Folder: {key.decode()}'
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    username = "pranavraopollukam@gmail.com"
    password = '1234'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    print(key)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        logging.info("Encryption key sent via email successfully.")
    except Exception as e:
        logging.error(f"Failed to send encryption key via email: {e}")

# Function to decrypt the folder using a computer-generated key
def decrypt_folder_with_generated_key():
    folder_path = filedialog.askdirectory()
    if not folder_path:
        messagebox.showerror("Error", "Please select a folder to decrypt")
        return

    try:
        key = get_decryption_key()
        if key is None:
            return

        fernet = Fernet(key)

        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                try:
                    with open(filepath, 'rb') as file:
                        encrypted_data = file.read()
                    decrypted_data = fernet.decrypt(encrypted_data)
                    with open(filepath, 'wb') as file:
                        file.write(decrypted_data)
                except InvalidToken:
                    messagebox.showerror("Error", f"Failed to decrypt file {filepath}: Invalid key.")
                    return

        messagebox.showinfo("Success", "Folder decrypted successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to decrypt folder: {str(e)}")

# Function to retrieve the decryption key
def get_decryption_key():
    key = simpledialog.askstring("Input", "Enter the decryption key:", show='*')
    if key:
        try:
            Fernet(key.encode())  # Validate the key
            return key.encode()
        except ValueError:
            messagebox.showerror("Error", "Invalid decryption key format.")
    return None

# Function to browse folder
def browse_folder():
    folder_path = filedialog.askdirectory()
    folderpath_entry.delete(0, 'end')
    folderpath_entry.insert(0, folder_path)

# Toggle encryption/decryption mode
def toggle_mode():
    if encryption_mode.get() == 1:
        image_label.pack(pady=10)
        select_image_button.pack(pady=5)
        encrypt_button.config(text="Encrypt Folder", command=encrypt_folder_with_image)
        decrypt_button.config(text="Decrypt Folder", command=decrypt_folder_with_image)
    else:
        image_label.pack_forget()
        select_image_button.pack_forget()
        encrypt_button.config(text="Encrypt Folder", command=encrypt_folder_with_generated_key)
        decrypt_button.config(text="Decrypt Folder", command=decrypt_folder_with_generated_key)

# Setup the GUI
app = Tk()
app.title("Folder Encryptor/Decryptor")
app.geometry("400x450")

# Encryption/Decryption mode selection
encryption_mode = IntVar(value=1)
Radiobutton(app, text="Use Image as Key", variable=encryption_mode, value=1, command=toggle_mode).pack(anchor=W)
Radiobutton(app, text="Use Computer-Generated Key", variable=encryption_mode, value=2, command=toggle_mode).pack(anchor=W)

# Image display
image_label = Label(app)
select_image_button = Button(app, text="Select Image as Key", command=select_image)

# Folder path entry
Label(app, text="Folder Path:").pack(pady=5)
folderpath_entry = Entry(app, width=50)
folderpath_entry.pack(pady=5)
Button(app, text="Browse", command=browse_folder).pack(pady=5)

# Encrypt/Decrypt buttons
encrypt_button = Button(app, text="Encrypt Folder", command=encrypt_folder_with_image)
encrypt_button.pack(pady=5)
decrypt_button = Button(app, text="Decrypt Folder", command=decrypt_folder_with_image)
decrypt_button.pack(pady=5)

app.mainloop()
