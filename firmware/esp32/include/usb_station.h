#pragma once

#include <stdio.h>
#include "station.h"

class UsbStation {
 public:
  static constexpr size_t LineCapacity = 96;

  UsbStation(Station& station, const char* boot) : station(station), boot(boot) {}

  template <typename Send>
  void capture(const Send& send) {
    if (connected && station.phase == Phase::WAIT_AI &&
        station.job != announcedJob) {
      announce(send);
    }
  }

  void checkHeartbeat(uint32_t now) {
    if (connected && now - station.lastBeat >= station.t.heartbeat) {
      connected = false;
      station.lost(now);
    }
  }

  void fault(const char* reason, uint32_t now) {
    connected = false;
    station.ready = false;
    // A late serial frame must not replace a manual stop or an existing trip.
    if (station.phase == Phase::FAULT ||
        (station.phase == Phase::OFF && !strcmp(station.reason, "MANUAL_OFF"))) return;
    station.stop(reason, now);
  }

  template <typename Send>
  void receive(char byte, uint32_t now, uint8_t home, uint8_t reach, const Send& send) {
    if (byte == '\n') {
      if (!discard) {
        if (length && line[length - 1] == '\r') --length;
        line[length] = '\0';
        handle(now, home, reach, send);
      }
      length = 0;
      discard = false;
    } else if (!discard) {
      if (length == sizeof(line) - 1 || (byte < ' ' && byte != '\r') ||
          byte > '~') {
        fault("SERIAL_FRAME", now);
        discard = true;
      } else {
        line[length++] = byte;
      }
    }
  }

 private:
  Station& station;
  const char* boot;
  char line[LineCapacity]{};
  size_t length = 0;
  bool discard = false, connected = false;
  uint32_t announcedJob = 0;
  uint32_t acceptedJob = 0;
  const char* accepted = nullptr;

  static bool sequence(const char* value) {
    if (strlen(value) != 8) return false;
    for (; *value; ++value)
      if ((*value < '0' || *value > '9') && (*value < 'a' || *value > 'f'))
        return false;
    return true;
  }

  void identifier(char* id, size_t size) const {
    snprintf(id, size, "%s-%lu", boot, (unsigned long)station.job);
  }

  template <typename Send>
  void announce(const Send& send) {
    char id[44], message[54];
    identifier(id, sizeof id);
    snprintf(message, sizeof message, "CAPTURE,%s\n", id);
    send(message);
    announcedJob = station.job;
  }

  template <typename Send>
  void handle(uint32_t now, uint8_t home, uint8_t reach, const Send& send) {
    // Bound field count and reject empty fields, including a trailing comma.
    const char* fields[4] = {line};
    size_t count = 1;
    for (char* c = line; *c; ++c) {
      if (*c != ',') continue;
      if (count == 4 || c == fields[count - 1] || !c[1]) {
        fault("SERIAL_FRAME", now);
        return;
      }
      *c = '\0';
      fields[count++] = c + 1;
    }
    if (count == 4 && !strcmp(fields[0], "PING") && sequence(fields[1]) &&
        (!strcmp(fields[3], "0") || !strcmp(fields[3], "1"))) {
      if (!strcmp(fields[2], "-")) {
        station.lost(now);
        station.lastBeat = now;
        connected = true;
      } else if (connected && !strcmp(fields[2], boot)) {
        station.command(now, fields[3][0] == '1', 0, "WAIT");
      } else {
        fault("SERIAL_SESSION", now);
        return;
      }
      if (station.phase == Phase::WAIT_AI) announce(send);
      char response[256];
      snprintf(response, sizeof response,
               "{\"v\":1,\"seq\":\"%s\",\"boot\":\"%s\",\"job\":%lu,"
               "\"completed\":%lu,\"phase\":\"%s\",\"ir\":%s,\"pwm\":%u,"
               "\"servo\":%u,\"reason\":\"%s\"}\n",
               fields[1], boot, (unsigned long)station.job,
               (unsigned long)station.completed, phaseName(station.phase),
               station.ir ? "true" : "false", station.duty(now),
               station.phase == Phase::PUSH ? reach : home,
               station.reason);
      send(response);
      return;
    }

    const char* result = nullptr;
    if (count == 3 && !strcmp(fields[0], "RESULT")) {
      if (!strcmp(fields[2], "PASS")) result = "PASS";
      if (!strcmp(fields[2], "FAIL")) result = "FAIL";
    } else if (count == 2 && !strcmp(fields[0], "HOLD")) {
      result = "HOLD";
    }
    if (!result) {
      fault("SERIAL_FRAME", now);
      return;
    }

    char id[44];
    identifier(id, sizeof id);
    if (!connected || strcmp(fields[1], id)) {
      fault("SERIAL_JOB", now);
      return;
    }
    if (accepted && acceptedJob == station.job) {
      if (strcmp(accepted, result)) {
        fault("SERIAL_CONFLICT", now);
        return;
      }
    } else {
      if (station.phase != Phase::WAIT_AI || !station.ready || !station.ir ||
          now - station.since >= station.t.inspection) {
        fault("SERIAL_JOB", now);
        return;
      }
      // Results never extend the heartbeat or grant PC readiness.
      station.applyVerdict(now, station.job,
                           !strcmp(result, "PASS") ? "OK" :
                           !strcmp(result, "FAIL") ? "NG" : "HOLD");
      accepted = result;
      acceptedJob = station.job;
    }
    char reply[56];
    snprintf(reply, sizeof reply, "ACK,%s,%s\n", id, result);
    send(reply);
  }
};
