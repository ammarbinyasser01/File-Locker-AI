import os
from cryptography.fernet import Fernet

KEY_FOLDER = "keys"
KEY_FILE = os.path.join(KEY_FOLDER, "master.key")


class Encryption:

    def __init__(self):

        if not os.path.exists(KEY_FOLDER):
            os.makedirs(KEY_FOLDER)

        if not os.path.exists(KEY_FILE):

            key = Fernet.generate_key()

            with open(KEY_FILE, "wb") as file:
                file.write(key)

        with open(KEY_FILE, "rb") as file:
            self.key = file.read()

        self.cipher = Fernet(self.key)

    ########################################################

    def encrypt_file(self, source_path, destination_path):

        with open(source_path, "rb") as file:
            data = file.read()

        encrypted = self.cipher.encrypt(data)

        with open(destination_path, "wb") as file:
            file.write(encrypted)

    ########################################################

    def decrypt_file(self, source_path, destination_path):

        with open(source_path, "rb") as file:
            data = file.read()

        decrypted = self.cipher.decrypt(data)

        with open(destination_path, "wb") as file:
            file.write(decrypted)