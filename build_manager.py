"""
AI Voice Studio — Build Manager
================================
Run this script to build the exe and compile the installers.
This script can also be bundled into its own exe using:
    py -3.10 -m PyInstaller --onefile --noconsole --name=BuildManager build_manager.py

What it does:
  1. Checks Python 3.10 and required tools
  2. Installs PyInstaller if missing
  3. Detects / downloads Inno Setup if missing
  4. Builds AI_Voice_Studio.exe via PyInstaller
  5. Compiles both .iss installers
  6. Shows you the final output files
"""

import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import tempfile
import webbrowser

# ── Colours (matching main app theme) ────────────────────────
BG      = "#1a1b2e"
CARD    = "#1e1f33"
SURFACE = "#2a2b45"
BORDER  = "#3a3b5c"
BLUE    = "#7aa2f7"
GREEN   = "#9ece6a"
RED     = "#f7768e"
YELLOW  = "#e0af68"
PURPLE  = "#bb9af7"
FG      = "#c0caf5"
FG_DIM  = "#565f89"

# ── Paths ─────────────────────────────────────────────────────
BASE        = os.path.dirname(os.path.realpath(__file__))
SPEC_FILE   = os.path.join(BASE, "ai_voice_studio.spec")
ISS_PUBLIC  = os.path.join(BASE, "installer_public.iss")
ISS_DEV     = os.path.join(BASE, "installer_dev.iss")
DIST_DIR    = os.path.join(BASE, "dist", "AI_Voice_Studio")
OUT_PUBLIC  = os.path.join(BASE, "setup_output", "AI_Voice_Studio_Setup_v1.0.exe")
OUT_DEV     = os.path.join(BASE, "dev_setup",    "AI_Voice_Studio_Dev_Setup.exe")

ISCC_PATHS  = [
    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    r"C:\Program Files\Inno Setup 6\ISCC.exe",
]
INNO_URL    = "https://jrsoftware.org/download.php/is.exe"
INNO_DL_PAGE = "https://jrsoftware.org/isdl.php"

# ─────────────────────────────────────────────────────────────
class BuildManager(tk.Tk):
# ─────────────────────────────────────────────────────────────
    def __init__(self):
        super().__init__()
        self.title("AI Voice Studio — Build Manager")
        self.geometry("680x620")
        self.configure(bg=BG)
        self.resizable(False, False)

        self._console_mode = tk.BooleanVar(value=False)
        self._building     = False

        style = ttk.Style(); style.theme_use("clam")
        style.configure("TProgressbar",
                        troughcolor=SURFACE, background=BLUE,
                        bordercolor=SURFACE, lightcolor=BLUE,
                        darkcolor=BLUE, relief="flat")

        self._build_ui()
        self._check_tools()

    # ── UI ────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=PURPLE, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="AI Voice Studio — Build Manager",
                 bg=PURPLE, fg=BG,
                 font=("Segoe UI", 14, "bold")).pack()
        tk.Label(hdr, text="by domore100",
                 bg=PURPLE, fg=BG,
                 font=("Segoe UI", 9)).pack()

        # Tool status section
        sf = tk.LabelFrame(self, text="  Environment Check  ",
                           bg=CARD, fg=PURPLE,
                           font=("Segoe UI", 9, "bold"),
                           bd=2, relief="groove", padx=10, pady=8)
        sf.pack(fill="x", padx=14, pady=(14,6))

        self._py_lbl    = self._status_row(sf, "Python 3.10")
        self._pi_lbl    = self._status_row(sf, "PyInstaller")
        self._inno_lbl  = self._status_row(sf, "Inno Setup 6")
        self._spec_lbl  = self._status_row(sf, "Spec file  (ai_voice_studio.spec)")
        self._iss_lbl   = self._status_row(sf, "Installer scripts  (.iss files)")

        # Build options
        of = tk.LabelFrame(self, text="  Build Options  ",
                           bg=CARD, fg=PURPLE,
                           font=("Segoe UI", 9, "bold"),
                           bd=2, relief="groove", padx=10, pady=8)
        of.pack(fill="x", padx=14, pady=6)

        tk.Checkbutton(of,
                       text="Show console window in built exe  (useful for debugging errors)",
                       variable=self._console_mode,
                       bg=CARD, fg=FG, selectcolor=SURFACE,
                       activebackground=CARD, activeforeground=FG,
                       font=("Segoe UI", 9)).pack(anchor="w")

        # Log
        lf = tk.LabelFrame(self, text="  Build Log  ",
                           bg=CARD, fg=PURPLE,
                           font=("Segoe UI", 9, "bold"),
                           bd=2, relief="groove", padx=6, pady=6)
        lf.pack(fill="both", expand=True, padx=14, pady=6)

        self._log = tk.Text(lf, bg=SURFACE, fg=FG,
                            insertbackground=BLUE, relief="flat",
                            font=("Consolas", 8), wrap="word",
                            height=12, state="disabled")
        sb = ttk.Scrollbar(lf, orient="vertical", command=self._log.yview)
        self._log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._log.pack(fill="both", expand=True)

        # Progress bar
        self._progress = ttk.Progressbar(self, mode="indeterminate", length=640)
        self._progress.pack(padx=14, pady=(0,6))

        # Buttons
        br = tk.Frame(self, bg=BG); br.pack(pady=8)

        self._build_btn = tk.Button(br,
            text="▶  Build Everything",
            command=self._start_build,
            bg=GREEN, fg=BG, relief="flat", cursor="hand2",
            padx=20, pady=8, font=("Segoe UI", 10, "bold"), bd=0)
        self._build_btn.pack(side="left", padx=6)

        tk.Button(br,
            text="📁  Open Output Folder",
            command=self._open_output,
            bg=SURFACE, fg=FG, relief="flat", cursor="hand2",
            padx=12, pady=8, font=("Segoe UI", 9), bd=0
            ).pack(side="left", padx=6)

        tk.Button(br,
            text="↺  Re-check",
            command=self._check_tools,
            bg=SURFACE, fg=FG, relief="flat", cursor="hand2",
            padx=12, pady=8, font=("Segoe UI", 9), bd=0
            ).pack(side="left", padx=6)

    def _status_row(self, parent, label):
        row = tk.Frame(parent, bg=CARD); row.pack(fill="x", pady=2)
        tk.Label(row, text=label, bg=CARD, fg=FG,
                 font=("Segoe UI", 9), width=38, anchor="w").pack(side="left")
        lbl = tk.Label(row, text="checking…", bg=CARD, fg=YELLOW,
                       font=("Segoe UI", 9, "bold"))
        lbl.pack(side="left")
        return lbl

    def _set_status(self, lbl, ok, text=None):
        if ok:
            lbl.config(text=text or "✅  OK", fg=GREEN)
        else:
            lbl.config(text=text or "❌  Not found", fg=RED)

    # ── Tool checks ───────────────────────────────────────────
    def _check_tools(self):
        threading.Thread(target=self._do_check, daemon=True).start()

    def _do_check(self):
        # Python 3.10
        try:
            r = subprocess.run(["py", "-3.10", "--version"],
                               capture_output=True, text=True)
            ok = r.returncode == 0
            ver = r.stdout.strip() or r.stderr.strip()
            self.after(0, lambda: self._set_status(
                self._py_lbl, ok, f"✅  {ver}" if ok else "❌  Not found"))
        except Exception:
            self.after(0, lambda: self._set_status(self._py_lbl, False))

        # PyInstaller
        try:
            r = subprocess.run(["py", "-3.10", "-m", "PyInstaller", "--version"],
                               capture_output=True, text=True)
            ok = r.returncode == 0
            ver = r.stdout.strip()
            self.after(0, lambda: self._set_status(
                self._pi_lbl, ok, f"✅  v{ver}" if ok else "⚠️  Will install automatically"))
        except Exception:
            self.after(0, lambda: self._set_status(
                self._pi_lbl, False, "⚠️  Will install automatically"))

        # Inno Setup
        iscc = self._find_iscc()
        self.after(0, lambda: self._set_status(
            self._inno_lbl,
            iscc is not None,
            f"✅  Found" if iscc else "❌  Not found — click Build to get install link"))

        # Spec file
        ok = os.path.isfile(SPEC_FILE)
        self.after(0, lambda: self._set_status(self._spec_lbl, ok))

        # ISS files
        ok = os.path.isfile(ISS_PUBLIC) and os.path.isfile(ISS_DEV)
        self.after(0, lambda: self._set_status(
            self._iss_lbl, ok,
            "✅  Both found" if ok else "❌  Missing — place .iss files next to this script"))

    def _find_iscc(self):
        for p in ISCC_PATHS:
            if os.path.isfile(p):
                return p
        return None

    # ── Logging ───────────────────────────────────────────────
    def _log_write(self, text, color=FG):
        self._log.config(state="normal")
        self._log.insert(tk.END, text + "\n")
        self._log.see(tk.END)
        self._log.config(state="disabled")

    def _log_clear(self):
        self._log.config(state="normal")
        self._log.delete("1.0", tk.END)
        self._log.config(state="disabled")

    # ── Build ─────────────────────────────────────────────────
    def _start_build(self):
        if self._building:
            return
        self._building = True
        self._build_btn.config(state="disabled", text="Building…")
        self._log_clear()
        self._progress.start(12)
        threading.Thread(target=self._do_build, daemon=True).start()

    def _do_build(self):
        try:
            self._run_build()
        except Exception as e:
            self.after(0, lambda: self._log_write(f"\n❌  FAILED: {e}", RED))
        finally:
            self.after(0, self._build_done)

    def _run_build(self):
        log = lambda t: self.after(0, lambda msg=t: self._log_write(msg))

        # ── Step 1: Install PyInstaller ───────────────────────
        log("─── Step 1: PyInstaller ───────────────────────────")
        log("Installing / verifying PyInstaller...")
        r = subprocess.run(
            ["py", "-3.10", "-m", "pip", "install", "pyinstaller"],
            capture_output=True, text=True, cwd=BASE)
        log(r.stdout.strip() or "OK")

        # ── Step 2: Build exe ─────────────────────────────────
        log("\n─── Step 2: Building EXE ──────────────────────────")
        log("Running PyInstaller — this takes 3-5 minutes...")

        env = os.environ.copy()
        env["AVS_CONSOLE"] = "1" if self._console_mode.get() else "0"

        r = subprocess.run(
            ["py", "-3.10", "-m", "PyInstaller",
             "ai_voice_studio.spec", "--clean", "--noconfirm"],
            capture_output=True, text=True, cwd=BASE, env=env)

        if r.returncode != 0:
            raise RuntimeError(
                "PyInstaller failed:\n" + r.stderr[-1500:])

        log("✅  EXE built: dist\\AI_Voice_Studio\\AI_Voice_Studio.exe")

        # ── Step 3: Compile installers ────────────────────────
        log("\n─── Step 3: Compiling Installers ──────────────────")
        iscc = self._find_iscc()

        if iscc is None:
            log("⚠️  Inno Setup not found!")
            log("    Download from: https://jrsoftware.org/isdl.php")
            log("    Install it, then click Re-check and Build again.")
            self.after(0, lambda: webbrowser.open(INNO_DL_PAGE))
            return

        # Compile dev installer first (public installer bundles it)
        if os.path.isfile(ISS_DEV):
            log("Compiling dev installer...")
            os.makedirs(os.path.join(BASE, "dev_setup"), exist_ok=True)
            r = subprocess.run([iscc, ISS_DEV],
                               capture_output=True, text=True, cwd=BASE)
            if r.returncode == 0:
                log("✅  Dev installer: dev_setup\\AI_Voice_Studio_Dev_Setup.exe")
            else:
                log(f"⚠️  Dev installer failed:\n{r.stderr[-800:]}")

        # Compile public installer
        if os.path.isfile(ISS_PUBLIC):
            log("Compiling public installer...")
            os.makedirs(os.path.join(BASE, "setup_output"), exist_ok=True)
            r = subprocess.run([iscc, ISS_PUBLIC],
                               capture_output=True, text=True, cwd=BASE)
            if r.returncode != 0:
                raise RuntimeError(
                    "Inno Setup failed:\n" + r.stderr[-1500:])
            log("✅  Public installer: setup_output\\AI_Voice_Studio_Setup_v1.0.exe")
        else:
            log("⚠️  installer_public.iss not found — skipping")

        log("\n══════════════════════════════════════════════")
        log("  ALL DONE!")
        log("  Release file:")
        log("  setup_output\\AI_Voice_Studio_Setup_v1.0.exe")
        log("══════════════════════════════════════════════")

    def _build_done(self):
        self._progress.stop()
        self._progress["value"] = 0
        self._building = False
        self._build_btn.config(state="normal", text="▶  Build Everything")
        self._check_tools()

    def _open_output(self):
        folder = os.path.join(BASE, "setup_output")
        os.makedirs(folder, exist_ok=True)
        os.startfile(folder)


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = BuildManager()
    app.mainloop()
