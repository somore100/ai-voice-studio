# hook_vosk.py — PyInstaller runtime hook for Vosk
# Vosk's __init__.py calls os.add_dll_directory() on its own folder.
# Inside a PyInstaller bundle the folder is in _internal\vosk\
# This hook patches the path before vosk loads so it finds its DLLs.
import os
import sys

# When frozen, sys._MEIPASS points to the _internal\ folder
if hasattr(sys, '_MEIPASS'):
    vosk_path = os.path.join(sys._MEIPASS, 'vosk')
    if os.path.isdir(vosk_path):
        os.add_dll_directory(vosk_path)
