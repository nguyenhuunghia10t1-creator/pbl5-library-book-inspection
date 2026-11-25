# PBL5 · Book inspection conveyor

A book stops at the IR sensor while a Windows PC inspects its cover. An OK book continues to the end tray. For NG, the conveyor controller extends the pusher, retracts it and waits before restarting the belt. The PC connects by USB to a bridge ESP32. The bridge exchanges messages with the conveyor ESP32 over ESP-NOW.

**Start here:** [Field checklist for 22 November](docs/FIELD_CHECKLIST.md) · [Printable operator guide](docs/STATION_QUICKSTART.html) · [Installation and troubleshooting](docs/INSPECTION_STATION.md).

## Run on Windows

Open one launcher at a time. Both boards in the installed pair already have their role-specific firmware.

| To try | Launcher | What decides OK/NG |
|---|---|---|
| Actual belt, sensor and pusher | [ManualMechanics.cmd](scripts/windows/ManualMechanics.cmd) | Operator buttons |
| USB camera and classifier on the PC | [TestCameraAI.cmd](scripts/windows/TestCameraAI.cmd) | Model on a captured frame |
| Offline practice without devices | [SimulateBooks.cmd](scripts/windows/SimulateBooks.cmd) | Selected outcome or model on a supplied image |
| Direct OK/NG sorting | [DirectSorting.cmd](scripts/windows/DirectSorting.cmd) | Highest model class on the frame captured after the IR stop |
| Calibrated sorting | [InspectBooks.cmd](scripts/windows/InspectBooks.cmd) | Model after the known-book checks pass |

For a new PC, install Python 3.11, create `.venv-inspection`, install `requirements-inspection.txt` and supply the trained classifier at `weights/best.pt`. The compatible model path, class mapping and image size are configurable in [station.json](configs/station.json). See the [setup guide](docs/INSPECTION_STATION.md).

## Set up on another Windows PC

From the repository root, install the dependencies with Python 3.11 and open the simulator.

```powershell
py -3.11 -m venv .venv-inspection
& ./.venv-inspection/Scripts/python.exe -m pip install -r requirements-inspection.txt
& ./scripts/windows/SimulateBooks.cmd
```

The simulator can run a manually selected OK or NG cycle without an ESP32, a camera, or a model. For camera testing or automatic sorting, obtain the team's classifier through a private channel and place it at `weights/best.pt`. Verify it with `Get-FileHash weights/best.pt`. The installed two-class checkpoint has SHA-256 `662e543e1d29538f799a444583682d9f80bce7ad7e5c5f0e4fb67aa42bf0c357`. For a different camera, update the device name in [station.json](configs/station.json). For physical operation, follow the [connection guide](docs/INSPECTION_STATION.md) to select the actual COM port and configure the radio bridge.

The [Colab notebook](vision/yolo/train_book_defect_v23_colab.ipynb) documents how to train a two-class classifier on the book-defect-v23 dataset.

## Repository map

| Location | Purpose |
|---|---|
| `firmware/esp32/` · `firmware/espnow-bridge/` | Conveyor receiver and PC bridge. [Pairing and build instructions](firmware/espnow-bridge/README.md) |
| `software/controller/` · `software/inspection/` · `software/web/` | Transport and simulator, decisions and SQLite, operator screen |
| `vision/opencv/` · `vision/yolo/` | Camera acquisition, cover preparation and classifier inference |
| `configs/` · `weights/` | Station settings, fixed damaged-cover check and local model |
| `data/local/station/` · `data/local/espnow/` | Local inspection records and private board pairing |
| `scripts/windows/` · `tests/` | Launchers and software regression tests |
| `docs/` · [PROGRESS.md](PROGRESS.md) | Operator instructions, engineering decisions and dated results |

## Development and earlier work

Run the station checks from the repository root with the station environment active and `httpx` installed for the HTTP tests.

```powershell
python scripts/check_repository.py
python -B -m unittest discover -s tests -v
node --test tests/web/station_ui.test.js
```

The [QR cover collector](docs/COVER_CAPTURE.md) still has its own [launcher](scripts/windows/CaptureCovers.cmd) and `.venv`. The [Damaged Books detector study](docs/DAMAGED_BOOKS_RUN1_ANALYSIS.md) and [annotation rules](docs/DAMAGED_BOOKS_ANNOTATION_RULES.md) document earlier training work. Original lessons remain in `examples/opencv_basics/`. For team changes, see the [contribution guide](CONTRIBUTING.md) and [design decisions](docs/DECISIONS.md).
