"""
download_models.py
Called by installer to download AI models into the app folder.
Uses TTS_HOME env var to force models into app\models\ instead of AppData.
"""
import sys
import os

# Force models into app folder (set by installer via TTS_HOME env var)
# If not set, use folder next to this script
_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
_MODELS_DIR = os.environ.get("TTS_HOME", os.path.join(_SCRIPT_DIR, "models"))
os.environ["TTS_HOME"] = _MODELS_DIR
os.makedirs(_MODELS_DIR, exist_ok=True)

print(f"Models directory: {_MODELS_DIR}")


def download_whisper():
    print("Downloading Whisper STT model (small, ~150MB)...")
    import whisper
    out_dir = os.path.join(_MODELS_DIR, "whisper")
    os.makedirs(out_dir, exist_ok=True)
    whisper.load_model("small", download_root=out_dir)
    print(f"Whisper saved to: {out_dir}")


def download_vctk():
    print("Downloading VCTK English voices (~100MB)...")
    from TTS.api import TTS
    TTS(model_name="tts_models/en/vctk/vits", progress_bar=True, gpu=False)
    print("VCTK done.")


def download_xtts():
    print("Downloading XTTS-v2 multilingual voices (~2GB)...")
    import torch
    import torch.serialization
    try:
        from TTS.tts.configs.xtts_config import XttsConfig
        torch.serialization.add_safe_globals([XttsConfig])
    except Exception:
        pass
    from TTS.api import TTS
    TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        progress_bar=True, gpu=False)
    print("XTTS-v2 done.")


if __name__ == "__main__":
    args = sys.argv[1:]
    do_all     = "--all"     in args
    do_whisper = "--whisper" in args or do_all
    do_vctk    = "--vctk"   in args or do_all
    do_xtts    = "--xtts"   in args or do_all

    if not any([do_whisper, do_vctk, do_xtts]):
        print("Usage: download_models.py --all | --whisper | --vctk | --xtts")
        sys.exit(1)

    errors = []

    if do_whisper:
        try:
            download_whisper()
        except Exception as e:
            print(f"Whisper error: {e}")
            errors.append(f"Whisper: {e}")

    if do_vctk:
        try:
            download_vctk()
        except Exception as e:
            print(f"VCTK error: {e}")
            errors.append(f"VCTK: {e}")

    if do_xtts:
        try:
            download_xtts()
        except Exception as e:
            print(f"XTTS error: {e}")
            errors.append(f"XTTS: {e}")

    if errors:
        print("\nErrors occurred:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    print("\nAll models downloaded successfully.")
    sys.exit(0)
