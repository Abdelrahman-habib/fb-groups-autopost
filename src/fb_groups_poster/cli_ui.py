from __future__ import annotations

import sys
import threading
import time


class Spinner:
    """Minimal dot spinner for pretty stage feedback in the CLI.

    Usage:
        sp = Spinner("Doing work")
        sp.start()
        ... do work ...
        sp.succeed(" — done")
    """

    def __init__(self, label: str):
        self.label = label
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._frames =  ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self._file = sys.stdout

    def _run(self) -> None:
        idx = 0
        while not self._stop.is_set():
            frame = self._frames[idx % len(self._frames)]
            self._file.write(f"\r[ {frame} ] {self.label}")
            self._file.flush()
            idx += 1
            time.sleep(0.2)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=1)

    def succeed(self, suffix: str = "") -> None:
        self.stop()
        line = f"\r[ ✅ ] {self.label}{suffix}\n"
        self._file.write(line)
        self._file.flush()

    def fail(self, reason: str = "") -> None:
        self.stop()
        detail = f": {reason}" if reason else ""
        line = f"\r[ ❌ ] {self.label}{detail}\n"
        self._file.write(line)
        self._file.flush()


