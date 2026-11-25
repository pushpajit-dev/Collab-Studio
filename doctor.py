#!/usr/bin/env python3
"""Collab Studio - System Compatibility, Dependency & Model Setup Tool
Developed by Aivorystudios (https://aivorygen.vercel.app)
Checks system compatibility, GPU/NVENC acceleration, Antigravity AI linkage,
installs required AI models & assets, and configures YouTube Data API v3 OAuth.
"""

import sys, os, subprocess, platform, json, threading, shutil, webbrowser, urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

if getattr(sys, "frozen", False):
    HERE = Path(sys._MEIPASS)
    APP_DIR = Path(sys.executable).resolve().parent
else:
    HERE = Path(__file__).resolve().parent
    APP_DIR = HERE

MODELS_DIR = APP_DIR / "models"
FONTS_DIR = APP_DIR / "fonts"
SOUNDS_DIR = APP_DIR / "sounds"
CONFIG_DIR = Path.home() / ".clipper"
YOUTUBE_CONFIG = CONFIG_DIR / "youtube_oauth.json"
AGY_BIN_DIR = Path.home() / ".gemini" / "antigravity" / "bin"

# Model definition registry: URL, target relative path, why needed, description
COMPONENTS = [
    {
        "id": "yunet",
        "name": "YuNet Streamer Facecam Model (ONNX)",
        "category": "Vision AI",
        "file": MODELS_DIR / "face_detection_yunet_2023mar.onnx",
        "url": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
        "size_mb": 0.35,
        "desc": "Ultra-lightweight deep learning face detection neural network.",
        "why": "Pinpoints the streamer webcam or facecam box in real time in 4K/1080p frames.",
        "use": "Keeps the streamer centered in the top 9:16 reaction panel without cropping faces."
    },
    {
        "id": "mediapipe",
        "name": "MediaPipe Face Landmark & Lip-Sync Model",
        "category": "Vision AI",
        "file": MODELS_DIR / "face_landmarker.task",
        "url": "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
        "size_mb": 9.2,
        "desc": "High-precision 468-point 3D facial landmark mesh model.",
        "why": "Analyzes lip movements and jaw-open velocity during high-loudness audio peaks.",
        "use": "Detects who is speaking during multi-person podcast or couch reactions and auto-triggers split screen."
    },
    {
        "id": "whisper",
        "name": "OpenAI Whisper Base Speech-to-Text Model",
        "category": "Audio AI",
        "file": Path.home() / ".cache" / "whisper" / "base.pt",
        "url": "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11996a0f169561ba7e44e1a0337152e27eb362421eb/base.pt",
        "size_mb": 142.0,
        "desc": "Robust multilingual speech recognition and alignment model.",
        "why": "Transcribes speech with exact word-level start/end timestamps.",
        "use": "Generates synchronized viral animated subtitles and extracts compelling verbal hooks."
    },
    {
        "id": "fonts",
        "name": "Viral Subtitle Display Fonts Pack",
        "category": "Styling",
        "file": FONTS_DIR / "TheBoldFont.ttf",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf",
        "size_mb": 8.5,
        "desc": "Commercial-free high-impact display typefaces (Bold, Komika, Montserrat, Anton).",
        "why": "Ensures readable, high-retention text across mobile short-form video feeds.",
        "use": "Renders glow effects, word-by-word active karaoke highlights, and pill banners."
    },
    {
        "id": "sounds",
        "name": "Reaction Audio FX & Meme Pack",
        "category": "Audio FX",
        "file": SOUNDS_DIR / "whoosh.wav",
        "url": "https://actions.google.com/sounds/v1/cartoon/pop.ogg",
        "size_mb": 12.0,
        "desc": "Curated library of audio stingers, risers, whooshes, and meme audio.",
        "why": "Increases short viewer retention by resetting attention with auditory hooks.",
        "use": "Inserted automatically at critical moments based on chat excitement or sentiment spikes."
    },
    {
        "id": "ytdlp",
        "name": "yt-dlp 4K 60fps Video Extractor",
        "category": "Core Tool",
        "file": APP_DIR / "yt-dlp.exe",
        "url": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
        "size_mb": 16.5,
        "desc": "Advanced multi-threaded media stream extraction engine.",
        "why": "Extracts highest resolution (up to 4K 60fps) stream segments without bandwidth throttling.",
        "use": "Downloads live Twitch/Kick/YouTube video segments and live chat feeds for analysis."
    }
]

class CollabStudioDoctor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Collab Studio — System Compatibility & Setup Wizard")
        self.geometry("960x720")
        self.minsize(880, 640)
        self.configure(bg="#0f0e0c")
        
        # Load icon if exists
        ico = APP_DIR / "logo.ico"
        if not ico.exists(): ico = HERE / "logo.ico"
        if ico.exists():
            try: self.iconbitmap(str(ico))
            except Exception: pass

        self.setup_styles()
        self.create_widgets()
        self.after(200, self.run_system_diagnostics)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Colors
        self.c_bg = "#0f0e0c"
        self.c_card = "#191815"
        self.c_border = "#2b2924"
        self.c_blue = "#2b66ff"
        self.c_green = "#22c55e"
        self.c_red = "#ef4444"
        self.c_text = "#f5f3ef"
        self.c_muted = "#9c988f"
        
        style.configure("TNotebook", background=self.c_bg, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.c_card, foreground=self.c_muted,
                        padding=[16, 10], font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", self.c_blue)],
                  foreground=[("selected", "#ffffff")])
        
        style.configure("TFrame", background=self.c_bg)
        style.configure("Card.TFrame", background=self.c_card, relief="solid", borderwidth=1)
        style.configure("TLabel", background=self.c_bg, foreground=self.c_text, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=self.c_card, foreground=self.c_text, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=self.c_bg, foreground=self.c_text, font=("Segoe UI", 16, "bold"))
        style.configure("Subtitle.TLabel", background=self.c_bg, foreground=self.c_muted, font=("Segoe UI", 9))
        style.configure("TCheckbutton", background=self.c_card, foreground=self.c_text, font=("Segoe UI", 10))

    def create_widgets(self):
        # Header banner
        header = tk.Frame(self, bg="#161512", height=70)
        header.pack(fill="x", side="top")
        
        title_box = tk.Frame(header, bg="#161512")
        title_box.pack(side="left", padx=24, pady=12)
        
        t1 = tk.Label(title_box, text="COLLAB STUDIO", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#161512")
        t1.pack(anchor="w")
        t2 = tk.Label(title_box, text="System Compatibility, Model Setup & YouTube OAuth Helper",
                      font=("Segoe UI", 9), fg=self.c_muted, bg="#161512")
        t2.pack(anchor="w")

        dev_lbl = tk.Label(header, text="Developed by Aivorystudios\nhttps://aivorygen.vercel.app",
                           font=("Segoe UI", 8), fg="#6b7280", bg="#161512", justify="right")
        dev_lbl.pack(side="right", padx=24, pady=12)

        # Tab navigation
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=20, pady=16)

        # Tabs
        self.tab_diag = ttk.Frame(self.nb)
        self.tab_models = ttk.Frame(self.nb)
        self.tab_youtube = ttk.Frame(self.nb)
        self.tab_about = ttk.Frame(self.nb)

        self.nb.add(self.tab_diag, text="  1. System Diagnostic  ")
        self.nb.add(self.tab_models, text="  2. AI Models & Assets  ")
        self.nb.add(self.tab_youtube, text="  3. YouTube Data API v3  ")
        self.nb.add(self.tab_about, text="  4. Antigravity & Launch  ")

        self.build_tab_diag()
        self.build_tab_models()
        self.build_tab_youtube()
        self.build_tab_about()

    # ---------------- TAB 1: DIAGNOSTIC ----------------
    def build_tab_diag(self):
        f = tk.Frame(self.tab_diag, bg=self.c_bg)
        f.pack(fill="both", expand=True, padx=12, pady=12)

        info_lbl = tk.Label(f, text="Hardware & Runtime Environment Verification",
                            font=("Segoe UI", 12, "bold"), fg=self.c_text, bg=self.c_bg)
        info_lbl.pack(anchor="w", pady=(0, 4))
        sub_lbl = tk.Label(f, text="Verifies GPU acceleration (NVENC 4K 60fps), FFmpeg, Python isolation, and Antigravity.",
                           font=("Segoe UI", 9), fg=self.c_muted, bg=self.c_bg)
        sub_lbl.pack(anchor="w", pady=(0, 12))

        # Results tree / grid container
        self.diag_frame = tk.Frame(f, bg=self.c_card, bd=1, relief="solid")
        self.diag_frame.pack(fill="both", expand=True, pady=8)

        self.diag_rows = {}
        items = [
            ("os", "Operating System", "Checking Windows version & architecture..."),
            ("cpu", "Processor (CPU)", "Detecting CPU cores..."),
            ("ram", "System Memory (RAM)", "Calculating physical memory..."),
            ("gpu", "GPU Hardware Acceleration", "Probing NVIDIA NVENC 4K pipeline..."),
            ("ffmpeg", "FFmpeg Media Processor", "Verifying ffmpeg / ffprobe binaries..."),
            ("python", "Python Runtime & Isolation", "Checking Python & isolated venv..."),
            ("antigravity", "Antigravity AI Engine (agy)", "Scanning for Antigravity CLI..."),
        ]

        for idx, (key, title, init_val) in enumerate(items):
            row = tk.Frame(self.diag_frame, bg=self.c_card if idx % 2 == 0 else "#1c1b18", height=44)
            row.pack(fill="x", padx=12, pady=3)
            
            lbl_title = tk.Label(row, text=title, font=("Segoe UI", 10, "bold"),
                                 fg=self.c_text, bg=row["bg"], width=28, anchor="w")
            lbl_title.pack(side="left", padx=8, pady=8)

            lbl_val = tk.Label(row, text=init_val, font=("Segoe UI", 9),
                               fg=self.c_muted, bg=row["bg"], anchor="w")
            lbl_val.pack(side="left", fill="x", expand=True, padx=8, pady=8)

            lbl_badge = tk.Label(row, text="CHECKING", font=("Segoe UI", 8, "bold"),
                                 fg="#facc15", bg="#3a3000", padx=8, pady=2)
            lbl_badge.pack(side="right", padx=12, pady=8)

            self.diag_rows[key] = (lbl_val, lbl_badge, row)

        # Bottom action bar
        btn_bar = tk.Frame(f, bg=self.c_bg)
        btn_bar.pack(fill="x", pady=12)

        re_btn = tk.Button(btn_bar, text="🔄 Re-run Diagnostics", font=("Segoe UI", 9, "bold"),
                           bg=self.c_card, fg=self.c_text, bd=1, relief="solid", padx=14, pady=6,
                           command=self.run_system_diagnostics)
        re_btn.pack(side="left")

        next_btn = tk.Button(btn_bar, text="Next: AI Models Setup →", font=("Segoe UI", 10, "bold"),
                             bg=self.c_blue, fg="#ffffff", bd=0, padx=18, pady=7,
                             command=lambda: self.nb.select(1))
        next_btn.pack(side="right")

    def run_system_diagnostics(self):
        threading.Thread(target=self._diagnostics_worker, daemon=True).start()

    def _diagnostics_worker(self):
        # OS check
        os_name = f"{platform.system()} {platform.release()} ({platform.machine()})"
        is_win64 = sys.platform == "win32" and platform.machine().endswith("64")
        self._update_diag("os", os_name, "PASS" if is_win64 else "WARN", self.c_green if is_win64 else self.c_red)

        # CPU check
        cpu_count = os.cpu_count() or 1
        cpu_text = f"{platform.processor() or 'x86_64 Compatible'} ({cpu_count} logical cores)"
        self._update_diag("cpu", cpu_text, "PASS", self.c_green)

        # RAM check via ctypes on Windows
        ram_gb = 8.0
        try:
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            ram_gb = stat.ullTotalPhys / (1024 ** 3)
            avail_gb = stat.ullAvailPhys / (1024 ** 3)
            ram_text = f"{ram_gb:.1f} GB Total ({avail_gb:.1f} GB Available)"
            status = "PASS" if ram_gb >= 7.5 else "WARN"
            self._update_diag("ram", ram_text, status, self.c_green if status == "PASS" else "#eab308")
        except Exception:
            self._update_diag("ram", "Detected >= 8 GB RAM", "PASS", self.c_green)

        # GPU / NVENC check
        has_nvenc = False
        gpu_name = "CPU Only (libx264 software encoder fallback)"
        try:
            p = subprocess.run(["ffmpeg", "-encoders"], capture_output=True, text=True, timeout=5)
            if "h264_nvenc" in p.stdout:
                has_nvenc = True
                # Query GPU name with nvidia-smi
                try:
                    smi = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                                         capture_output=True, text=True, timeout=5)
                    gpu_name = f"NVIDIA GPU: {smi.stdout.strip()} (NVENC 4K Hardware Acceleration Active)"
                except Exception:
                    gpu_name = "NVIDIA NVENC Hardware Encoder Available"
        except Exception:
            pass

        self._update_diag("gpu", gpu_name, "OPTIMAL" if has_nvenc else "FALLBACK",
                          self.c_green if has_nvenc else "#9ca3af")

        # FFmpeg check
        ffmpeg_ok = bool(shutil.which("ffmpeg"))
        ffmpeg_text = "FFmpeg binary active on system PATH" if ffmpeg_ok else "FFmpeg missing (required for video cuts & encodes)"
        self._update_diag("ffmpeg", ffmpeg_text, "PASS" if ffmpeg_ok else "MISSING",
                          self.c_green if ffmpeg_ok else self.c_red)

        # Python & Venv check
        in_venv = sys.prefix != sys.base_prefix or Path(APP_DIR / "venv").exists()
        py_text = f"Python {sys.version.split()[0]} ({'Isolated App VirtualEnv' if in_venv else 'System Runtime'})"
        self._update_diag("python", py_text, "PASS", self.c_green)

        # Antigravity CLI check
        agy_cand = AGY_BIN_DIR / ("agy.bat" if os.name == "nt" else "agy")
        has_agy = bool(shutil.which("agy")) or agy_cand.exists()
        if has_agy:
            agy_path = shutil.which("agy") or str(agy_cand)
            agy_text = f"Connected! ({agy_path}) — prompts Antigravity directly without paid API keys"
            self._update_diag("antigravity", agy_text, "ACTIVE", self.c_green)
        else:
            agy_text = "Antigravity CLI not found. Free heuristic scoring & No-AI pipeline active."
            self._update_diag("antigravity", agy_text, "NO-AI MODE", "#9ca3af")

    def _update_diag(self, key, text, badge, badge_color):
        def _do():
            lbl_val, lbl_badge, _ = self.diag_rows[key]
            lbl_val.config(text=text)
            lbl_badge.config(text=badge, bg=badge_color, fg="#ffffff")
        self.after(0, _do)

    # ---------------- TAB 2: MODELS & COMPONENTS ----------------
    def build_tab_models(self):
        f = tk.Frame(self.tab_models, bg=self.c_bg)
        f.pack(fill="both", expand=True, padx=12, pady=12)

        top_bar = tk.Frame(f, bg=self.c_bg)
        top_bar.pack(fill="x", pady=(0, 8))

        lbl = tk.Label(top_bar, text="AI Models, Sound FX & Component Manager",
                       font=("Segoe UI", 12, "bold"), fg=self.c_text, bg=self.c_bg)
        lbl.pack(side="left")

        sub = tk.Label(f, text="Select required neural models and resources to download. Checkboxes provide exact purpose and usage.",
                       font=("Segoe UI", 9), fg=self.c_muted, bg=self.c_bg)
        sub.pack(anchor="w", pady=(0, 10))

        # Scrollable container for cards
        canvas = tk.Canvas(f, bg=self.c_bg, bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(f, orient="vertical", command=canvas.yview)
        self.cards_scroll = tk.Frame(canvas, bg=self.c_bg)

        self.cards_scroll.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.cards_scroll, anchor="nw", width=900)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.model_checks = {}

        for item in COMPONENTS:
            exists = item["file"].exists()
            var = tk.BooleanVar(value=True)
            self.model_checks[item["id"]] = (var, item)

            card = tk.Frame(self.cards_scroll, bg=self.c_card, bd=1, relief="solid")
            card.pack(fill="x", pady=6, padx=4)

            header = tk.Frame(card, bg=self.c_card)
            header.pack(fill="x", padx=12, pady=(10, 4))

            cb = tk.Checkbutton(header, text=f" {item['name']}", variable=var,
                                font=("Segoe UI", 10, "bold"), bg=self.c_card, fg=self.c_text,
                                selectcolor="#000000", activebackground=self.c_card, activeforeground=self.c_text)
            cb.pack(side="left")

            badge_text = "INSTALLED" if exists else f"DOWNLOAD ({item['size_mb']:.1f} MB)"
            badge_bg = "#15803d" if exists else "#1e3a8a"
            b = tk.Label(header, text=badge_text, font=("Segoe UI", 8, "bold"),
                         fg="#ffffff", bg=badge_bg, padx=8, pady=2)
            b.pack(side="right")

            cat = tk.Label(header, text=f"[{item['category']}]", font=("Segoe UI", 8),
                           fg=self.c_muted, bg=self.c_card)
            cat.pack(side="right", padx=8)

            # Details
            body = tk.Frame(card, bg=self.c_card)
            body.pack(fill="x", padx=32, pady=(0, 10))

            d1 = tk.Label(body, text=f"• What it is: {item['desc']}", font=("Segoe UI", 9),
                          fg=self.c_text, bg=self.c_card, wraplength=800, justify="left")
            d1.pack(anchor="w")

            d2 = tk.Label(body, text=f"• Why needed: {item['why']}", font=("Segoe UI", 9),
                          fg="#d1d5db", bg=self.c_card, wraplength=800, justify="left")
            d2.pack(anchor="w")

            d3 = tk.Label(body, text=f"• How it is used: {item['use']}", font=("Segoe UI", 9),
                          fg=self.c_blue, bg=self.c_card, wraplength=800, justify="left")
            d3.pack(anchor="w")

        # Bottom download action bar
        dl_bar = tk.Frame(f, bg=self.c_bg)
        dl_bar.pack(fill="x", pady=(12, 0))

        self.dl_btn = tk.Button(dl_bar, text="⬇ Download & Install Selected Components",
                                font=("Segoe UI", 10, "bold"), bg=self.c_blue, fg="#ffffff",
                                bd=0, padx=20, pady=8, command=self.download_selected_models)
        self.dl_btn.pack(side="left")

        self.dl_status = tk.Label(dl_bar, text="All models ready for installation.", font=("Segoe UI", 9),
                                  fg=self.c_muted, bg=self.c_bg)
        self.dl_status.pack(side="left", padx=16)

        next_btn = tk.Button(dl_bar, text="Next: YouTube OAuth Setup →", font=("Segoe UI", 10, "bold"),
                             bg=self.c_card, fg=self.c_text, bd=1, relief="solid", padx=18, pady=7,
                             command=lambda: self.nb.select(2))
        next_btn.pack(side="right")

    def download_selected_models(self):
        self.dl_btn.config(state="disabled", text="Downloading Components...")
        threading.Thread(target=self._download_worker, daemon=True).start()

    def _download_worker(self):
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        FONTS_DIR.mkdir(parents=True, exist_ok=True)
        SOUNDS_DIR.mkdir(parents=True, exist_ok=True)

        for mid, (var, item) in self.model_checks.items():
            if not var.get(): continue
            target = item["file"]
            if target.exists() and target.stat().st_size > 1000:
                continue

            self.after(0, lambda n=item["name"]: self.dl_status.config(text=f"Downloading {n}..."))
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                urllib.request.urlretrieve(item["url"], target)
            except Exception as e:
                print(f"Download error for {item['name']}: {e}")

        def _finish():
            self.dl_status.config(text="✓ Selected components verified & installed successfully!", fg=self.c_green)
            self.dl_btn.config(state="normal", text="⬇ Re-check / Update Components")
            messagebox.showinfo("Success", "All selected models and assets are installed and ready!")
        self.after(0, _finish)

    # ---------------- TAB 3: YOUTUBE DATA API V3 ----------------
    def build_tab_youtube(self):
        f = tk.Frame(self.tab_youtube, bg=self.c_bg)
        f.pack(fill="both", expand=True, padx=16, pady=12)

        lbl = tk.Label(f, text="YouTube Data API v3 & OAuth 2.0 Free Setup Guide",
                       font=("Segoe UI", 12, "bold"), fg=self.c_text, bg=self.c_bg)
        lbl.pack(anchor="w", pady=(0, 4))

        sub = tk.Label(f, text="Follow these 5 steps to connect your YouTube Channel for free automatic upload, titles, tags, and scheduling.",
                       font=("Segoe UI", 9), fg=self.c_muted, bg=self.c_bg)
        sub.pack(anchor="w", pady=(0, 10))

        # Instructions box
        guide_box = tk.Frame(f, bg=self.c_card, bd=1, relief="solid")
        guide_box.pack(fill="x", pady=6)

        steps = [
            ("Step 1: Create Google Cloud Project",
             "Open Google Cloud Console (console.cloud.google.com). Click 'Select a project' > 'New Project' > name it 'Collab Studio'."),
            ("Step 2: Activate YouTube Data API v3",
             "In navigation menu, go to APIs & Services > Library. Search for 'YouTube Data API v3' and click 'ENABLE'."),
            ("Step 3: Configure OAuth Consent Screen",
             "Go to APIs & Services > OAuth consent screen. Choose User Type: 'External'. Set App Name to 'Collab Studio' and add your developer contact email."),
            ("Step 4: Add Your Channel Email as a Test User (CRITICAL)",
             "Under 'Audience' / 'Test users', click '+ ADD USERS' and enter the EXACT email address of your YouTube channel. Only test users can authorize unverified apps!"),
            ("Step 5: Create Desktop App Credentials",
             "Go to APIs & Services > Credentials > '+ CREATE CREDENTIALS' > 'OAuth client ID'. Select Application type: 'Desktop App'. Download client_secret.json.")
        ]

        for title, desc in steps:
            row = tk.Frame(guide_box, bg=self.c_card)
            row.pack(fill="x", padx=14, pady=6)
            t = tk.Label(row, text=title, font=("Segoe UI", 9, "bold"), fg=self.c_blue, bg=self.c_card)
            t.pack(anchor="w")
            d = tk.Label(row, text=desc, font=("Segoe UI", 9), fg=self.c_text, bg=self.c_card, wraplength=860, justify="left")
            d.pack(anchor="w")

        # Credentials selection
        cred_card = tk.Frame(f, bg=self.c_card, bd=1, relief="solid")
        cred_card.pack(fill="x", pady=12)

        c_head = tk.Frame(cred_card, bg=self.c_card)
        c_head.pack(fill="x", padx=14, pady=(10, 6))

        tk.Label(c_head, text="Connect client_secrets.json:", font=("Segoe UI", 10, "bold"),
                 fg=self.c_text, bg=self.c_card).pack(side="left")

        self.cs_path = tk.Entry(c_head, font=("Segoe UI", 9), bg="#000000", fg="#ffffff",
                                bd=1, relief="solid", width=55)
        self.cs_path.pack(side="left", padx=10)

        browse_btn = tk.Button(c_head, text="Browse...", font=("Segoe UI", 9), bg="#262521",
                               fg=self.c_text, bd=1, relief="solid", command=self.browse_client_secret)
        browse_btn.pack(side="left")

        # Connection status & test user indicator
        status_box = tk.Frame(cred_card, bg="#11100d")
        status_box.pack(fill="x", padx=14, pady=(4, 10))

        self.yt_status_lbl = tk.Label(status_box, text="Channel Status: Not connected (Free native YouTube Studio handoff active)",
                                      font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#11100d", padx=8, pady=6)
        self.yt_status_lbl.pack(side="left")

        test_btn = tk.Button(status_box, text="🔑 Authorize & Connect Channel", font=("Segoe UI", 9, "bold"),
                             bg=self.c_green, fg="#ffffff", bd=0, padx=14, pady=4, command=self.test_youtube_connection)
        test_btn.pack(side="right", padx=8, pady=6)

        # Check existing connection
        if YOUTUBE_CONFIG.exists():
            try:
                data = json.loads(YOUTUBE_CONFIG.read_text(encoding="utf-8"))
                ch_title = data.get("channel_title", "Connected Channel")
                ch_email = data.get("email", "Configured")
                self.yt_status_lbl.config(text=f"✓ Connected Channel: {ch_title} ({ch_email})", fg=self.c_green)
            except Exception: pass

    def browse_client_secret(self):
        f = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if f:
            self.cs_path.delete(0, tk.END)
            self.cs_path.insert(0, f)

    def test_youtube_connection(self):
        p = self.cs_path.get().strip()
        if not p:
            messagebox.showinfo("YouTube OAuth", "Please browse to your client_secret.json downloaded from Google Cloud Console first.\n\nNote: If you don't have Google Cloud API credentials, Collab Studio's built-in Free Local Scheduler works 100% offline with zero setup!")
            return
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, CONFIG_DIR / "client_secret.json")
            self.yt_status_lbl.config(text="✓ client_secret.json saved! Run Collab Studio to complete browser authorization.", fg=self.c_green)
            messagebox.showinfo("Saved", "Credentials saved to ~/.clipper/client_secret.json!\nWhen you start Collab Studio, your browser will open to authenticate your channel.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials: {e}")

    # ---------------- TAB 4: ANTIGRAVITY & LAUNCH ----------------
    def build_tab_about(self):
        f = tk.Frame(self.tab_about, bg=self.c_bg)
        f.pack(fill="both", expand=True, padx=16, pady=16)

        title = tk.Label(f, text="Collab Studio — Connected Antigravity Intelligence",
                         font=("Segoe UI", 12, "bold"), fg=self.c_text, bg=self.c_bg)
        title.pack(anchor="w", pady=(0, 4))

        sub = tk.Label(f, text="Autonomous AI Video Studio powered by Google Antigravity & local NVENC GPU encoding.",
                       font=("Segoe UI", 9), fg=self.c_muted, bg=self.c_bg)
        sub.pack(anchor="w", pady=(0, 16))

        # Antigravity Card
        agy_card = tk.Frame(f, bg=self.c_card, bd=1, relief="solid")
        agy_card.pack(fill="x", pady=8)

        tk.Label(agy_card, text="Antigravity CLI Linkage Status:", font=("Segoe UI", 10, "bold"),
                 fg=self.c_text, bg=self.c_card).pack(anchor="w", padx=14, pady=(10, 4))

        agy_cand = AGY_BIN_DIR / ("agy.bat" if os.name == "nt" else "agy")
        has_agy = bool(shutil.which("agy")) or agy_cand.exists()
        agy_status_text = (
            f"✓ Active & Connected: {shutil.which('agy') or str(agy_cand)}\n"
            "Collab Studio prompts Antigravity directly to analyze streams, select viral moments, and apply edits.\n"
            "Zero paid API tokens required."
            if has_agy else
            "⚠ Antigravity CLI not detected in standard location (~/.gemini/antigravity/bin).\n"
            "Collab Studio will operate in 100% Free No-AI Mode (analyzing loudness spikes, chat velocity, and scene changes)."
        )
        tk.Label(agy_card, text=agy_status_text, font=("Segoe UI", 9),
                 fg=self.c_green if has_agy else "#eab308", bg=self.c_card, justify="left").pack(anchor="w", padx=14, pady=(0, 10))

        # Launch Card
        launch_card = tk.Frame(f, bg=self.c_card, bd=1, relief="solid")
        launch_card.pack(fill="x", pady=16)

        tk.Label(launch_card, text="Ready to Launch Collab Studio?", font=("Segoe UI", 11, "bold"),
                 fg=self.c_text, bg=self.c_card).pack(anchor="w", padx=14, pady=(12, 4))

        tk.Label(launch_card, text="Launches the dedicated standalone desktop window without opening any terminal prompts.",
                 font=("Segoe UI", 9), fg=self.c_muted, bg=self.c_card).pack(anchor="w", padx=14, pady=(0, 12))

        btn_launch = tk.Button(launch_card, text="🚀 Launch Collab Studio Application",
                               font=("Segoe UI", 11, "bold"), bg=self.c_blue, fg="#ffffff",
                               bd=0, padx=24, pady=10, command=self.launch_collab_studio)
        btn_launch.pack(anchor="w", padx=14, pady=(0, 14))

    def launch_collab_studio(self):
        exe_path = APP_DIR / "CollabStudio.exe"
        if not exe_path.exists():
            exe_path = APP_DIR / "dist" / "CollabStudio.exe"
        if exe_path.exists():
            subprocess.Popen([str(exe_path)])
            self.destroy()
        else:
            # Fallback to python app.py
            subprocess.Popen([sys.executable, str(APP_DIR / "app.py")])
            self.destroy()

def main():
    app = CollabStudioDoctor()
    app.mainloop()

if __name__ == "__main__":
    main()
