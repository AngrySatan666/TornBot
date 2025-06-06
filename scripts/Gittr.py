from datetime import datetime
import subprocess
import os

my_dir = os.path.dirname(os.path.abspath(__file__))

def up (x) :
    try :
        res = subprocess.run(["git", "commit", "-m", x], check=True, capture_output=True)
        print("Commit successful:", res.stdout.decode().strip())
    except subprocess.CalledProcessError as e:
        print("Error occurred:", e.stderr.decode().strip())

def New (x) :
    try:
        subprocess.run (["cd", f"C:\\.Repo\\{x}", "&&", "git", "init", "&&", "git"], check=True, capture_output=True)
        res = subprocess.run(["git", "checkout", "-b", x], check=True, capture_output=True)
        print("Branch created successfully:", res.stdout.decode().strip())
    except subprocess.CalledProcessError as e:
        print("Error occurred:", e.stderr.decode().strip())
