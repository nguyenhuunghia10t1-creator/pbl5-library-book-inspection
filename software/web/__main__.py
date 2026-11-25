import argparse
import json
import socket
import threading
import urllib.error
import urllib.request
import webbrowser
import uvicorn
from .app import create_app


def main():
    parser = argparse.ArgumentParser(description="PBL5 book inspection station")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--simulate", action="store_true")
    modes.add_argument("--camera-test", action="store_true")
    modes.add_argument("--manual", action="store_true", help="Test real mechanics with operator OK/NG decisions.")
    modes.add_argument("--direct", action="store_true", help="Route by the top class of a fresh post-stop frame.")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    url = f"http://127.0.0.1:{args.port}/"
    page_url = url + "?mode=camera-test" if args.camera_test else url
    mode = ("camera-test" if args.camera_test else "simulation" if args.simulate
            else "hardware-manual" if args.manual else "hardware")
    # Reserve the port before starting the service that owns the camera or USB.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        try:
            listener.bind(("127.0.0.1", args.port))
        except OSError:
            try:
                with urllib.request.urlopen(url + "api/status", timeout=2) as response:
                    current = json.load(response)
            except (OSError, ValueError, urllib.error.URLError):
                parser.exit(1, f"Port {args.port} is busy. Close the other application.\n")
            if not isinstance(current, dict) or (current.get("mode") != mode or bool(current.get("direct_routing")) != args.direct):
                parser.exit(1, "Another station mode is open. Stop the belt, press Ctrl+C in "
                               "its console, then open the desired launcher.\n")
            if not args.no_browser:
                webbrowser.open(page_url)
            return
        listener.listen()
        if not args.no_browser:
            threading.Timer(1.3, lambda: webbrowser.open(page_url)).start()
        app = create_app(args.simulate, camera_test=args.camera_test, manual=args.manual, direct=args.direct)
        uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=args.port,
                                      access_log=False)).run(sockets=[listener])


if __name__ == "__main__":
    main()
