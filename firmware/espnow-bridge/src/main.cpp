#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>

#include "station_pair.h"

namespace {
constexpr uint8_t Channel = 1;
constexpr size_t MaxPacket = 250;
constexpr uint32_t PairWindowMs = 200;

struct Packet {
  uint8_t bytes[MaxPacket];
  size_t length;
};

QueueHandle_t received = nullptr;
uint8_t localMac[6]{};
bool radioReady = false;
uint32_t txQueued = 0;
uint32_t rxForwarded = 0;
char line[96]{};
size_t used = 0;
bool discard = false;
char result[96]{};
uint32_t resultAt = 0;

void fromStation(const esp_now_recv_info_t* info, const uint8_t* bytes, int length) {
  if (!info || !bytes || length < 2 || length > static_cast<int>(MaxPacket) ||
      memcmp(info->src_addr, StationMac, 6) || memcmp(info->des_addr, localMac, 6) ||
      bytes[length - 1] != '\n') return;
  Packet packet{};
  memcpy(packet.bytes, bytes, length);
  packet.length = length;
  xQueueSend(received, &packet, 0);
}

bool startRadio() {
  if (!received || !WiFi.mode(WIFI_STA) ||
      esp_wifi_get_mac(WIFI_IF_STA, localMac) != ESP_OK ||
      memcmp(localMac, BridgeMac, 6) ||
      esp_wifi_set_channel(Channel, WIFI_SECOND_CHAN_NONE) != ESP_OK ||
      esp_now_init() != ESP_OK || esp_now_set_pmk(PairPmk) != ESP_OK) return false;
  esp_now_peer_info_t peer{};
  memcpy(peer.peer_addr, StationMac, 6);
  memcpy(peer.lmk, PairLmk, ESP_NOW_KEY_LEN);
  peer.channel = Channel;
  peer.ifidx = WIFI_IF_STA;
  peer.encrypt = true;
  return esp_now_add_peer(&peer) == ESP_OK && esp_now_register_recv_cb(fromStation) == ESP_OK;
}

void handleLine() {
  if (!strcmp(line, "BRIDGE?")) {
    result[0] = 0;
    Serial.printf("PBL5_BRIDGE,1,%s,%02X:%02X:%02X:%02X:%02X:%02X,CH=%u,TX_QUEUE=%lu,RX=%lu\n",
                  radioReady ? "RADIO_READY" : "RADIO_ERROR", localMac[0], localMac[1],
                  localMac[2], localMac[3], localMac[4], localMac[5], Channel,
                  static_cast<unsigned long>(txQueued), static_cast<unsigned long>(rxForwarded));
    return;
  }
  if (!strncmp(line, "RESULT,", 7) || !strncmp(line, "HOLD,", 5)) {
    memcpy(result, line, used + 1);
    resultAt = millis();
    return;
  }
  if (radioReady && !strncmp(line, "PING,", 5)) {
    // Python writes a decision and its heartbeat together. Keep both in one
    // datagram so the receiver cannot get an isolated decision after a loss.
    char wire[MaxPacket];
    const bool withResult = result[0] && millis() - resultAt < PairWindowMs &&
                            used >= 2 && !strcmp(line + used - 2, ",1");
    const int length = withResult ? snprintf(wire, sizeof wire, "%s\n%s\n", result, line)
                                  : snprintf(wire, sizeof wire, "%s\n", line);
    if (length > 0 && length < static_cast<int>(sizeof wire) &&
        esp_now_send(StationMac, reinterpret_cast<const uint8_t*>(wire), length) == ESP_OK)
      ++txQueued;
  }
  // Only the conveyor sends CAPTURE, ACK and telemetry. Missing replies time out.
  result[0] = 0;
}

void fromPc(char c) {
  if (c == '\n') {
    if (!discard) {
      if (used && line[used - 1] == '\r') --used;
      line[used] = 0;
      handleLine();
    }
    used = 0;
    discard = false;
  } else if (!discard) {
    if (used >= sizeof line - 1 || (c < ' ' && c != '\r') || c > '~') {
      discard = true;
      result[0] = 0;
    } else {
      line[used++] = c;
    }
  }
}
}  // namespace

void setup() {
  Serial.begin(115200);
  received = xQueueCreate(8, sizeof(Packet));
  radioReady = startRadio();
}

void loop() {
  for (size_t i = 0; i < MaxPacket && Serial.available(); ++i)
    fromPc(static_cast<char>(Serial.read()));
  Packet packet;
  if (received && xQueueReceive(received, &packet, 0) == pdTRUE) {
    Serial.write(packet.bytes, packet.length);
    ++rxForwarded;
  }
  delay(1);
}
