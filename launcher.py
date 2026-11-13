import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import sys
from backend import BASE_DIR, ConfigManager


class OmnitrixCanvas(tk.Canvas):
    def __init__(self, parent, size=72):
        super().__init__(parent, width=size, height=size, bg="#0D1117", highlightthickness=0)
        p = 6
        self.create_oval(p, p, size - p, size - p, fill="#161B22", outline="#39FF14", width=3)
        self.create_polygon(p + 12, p + 8, size - p - 12, p + 8, size // 2, size // 2, fill="#39FF14")
        self.create_polygon(p + 12, size - p - 8, size - p - 12, size - p - 8, size // 2, size // 2, fill="#39FF14")


class Ben10LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ben 10: Protector of Earth - PC Edition v2.0")
        self.root.configure(bg="#0D1117")
        if sys.platform.startswith("win"):
            self.root.geometry("760x500")
            self.root.resizable(False, False)

        self.cfg = ConfigManager.load()
        self._build_style()
        self._build_ui()
        self._sync_low_pc_state()

    def _build_style(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TNotebook", background="#0D1117", borderwidth=0)
        s.configure("TNotebook.Tab", background="#161B22", foreground="#C9D1D9", padding=, font=("Arial", 9, "bold"))
        s.map("TNotebook.Tab", background=[("selected", "#21262D")], foreground=[("selected", "#39FF14")])
        s.configure("Dark.TFrame", background="#0D1117")
        s.configure("Card.TFrame", background="#161B22")
        s.configure("Dark.TRadiobutton", background="#161B22", foreground="#FFFFFF", font=("Arial", 9))
        s.configure("Dark.TCheckbutton", background="#161B22", foreground="#FFFFFF", font=("Arial", 9))

    def _build_ui(self):
        hdr = tk.Frame(self.root, bg="#0D1117", pady=12, padx=18)
        hdr.pack(fill="x")
        OmnitrixCanvas(hdr, 68).pack(side="left", padx=(0, 14))

        tf = tk.Frame(hdr, bg="#0D1117")
        tf.pack(side="left", fill="y", pady=6)
        tk.Label(tf, text="BEN 10: PROTECTOR OF EARTH", font=("Arial", 17, "bold"), bg="#0D1117", fg="#FFFFFF").pack(anchor="w")
        tk.Label(tf, text="PC EDITION v2.0  |  60 FPS & LOW-END PC OPTIMIZED", font=("Arial", 8, "bold"), bg="#0D1117", fg="#39FF14").pack(anchor="w")

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        t1, t2, t3 = ttk.Frame(nb, style="Dark.TFrame"), ttk.Frame(nb, style="Dark.TFrame"), ttk.Frame(nb, style="Dark.TFrame")
        nb.add(t1, text="  PLAY  ")
        nb.add(t2, text="  SETTINGS  ")
        nb.add(t3, text="  CONTROLS  ")

        # Tab 1: PLAY
        c1 = ttk.Frame(t1, style="Card.TFrame", padding=18)
        c1.pack(fill="both", expand=True, pady=10)
        tk.Label(c1, text="GAME DATA DIRECTORY", font=("Arial", 9, "bold"), bg="#161B22", fg="#8B949E").pack(anchor="w")

        rf = tk.Frame(c1, bg="#0D1117", padx=10, pady=8)
        rf.pack(fill="x", pady=(6, 14))
        self.lbl_rom = tk.Label(rf, text=self._rom_txt(), font=("Arial", 9), bg="#0D1117", fg="#E6EDF3", wraplength=430, justify="left")
        self.lbl_rom.pack(side="left", fill="x", expand=True)
        tk.Button(rf, text="SELECT FILE", font=("Arial", 8, "bold"), bg="#21262D", fg="#39FF14", relief="flat", padx=10, pady=5, command=self._pick_rom).pack(side="right")

        info_text = (
            "• 60 FPS hardware patch & dual-core speed boost enabled\n"
            "• Optimized Direct3D 11 pipeline for old & modern PCs\n"
            "• Native Keyboard + Mouse & XInput Gamepad profiles"
        )
        tk.Label(c1, text=info_text, font=("Arial", 9), bg="#161B22", fg="#8B949E", justify="left").pack(anchor="w", pady=(0, 14))

        self.btn_play = tk.Button(c1, text="▶  PLAY GAME", font=("Arial", 13, "bold"), bg="#39FF14", fg="#0D1117", relief="flat", pady=12, command=self._play)
        self.btn_play.pack(side="bottom", fill="x")

        # Tab 2: SETTINGS
        c2 = ttk.Frame(t2, style="Card.TFrame", padding=18)
        c2.pack(fill="both", expand=True, pady=10)

        tk.Label(c2, text="INPUT PROFILE", font=("Arial", 9, "bold"), bg="#161B22", fg="#39FF14").pack(anchor="w")
        self.v_ctrl = tk.StringVar(value=self.cfg["control_scheme"])
        for txt, val in [("Keyboard + Mouse (WASD + Click Attacks)", "keyboard_mouse"), ("Xbox / PlayStation Controller (XInput)", "gamepad")]:
            ttk.Radiobutton(c2, text=txt, variable=self.v_ctrl, value=val, style="Dark.TRadiobutton", command=self._save_opts).pack(anchor="w", pady=1)

        tk.Label(c2, text="RENDER RESOLUTION", font=("Arial", 9, "bold"), bg="#161B22", fg="#39FF14").pack(anchor="w", pady=(10, 2))
        self.v_res = tk.StringVar(value=str(self.cfg["resolution"]))
        rf2 = tk.Frame(c2, bg="#161B22")
        rf2.pack(anchor="w")
        self.res_btns = []
        for txt, val in [("480p (Native)", "1"), ("720p (HD)", "2"), ("1080p (FullHD)", "3"), ("4K (Ultra)", "6")]:
            rb = ttk.Radiobutton(rf2, text=txt, variable=self.v_res, value=val, style="Dark.TRadiobutton", command=self._save_opts)
            rb.pack(side="left", padx=(0, 12))
            self.res_btns.append(rb)

        tk.Label(c2, text="PERFORMANCE & DISPLAY", font=("Arial", 9, "bold"), bg="#161B22", fg="#39FF14").pack(anchor="w", pady=(10, 2))
        self.v_fps60 = tk.BooleanVar(value=self.cfg.get("fps_60", True))
        self.v_lowpc = tk.BooleanVar(value=self.cfg.get("low_end_pc", False))
        self.v_fs = tk.BooleanVar(value=self.cfg.get("fullscreen", True))
        self.v_vs = tk.BooleanVar(value=self.cfg.get("vsync", False))

        ttk.Checkbutton(c2, text="Unlock 60 FPS Mode (Recommended)", variable=self.v_fps60, style="Dark.TCheckbutton", command=self._save_opts).pack(anchor="w", pady=1)
        ttk.Checkbutton(c2, text="Low-End / Old PC Mode (Forces 480p & Fast Hacks)", variable=self.v_lowpc, style="Dark.TCheckbutton", command=self._on_low_pc_toggle).pack(anchor="w", pady=1)
        ttk.Checkbutton(c2, text="Fullscreen Mode (16:9 Widescreen)", variable=self.v_fs, style="Dark.TCheckbutton", command=self._save_opts).pack(anchor="w", pady=1)
        ttk.Checkbutton(c2, text="Enable VSync (Turn off if FPS drops below 60)", variable=self.v_vs, style="Dark.TCheckbutton", command=self._save_opts).pack(anchor="w", pady=1)

        # Tab 3: CONTROLS
        c3 = ttk.Frame(t3, style="Card.TFrame", padding=18)
        c3.pack(fill="both", expand=True, pady=10)
        keys = [
            ("W A S D", "Move Character"),
            ("SPACEBAR", "Jump / Double Jump"),
            ("LEFT CLICK", "Light Attack"),
            ("RIGHT CLICK", "Heavy Attack"),
            ("LEFT SHIFT", "Block / Grab / Interact"),
            ("1 / 2 / 3 / 4", "Alien Transformations"),
            ("Q / E", "Camera / Cycle Forms"),
            ("ESC / TAB", "Pause / Upgrades Menu")
        ]
        for k, desc in keys:
            row = tk.Frame(c3, bg="#161B22")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=k, font=("Consolas", 9, "bold"), bg="#0D1117", fg="#39FF14", width=16).pack(side="left", padx=(0, 10))
            tk.Label(row, text=desc, font=("Arial", 9), bg="#161B22", fg="#C9D1D9").pack(side="left")

    def _sync_low_pc_state(self):
        is_low = self.v_lowpc.get()
        state = "disabled" if is_low else "normal"
        for rb in self.res_btns:
            rb.configure(state=state)
        if is_low:
            self.v_res.set("1")

    def _on_low_pc_toggle(self):
        self._sync_low_pc_state()
        self._save_opts()

    def _rom_txt(self):
        p = self.cfg.get("game_path", "")
        return f"Loaded: {os.path.basename(p)}" if p and os.path.exists(p) else "No game data selected"

    def _pick_rom(self):
        p = filedialog.askopenfilename(filetypes=[("Game Data", "*.rvz *.iso *.wbfs"), ("All", "*.*")])
        if p:
            self.cfg["game_path"] = p
            ConfigManager.save(self.cfg)
            self.lbl_rom.config(text=self._rom_txt())

    def _save_opts(self):
        self.cfg.update({
            "control_scheme": self.v_ctrl.get(),
            "resolution": self.v_res.get(),
            "fullscreen": self.v_fs.get(),
            "vsync": self.v_vs.get(),
            "fps_60": self.v_fps60.get(),
            "low_end_pc": self.v_lowpc.get()
        })
        ConfigManager.save(self.cfg)

    def _play(self):
        gp = self.cfg.get("game_path", "")
        if not gp or not os.path.exists(gp):
            messagebox.showwarning("Missing Game Data", "Please select your game image file (.rvz / .iso) first!")
            return

        self.btn_play.configure(state="disabled", text="LAUNCHING...")
        self.root.update_idletasks()

        try:
            ConfigManager.apply_dolphin(self.cfg)
            exe = os.path.join(BASE_DIR, "Engine", "Ben10Game.exe")
            if not sys.platform.startswith("win"):
                messagebox.showinfo("Test OK", f"v2.0 Config written!\n60 FPS: {self.cfg['fps_60']}\nLow-End PC: {self.cfg['low_end_pc']}")
                self.btn_play.configure(state="normal", text="▶  PLAY GAME")
                return
            if not os.path.exists(exe):
                messagebox.showerror("Engine Missing", "Core game files not found inside 'Engine' folder.")
                self.btn_play.configure(state="normal", text="▶  PLAY GAME")
                return
            subprocess.Popen([exe, "-b", "-e", gp])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to start game:\n{e}")
            self.btn_play.configure(state="normal", text="▶  PLAY GAME")


if __name__ == "__main__":
    root = tk.Tk()
    Ben10LauncherApp(root)
    root.mainloop()
    
