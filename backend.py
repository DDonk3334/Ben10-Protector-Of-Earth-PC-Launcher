import json
import os
import shutil
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "settings.json")


class ConfigManager:
    DEFAULTS = {
        "game_path": "",
        "control_scheme": "keyboard_mouse",
        "resolution": "2",
        "fullscreen": True,
        "vsync": False,
        "fps_60": True,
        "low_end_pc": False
    }

    @staticmethod
    def load():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return {**ConfigManager.DEFAULTS, **data}
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
        user_dir = os.path.join(BASE_DIR, "Engine", "User")
        cfg_dir = os.path.join(user_dir, "Config")
        gs_dir = os.path.join(user_dir, "GameSettings")
        os.makedirs(cfg_dir, exist_ok=True)
        os.makedirs(gs_dir, exist_ok=True)

        low_pc = bool(data.get("low_end_pc", False))
        fps_60 = bool(data.get("fps_60", True))
        res = "1" if low_pc else str(data.get("resolution", "2"))

        # 1. Graphics & Low-End PC Optimization
        gfx = (
            "[Settings]\n"
            f"InternalResolution = {res}\n"
            f"VSync = {bool(data.get('vsync', False))}\n"
            "AspectRatio = 1\n"
            f"HiresTextures = {not low_pc}\n"
            "ShowFPS = False\n"
            "FastDepthCalc = True\n"
            "ShaderCompilationMode = 3\n"
            "CompileShadersBeforeStarting = True\n"
            "MSAA = 1\n"
            "MaxAnisotropy = 0\n"
            "[Hacks]\n"
            "EFBAccessEnable = False\n"
            "BBoxEnable = False\n"
            "ForceProgressive = True\n"
            "EFBToTextureEnable = True\n"
            "EFBScaledCopy = True\n"
            "DeferEFBCopies = True\n"
            "[Hardware]\n"
            "GFXBackend = D3D\n"
        )
        with open(os.path.join(cfg_dir, "GFX.ini"), "w", encoding="utf-8") as f:
            f.write(gfx)

        # 2. Core Speed, Dual-Core & Clean PC Wrapper Interface
        oc_rate = "1.55" if fps_60 else "1.0"
        ini = (
            "[Core]\n"
            "CPUThread = True\n"
            "Fastmem = True\n"
            "EnableCheats = True\n"
            f"Overclock = {oc_rate}\n"
            f"OverclockEnable = {fps_60}\n"
            "SyncOnSkipIdle = True\n"
            "[Display]\n"
            f"Fullscreen = {bool(data.get('fullscreen', True))}\n"
            "RenderToMain = True\n"
            "[Interface]\n"
            "ConfirmStop = False\n"
            "HideCursor = True\n"
            "UsePanicHandlers = False\n"
            "OnScreenDisplayMessages = False\n"
        )
        with open(os.path.join(cfg_dir, "Dolphin.ini"), "w", encoding="utf-8") as f:
            f.write(ini)

        # 3. 60 FPS Gecko Patch for USA (RB7E4F) and PAL (RB7P4F)
        if fps_60:
            game_ini = (
                "[Core]\n"
                "Overclock = 1.55\n"
                "OverclockEnable = True\n"
                "[Gecko]\n"
                "$60 FPS Unlock\n"
                "04215620 60000000\n"
                "04215624 38600001\n"
                "[Gecko_Enabled]\n"
                "$60 FPS Unlock\n"
            )
        else:
            game_ini = (
                "[Core]\n"
                "Overclock = 1.0\n"
                "OverclockEnable = False\n"
            )

        for game_id in ("RB7E4F", "RB7P4F"):
            with open(os.path.join(gs_dir, f"{game_id}.ini"), "w", encoding="utf-8") as f:
                f.write(game_ini)

        # 4. Controls Profile Injection
        scheme = data.get("control_scheme", "keyboard_mouse")
        src = os.path.join(BASE_DIR, "profiles", f"{scheme}.ini")
        dst = os.path.join(cfg_dir, "WiimoteNew.ini")
        if os.path.exists(src):
            shutil.copyfile(src, dst)
            
