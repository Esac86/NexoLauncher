import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import webbrowser
import ctypes
import os
import gc
from app.services.config import load_config, save_config
from app.services.versions import VersionService
from app.services.minecraft import PlayService
from app.utils.helpers import resource_path

PRIMARIO = "#FF55FF"
SECUNDARIO = "#55FFFF"
APP_NAME = "Nexo Abierto Launcher"

class VersionComboBox(ctk.CTkComboBox):
    __slots__ = ("versions", "on_version_change")
    def __init__(self, parent, on_version_change=None, **kwargs):
        self.versions = VersionService.get_versions("release")
        self.on_version_change = on_version_change
        config = {
            "values": self.versions,
            "height": 50,
            "width": 320,
            "corner_radius": 16,
            "fg_color": "#0b1220",
            "border_color": PRIMARIO,
            "border_width": 2,
            "button_color": PRIMARIO,
            "button_hover_color": SECUNDARIO,
            "font": ("Segoe UI", 14),
            "state": "readonly",
            "command": self._on_select
        }
        config.update(kwargs)
        super().__init__(parent, **config)
        if self.versions:
            self.set(self.versions[0])

    def _on_select(self, choice):
        if self.on_version_change:
            self.on_version_change(choice)

    def get_selected_version(self):
        return self.get()

    def is_selected_installed(self):
        return VersionService.is_installed(self.get())

class Launcher(ctk.CTk):
    def __init__(self, play_callback):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("850x550")
        self.resizable(False, False)
        self.configure(fg_color="#020617")

        ico_path = resource_path("img/favicon.ico")
        self._set_taskbar_icon(ico_path)

        self.play_service = PlayService(play_callback, self.update_button_state)
        self._setup_ui()
        self._center_window()
        self._load_config()
        gc.collect()

    def _set_taskbar_icon(self, ico_path):
        try:
            myappid = u'nexo.abierto.launcher.1.0' 
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            if os.path.exists(ico_path):
                self.iconbitmap(ico_path)
        except:
            pass

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_ui(self):
        container = ctk.CTkFrame(self, fg_color="#020617")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        card = ctk.CTkFrame(container, corner_radius=28, fg_color="#0b1220",
                            border_width=2, border_color=PRIMARIO)
        card.pack(fill="both", expand=True)
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)
        card.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(card, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        try:
            with Image.open(resource_path("img/favicon.ico")) as img:
                pil_img = img.resize((260, 260))
                self.logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(260, 260))
            
            logo_label = ctk.CTkLabel(left_frame, image=self.logo_img, text="")
            logo_label.place(relx=0.5, rely=0.5, anchor="center")
            logo_label.bind("<Button-1>", lambda e: webbrowser.open("https://discord.nexoabierto.com"))
        except:
            ctk.CTkLabel(left_frame, text="NEXO", font=("Segoe UI", 48, "bold"), text_color=PRIMARIO).place(relx=0.5, rely=0.5, anchor="center")

        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        right_frame.grid_rowconfigure((0, 6), weight=1)

        self.user = ctk.CTkEntry(right_frame, placeholder_text="Nombre de usuario",
                                 height=50, width=320, corner_radius=16, fg_color="#0b1220",
                                 border_color=PRIMARIO, border_width=2, text_color=SECUNDARIO,
                                 font=("Segoe UI", 14))
        self.user.grid(row=1, column=0, pady=10)

        self.combo = VersionComboBox(right_frame, on_version_change=lambda _: self.check_version_installed())
        self.combo.grid(row=2, column=0, pady=10)

        self.status_label = ctk.CTkLabel(right_frame, text="", font=("Segoe UI", 12), text_color="#AAAAAA")
        self.status_label.grid(row=3, column=0, pady=(10, 0))

        self.progress_bar = ctk.CTkProgressBar(right_frame, width=320, height=12, 
                                               corner_radius=6, progress_color=PRIMARIO, fg_color="#1e293b")
        self.progress_bar.set(0)
        self.progress_bar.grid(row=4, column=0, pady=(5, 10))
        self.progress_bar.grid_remove()

        self.play_btn = ctk.CTkButton(right_frame, text="▶ JUGAR", height=56, width=320,
                                      corner_radius=18, font=("Segoe UI", 20, "bold"),
                                      fg_color=PRIMARIO, hover_color=SECUNDARIO,
                                      command=self._on_play_click)
        self.play_btn.grid(row=5, column=0, pady=10)

    def _load_config(self):
        cfg = load_config()
        if cfg.get("username"):
            self.user.insert(0, cfg["username"])
        if cfg.get("version") and cfg["version"] in self.combo.versions:
            self.combo.set(cfg["version"])
        self.check_version_installed()

    def _on_play_click(self):
        username = self.user.get().strip()
        if not username:
            messagebox.showwarning("Atención", "Escribe un nombre de usuario")
            return
        save_config(username=username, version=self.combo.get_selected_version())
        self.play_service.launch(username, self.combo.get_selected_version())

    def check_version_installed(self):
        if self.combo.is_selected_installed():
            self.play_btn.configure(text="▶ JUGAR")
        else:
            self.play_btn.configure(text="📥 INSTALAR")

    def update_button_state(self, state, current=0, total=0, message=None):
        if state == "installing":
            self.progress_bar.grid()
            self.play_btn.configure(text="⏳ INSTALANDO...", state="disabled", fg_color="#444444")
            
            if total > 0:
                progress_val = current / total
                self.progress_bar.set(progress_val)
                mb_current = current / (1024 * 1024)
                mb_total = total / (1024 * 1024)
                self.status_label.configure(text=f"Descargando: {mb_current:.1f}MB / {mb_total:.1f}MB")
            else:
                self.progress_bar.configure(mode="indeterminate")
                self.progress_bar.start()
                self.status_label.configure(text="Preparando archivos...")

        elif state == "playing":
            self.progress_bar.grid_remove()
            self.status_label.configure(text="¡Disfruta del juego!")
            self.play_btn.configure(text="🎮 JUGANDO...", state="disabled", fg_color="#444444")

        elif state == "ready":
            self.progress_bar.grid_remove()
            self.status_label.configure(text="")
            self.play_btn.configure(text="▶ JUGAR", state="normal", fg_color=PRIMARIO)
            self.check_version_installed()
            gc.collect()

        elif state == "error":
            self.progress_bar.grid_remove()
            self.play_btn.configure(state="normal", fg_color=PRIMARIO)
            self.check_version_installed()
            if message:
                messagebox.showerror("Error", message)