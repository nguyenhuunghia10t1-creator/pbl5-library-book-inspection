r"""Launch the desktop collector from any working directory."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from software.desktop.cover_capture_app import main


if __name__ == "__main__":
    raise SystemExit(main())
