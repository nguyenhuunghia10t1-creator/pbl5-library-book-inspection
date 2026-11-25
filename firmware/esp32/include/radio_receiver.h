#pragma once

#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>

#include "radio_request.h"
#include "station_pair.h"

namespace Receiver {
constexpr uint8_t Channel = 1;
struct Request {
  char bytes[RadioRequest::MaxLength];
  size_t length;
  uint32_t receivedAt;
};
static QueueHandle_t inbox;
static uint8_t localMac[6];

inline void onPacket(const esp_now_recv_info_t* info, const uint8_t* data, int length) {
  if (!info || !data || memcmp(info->src_addr, BridgeMac, 6) ||
      memcmp(info->des_addr, StationMac, 6)) return;
  Request packet{};
  if (length > 0 && length <= static_cast<int>(sizeof packet.bytes)) {
    packet.length = length;
    memcpy(packet.bytes, data, packet.length);
  }
  packet.receivedAt = millis();
  xQueueSend(inbox, &packet, 0);
}

inline bool start() {
  inbox = xQueueCreate(4, sizeof(Request));
  if (!inbox || !WiFi.mode(WIFI_STA) ||
      esp_wifi_get_mac(WIFI_IF_STA, localMac) != ESP_OK ||
      memcmp(localMac, StationMac, 6) || esp_wifi_set_ps(WIFI_PS_NONE) != ESP_OK ||
      esp_wifi_set_channel(Channel, WIFI_SECOND_CHAN_NONE) != ESP_OK ||
      esp_now_init() != ESP_OK || esp_now_set_pmk(PairPmk) != ESP_OK) return false;
  esp_now_peer_info_t peer{};
  memcpy(peer.peer_addr, BridgeMac, 6);
  memcpy(peer.lmk, PairLmk, ESP_NOW_KEY_LEN);
  peer.channel = Channel;
  peer.ifidx = WIFI_IF_STA;
  peer.encrypt = true;
  return esp_now_add_peer(&peer) == ESP_OK && esp_now_register_recv_cb(onPacket) == ESP_OK;
}

inline void poll(UsbStation& protocol, const char* boot, uint8_t home, uint8_t reach) {
  Request packet;
  if (xQueueReceive(inbox, &packet, 0) != pdTRUE) return;
  const uint32_t now = millis();
  if (now - packet.receivedAt > 250 || !RadioRequest::valid(packet.bytes, packet.length, boot)) {
    protocol.fault("RADIO_FRAME", now);
    return;
  }
  // A poll returns at most one ACK or CAPTURE followed by one matching JSON status.
  // Send them together, preserving USB line order across the wireless hop.
  uint8_t reply[RadioRequest::MaxLength];
  size_t used = 0;
  bool overflow = false;
  auto append = [&](const char* line) {
    const size_t n = strlen(line);
    if (n > sizeof(reply) - used) { overflow = true; return; }
    memcpy(reply + used, line, n);
    used += n;
  };
  for (size_t i = 0; i < packet.length; ++i)
    protocol.receive(packet.bytes[i], now, home, reach, append);
  if (overflow || !used || esp_now_send(BridgeMac, reply, used) != ESP_OK)
    protocol.fault("RADIO_REPLY", now);
}
}
