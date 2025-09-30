Version = [0,0,1]
State = "SCR"

import subprocess
import time, os
from datetime import datetime
import argparse

_dir = os.path.dirname(os.path.abspath(__file__))
POINTS_SCRIPT = os.path.join(_dir, "points.py")

def run_script():
    """Runs points.py as a separate process."""
    try:
        subprocess.run(["python", POINTS_SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to execute {POINTS_SCRIPT}: {e}")

def PerMin():
    """Runs points2.py once per minute."""
    last_run_minute = None
    while True:
        now = datetime.now()
        current_minute = now.minute
        if current_minute != last_run_minute:
            run_script()
            last_run_minute = current_minute
        time.sleep(1)

def PerSec(x):
    """Runs points2.py once per second."""
    while True:
        run_script()
        time.sleep(x)

if __name__ == "__main__":
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Running {POINTS_SCRIPT}...")
    parser = argparse.ArgumentParser(description="Script scheduler for points2.py")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--Perm", action="store_true", help="Run once per minute")
    group.add_argument("--sec", "--s", type=int, dest="seconds", help="Run every N seconds")

    args = parser.parse_args()

    print("[INFO] Starting script scheduler...")

    if args.Perm:
        PerMin()
    elif args.seconds:
        PerSec(args.seconds)
    else:
        print("[INFO] No arguments provided. Defaulting to PerSec(10).")
        PerSec(10)
