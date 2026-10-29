"""Relocation regressions: paths must work independently of the shell directory."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from vision.opencv.config import ROOT


class RelocationTests(unittest.TestCase):
    def test_default_config_from_another_directory(self):
        code = ("import sys,json;sys.path.insert(0,sys.argv[1]);"
                "from vision.opencv.config import ROOT,load_config;"
                "print(json.dumps({'root':str(ROOT),'output':load_config().output_dir}))")
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, "-c", code, str(ROOT)], cwd=folder,
                                    capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        config = json.loads(result.stdout)
        self.assertEqual(config["output"], "data/opencv/collection")
        self.assertEqual(Path(config["root"]), Path(__file__).resolve().parents[1])

    def test_script_launcher_from_another_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, str(ROOT / "scripts/capture_covers.py"), "--help"],
                                    cwd=folder, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--camera", result.stdout)

    def test_module_entrypoint(self):
        result = subprocess.run([sys.executable, "-m", "vision.opencv", "--help"],
                                cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--image", result.stdout)


if __name__ == "__main__":
    unittest.main()
