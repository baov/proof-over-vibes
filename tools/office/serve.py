#!/usr/bin/env python3
"""Show the roles of a run working on an isometric office floor.

Run it from the project you are working on, then start your agent workflow:

    python3 tools/office/serve.py --root .
"""

from __future__ import annotations

import argparse
import tempfile
import threading
import webbrowser
from pathlib import Path

from floor.demo import run_demo
from floor.server import make_server


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".", help="project whose .plans/ and .reviews/ are watched (default: .)")
    parser.add_argument("--port", type=int, default=8765, help="port to listen on, 0 picks a free one (default: 8765)")
    parser.add_argument("--no-open", action="store_true", help="do not open the browser")
    parser.add_argument("--demo", action="store_true", help="watch a scripted run in a temporary folder instead of --root")
    arguments = parser.parse_args()

    root = Path(arguments.root).resolve()
    if arguments.demo:
        root = Path(tempfile.mkdtemp(prefix="office-demo-"))
        threading.Thread(target=run_demo, args=(root,), daemon=True).start()
    server = make_server(root, port=arguments.port)
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"Office floor on {url} (watching {root}) — Ctrl+C to stop")
    if not arguments.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
