"""Create the private build header for one bridge and one conveyor."""

import argparse
from pathlib import Path
import re
import secrets


def mac(value):
    if not re.fullmatch(r"(?:[A-Fa-f0-9]{2}:){5}[A-Fa-f0-9]{2}", value):
        raise argparse.ArgumentTypeError("Expected six colon-separated MAC bytes.")
    return bytes.fromhex(value.replace(":", ""))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", required=True, type=mac)
    parser.add_argument("--station", required=True, type=mac)
    args = parser.parse_args()
    if args.bridge == args.station:
        parser.error("Use two distinct station-interface MAC addresses.")
    target = Path(__file__).resolve().parents[2] / "data/local/espnow/station_pair.h"
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = ["#pragma once", "#include <stdint.h>"]
    for name, value in (("BridgeMac", args.bridge), ("StationMac", args.station),
                        ("PairPmk", secrets.token_bytes(16)), ("PairLmk", secrets.token_bytes(16))):
        octets = ", ".join(f"0x{byte:02x}" for byte in value)
        lines.append(f"constexpr uint8_t {name}[] = {{{octets}}};")
    try:
        with target.open("x", encoding="ascii") as stream:
            stream.write("\n".join(lines) + "\n")
    except FileExistsError:
        parser.exit(1, "Pair header already exists. Reuse it to rebuild this pair.\n")
    print("Pair header created in data/local/espnow.")
