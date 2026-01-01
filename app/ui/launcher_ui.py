import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import ctypes
import os
import gc
import threading
from app.services.config import load_config, save_config
from app.services.versions import VersionService
from app.services.minecraft import PlayService
from app.services.updater import UpdateService, CURRENT_VERSION
from app.ui.update_ui import AutoUpdateDialog
from app.utils.helpers import resource_path

PRIMARIO = "#FF55FF"
SECUNDARIO = "#55FFFF"
APP_NAME = "Nexo Abierto Launcher"

class VersionPicker(ctk.CTkFrame):
    def __init__(self, parent, on_version_change=None, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.versions = VersionService.get_versions("release")
        self.on_version_change = on_version_change
        self.is_open = False
        self._disabled = False

        self.main_button = ctk.CTkButton(
            self, 
            text="Seleccionar Versión",
            height=50, 
            width=320, 
            corner_radius=16,
            fg_color="#0b1220", 
            border_color=PRIMARIO, 
            border_width=2,
            text_color=SECUNDARIO, 
            font=("Segoe UI Semibold", 15),
            hover_color="#1e293b",
            command=self._toggle_dropdown
        )
        self.main_button.pack()

        self.dropdown_frame = ctk.CTkScrollableFrame(
            self.master.master, 
            width=300, 
            height=200,
            fg_color="#0b1220", 
            border_color=PRIMARIO, 
            border_width=2,
            corner_radius=12,
            scrollbar_button_color=PRIMARIO,
            scrollbar_button_hover_color=SECUNDARIO
        )
        
        self._populate_list()

    def set_state(self, state):
        self._disabled = (state == "disabled")
        self.main_button.configure(state=state)
        if self.is_open and self._disabled:
            self._close_dropdown()

    def _populate_list(self):
        for version in self.versions:
            btn = ctk.CTkButton(
                self.dropdown_frame,
                text=version,
                fg_color="transparent",
                text_color="#FFFFFF",
                hover_color="#1e293b",
                font=("Segoe UI", 13),
                anchor="center",
                height=35,
                command=lambda v=version: self._select_version(v)
            )
            btn.pack(fill="x", padx=5, pady=2)

    def _toggle_dropdown(self):
        if self._disabled: return
        if self.is_open:
            self._close_dropdown()
        else:
            self._open_dropdown()

    def _open_dropdown(self):
        self.main_button.update_idletasks()
        parent_frame = self.master.master
        x = self.main_button.winfo_rootx() - parent_frame.winfo_rootx()
        y = self.main_button.winfo_rooty() - parent_frame.winfo_rooty() + self.main_button.winfo_height()
        
        self.dropdown_frame.place(x=x, y=y)
        self.dropdown_frame.lift()
        self.main_button.configure(border_color=SECUNDARIO)
        self.is_open = True
        
        self.master.winfo_toplevel().bind("<Button-1>", self._check_click_outside, add="+")

    def _close_dropdown(self):
        self.dropdown_frame.place_forget()
        self.main_button.configure(border_color=PRIMARIO)
        self.is_open = False
        self.master.winfo_toplevel().unbind("<Button-1>")

    def _check_click_outside(self, event):
        if not self.is_open: return
        target = event.widget
        if target != self.main_button and not str(target).startswith(str(self.dropdown_frame)):
            self._close_dropdown()

    def _select_version(self, version):
        self.main_button.configure(text=version)
        self._close_dropdown()
        if self.on_version_change:
            self.on_version_change(version)

    def get(self):
        return self.main_button.cget("text")

    def set(self, value):
        self.main_button.configure(text=value)

    def is_selected_installed(self):
        return VersionService.is_installed(self.get())


class Launcher(ctk.CTk):
    def __init__(self, play_callback):
        super().__init__()

        self.title(f"{APP_NAME} v{CURRENT_VERSION}")
        self.geometry("850x550")
        self.resizable(False, False)
        self.configure(fg_color="#020617")

        ico_path = resource_path("img/favicon.ico")
        self._set_taskbar_icon(ico_path)

        self.play_service = PlayService(play_callback, self.update_button_state)

        self._setup_ui()
        self._center_window()
        self._load_config()
        self._check_updates()

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
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_ui(self):
        container = ctk.CTkFrame(self, fg_color="#020617")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        card = ctk.CTkFrame(
            container,
            corner_radius=28,
            fg_color="#0b1220",
            border_width=2,
            border_color=PRIMARIO
        )
        card.pack(fill="both", expand=True)
        card.grid_columnconfigure((0, 1), weight=1)
        card.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(card, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        try:
            with Image.open(resource_path("img/favicon.ico")) as img:
                img = img.resize((260, 260))
                self.logo_img = ctk.CTkImage(img, img, size=(260, 260))
            ctk.CTkLabel(left_frame, image=self.logo_img, text="") \
                .place(relx=0.5, rely=0.5, anchor="center")
        except:
            ctk.CTkLabel(
                left_frame,
                text="NEXO",
                font=("Segoe UI", 48, "bold"),
                text_color=PRIMARIO
            ).place(relx=0.5, rely=0.5, anchor="center")

        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        right_frame.grid_rowconfigure((0, 7), weight=1)

        self.user = ctk.CTkEntry(
            right_frame,
            placeholder_text="Nombre de usuario",
            height=50, width=320, corner_radius=16,
            fg_color="#0b1220", border_color=PRIMARIO, border_width=2,
            text_color=SECUNDARIO, placeholder_text_color="#94a3b8",
            font=("Segoe UI Semibold", 16), justify="center"
        )
        self.user.grid(row=1, column=0, pady=10)

        self.combo = VersionPicker(
            right_frame,
            on_version_change=lambda _: self.check_version_installed()
        )
        self.combo.grid(row=2, column=0, pady=10)

        self.status_label = ctk.CTkLabel(
            right_frame, text="", font=("Segoe UI", 12), text_color="#AAAAAA"
        )
        self.status_label.grid(row=3, column=0, pady=(10, 0))

        self.progress_bar = ctk.CTkProgressBar(
            right_frame, width=320, height=12, corner_radius=6,
            progress_color=PRIMARIO, fg_color="#1e293b"
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=4, column=0, pady=(5, 10))
        self.progress_bar.grid_remove()

        self.play_btn = ctk.CTkButton(
            right_frame,
            text="▶ JUGAR",
            height=56, width=320, corner_radius=18,
            font=("Segoe UI", 20, "bold"),
            fg_color=PRIMARIO, hover_color=SECUNDARIO,
            command=self._on_play_click
        )
        self.play_btn.grid(row=5, column=0, pady=10)

        ctk.CTkLabel(
            right_frame,
            text=f"Launcher v{CURRENT_VERSION}",
            font=("Segoe UI", 10),
            text_color="#555555"
        ).grid(row=6, column=0, pady=(5, 0))


    def _load_config(self):
        cfg = load_config()
        if cfg.get("username"):
            self.user.insert(0, cfg["username"])
        
        saved_v = cfg.get("version")
        if saved_v in self.combo.versions:
            self.combo.set(saved_v)
        self.check_version_installed()

    def _check_updates(self):
        def check():
            info = UpdateService.check_for_updates()
            if info:
                self.after(500, lambda: AutoUpdateDialog(self, info, UpdateService))
        threading.Thread(target=check, daemon=True).start()

    def _on_play_click(self):
        username = self.user.get().strip()
        if not username:
            messagebox.showwarning("Atención", "Escribe un nombre de usuario")
            return
        save_config(username=username, version=self.combo.get())
        self.play_service.launch(username, self.combo.get())

    def check_version_installed(self):
        self.play_btn.configure(
            text="▶ JUGAR" if self.combo.is_selected_installed() else "🔥 INSTALAR"
        )

    def update_button_state(self, state, current=0, total=0, message=None):
        if state == "installing":
            self.combo.set_state("disabled")
            self.progress_bar.grid()
            self.play_btn.configure(text="⏳ INSTALANDO...", state="disabled", fg_color="#444444")
            if total > 0:
                self.progress_bar.set(current / total)
                self.status_label.configure(
                    text=f"Descargando: {current/1024/1024:.1f}MB / {total/1024/1024:.1f}MB"
                )
            else:
                self.progress_bar.configure(mode="indeterminate")
                self.progress_bar.start()
                self.status_label.configure(text="Preparando archivos...")

        elif state == "playing":
            self.combo.set_state("disabled")
            self.progress_bar.grid_remove()
            self.play_btn.configure(text="🎮 JUGANDO...", state="disabled")

        elif state == "ready":
            self.combo.set_state("normal") 
            self.progress_bar.grid_remove()
            self.status_label.configure(text="")
            self.play_btn.configure(state="normal", fg_color=PRIMARIO)
            self.check_version_installed()
            gc.collect()

        elif state == "error":
            self.combo.set_state("normal")
            self.progress_bar.grid_remove()
            self.play_btn.configure(state="normal", fg_color=PRIMARIO)
            self.check_version_installed()
            if message:
                messagebox.showerror("Error", message)