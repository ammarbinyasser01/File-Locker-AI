# 🔒 File Locker AI

File Locker AI is a secure desktop application built with Python and CustomTkinter that allows users to encrypt files and protect access using both password authentication and OpenCV-based facial recognition.

## Features

- User Registration & Login
- Password Authentication (SHA-256)
- Face Registration & Face Login
- AES File Encryption using Fernet
- Secure File Vault
- Restore Encrypted Files
- SQLite Database
- Modern CustomTkinter GUI

## Technologies Used

- Python
- CustomTkinter
- OpenCV (LBPH Face Recognition)
- Cryptography (Fernet)
- SQLite
- NumPy
- Pillow

## Project Structure

```
File Locker AI/
│
├── backend/
├── gui/
├── database/
├── faces/
├── keys/
├── model/
├── restored/
├── vault/
├── main.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository.

```bash
git clone <repository-url>
cd "File Locker AI"
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Run the application.

```bash
python main.py
```

## How It Works

1. Register a new account.
2. Capture your face using the webcam.
3. Login using either:
   - Username & Password
   - Face Recognition
4. Lock files into the encrypted vault.
5. Double-click a file to restore it.

## License

This project was developed for educational purposes.
