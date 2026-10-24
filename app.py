import tkinter as tk
import requests
import subprocess
import sys
import os
from threading import Thread

# ── bump this AND version.txt on github every update ──
LOCAL_VERSION = "1.1"

RAW_BASE    = "https://raw.githubusercontent.com/ImH0boAlt/test/main"
VERSION_URL = f"{RAW_BASE}/version.txt"
SCRIPT_URL  = f"{RAW_BASE}/app.py"
SCRIPT_PATH = os.path.abspath(__file__)

BG     = "#1a1a2e"
BG2    = "#16213e"
FG     = "#e0e0e0"
FG_DIM = "#888899"
GREEN  = "#4ade80"
YELLOW = "#facc15"
ACCENT = "#7c6ef5"


def check_and_update(status_label):
    try:
        r = requests.get(VERSION_URL, timeout=6)
        r.raise_for_status()
        remote = r.text.strip()

        if float(remote) <= float(LOCAL_VERSION):
            status_label.after(0, lambda: status_label.config(
                text="✓  up to date", fg=GREEN
            ))
            return

        # newer version found — tell the user
        status_label.after(0, lambda: status_label.config(
            text=f"updating to v{remote}...", fg=YELLOW
        ))

        # download new app.py
        new_script = requests.get(SCRIPT_URL, timeout=15)
        new_script.raise_for_status()

        new_path = SCRIPT_PATH + ".new"
        with open(new_path, "wb") as f:
            f.write(new_script.content)

        # bat waits for us to die, swaps the file, relaunches
        bat_path = os.path.join(os.path.dirname(SCRIPT_PATH), "_updater.bat")
        with open(bat_path, "w") as f:
            f.write(f"""@echo off
timeout /t 2 /nobreak > nul
move /y "{new_path}" "{SCRIPT_PATH}"
python "{SCRIPT_PATH}"
del "%~f0"
""")

        subprocess.Popen(
            ["cmd", "/c", bat_path],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            close_fds=True,
        )

        sys.exit(0)

    except Exception as e:
        status_label.after(0, lambda: status_label.config(
            text=f"update check failed: {e}", fg="#f87171"
        ))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"my app  —  v{LOCAL_VERSION}")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.geometry("360x220")
        self._build()
        Thread(target=check_and_update, args=(self.status,), daemon=True).start()

    def _build(self):
        tk.Frame(self, bg=BG2, pady=20).pack(fill="x")

        tk.Label(
            self, text="hello bitch.",
            bg=BG, fg=FG,
            font=("Segoe UI", 32, "bold"),
        ).pack(pady=24)

        self.status = tk.Label(
            self, text="checking for updates...",
            bg=BG, fg=FG_DIM,
            font=("Segoe UI", 9),
        )
        self.status.pack()

        tk.Label(
            self, text=f"v{LOCAL_VERSION}",
            bg=BG, fg=FG_DIM,
            font=("Segoe UI", 8),
        ).pack(side="bottom", pady=8)


if __name__ == "__main__":
    app = App()
    app.mainloop()
