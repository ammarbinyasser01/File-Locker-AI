import os
import shutil
import datetime

from backend.encryption import Encryption

enc = Encryption()

VAULT = "vault"
RESTORED = "restored"


if not os.path.exists(VAULT):
    os.makedirs(VAULT)

if not os.path.exists(RESTORED):
    os.makedirs(RESTORED)


def file_type(path):

    if os.path.isdir(path):
        return "Folder"

    return os.path.splitext(path)[1].replace(".", "").upper()


############################################################


def lock_file(path):

    filename = os.path.basename(path)

    encrypted_name = filename + ".enc"

    destination = os.path.join(
        VAULT,
        encrypted_name
    )

    enc.encrypt_file(
        path,
        destination
    )

    return (

        filename,

        encrypted_name,

        file_type(path),

        datetime.datetime.now().strftime("%d-%m-%Y")

    )


############################################################


def restore_file(encrypted_name, original_name):

    source = os.path.join(
        VAULT,
        encrypted_name
    )

    destination = os.path.join(
        RESTORED,
        original_name
    )

    enc.decrypt_file(
        source,
        destination
    )

    os.remove(source)

    return destination


############################################################


def delete_original(path):

    if os.path.isfile(path):

        os.remove(path)

    elif os.path.isdir(path):

        shutil.rmtree(path)