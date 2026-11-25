# PC-side ESP-NOW bridge

Connect the bridge to Windows by USB at 115200 baud. The conveyor board needs a separate receiver firmware. The standalone button/IR/servo firmware can still be used to test the mechanism independently.

## Build and pair

The first build needs the Wi-Fi station MAC addresses of both boards. With classic ESP32 boards these normally match the base MAC reported by esptool. From the repository root, run:

```text
python firmware/espnow-bridge/provision_pair.py --bridge <bridge-mac> --station <conveyor-mac>
platformio run --project-dir firmware/espnow-bridge --environment esp32dev
```

The first command creates `data/local/espnow/station_pair.h` once. Keep this private file for both firmware builds, including later rebuilds. It contains the two MAC addresses and random ESP-NOW keys. Before upload, identify the bridge by MAC. Add `--target upload --upload-port COMx` to the PlatformIO command using the verified port.

## Receiver contract

Both radios use station mode, channel 1, encrypted unicast, the same PMK/LMK, and the other board as peer. A packet carries up to 250 bytes of ASCII with a final LF. The bridge forwards each PC heartbeat. A RESULT or HOLD immediately followed by a ready heartbeat travels with that heartbeat in the same packet, in serial order. The receiver passes both lines to the existing job-ID and heartbeat checks. It returns ACK and/or CAPTURE before the matching JSON status in one datagram. The conveyor authorizes motion and generates acknowledgements.

For a local check with the station console closed, send `BRIDGE?` and LF at 115200 baud. `RADIO_READY` means this bridge initialized its radio and registered the peer. `TX_QUEUE` counts packets accepted by the local radio driver. `RX` counts received peer packets forwarded to USB. End-to-end acceptance requires a genuine matching response to a readiness-disabled PING from the powered conveyor.

Build the conveyor with `platformio run --project-dir firmware/esp32 --environment espnow_receiver`. Flash the verified conveyor MAC using this environment and the same private header. USB on the receiver prints its boot identity and initial output state. The PC sends control requests through the bridge. For the first radio test, power the detached receiver by USB from a separate supply, connect the bridge to the PC, and keep motor and servo power off.
