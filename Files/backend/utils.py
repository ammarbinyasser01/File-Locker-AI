import hashlib
import os


def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


#####################################################


def is_image(path):

    extensions = [

        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".gif",
        ".webp"

    ]

    return os.path.splitext(path)[1].lower() in extensions