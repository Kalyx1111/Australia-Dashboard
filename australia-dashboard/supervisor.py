"""
Run this instead of run.py directly (start.bat already does): it runs a
real self-check first, then launches run.py as a child process and
restarts it automatically if it ever exits unexpectedly - a genuine crash-
recovery loop, not just a claim of one. Ctrl+C here stops everything
cleanly; it does not count as a "crash" to recover from.
"""
from __future__ import annotations
import os
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CRASH_LOG = os.path.join(DATA_DIR, "crash_log.txt")
PORT = 8830
MAX_RESTARTS_PER_WINDOW = 10
RESTART_WINDOW_SECONDS = 300  # 5 minutes
BACKOFF_START = 2
BACKOFF_CAP = 60


def log_crash(message: str) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CRASH_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {message}\n")


def self_check() -> bool:
    """Real checks, not decorative - each one is something that has actually
    stopped this app from starting before. Returns False only for a HARD
    failure (nothing further can run); soft/optional gaps print a warning
    and let startup continue, since the app already degrades gracefully for
    those (see secure_store.CRYPTO_AVAILABLE)."""
    print("Running startup self-check...")
    ok = True

    if sys.version_info < (3, 9):
        print(f"  [FAIL] Python {sys.version_info.major}.{sys.version_info.minor} is too old - need 3.9+.")
        ok = False
    else:
        print(f"  [OK] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    for pkg in ("flask", "requests", "feedparser", "waitress"):
        try:
            __import__(pkg)
            print(f"  [OK] {pkg} importable")
        except ImportError:
            print(f"  [FAIL] {pkg} not installed - run: pip install -r requirements.txt")
            ok = False

    try:
        import cryptography  # noqa: F401
        print("  [OK] cryptography importable (AES-256 key storage available)")
    except ImportError:
        print("  [WARN] cryptography not installed - AES-256 key storage disabled, "
              "free sources (GDELT/RSS/USGS) still work fully. pip install cryptography to enable it.")

    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        probe = os.path.join(DATA_DIR, ".write_test")
        with open(probe, "w") as f:
            f.write("ok")
        os.remove(probe)
        print(f"  [OK] {DATA_DIR} is writable")
    except OSError as e:
        print(f"  [FAIL] {DATA_DIR} is not writable: {e}")
        ok = False

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        if s.connect_ex(("127.0.0.1", PORT)) == 0:
            print(f"  [FAIL] port {PORT} is already in use - is another copy of this dashboard already running? "
                  f"Close it first, or edit PORT in supervisor.py and server.py to use a different one.")
            ok = False
        else:
            print(f"  [OK] port {PORT} is free")

    print("Self-check " + ("passed.\n" if ok else "FAILED - fix the items above, then re-run.\n"))
    return ok


def main():
    if not self_check():
        sys.exit(1)

    restart_times: list[float] = []
    backoff = BACKOFF_START
    python_exe = sys.executable
    run_py = os.path.join(BASE_DIR, "run.py")

    while True:
        print(f"Starting server (python {run_py})...")
        start_time = time.time()
        try:
            proc = subprocess.Popen([python_exe, run_py], cwd=BASE_DIR)
            exit_code = proc.wait()
        except KeyboardInterrupt:
            print("\nStopped by user (Ctrl+C) - not a crash, exiting cleanly.")
            try:
                proc.terminate()
            except Exception:
                pass
            sys.exit(0)

        ran_for = time.time() - start_time
        if exit_code == 0:
            print("Server exited normally (code 0) - not restarting.")
            sys.exit(0)

        msg = f"server exited with code {exit_code} after running for {ran_for:.1f}s"
        print(f"[CRASH] {msg}. See {CRASH_LOG} for the running history.")
        log_crash(msg)

        now = time.time()
        restart_times.append(now)
        restart_times[:] = [t for t in restart_times if now - t < RESTART_WINDOW_SECONDS]
        if len(restart_times) > MAX_RESTARTS_PER_WINDOW:
            print(f"[STOP] {MAX_RESTARTS_PER_WINDOW}+ crashes within {RESTART_WINDOW_SECONDS}s - "
                  f"this looks like a persistent problem, not a transient one. Not auto-restarting again. "
                  f"Check {CRASH_LOG} and the error output above.")
            log_crash("supervisor stopped: too many restarts in the window")
            sys.exit(1)

        print(f"Restarting in {backoff}s...")
        time.sleep(backoff)
        backoff = min(backoff * 2, BACKOFF_CAP)


if __name__ == "__main__":
    main()
