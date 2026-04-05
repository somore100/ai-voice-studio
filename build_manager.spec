# ─────────────────────────────────────────────────────────────
#  Build Manager — PyInstaller spec
#  Bundles build_manager.py + both .iss files into one exe
#
#  Run with:
#    py -3.10 -m PyInstaller build_manager.spec --clean --noconfirm
# ─────────────────────────────────────────────────────────────
import os

block_cipher = None

# Bundle the .iss files and logo inside the exe as data
_datas = []
for f in ["installer_public.iss", "installer_dev.iss",
          "ai_voice_studio.spec", "hook_vosk.py",
          "requirements.txt", "LICENSE.txt", "logo.ico"]:
    if os.path.isfile(f):
        _datas.append((f, "."))

a = Analysis(
    ["build_manager.py"],
    pathex=["."],
    binaries=[],
    datas=_datas,
    hiddenimports=["tkinter", "tkinter.ttk", "tkinter.messagebox"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="BuildManager",
    debug=False,
    strip=False,
    upx=True,
    # Keep console ON for the build manager so you see pip/PyInstaller output
    console=False,
    icon="logo.ico",
    onefile=True,
)
