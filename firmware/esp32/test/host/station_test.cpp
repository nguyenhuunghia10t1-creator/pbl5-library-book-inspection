// Build on a PC with any C++11 compiler. Exercises the exact firmware control
// logic.
#include "../../include/station.h"
#include "../../include/usb_station.h"
#include "../../include/radio_request.h"

#include <assert.h>
#include <stdio.h>
#include <string>

struct Rig {
  Station s;
  uint32_t now = 4000;
  Rig() {
    s.tick(now, false);
    step(200, false);
    s.button(now);
    assert(s.phase == Phase::RUN);
  }
  void step(unsigned ms, bool ir) {
    while (ms) {
      unsigned part = ms > 25 ? 25 : ms;
      now += part;
      ms -= part;
      s.command(now, true, 0, "WAIT");
      s.tick(now, ir);
    }
  }
  void book() {
    step(25, true);
    assert(s.phase == Phase::WAIT_AI && s.duty(now) == 0);
  }
  void send(const char* result) { s.command(now, true, s.job, result); }
};

// Feed the same byte-oriented USB parser used by loop(), with deterministic time.
static void testUsb() {
  const char boot[] = "0123456789abcdef0123456789abcdef";
  const std::string id = std::string(boot) + "-1";
  const std::string ping = std::string("PING,12345678,") + boot + ",1\n";
  const std::string hello = "PING,12345678,-,0\n";
  for (const char* verdict : {"PASS", "FAIL", "HOLD", "WRONG_ID", "MANUAL",
                              "BAD_FRAME", "TIMEOUT", "LINK_LOST"}) {
    Station s;
    uint32_t now = 4000;
    UsbStation usb(s, boot);
    std::string tx;
    const auto send = [&](const char* line) { tx += line; };
    const auto receive = [&](const std::string& bytes) {
      for (char byte : bytes) usb.receive(byte, now, 0, 180, send);
    };
    receive(hello);
    assert(s.phase == Phase::OFF && !s.ready);
    receive(ping);
    s.tick(now, false);
    now += s.t.clear;
    s.tick(now, false);
    s.button(now);
    s.tick(now, true);
    tx.clear();
    usb.capture(send);
    usb.capture(send);
    assert(s.duty(now) == 0 && tx == "CAPTURE," + id + "\n");
    tx.clear();
    receive(ping);
    assert(tx.find("CAPTURE," + id + "\n{") == 0 && s.job == 1);
    tx.clear();
    std::string choice(verdict);
    if (choice == "PASS" || choice == "FAIL" || choice == "HOLD") {
      const std::string result = choice == "HOLD" ? "HOLD," + id :
                                  "RESULT," + id + "," + choice;
      receive(result);
      assert(tx.empty() && s.phase == Phase::WAIT_AI);
      receive("\r\n");
      assert(tx == "ACK," + id + "," + choice + "\n");
      const Phase accepted = s.phase;
      assert(accepted == (choice == "PASS" ? Phase::RELEASE :
                         choice == "FAIL" ? Phase::PUSH : Phase::FAULT));
      now++;
      const uint32_t entered = s.since;
      tx.clear();
      receive(result + "\n");
      assert(s.phase == accepted && s.since == entered && tx.find("ACK,") == 0);
      receive("RESULT," + id + (choice == "FAIL" ? ",PASS\n" : ",FAIL\n"));
      assert(s.phase == Phase::FAULT && s.duty(now) == 0);
    } else if (choice == "WRONG_ID") {
      receive("RESULT," + std::string(boot) + "-2,PASS\n");
    } else if (choice == "MANUAL") {
      s.button(now);
      receive("RESULT," + id + ",PASS\n");
      assert(s.phase == Phase::OFF && !strcmp(s.reason, "MANUAL_OFF"));
    } else if (choice == "BAD_FRAME") {
      receive(std::string(120, 'x') + "\n");
    } else if (choice == "TIMEOUT") {
      now += s.t.inspection;
      receive("RESULT," + id + ",PASS\n");
    } else {
      now += s.t.heartbeat;
      usb.checkHeartbeat(now);
      receive("RESULT," + id + ",FAIL\n");
    }
    assert(!s.enabled() && s.duty(now) == 0 && s.completed == 0);
    receive(hello);
    receive(ping);
    assert(!s.enabled());
  }
}

int main() {
  const std::string radioBoot = "0123456789abcdef0123456789abcdef";
  const std::string hello = "PING,12345678,-,0\n";
  const std::string ready = "PING,12345678," + radioBoot + ",1\n";
  const std::string decision = "RESULT," + radioBoot + "-1,PASS\n";
  const auto valid = [&](const std::string& wire) {
    return RadioRequest::valid(wire.data(), wire.size(), radioBoot.c_str());
  };
  assert(valid(hello) && valid(ready) && valid(decision + ready));
  assert(!valid(decision) && !valid(hello + hello) && !valid(decision + hello));
  assert(!valid(decision + "PING,12345678," + radioBoot + ",0\n"));
  assert(!valid(decision + ready + ready) && !valid(ready.substr(0, ready.size() - 1)));
  assert(!valid(std::string("PING,12345678,") + std::string(32, '7') + ",1\n"));
  for (const std::string choice : {"PASS", "FAIL", "HOLD"}) {
    Station station;
    UsbStation wire(station, radioBoot.c_str());
    uint32_t now = 4000;
    const auto exchange = [&](const std::string& bytes) {
      assert(valid(bytes));
      std::string reply;
      for (char c : bytes) wire.receive(c, now, 0, 180, [&](const char* s) { reply += s; });
      assert(!reply.empty() && reply.size() <= RadioRequest::MaxLength);
      return reply;
    };
    exchange(hello);
    exchange(ready);
    station.tick(now, false);
    now += 200;
    station.button(now);
    station.tick(++now, true);
    assert(exchange(ready).find("CAPTURE,") == 0);
    const auto id = radioBoot + "-1";
    const auto command = choice == "HOLD" ? "HOLD," + id : "RESULT," + id + "," + choice;
    const auto reply = exchange(command + "\n" + ready);
    assert(reply.find("ACK," + id + "," + choice + "\n{") == 0);
    assert(station.phase == (choice == "PASS" ? Phase::RELEASE :
                             choice == "FAIL" ? Phase::PUSH : Phase::FAULT));
    wire.checkHeartbeat(now + station.t.heartbeat);
    assert(!station.enabled());
  }
  testUsb();
  {
    Rig r;
    r.book();
    r.s.command(r.now, true, 99, "NG");
    assert(r.s.phase == Phase::WAIT_AI);
    r.send("OK");
    assert(r.s.phase == Phase::RELEASE);
    r.step(300, true);
    r.send("NG");
    assert(r.s.phase == Phase::RELEASE && r.s.job == 1);
    r.step(250, false);
    assert(r.s.completed == 1 && r.s.phase == Phase::RUN);
    r.book();
    assert(r.s.job == 2);
  }
  {
    Rig r;
    r.book();
    r.send("NG");
    r.step(699, true);
    assert(r.s.phase == Phase::PUSH);
    r.send("NG");
    r.step(1, true);
    assert(r.s.phase == Phase::RETRACT);
    r.step(700, false);
    assert(r.s.phase == Phase::SETTLE);
    r.step(1999, false);
    assert(!r.s.motorOn());
    r.step(1, false);
    assert(r.s.completed == 1 && r.s.motorOn());
  }
  {
    Rig r;
    r.book();
    r.send("NG");
    r.step(3600, true);
    assert(r.s.phase == Phase::FAULT && !r.s.completed);
  }
  {
    Rig r;
    r.book();
    r.send("OK");
    r.step(5010, true);
    assert(r.s.phase == Phase::FAULT);
  }
  const char* verdicts[] = {"WAIT", "NG", "OK"};
  for (const char* value : verdicts) {
    Rig r;
    r.book();
    r.send(value);
    r.s.button(r.now);
    r.send("NG");
    assert(r.s.phase == Phase::OFF && r.s.duty(r.now) == 0);
    r.step(3200, false);
    assert(r.s.phase == Phase::OFF);
  }
  {
    Rig r;
    r.book();
    r.send("NG");
    r.s.tick(r.now + 1000, true);
    assert(r.s.phase == Phase::FAULT && !r.s.ready);
    r.s.command(r.now + 1100, true, 1, "OK");
    assert(!r.s.motorOn());
  }
  {
    Rig r;
    r.book();
    r.s.command(r.now, false, r.s.job, "OK");
    assert(r.s.phase == Phase::FAULT);
  }
  {
    Rig r;
    r.book();
    r.step(10001, true);
    r.send("OK");
    assert(r.s.phase == Phase::FAULT);
  }
  puts(
      "PASS: USB capture/result/ack, firmware control, jam, timeouts, "
      "duplicates and manual OFF");
}
