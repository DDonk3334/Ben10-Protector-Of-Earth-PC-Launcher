import tkinter as tk
from tkinter import filedialog, messagebox
import os, subprocess, sys
from backend import BASE_DIR, ConfigManager

C = {
    "bg": "#0B0E11", "side": "#13181E", "card": "#1A212B",
    "acc": "#39FF14", "txt": "#FFFFFF", "dim": "#8A99AD"
}

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ben 10: Protector of Earth - PC Edition")
        self.root.configure(bg=C["bg"])
        if sys.platform.startswith("win"):
            self.root.geometry("720x450")
            self.root.resizable(False, False)

        self.cfg = ConfigManager.load()
        self.btns, self.tabs = {}, {}

        self.side = tk.Frame(root, bg=C["side"], width=180)
        self.side.pack(side="left", fill="y")
        self.side.pack_propagate(False)

        self.main = tk.Frame(root, bg=C["bg"])
        self.main.pack(side="right", fill="both", expand=True, padx=16, pady=14)

        self._init_sidebar()
        self._init_tabs()
        self.show_tab("play")

    def _init_sidebar(self):
        cv = tk.Canvas(self.side, width=60, height=60, bg=C["side"], highlightthickness=0)
        cv.pack(pady=(16, 6))
        cv.create_oval(5, 5, 55, 55, outline=C["acc"], width=3, fill="#0D1115")
        cv.create_polygon(16, 14, 44, 14, 30, 30, fill=C["acc"])
        cv.create_polygon(16, 46, 44, 46, 30, 30, fill=C["acc"])

        tk.Label(self.side, text="BEN 10: POE", font=("Arial", 12, "bold"), bg=C["side"], fg=C["txt"]).pack()
        tk.Label(self.side, text="PC EDITION v1.0", font=("Arial", 8, "bold"), bg=C["side"], fg=C["acc"]).pack(pady=(0, 16))

        menu = [("play", "[>] Home"), ("opts", "[*] Settings"), ("keys", "[+] Controls"), ("info", "[i] About")]
        for tid, label in menu:
            b = tk.Button(
                self.side, text=label, anchor="w", font=("Arial", 9, "bold"),
                bg=C["side"], fg=C["dim"], relief="flat", padx=14, pady=9,
                command=lambda t=tid: self.show_tab(t)
            )
            b.pack(fill="x", pady=2)
            self.btns[tid] = b

    def _init_tabs(self):
        # TAB 1: HOME
        p1 = tk.Frame(self.main, bg=C["bg"])
        tk.Label(p1, text="PROTECTOR OF EARTH - LAUNCHER", font=("Arial", 12, "bold"), bg=C["bg"], fg=C["txt"]).pack(anchor="w")
        
        c1 = tk.Frame(p1, bg=C["card"], padx=12, pady=12)
        c1.pack(fill="x", pady=12)
        self.lbl_rom = tk.Label(c1, text=self._rom_txt(), font=("Arial", 9), bg=C["card"], fg=C["txt"], wraplength=380, justify="left")
        self.lbl_rom.pack(anchor="w", pady=(0, 8))
        tk.Button(c1, text="Select Game (.rvz / .iso)", font=("Arial", 9, "bold"), bg="#283240", fg=C["txt"], relief="flat", padx=10, pady=5, command=self._pick_rom).pack(anchor="w")

        self.lbl_sum = tk.Label(p1, text=self._sum_txt(), font=("Arial", 8), bg=C["bg"], fg=C["dim"])
        self.lbl_sum.pack(anchor="w", pady=4)

        tk.Button(p1, text="PLAY GAME", font=("Arial", 12, "bold"), bg=C["acc"], fg="#000000", relief="flat", pady=12, command=self._play).pack(side="bottom", fill="x")
        self.tabs["play"] = p1

        # TAB 2: SETTINGS
        p2 = tk.Frame(self.main, bg=C["bg"])
        tk.Label(p2, text="GRAPHICS & INPUT", font=("Arial", 12, "bold"), bg=C["bg"], fg=C["txt"]).pack(anchor="w", pady=(0, 8))
        
        self.v_ctrl = tk.StringVar(value=self.cfg["control_scheme"])
        for t, v in [("Keyboard + Mouse", "keyboard_mouse"), ("Gamepad (XInput)", "gamepad")]:
            tk.Radiobutton(p2, text=t, variable=self.v_ctrl, value=v, bg=C["bg"], fg=C["txt"], selectcolor=C["card"], command=self._save_opts).pack(anchor="w")

        tk.Label(p2, text="Resolution:", font=("Arial", 9, "bold"), bg=C["bg"], fg=C["acc"]).pack(anchor="w", pady=(10, 2))
        self.v_res = tk.StringVar(value=self.cfg["resolution"])
        for t, v in [("480p Native", "1"), ("720p HD", "2"), ("1080p Full HD", "3"), ("4K UHD", "6")]:
            tk.Radiobutton(p2, text=t, variable=self.v_res, value=v, bg=C["bg"], fg=C["txt"], selectcolor=C["card"], command=self._save_opts).pack(anchor="w")

        self.v_fs = tk.BooleanVar(value=self.cfg["fullscreen"])
        tk.Checkbutton(p2, text="Fullscreen Mode", variable=self.v_fs, bg=C["bg"], fg=C["txt"], selectcolor=C["card"], command=self._save_opts).pack(anchor="w", pady=(10, 0))
        self.tabs["opts"] = p2

        # TAB 3: CONTROLS
        p3 = tk.Frame(self.main, bg=C["bg"])
        tk.Label(p3, text="PC KEYBINDINGS", font=("Arial", 12, "bold"), bg=C["bg"], fg=C["txt"]).pack(anchor="w", pady=(0, 8))
        keys = [
            ("WASD", "Move Character"), ("SPACE", "Jump (A)"), ("LMB", "Light Attack (Shake)"),
            ("RMB", "Heavy Attack (Nunchuk)"), ("SHIFT", "Block / Grab (B)"), ("1-4", "Select Alien"), ("ESC", "Pause")
        ]
        for k, d in keys:
            tk.Label(p3, text=f"{k:<8} -  {d}", font=("Courier", 9), bg=C["bg"], fg=C["txt"]).pack(anchor="w", pady=2)
        self.tabs["keys"] = p3

        # TAB 4: ABOUT
        p4 = tk.Frame(self.main, bg=C["bg"])
        tk.Label(p4, text="ABOUT PROJECT", font=("Arial", 12, "bold"), bg=C["bg"], fg=C["txt"]).pack(anchor="w", pady=(0, 8))
        tk.Label(p4, text="Open-source PC wrapper for Ben 10: Protector of Earth (Wii).\n60 FPS, 16:9 Widescreen, custom mouse motion controls.\n\nNo copyrighted ROMs included.", font=("Arial", 9), bg=C["bg"], fg=C["dim"], justify="left", wraplength=380).pack(anchor="w")
        self.tabs["info"] = p4

    def show_tab(self, tid):
        for f in self.tabs.values(): f.pack_forget()
        self.tabs[tid].pack(fill="both", expand=True)
        for k, b in self.btns.items(): b.config(bg=C["card"] if k == tid else C["side"], fg=C["acc"] if k == tid else C["dim"])

    def _rom_txt(self):
        p = self.cfg.get("game_path", "")
        return f"Ready: {os.path.basename(p)}" if p and os.path.exists(p) else "No ROM selected. Pick your .rvz / .iso file."

    def _sum_txt(self):
        res = {"1": "480p", "2": "720p", "3": "1080p", "6": "4K"}.get(self.cfg["resolution"], "1080p")
        return f"Profile: {self.cfg['control_scheme']} | {res} | Fullscreen: {self.cfg['fullscreen']}"

    def _pick_rom(self):
        p = filedialog.askopenfilename(filetypes=[("Wii Images", "*.rvz *.iso *.wbfs"), ("All", "*.*")])
        if p:
            self.cfg["game_path"] = p
            ConfigManager.save(self.cfg)
            self.lbl_rom.config(text=self._rom_txt())

    def _save_opts(self):
        self.cfg.update({"control_scheme": self.v_ctrl.get(), "resolution": self.v_res.get(), "fullscreen": self.v_fs.get()})
        ConfigManager.save(self.cfg)
        self.lbl_sum.config(text=self._sum_txt())

    def _play(self):
        gp = self.cfg.get("game_path", "")
        if not gp or not os.path.exists(gp):
            messagebox.showwarning("Error", "Select game image first!")
            return
        ConfigManager.apply_dolphin(self.cfg)
        exe = os.path.join(BASE_DIR, "Dolphin", "Dolphin.exe")
        if not sys.platform.startswith("win"):
            messagebox.showinfo("Test OK", f"Configs written!\nCommand: Dolphin.exe -b -e {os.path.basename(gp)}")
            return
        if not os.path.exists(exe):
            messagebox.showerror("Missing Dolphin", "Put Dolphin.exe inside 'Dolphin' folder.")
            return
        subprocess.Popen([exe, "-b", "-e", gp])

if __name__ == "__main__":
    root = tk.Tk()
    LauncherApp(root)
    root.mainloop()
    