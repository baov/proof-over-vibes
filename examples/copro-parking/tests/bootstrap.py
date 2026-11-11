"""Puts `src` on the import path so that `python3 -m unittest discover -s tests` works as is."""
import sys
from pathlib import Path

SRC = str(Path(__file__).resolve().parent.parent / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
