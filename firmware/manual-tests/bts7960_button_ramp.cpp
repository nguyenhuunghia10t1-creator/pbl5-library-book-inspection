/*
 * CHE DO HIEN TAI: CONVEYOR_IR_TEST = true.
 * Nut GPIO23 dung INPUT voi dien tro NGOAI 10k keo len 3V3, KHONG NOI 5V.
 * Nut noi GPIO23 xuong GND. Bam: chay tang dan 2 s; bam lai: PWM=0 ngay.
 * GPIO19 LOW: PWM=0 ngay, MG995 GPIO22 gat 180 do, cho 700 ms, ve 0 do, cho 700 ms.
 * Chi chay lai khi servo het thoi gian ve va IR HIGH lien tuc 2 s, nut van BAT.
 * Mot luot gat moi chi duoc cho phep sau khi IR HIGH lien tuc 2 s va servo da ve.
 * Vat xuat hien lai trong luc cho: dem lai tu dau. Nut TAT huy gat, ra lenh ve 0 do.
 *
 * Test doc lap: ESP32 thuong 38 chan + BTS7960 + Nut nhan + Cam bien hong ngoai + Servo MG995.
 * Khong them file nay vao src/ cua firmware chinh.
 *
 * Dau day theo cau hinh:
 *   1. Driver BTS7960 (bang tai):
 *      - GPIO18 -> RPWM; LPWM -> GND.
 *      - VCC, R_EN, L_EN -> 3V3; GND -> GND chung voi ESP32.
 *      - B+, B- -> Nguon ngoai cap cho dong co; M+, M- -> 2 day dong co.
 *   2. Nut nhan thuong mo (NO):
 *      - GPIO23 -> chan 1 nut nhan; chan 2 -> GND; dien tro 10k tu GPIO23 len 3V3.
 *   3. Cam bien hong ngoai vat can 3 chan (VCC, GND, OUT):
 *      - VCC -> 3V3 ESP32 (de tin hieu OUT o muc 3.3V an toan cho ESP32).
 *      - GND -> GND chung voi ESP32.
 *      - OUT -> GPIO19 (dung INPUT_PULLUP, mac dinh active LOW khi co vat can).
 *   4. Servo MG995 3 chan (Signal, VCC, GND):
 *      - Signal (Cam/Vang) -> GPIO22.
 *      - VCC (Do)          -> Nguon ngoai 5V-6V (>= 2A). TUYET DOI KHONG lay tu 3V3 ESP32.
 *      - GND (Nau/Den)     -> Noi chung GND nguon ngoai voi GND ESP32.
 *
 * Hanh vi:
 *   - Khoi dong: He thong TAT, bang tai PWM = 0, Servo o 0 do.
 *   - Bam nut GPIO23 lan 1: BAT he thong, bang tai ramp 0% -> 100% trong 2000 ms.
 *   - Bam nut GPIO23 lan 2: TAT he thong, PWM = 0 ngay, huy gat va dua servo ve 0 do.
 *   - Khi he thong dang BAT va cam bien hong ngoai (GPIO19) phat hien vat can:
 *     1) Bang tai DUNG NGAY (PWM = 0) de vat dung tai vi tri gat.
 *     2) Servo MG995 quay len 180 do trong SERVO_PUSH_HOLD_MS (700 ms).
 *     3) Servo MG995 thu ve 0 do trong SERVO_RETURN_HOLD_MS (700 ms).
 *     4) Cho IR het vat lien tuc 2000 ms va servo het thoi gian ve, roi ramp chay lai 2000 ms.
 *   - Thoi gian cho servo khong phai feedback xac nhan goc co khi.
 *
 * Tuong thich Arduino-ESP32 core 2.x va 3.x. Khong can thu vien ngoai.
 */

#include <Arduino.h>
#include <esp_arduino_version.h>

constexpr uint8_t RPWM_PIN = 18;
constexpr uint8_t IR_SENSOR_PIN = 19;
constexpr uint8_t SERVO_PIN = 22;
constexpr uint8_t BUTTON_PIN = 23;
constexpr bool CONVEYOR_IR_TEST = true;
constexpr uint32_t IR_CLEAR_WAIT_MS = 2000;

// Hau het module hong ngoai 3 chan (LM393 / FC-51) xuat LOW khi phat hien vat can.
constexpr int IR_ACTIVE_LEVEL = LOW;

constexpr uint32_t PWM_FREQUENCY_HZ = 20000;
constexpr uint8_t PWM_RESOLUTION_BITS = 10;
constexpr uint16_t PWM_MAX = (1U << PWM_RESOLUTION_BITS) - 1U;

constexpr uint32_t SERVO_FREQUENCY_HZ = 50;
constexpr uint8_t SERVO_RESOLUTION_BITS = 14;
constexpr uint32_t SERVO_PERIOD_US = 20000;
constexpr uint16_t SERVO_MIN_US = 500;   // Xung 0 do cho MG995
constexpr uint16_t SERVO_MAX_US = 2400;  // Xung 180 do cho MG995
constexpr uint8_t SERVO_HOME_ANGLE = 0;
constexpr uint8_t SERVO_PUSH_ANGLE = 180;

constexpr uint32_t RAMP_DURATION_MS = 2000;
constexpr uint32_t SERVO_PUSH_HOLD_MS = 700;
constexpr uint32_t SERVO_RETURN_HOLD_MS = 700;
constexpr uint32_t DEBOUNCE_MS = 35;
constexpr uint32_t IR_DEBOUNCE_MS = 30;

constexpr uint8_t MOTOR_PWM_CHANNEL = 0;  // Timer 0
constexpr uint8_t SERVO_PWM_CHANNEL = 2;  // Timer 1 (tach rieng tan so voi Timer 0)

enum class CycleState : uint8_t {
  IDLE_OR_RUNNING = 0,
  SERVO_PUSHING,
  SERVO_RETURNING,
};

bool hardwareReady = false;
bool requestedOn = false;
bool rampActive = false;
uint16_t currentDuty = 0;
uint16_t rampStartDuty = 0;
uint16_t targetDuty = 0;
uint32_t rampStartedAt = 0;

CycleState cycleState = CycleState::IDLE_OR_RUNNING;
uint32_t stateStartedAt = 0;
uint8_t currentServoAngle = SERVO_HOME_ANGLE;

int lastRawButton = HIGH;
int stableButton = HIGH;
bool buttonArmed = false;
uint32_t rawButtonChangedAt = 0;

int lastRawIr = HIGH;
int stableIr = HIGH;
bool irArmed = true;
uint32_t rawIrChangedAt = 0;
bool irPaused = false;
bool irClearWaiting = false;
uint32_t irClearSince = 0;

void writeMotorPwm(uint16_t duty) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(RPWM_PIN, duty);
#else
  ledcWrite(MOTOR_PWM_CHANNEL, duty);
#endif
}

uint32_t angleToServoDuty(uint8_t angle) {
  const uint8_t clamped = (angle > 180) ? 180 : angle;
  const uint32_t pulseUs =
      SERVO_MIN_US +
      (uint32_t(SERVO_MAX_US - SERVO_MIN_US) * uint32_t(clamped)) / 180U;
  const uint32_t maxDuty = (1UL << SERVO_RESOLUTION_BITS) - 1UL;
  return (pulseUs * maxDuty) / SERVO_PERIOD_US;
}

void writeServoAngle(uint8_t angle) {
  currentServoAngle = (angle > 180) ? 180 : angle;
  const uint32_t duty = angleToServoDuty(currentServoAngle);
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(SERVO_PIN, duty);
#else
  ledcWrite(SERVO_PWM_CHANNEL, duty);
#endif
}

bool beginHardwarePwm() {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  if (!ledcAttachChannel(RPWM_PIN, PWM_FREQUENCY_HZ, PWM_RESOLUTION_BITS,
                         MOTOR_PWM_CHANNEL)) {
    return false;
  }
  if (!ledcAttachChannel(SERVO_PIN, SERVO_FREQUENCY_HZ, SERVO_RESOLUTION_BITS,
                         SERVO_PWM_CHANNEL)) {
    return false;
  }
#else
  if (ledcSetup(MOTOR_PWM_CHANNEL, PWM_FREQUENCY_HZ, PWM_RESOLUTION_BITS) == 0) {
    return false;
  }
  ledcAttachPin(RPWM_PIN, MOTOR_PWM_CHANNEL);

  if (ledcSetup(SERVO_PWM_CHANNEL, SERVO_FREQUENCY_HZ, SERVO_RESOLUTION_BITS) == 0) {
    return false;
  }
  ledcAttachPin(SERVO_PIN, SERVO_PWM_CHANNEL);
#endif
  writeMotorPwm(0);
  writeServoAngle(SERVO_HOME_ANGLE);
  return true;
}

void startMotorRampTo(uint16_t newTarget, uint32_t now) {
  rampStartDuty = currentDuty;
  targetDuty = newTarget;
  rampStartedAt = now;
  rampActive = (currentDuty != targetDuty);
}

void stopMotorImmediately() {
  rampActive = false;
  rampStartDuty = 0;
  targetDuty = 0;
  currentDuty = 0;
  writeMotorPwm(0);
}

void updateRamp(uint32_t now) {
  if (!rampActive) {
    return;
  }

  const uint32_t elapsed = now - rampStartedAt;
  uint16_t nextDuty;
  if (elapsed >= RAMP_DURATION_MS) {
    nextDuty = targetDuty;
    rampActive = false;
  } else {
    const int32_t difference = int32_t(targetDuty) - int32_t(rampStartDuty);
    nextDuty = uint16_t(int32_t(rampStartDuty) +
                        difference * int32_t(elapsed) / int32_t(RAMP_DURATION_MS));
  }

  if (nextDuty != currentDuty) {
    currentDuty = nextDuty;
    writeMotorPwm(currentDuty);
  }
  if (!rampActive) {
    Serial.printf("[DONE] PWM=%u/%u\n", unsigned(currentDuty), unsigned(PWM_MAX));
  }
}

void pollButton(uint32_t now) {
  const int raw = digitalRead(BUTTON_PIN);
  if (raw != lastRawButton) {
    lastRawButton = raw;
    rawButtonChangedAt = now;
  }

  if (uint32_t(now - rawButtonChangedAt) < DEBOUNCE_MS || raw == stableButton) {
    return;
  }
  stableButton = raw;

  if (stableButton == HIGH) {
    buttonArmed = true;
    return;
  }

  if (!buttonArmed) {
    return;
  }
  buttonArmed = false;
  requestedOn = !requestedOn;

  if (CONVEYOR_IR_TEST) {
    if (requestedOn) {
      if (irPaused || cycleState != CycleState::IDLE_OR_RUNNING ||
          digitalRead(IR_SENSOR_PIN) == IR_ACTIVE_LEVEL) {
        stopMotorImmediately();
        Serial.println("[BUTTON] ON: waiting for servo home and IR clear for 2000 ms.");
      } else {
        startMotorRampTo(PWM_MAX, now);
        Serial.println("[BUTTON] ON: ramp to 100% in 2000 ms.");
      }
    } else {
      stopMotorImmediately();
      if (cycleState != CycleState::IDLE_OR_RUNNING) {
        writeServoAngle(SERVO_HOME_ANGLE);
        cycleState = CycleState::SERVO_RETURNING;
        stateStartedAt = now;
        irPaused = true;
        Serial.println("[SERVO] Cancel: returning to 0 deg.");
      }
      Serial.println("[BUTTON] OFF: PWM=0.");
    }
    return;
  }

  if (requestedOn) {
    cycleState = CycleState::IDLE_OR_RUNNING;
    writeServoAngle(SERVO_HOME_ANGLE);
    irArmed = (stableIr != IR_ACTIVE_LEVEL);
    startMotorRampTo(PWM_MAX, now);
    Serial.printf("[BUTTON] ON: PWM=%u -> %u, ramp=%lu ms\n",
                  unsigned(currentDuty), unsigned(targetDuty),
                  static_cast<unsigned long>(RAMP_DURATION_MS));
  } else {
    if (cycleState != CycleState::IDLE_OR_RUNNING) {
      cycleState = CycleState::IDLE_OR_RUNNING;
      writeServoAngle(SERVO_HOME_ANGLE);
      Serial.println("[BUTTON] OFF during servo cycle -> Servo reset to 0 deg.");
    }
    startMotorRampTo(0, now);
    Serial.printf("[BUTTON] OFF: PWM=%u -> %u, ramp=%lu ms\n",
                  unsigned(currentDuty), unsigned(targetDuty),
                  static_cast<unsigned long>(RAMP_DURATION_MS));
  }
}

void updateConveyorIr(uint32_t now) {
  // Stop on any active reading; require a continuous clear interval to resume.
  if (digitalRead(IR_SENSOR_PIN) == IR_ACTIVE_LEVEL) {
    if (!irPaused) {
      Serial.println("[IR] OBSTACLE: PWM=0.");
    }
    irPaused = true;
    irClearWaiting = false;
    if (rampActive || currentDuty != 0) {
      stopMotorImmediately();
    }
    if (requestedOn && irArmed && cycleState == CycleState::IDLE_OR_RUNNING) {
      irArmed = false;
      writeServoAngle(SERVO_PUSH_ANGLE);
      cycleState = CycleState::SERVO_PUSHING;
      stateStartedAt = now;
      Serial.println("[SERVO] Obstacle: push to 180 deg, wait 700 ms.");
    }
    return;
  }
  if (!irPaused) {
    return;
  }
  if (!irClearWaiting) {
    irClearWaiting = true;
    irClearSince = now;
    Serial.println("[IR] CLEAR: waiting 2000 ms.");
  }
  if (uint32_t(now - irClearSince) >= IR_CLEAR_WAIT_MS &&
      cycleState == CycleState::IDLE_OR_RUNNING) {
    irPaused = false;
    irClearWaiting = false;
    irArmed = true;
    if (requestedOn) {
      startMotorRampTo(PWM_MAX, now);
      Serial.println("[RESUME] IR clear 2000 ms: ramp to 100% in 2000 ms.");
    } else {
      Serial.println("[IR] Clear confirmed; button is OFF, motor stays stopped.");
    }
  }
}

void pollIrSensor(uint32_t now) {
  const int raw = digitalRead(IR_SENSOR_PIN);
  if (raw != lastRawIr) {
    lastRawIr = raw;
    rawIrChangedAt = now;
  }

  if (uint32_t(now - rawIrChangedAt) < IR_DEBOUNCE_MS) {
    return;
  }

  if (raw != stableIr) {
    stableIr = raw;
    if (stableIr != IR_ACTIVE_LEVEL) {
      irArmed = true;  // Vat can da roi khoi cam bien -> san sang cho vat tiep theo.
      Serial.println("[IR] Clear (ready for next obstacle).");
    }
  }

  if (!requestedOn || cycleState != CycleState::IDLE_OR_RUNNING) {
    return;
  }

  if (stableIr == IR_ACTIVE_LEVEL && irArmed) {
    irArmed = false;
    stopMotorImmediately();
    writeServoAngle(SERVO_PUSH_ANGLE);
    cycleState = CycleState::SERVO_PUSHING;
    stateStartedAt = now;
    Serial.println("[IR] Obstacle detected -> Conveyor STOP (PWM=0), Servo -> 180 deg.");
  }
}

void updateServoSequence(uint32_t now) {
  if (cycleState == CycleState::SERVO_PUSHING) {
    if (uint32_t(now - stateStartedAt) >= SERVO_PUSH_HOLD_MS) {
      writeServoAngle(SERVO_HOME_ANGLE);
      cycleState = CycleState::SERVO_RETURNING;
      stateStartedAt = now;
      Serial.println("[SERVO] Push 180 deg done -> Returning to 0 deg.");
    }
  } else if (cycleState == CycleState::SERVO_RETURNING) {
    if (uint32_t(now - stateStartedAt) >= SERVO_RETURN_HOLD_MS) {
      cycleState = CycleState::IDLE_OR_RUNNING;
      if (CONVEYOR_IR_TEST) {
        Serial.println("[SERVO] Return wait complete; IR clear gate controls conveyor.");
        return;
      }
      if (stableIr != IR_ACTIVE_LEVEL) {
        irArmed = true;
      }
      if (requestedOn) {
        startMotorRampTo(PWM_MAX, now);
        Serial.printf("[RESUME] Servo back at 0 deg -> Conveyor ramping 0 -> %u (%lu ms).\n",
                      unsigned(PWM_MAX), static_cast<unsigned long>(RAMP_DURATION_MS));
      }
    }
  }
}

void setup() {
  digitalWrite(RPWM_PIN, LOW);
  pinMode(RPWM_PIN, OUTPUT);
  digitalWrite(SERVO_PIN, LOW);
  pinMode(SERVO_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);  // External 10k pull-up to 3V3 only.
  pinMode(IR_SENSOR_PIN, INPUT_PULLUP);

  const uint32_t now = millis();
  lastRawButton = digitalRead(BUTTON_PIN);
  stableButton = lastRawButton;
  buttonArmed = (stableButton == HIGH);
  rawButtonChangedAt = now;

  lastRawIr = digitalRead(IR_SENSOR_PIN);
  stableIr = lastRawIr;
  irPaused = true;  // Also gate startup while the servo returns home.
  irArmed = true;
  rawIrChangedAt = now;

  Serial.begin(115200);
  hardwareReady = beginHardwarePwm();
  if (!hardwareReady) {
    digitalWrite(RPWM_PIN, LOW);
    Serial.println("[ERROR] LEDC init failed. PWM kept LOW; reset to retry.");
    return;
  }
  if (CONVEYOR_IR_TEST) {
    cycleState = CycleState::SERVO_RETURNING;
    stateStartedAt = millis();
    Serial.printf("[READY] BUTTON_IR_SERVO. PWM=0. GPIO23=%s. GPIO19=%s. GPIO22=MG995 home 0 deg. Clear wait=2000 ms.\n",
                  stableButton == HIGH ? "HIGH (released)" : "LOW (release before pressing)",
                  stableIr == IR_ACTIVE_LEVEL ? "LOW (obstacle)" : "HIGH (clear)");
  } else {
    Serial.println(
        "[READY] PWM=0, Servo=0 deg. GPIO23=Button, GPIO19=IR, GPIO22=MG995, GPIO18=RPWM.");
  }
}

void loop() {
  if (!hardwareReady) {
    return;
  }
  const uint32_t now = millis();
  pollButton(now);
  if (CONVEYOR_IR_TEST) {
    updateConveyorIr(now);
    updateServoSequence(now);
  } else {
    pollIrSensor(now);
    updateServoSequence(now);
  }
  updateRamp(now);
}
