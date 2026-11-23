"""Run the local web app and worker as one supervised process group."""
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time

from dotenv import load_dotenv


def main():
    os.chdir(Path(__file__).resolve().parent)
    load_dotenv()
    missing = [name for name in ("S3_BUCKET_NAME", "SQS_QUEUE_URL") if not os.getenv(name)]
    if missing:
        sys.exit("Missing configuration: " + ", ".join(missing) + ". See .env.example.")

    host = os.getenv("PHOTO_LAB_HOST", "127.0.0.1")
    try:
        port = int(os.getenv("PHOTO_LAB_PORT", "5000"))
        with socket.create_server((host, port)):
            pass
    except (ValueError, OSError, OverflowError) as error:
        sys.exit(f"Cannot listen on {host}: {error}")

    children = []

    def stop(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        children.append(subprocess.Popen([sys.executable, "-u", "worker.py"]))
        children.append(subprocess.Popen([
            sys.executable, "-m", "flask", "--app", "app", "run",
            "--host", host, "--port", str(port), "--no-reload", "--no-debugger",
        ]))
        print(f"Photo Lab starting at http://{host}:{port} — Ctrl+C stops both services.", flush=True)
        while True:
            for child in children:
                code = child.poll()
                if code is not None:
                    print(f"Service exited (status {code}); stopping Photo Lab.", file=sys.stderr)
                    return code or 1
            time.sleep(0.2)
    except KeyboardInterrupt:
        return 0
    finally:
        # Ignore further interrupts while reaping both child processes.
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


if __name__ == "__main__":
    sys.exit(main())
