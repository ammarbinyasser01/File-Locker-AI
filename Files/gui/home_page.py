import os
import customtkinter as ctk

from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from backend.database import Database
from backend.file_manager import (
    lock_file,
    restore_file,
    delete_original
)

db = Database()

# Only these can be previewed locally - everything else must be restored first.
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")

# Assumed to sit at the project root, one level above this gui/ folder,
# matching "restored folder inside the main project folder" from the spec.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESTORED_DIR = os.path.join(PROJECT_ROOT, "restored")

COLORS = {
    "bg": "#1a1a2e",
    "card": "#22223b",
    "accent": "#4361ee",
    "accent_hover": "#3a56d4",
    "text": "#f1f1f1",
    "muted": "#9a9ab0",
    "success": "#2ecc71",
    "success_hover": "#27ae60",
    "danger": "#e74c3c",
    "danger_hover": "#c0392b",
}


class HomePage(ctk.CTk):

    def __init__(self, username):

        super().__init__()

        self.username = username

        self._click_after_id = None
        self._click_row = None

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("File Locker AI")
        self.geometry("950x650")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])

        # ---------------- header ----------------
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text=f"\U0001F512 Welcome, {username}",
            font=("Arial", 26, "bold"),
            text_color=COLORS["text"]
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Exit",
            width=90,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            corner_radius=8,
            command=self.exit_to_registration
        ).pack(side="right")

        ctk.CTkButton(
            header,
            text="\uFF0B Add",
            width=90,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            corner_radius=8,
            command=self.open_add_menu
        ).pack(side="right", padx=10)

        # ---------------- table ----------------
        table_frame = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=12)
        table_frame.pack(fill="both", expand=True, padx=25, pady=(0, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=COLORS["card"],
            fieldbackground=COLORS["card"],
            foreground=COLORS["text"],
            rowheight=32,
            borderwidth=0,
            font=("Segoe UI", 11)
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["accent"],
            foreground="white",
            font=("Segoe UI", 11, "bold")
        )
        style.map("Treeview", background=[("selected", COLORS["accent_hover"])])

        columns = ("Name", "Date Added", "Type")

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=18,
            style="Treeview"
        )

        for column in columns:
            self.table.heading(column, text=column)
            self.table.column(column, width=280, anchor="center")

        self.table.pack(fill="both", expand=True, padx=15, pady=15)

        # single click -> remove/restore popup, double click -> preview (images only)
        self.table.bind("<Button-1>", self.on_row_click)
        self.table.bind("<Double-1>", self.on_row_double_click)

        ctk.CTkLabel(
            self,
            text="Click an item to remove & restore it  \u2022  Double-click an image to view it",
            text_color=COLORS["muted"],
            font=("Segoe UI", 11)
        ).pack(pady=(0, 15))

        self.load_files()

    ##########################################################

    def load_files(self):

        for item in self.table.get_children():
            self.table.delete(item)

        files = db.get_files(self.username)

        for row in files:
            self.table.insert(
                "",
                "end",
                iid=row[0],
                values=(row[2], row[5], row[4])
            )

    ##########################################################
    # "+" button: choose Files or Folder, then lock everything picked
    ##########################################################

    def open_add_menu(self):

        popup = ctk.CTkToplevel(self)
        popup.title("Add to vault")
        popup.geometry("300x160")
        popup.configure(fg_color=COLORS["bg"])
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(
            popup,
            text="What would you like to add?",
            text_color=COLORS["text"],
            font=("Segoe UI", 14)
        ).pack(pady=(20, 15))

        ctk.CTkButton(
            popup,
            text="\U0001F4C4 Select Files",
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=lambda: [popup.destroy(), self.add_files()]
        ).pack(pady=5, padx=30, fill="x")

        ctk.CTkButton(
            popup,
            text="\U0001F4C1 Select Folder",
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=lambda: [popup.destroy(), self.add_folder()]
        ).pack(pady=5, padx=30, fill="x")

    def add_files(self):
        paths = filedialog.askopenfilenames()
        if not paths:
            return
        self._lock_paths(list(paths))

    def add_folder(self):
        path = filedialog.askdirectory()
        if not path:
            return
        self._lock_paths([path])

    def _lock_paths(self, paths):

        locked_paths = []

        for path in paths:

            try:
                (
                    original_name,
                    encrypted_name,
                    file_type,
                    date_added
                ) = lock_file(path)

                db.add_file(
                    self.username,
                    original_name,
                    encrypted_name,
                    file_type,
                    date_added
                )

                locked_paths.append(path)

            except Exception as error:
                messagebox.showerror("Error", f"Could not lock {os.path.basename(path)}:\n{error}")

        self.load_files()

        if not locked_paths:
            return

        messagebox.showinfo("Success", f"{len(locked_paths)} item(s) locked successfully.")

        delete_originals = messagebox.askyesno(
            "Delete original?",
            "Do you want to delete the original file(s)/folder(s) from their current location?"
        )

        if delete_originals:
            for path in locked_paths:
                try:
                    delete_original(path)
                except Exception as error:
                    messagebox.showwarning("Cleanup issue", f"Could not delete original:\n{error}")

    ##########################################################
    # single click -> "remove from here?" popup (with double-click debounce)
    ##########################################################

    def on_row_click(self, event):

        row_id = self.table.identify_row(event.y)

        if not row_id:
            return

        if self._click_after_id:
            self.after_cancel(self._click_after_id)

        self._click_row = row_id
        self._click_after_id = self.after(300, self._handle_single_click)

    def _handle_single_click(self):

        self._click_after_id = None

        if not self._click_row:
            return

        selected = self._click_row
        self._click_row = None

        record = self._get_record(selected)

        if record is None:
            messagebox.showerror("Error", "File not found.")
            return

        answer = messagebox.askyesno(
            "Remove item",
            f"Do you want to remove '{record[2]}' from here?\n\n"
            "It will be decrypted and moved to this project's 'restored' folder."
        )

        if not answer:
            return

        self._restore_record(record)

    def _restore_record(self, record):

        try:
            restore_file(record[3], record[2])
            db.delete_file(record[0])

            messagebox.showinfo(
                "Success",
                "File restored successfully.\n\nCheck the restored folder."
            )

            self.load_files()

        except Exception as error:
            messagebox.showerror("Restore Failed", str(error))

    def _get_record(self, row_id):

        records = db.get_files(self.username)

        for record in records:
            if str(record[0]) == str(row_id):
                return record

        return None

    ##########################################################
    # double click -> preview, images only
    ##########################################################

    def on_row_double_click(self, event):

        if self._click_after_id:
            self.after_cancel(self._click_after_id)
            self._click_after_id = None
        self._click_row = None

        row_id = self.table.identify_row(event.y)

        if not row_id:
            return

        record = self._get_record(row_id)

        if record is None:
            messagebox.showerror("Error", "File not found.")
            return

        original_name = record[2]
        extension = os.path.splitext(original_name)[1].lower()

        if extension not in IMAGE_EXTENSIONS:
            messagebox.showinfo(
                "Cannot preview",
                "Only image files can be viewed locally.\n"
                "Click this item once to remove & restore it, then open it from the "
                "restored folder."
            )
            return

        answer = messagebox.askyesno(
            "View image",
            f"To view '{original_name}' it needs to be restored first. Restore and open it now?"
        )

        if not answer:
            return

        self._restore_record(record)
        self._open_restored_file(original_name)

    def _open_restored_file(self, original_name):

        restored_path = os.path.join(RESTORED_DIR, original_name)

        if not os.path.exists(restored_path):
            messagebox.showinfo(
                "Restored",
                f"'{original_name}' was restored, but I couldn't auto-locate it to open it.\n"
                f"Check: {RESTORED_DIR}"
            )
            return

        try:
            os.startfile(restored_path)
        except AttributeError:
            # os.startfile only exists on Windows
            messagebox.showinfo("Restored", f"'{original_name}' was restored to:\n{restored_path}")
        except Exception as error:
            messagebox.showwarning("Could not open file", str(error))

    ##########################################################

    def exit_to_registration(self):

        answer = messagebox.askyesno(
            "Exit",
            "Do you want to exit to the registration page?"
        )

        if not answer:
            return

        self.destroy()

        from gui.register_page import RegistrationPage
        RegistrationPage().mainloop()


##############################################################

if __name__ == "__main__":

    HomePage("Demo").mainloop()