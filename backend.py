import json
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "settings.json")

class ConfigManager:
    DEFAULTS = {
        "game_path": "",
        "control_scheme": "keyboard_mouse",
        "resolution": "3",
        "fullscreen": True,
        "vsync": True
    }

    @staticmethod
    def load():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**ConfigManager.DEFAULTS, **json.load(f)}
            except Exception:
                pass
        return ConfigManager.DEFAULTS.copy()

    @staticmethod
    def save(data):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass

    @staticmethod
    def apply_dolphin(data):
        cfg_dir = os.path.join(BASE_DIR, "Dolphin", "User", "Config")
        os.makedirs(cfg_dir, exist_ok=True)

        gfx = (
            "[Settings]\n"
            f"InternalResolution = {data['resolution']}\n"
            f"VSync = {data['vsync']}\n"
            "AspectRatio = 1\n"
            "HiresTextures = True\n"
        )
        with open(os.path.join(cfg_dir, "GFX.ini"), "w", encoding="utf-8") as f:
            f.write(gfx)

        ini = (
            "[Display]\n"
            f"Fullscreen = {data['fullscreen']}\n"
            "RenderToMain = True\n"
        )
        with open(os.path.join(cfg_dir, "Dolphin.ini"), "w", encoding="utf-8") as f:
            f.write(ini)

        src = os.path.join(BASE_DIR, "profiles", f"{data['control_scheme']}.ini")
        dst = os.path.join(cfg_dir, "WiimoteNew.ini")
        if os.path.exists(src):
            shutil.copyfile(src, dst)
            