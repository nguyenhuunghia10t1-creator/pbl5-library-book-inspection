 # Conveyor field checklist · 22 November 2026

**First job tomorrow:** watch one NG book from the sensor to the reject tray. On 21 November the controller completed one manual OK and one NG cycle. The next NG stopped with `NG_NOT_CLEAR`. Physical tray arrival still needs an observer.

## Bring and set up

- [ ] Bring the paired boards, USB data cable, phone and mount, and four distinct labeled books (two OK, two NG). Bring a compatible spare classifier if available.
- [ ] Label the boards **PC bridge** and **Conveyor**, mark belt direction and label both trays. Secure the cables away from the pusher. Keep the physical stop button visible.
- [ ] Mount the phone above the stopped book. Mark the stopping position and use steady lighting so the cover fills the same area on every pass.
- [ ] Before moving to another PC, back up the working source, model and station records. Keep the pairing header in a private backup. Several station modules and launchers are still uncommitted in this checkout.

## Run in order

| Step | Action | Pass when |
|---|---|---|
| 1 · Mechanics | Open [Manual Mechanics](../scripts/windows/ManualMechanics.cmd). Check COM and IR. With the mechanism clear, press physical Start. Feed one book at a time and select OK or NG within **8 s**. | OK reaches the end tray. NG clears IR, reaches the reject tray, and the pusher retracts before restart. One decision per book. If `NG_NOT_CLEAR` recurs, stop and isolate load power before inspecting the pusher travel or sensor position. |
| 2 · Camera | Stop the belt, close the station console and open [Camera Test](../scripts/windows/TestCameraAI.cmd). Move a book into and out of view, then capture it. | Both the preview and saved shot show the change. The last check returned 56 frame samples of a frozen view. Reconnect DroidCam and repeat if needed. |
| 3 · AI | Open [AI Inspection](../scripts/windows/InspectBooks.cmd). Save the empty belt. Calibrate on one OK/NG pair and test on the other pair with different book IDs. Run the fixed torn-cover check. | Independent samples include a correctly accepted OK and NG, with zero NG accepted as OK. The installed model previously called torn `IMG_7.jpg` OK at 99.90%. If blocked, demo in Manual Mechanics or change the classifier and repeat validation. |
| 4 · Evidence | Once the gates pass, run the planned 30-book pilot. Record truth, decision, observed tray and stops. Test physical stop and loss of camera/bridge under supervision. | Failures stop motion, recovery requires operator restart, and the log distinguishes accepted books, holds and actual tray outcomes. |

**Demo handoff:** take one labeled overview photo and one short video showing both routes and the operator screen. State whether decisions in the video came from the operator or the AI. For a PC-only rehearsal, open [Simulation](../scripts/windows/SimulateBooks.cmd).

## Repository audit

| Area | Disposition |
|---|---|
| Runtime | Keep the two firmware projects, station software, `configs/reference/IMG_7.jpg`, `weights/best.pt`, SQLite records and private pairing header together with their current paths. |
| Earlier research | In `docs/`, `COLAB_RUN1_ANALYSIS.md`, `DAMAGED_BOOKS_ANNOTATION_RULES.md`, `DAMAGED_BOOKS_RUN1_ANALYSIS.md`, `DAMAGED_BOOKS_RUN1_TABLES.md` and `reviews/` support detector research. The QR collector, OpenCV lessons and standalone firmware support separate experiments and recovery. |
| Removed duplication | Root `train/`, `valid/`, `test/`, `data.yaml` and both export READMEs are preserved inside `data/local/damaged_books_v1/Damaged Books.v1i.yolov11.zip`. The duplicate Colab extraction is recoverable from the ZIP in `colab-results/`. Firmware and host-test build caches regenerate on build. |
| Still missing | Observation of the NG exit, a changing DroidCam feed, a passing camera/model validation and a recorded end-to-end pilot. |
