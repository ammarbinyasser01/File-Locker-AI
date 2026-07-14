import sqlite3
import os

DATABASE_PATH = os.path.join("database", "locker.db")


class Database:

    def __init__(self):
        self.connection = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            face_registered INTEGER DEFAULT 0
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS vault(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            original_name TEXT,
            encrypted_name TEXT,
            file_type TEXT,
            date_added TEXT
        )
        """)

        self.connection.commit()

    ######################################

    def add_user(self, username, password):

        self.cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        self.connection.commit()

    ######################################

    def user_exists(self, username):

        self.cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        return self.cursor.fetchone()

    ######################################

    def verify_login(self, username, password):

        self.cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        return self.cursor.fetchone()

    ######################################

    def add_file(self, username, original_name,
                 encrypted_name,
                 file_type,
                 date_added):

        self.cursor.execute("""
        INSERT INTO vault(
            username,
            original_name,
            encrypted_name,
            file_type,
            date_added
        )

        VALUES(?,?,?,?,?)

        """,

        (
            username,
            original_name,
            encrypted_name,
            file_type,
            date_added
        ))

        self.connection.commit()

    ######################################

    def get_files(self, username):

        self.cursor.execute(
            "SELECT * FROM vault WHERE username=?",
            (username,)
        )

        return self.cursor.fetchall()

    ######################################

    def delete_file(self, file_id):

        self.cursor.execute(
            "DELETE FROM vault WHERE id=?",
            (file_id,)
        )

        self.connection.commit()