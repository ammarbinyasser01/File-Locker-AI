import customtkinter as ctk
from tkinter import messagebox

from backend.database import Database
from backend.utils import hash_password
from backend.face_auth import FaceAuth

db = Database()
face_auth = FaceAuth()


class LoginPage(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Login")
        self.geometry("500x600")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        ctk.CTkLabel(
            self,
            text="Login",
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

        ctk.CTkButton(
            self,
            text="Use Face Unlock",
            command=self.face_login
        ).pack(pady=15)

        ctk.CTkButton(
            self,
            text="Login",
            command=self.login
        ).pack(pady=10)

        ctk.CTkButton(
            self,
            text="Back",
            command=self.back
        ).pack(pady=10)

    ##########################################################

    def login(self):

        username = self.username.get().strip()
        password = hash_password(
            self.password.get()
        )

        if username == "":

            messagebox.showerror(
                "Error",
                "Enter username."
            )

            return

        if db.verify_login(
            username,
            password
        ):

            self.destroy()

            from gui.home_page import HomePage
            HomePage(username).mainloop()

        else:

            messagebox.showerror(
                "Login Failed",
                "Invalid username or password."
            )

    ##########################################################

    def face_login(self):

        username = self.username.get().strip()

        if username == "":

            messagebox.showerror(
                "Error",
                "Enter username first."
            )

            return

        if not db.user_exists(username):

            messagebox.showerror(
                "Error",
                "User does not exist."
            )

            return

        success, message = face_auth.verify_face(
            username
        )

        if success:

            messagebox.showinfo(
                "Success",
                message
            )

            self.destroy()

            from gui.home_page import HomePage
            HomePage(username).mainloop()

        else:

            messagebox.showerror(
                "Failed",
                message
            )

    ##########################################################

    def back(self):

        self.destroy()

        from gui.register_page import RegisterPage
        RegisterPage().mainloop()


if __name__ == "__main__":

    LoginPage().mainloop()