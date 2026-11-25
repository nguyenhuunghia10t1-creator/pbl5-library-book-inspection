#pragma once

#include <stddef.h>
#include <string.h>

namespace RadioRequest {
constexpr size_t MaxLength = 250;

// Validate the entire datagram before a decision can reach the motion controller.
inline bool valid(const char* data, size_t length, const char* boot) {
  if (length < 2 || length > MaxLength || data[length - 1] != '\n') return false;
  const char* end = data + length - 1;
  const char* ping = data;
  for (const char* p = data; p < end; ++p) {
    if (*p == '\n') {
      if (ping != data) return false;
      ping = p + 1;
    } else if (*p < ' ' || *p > '~') {
      return false;
    }
  }
  if (end - ping < 17 || memcmp(ping, "PING,", 5) || ping[13] != ',' ||
      end[-2] != ',' || (end[-1] != '0' && end[-1] != '1')) return false;
  for (unsigned i = 5; i < 13; ++i) {
    const char c = ping[i];
    if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
  }
  if (end - ping == 17 && ping[14] == '-') return ping == data && end[-1] == '0';
  if (end - ping != 48 || memcmp(ping + 14, boot, 32)) return false;
  if (ping == data) return true;
  const size_t first = static_cast<size_t>(ping - data - 1);
  return end[-1] == '1' && first < 96 &&
         ((first > 7 && !memcmp(data, "RESULT,", 7)) ||
          (first > 5 && !memcmp(data, "HOLD,", 5)));
}
}
