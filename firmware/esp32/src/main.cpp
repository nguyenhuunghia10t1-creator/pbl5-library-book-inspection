#include <Arduino.h>
#include <Preferences.h>
#include <esp_arduino_version.h>
#include <esp_system.h>

#include "usb_station.h"
#ifdef PBL5_ESPNOW_RECEIVER
#include "radio_receiver.h"
#endif

constexpr uint8_t Motor = 18, Sensor = 19, Servo = 22, Button = 23;
constexpr uint32_t Baud = 115200;

// Preserve actuator calibration saved by the earlier firmware.
struct SavedSettings {
  char ssid[33], password[65], token[41];
  uint16_t pushMs, returnMs;
  uint8_t home, reach;
};
uint8_t home = 0, reach = 180;
Station machine;
char boot[33];
UsbStation usb(machine, boot);
bool outputsReady = false;

#ifndef PBL5_ESPNOW_RECEIVER
class SerialOut {
 public:
  void enqueue(const char* message, uint32_t now) {
    size_t length = strlen(message);
    if (length > sizeof(data) - used) {
      usb.fault("SERIAL_TX_OVERFLOW", now);
      // Terminate any previously transmitted partial frame before replying again.
      head = 0;
      used = 1;
      data[0] = '\n';
      return;
    }
    size_t end = (head + used) % sizeof(data);
    size_t first = min(length, sizeof(data) - end);
    memcpy(data + end, message, first);
    memcpy(data, message + first, length - first);
    used += length;
  }

  void flush() {
    size_t count = min(used, sizeof(data) - head);
    count = min(count, static_cast<size_t>(Serial.availableForWrite()));
    if (count) {
      size_t written = Serial.write(reinterpret_cast<uint8_t*>(data + head), count);
      head = (head + written) % sizeof(data);
      used -= written;
    }
  }

 private:
  char data[1024];
  size_t head = 0, used = 0;
};
SerialOut out;
#endif

void loadCalibration() {
  SavedSettings saved{};
  Preferences nvs;
  if (!nvs.begin("pbl5", true)) return;
  const bool read = nvs.getBytesLength("settings") == sizeof saved &&
                    nvs.getBytes("settings", &saved, sizeof saved) == sizeof saved;
  nvs.end();
  if (read && saved.home <= 180 && saved.reach <= 180 && saved.home != saved.reach &&
      saved.pushMs >= 100 && saved.pushMs <= 10000 &&
      saved.returnMs >= 100 && saved.returnMs <= 10000) {
    home = saved.home;
    reach = saved.reach;
    machine.t.push = saved.pushMs;
    machine.t.retract = saved.returnMs;
  }
}

void writeOutputs(uint16_t duty, uint8_t angle) {
  uint32_t pulse = 500u + (1900u * angle) / 180u;
  uint32_t servoDuty = pulse * 16383u / 20000u;
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(Motor, duty);
  ledcWrite(Servo, servoDuty);
#else
  ledcWrite(0, duty);
  ledcWrite(2, servoDuty);
#endif
}
bool initOutputs() {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  return ledcAttachChannel(Motor, 20000, 10, 0) &&
         ledcAttachChannel(Servo, 50, 14, 2);
#else
  if (!ledcSetup(0, 20000, 10) || !ledcSetup(2, 50, 14)) return false;
  ledcAttachPin(Motor, 0);
  ledcAttachPin(Servo, 2);
  return true;
#endif
}
void setup() {
  digitalWrite(Motor, LOW);
  pinMode(Motor, OUTPUT);
  digitalWrite(Servo, LOW);
  pinMode(Servo, OUTPUT);
  pinMode(Button, INPUT_PULLUP);
  pinMode(Sensor, INPUT_PULLUP);
  Serial.begin(Baud);
  loadCalibration();
  snprintf(boot, sizeof boot, "%08lx%08lx%08lx%08lx",
           (unsigned long)esp_random(), (unsigned long)esp_random(),
           (unsigned long)esp_random(), (unsigned long)esp_random());
  machine.homeSince = millis();
  outputsReady = initOutputs();
  if (outputsReady) writeOutputs(0, home);
#ifdef PBL5_ESPNOW_RECEIVER
  const bool radioReady = Receiver::start();
  Serial.printf("PBL5_RECEIVER,1,%s,%02X:%02X:%02X:%02X:%02X:%02X,CH=%u,PHASE=%s,PWM=%u,HOME=%u,OUTPUTS=%s\n",
                radioReady ? "RADIO_READY" : "RADIO_ERROR",
                Receiver::localMac[0], Receiver::localMac[1], Receiver::localMac[2],
                Receiver::localMac[3], Receiver::localMac[4], Receiver::localMac[5],
                Receiver::Channel, phaseName(machine.phase), machine.duty(millis()), home,
                outputsReady ? "READY" : "ERROR");
  outputsReady = outputsReady && radioReady;
#endif
}

void loop() {
  if (!outputsReady) {
    delay(5);
    return;
  }
  static bool armed = false, lastHigh = false;
  static uint32_t changed = 0;
  uint32_t now = millis();
  bool high = digitalRead(Button), occupied = !digitalRead(Sensor);
  if (high != lastHigh) {
    changed = now;
    lastHigh = high;
  }
  if (high && now - changed >= 35) armed = true;
  if (!high && armed && machine.enabled()) {
    armed = false;
    machine.stop("MANUAL_OFF", now, true);
  }
  usb.checkHeartbeat(now);
  machine.tick(now, occupied);
  if (!high && armed && now - changed >= 35) {
    armed = false;
    machine.button(now);
  }

#ifdef PBL5_ESPNOW_RECEIVER
  Receiver::poll(usb, boot, home, reach);
#else
  const auto send = [now](const char* message) { out.enqueue(message, now); };
  for (size_t i = 0; i < UsbStation::LineCapacity && Serial.available(); ++i) {
    int byte = Serial.read();
    if (byte >= 0) usb.receive(static_cast<char>(byte), now, home, reach, send);
  }
  usb.capture(send);
#endif
  writeOutputs(machine.duty(millis()), machine.phase == Phase::PUSH ? reach : home);
#ifndef PBL5_ESPNOW_RECEIVER
  out.flush();
#endif
  delay(1);
}
