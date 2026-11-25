// MG996R: signal -> GPIO22, red -> external regulated 5 V,
// brown/black -> supply GND. Connect supply GND to ESP32 GND.
#include <Arduino.h>

constexpr uint8_t ServoPin = 22;
constexpr uint32_t FrameUs = 20000;
constexpr uint8_t DutyBits = 14;
constexpr uint32_t MinPulseUs = 500;
constexpr uint32_t MaxPulseUs = 2400;
constexpr uint32_t HalfCycleMs = 2500;
constexpr uint32_t StepMs = FrameUs / 1000;
uint32_t cycleStartMs;
uint32_t lastUpdateMs;
int previousHalf = -1;

void setup() {
  Serial.begin(115200);
  if (!ledcAttach(ServoPin, 50, DutyBits)) {
    Serial.println("SERVO_SWEEP: PWM setup failed");
    for (;;) delay(1000);
  }
  cycleStartMs = millis();
  lastUpdateMs = cycleStartMs - StepMs;
}

void loop() {
  const uint32_t now = millis();
  if (now - lastUpdateMs < StepMs) {
    delay(1);
    return;
  }
  lastUpdateMs = now;
  const uint32_t elapsed = now - cycleStartMs;
  const uint32_t phaseMs = elapsed % (2 * HalfCycleMs);
  cycleStartMs = now - phaseMs;
  const int half = phaseMs < HalfCycleMs ? 0 : 1;
  uint32_t travelMs = half == 0 ? phaseMs : 2 * HalfCycleMs - phaseMs;
  // Issue the exact endpoint on the first update after each reversal.
  if (half != previousHalf) travelMs = half == 0 ? 0 : HalfCycleMs;
  const uint32_t pulseUs = MinPulseUs + (MaxPulseUs - MinPulseUs) * travelMs / HalfCycleMs;
  ledcWrite(ServoPin, pulseUs * ((1u << DutyBits) - 1) / FrameUs);
  if (half != previousHalf) {
    Serial.printf("SERVO_SWEEP t=%lu ms command=%u deg\n",
                  static_cast<unsigned long>(now), half == 0 ? 0u : 180u);
    previousHalf = half;
  }
}
