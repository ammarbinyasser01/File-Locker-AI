import os

import customtkinter as ctk
from tkinter import messagebox

from backend.database import Database
from backend.utils import hash_password
from backend.face_auth import FaceAuth

db = Database()
face_auth = FaceAuth()


class RegisterPage(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("File Locker AI")
        self.geometry("500x600")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        ctk.CTkLabel(
            self,
            text="File Locker AI",
            font=("Arial", 28, "bold")
        ).pack(pady=30)

        self.username = ctk.CTkEntry(
            self,
            width=300,
            placeholder_text="Username"
        )
        self.username.pack(pady=10)

        self.password = ctk.CTkEntry(
            self,
            width=300,
            placeholder_text="Password",
            show="*"
        )
        self.password.pack(pady=10)

        self.face_btn = ctk.CTkButton(
            self,
            text="Register Face",
            command=self.register_face
        )
        self.face_btn.pack(pady=15)

        self.register_btn = ctk.CTkButton(
            self,
            text="Register",
            command=self.register
        )
        self.register_btn.pack(pady=10)

        self.login_btn = ctk.CTkButton(
            self,
            text="Login",
            command=self.open_login
        )
        self.login_btn.pack(pady=10)

    ##########################################################

    def register_face(self):

        username = self.username.get().strip()

        if username == "":

            messagebox.showerror(
                "Error",
                "Enter username first."
            )

            return

        if db.user_exists(username):

            messagebox.showerror(
                "Error",
                "Username already exists."
            )

            return

        success, message = face_auth.register_face(
            username
        )

        if success:

            messagebox.showinfo(
                "Success",
                message
            )

        else:

            messagebox.showerror(
                "Failed",
                message
            )

    ##########################################################

    def register(self):

        username = self.username.get().strip()
        password = self.password.get().strip()

        if username == "" or password == "":

            messagebox.showerror(
                "Error",
                "Fill all fields."
            )

            return

        if db.user_exists(username):

            messagebox.showerror(
                "Error",
                "Username already exists."
            )

            return

        folder = face_auth.user_folder(
            username
        )

        if len(os.listdir(folder)) == 0:

            messagebox.showerror(
                "Error",
                "Please register your face first."
            )

            return

        db.add_user(
            username,
            hash_password(password)
        )

        messagebox.showinfo(
            "Success",
            "Registration completed successfully."
        )

        self.destroy()

        from gui.login_page import LoginPage
        LoginPage().mainloop()

    ##########################################################

    def open_login(self):

        self.destroy()

        from gui.login_page import LoginPage
        LoginPage().mainloop()


if __name__ == "__main__":

    RegisterPage().mainloop()