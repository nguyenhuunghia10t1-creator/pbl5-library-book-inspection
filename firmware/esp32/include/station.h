#pragma once
#include <stdint.h>
#include <string.h>

// All time comparisons use unsigned elapsed milliseconds (also across millis
// wrap).
struct Timing {
  uint32_t heartbeat = 1000, inspection = 10000, push = 700, retract = 700;
  uint32_t afterRetract = 2000, clear = 180, releaseLimit = 5000, ramp = 2000;
};
enum class Phase { OFF, RUN, WAIT_AI, PUSH, RETRACT, SETTLE, RELEASE, FAULT };
inline const char* phaseName(Phase p) {
  static const char* names[] = {"OFF",     "RUN",    "WAIT_AI", "PUSH",
                                "RETRACT", "SETTLE", "RELEASE", "FAULT"};
  return names[static_cast<unsigned>(p)];
}
struct Station {
  Timing t;
  Phase phase = Phase::OFF;
  bool ir = false, clearTracked = false, ready = false;
  uint32_t job = 0, completed = 0, since = 0, clearSince = 0, lastBeat = 0,
           motorSince = 0, homeSince = 0;
  const char* reason = "STARTUP";
  bool enabled() const { return phase != Phase::OFF && phase != Phase::FAULT; }
  bool motorOn() const {
    return phase == Phase::RUN || phase == Phase::RELEASE;
  }
  uint16_t duty(uint32_t now) const {
    if (!motorOn()) return 0;
    uint32_t elapsed = now - motorSince;
    return elapsed >= t.ramp ? 1023 : elapsed * 1023 / t.ramp;
  }
  void enter(Phase next, uint32_t now) {
    phase = next;
    since = now;
  }
  void stop(const char* why, uint32_t now, bool manual = false) {
    if (phase == Phase::PUSH || phase == Phase::RETRACT) homeSince = now;
    reason = why;
    enter(manual ? Phase::OFF : Phase::FAULT, now);
  }
  void lost(uint32_t now) {
    ready = false;
    if (enabled()) stop("LINK_LOST", now);
  }
  bool clearLongEnough(uint32_t now) const {
    return clearTracked && !ir && now - clearSince >= t.clear;
  }
  void button(uint32_t now) {
    if (enabled()) {
      stop("MANUAL_OFF", now, true);
      return;
    }
    if (!ready || now - lastBeat >= t.heartbeat) {
      reason = "PC_NOT_READY";
      return;
    }
    if (!clearLongEnough(now)) {
      reason = "CLEAR_STATION";
      return;
    }
    if (now - homeSince < t.retract + t.afterRetract) {
      reason = "RETURN_WAIT";
      return;
    }
    motorSince = now;
    reason = "";
    enter(Phase::RUN, now);
  }
  void command(uint32_t now, bool healthy, uint32_t id, const char* verdict) {
    lastBeat = now;
    ready = healthy;
    if (!healthy) {
      if (enabled()) stop("PC_NOT_READY", now);
      return;
    }
    applyVerdict(now, id, verdict);
  }
  void applyVerdict(uint32_t now, uint32_t id, const char* verdict) {
    if (phase != Phase::WAIT_AI || id != job) return;
    if (now - since >= t.inspection) {
      stop("AI_TIMEOUT", now);
      return;
    }
    if (!ir && strcmp(verdict, "WAIT")) {
      stop("BOOK_MOVED", now);
      return;
    }
    if (!strcmp(verdict, "HOLD"))
      stop("INSPECTION_HOLD", now);
    else if (!strcmp(verdict, "OK")) {
      motorSince = now;
      enter(Phase::RELEASE, now);
    } else if (!strcmp(verdict, "NG"))
      enter(Phase::PUSH, now);
  }
  void tick(uint32_t now, bool occupied) {
    ir = occupied;
    if (ir)
      clearTracked = false;
    else if (!clearTracked) {
      clearTracked = true;
      clearSince = now;
    }
    if (ready && now - lastBeat >= t.heartbeat) lost(now);
    switch (phase) {
      case Phase::RUN:
        if (ir) {
          if (job == UINT32_MAX) {
            stop("JOB_LIMIT", now);
            break;
          }
          ++job;
          enter(Phase::WAIT_AI, now);
        }
        break;
      case Phase::WAIT_AI:
        if (clearLongEnough(now))
          stop("BOOK_MOVED", now);
        else if (now - since >= t.inspection)
          stop("AI_TIMEOUT", now);
        break;
      case Phase::PUSH:
        if (now - since >= t.push) {
          homeSince = now;
          enter(Phase::RETRACT, now);
        }
        break;
      case Phase::RETRACT:
        if (now - since >= t.retract) enter(Phase::SETTLE, now);
        break;
      case Phase::SETTLE:
        if (now - since >= t.afterRetract) {
          if (!clearLongEnough(now))
            stop("NG_NOT_CLEAR", now);
          else {
            completed = job;
            motorSince = now;
            enter(Phase::RUN, now);
          }
        }
        break;
      case Phase::RELEASE:
        if (clearLongEnough(now)) {
          completed = job;
          enter(Phase::RUN, now);
        } else if (now - since >= t.releaseLimit)
          stop("RELEASE_JAM", now);
        break;
      default:
        break;
    }
  }
};
