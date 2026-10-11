"""Entry point: python run.py (or, for auto crash-recovery, python supervisor.py - start.bat uses that)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import secure_store  # noqa: E402

secure_store.load_into_environ()
try:
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
except FileNotFoundError:
    pass

from app.server import create_app  # noqa: E402

if __name__ == "__main__":
    app = create_app(poll_interval=180)
    print("\nAUSTRALIA DASHBOARD running at http://127.0.0.1:8830\n")
    # waitress, not Flask's own dev server: a real production WSGI server
    # (threaded, not the single-request-at-a-time dev server Werkzeug warns
    # about), and specifically chosen because - unlike gunicorn - it runs on
    # Windows. supervisor.py is what gives you crash recovery; this process
    # exiting (for any reason) is exactly the signal it restarts on.
    from waitress import serve
    serve(app, host="127.0.0.1", port=8830, threads=4)
