import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import ctypes
import os
import threading

from app.services.config import load_config, save_config
from app.services.versions import VersionService
from app.services.minecraft import PlayService
from app.services.updater import UpdateService, CURRENT_VERSION
from app.ui.update import AutoUpdateDialog
from app.ui.components.switches import DualToggleSwitch, ToggleSwitch
from app.ui.components.version_picker import VersionPicker
from app.ui.auth.microsoft import MicrosoftAuthHandler

from app.utils.resources import resource_path
from app.utils.tray import SystemTray

PRIMARIO = "#FF55FF"
SECUNDARIO = "#55FFFF"
APP_NAME = "Nexo Abierto Launcher"
AZURE_CLIENT_ID = "5df0d729-2718-4ad1-9793-0cf6c3212ad2"
AZURE_REDIRECT_URI = "http://localhost:25566/callback"
MICROSOFT_LOGIN_ENABLED = True


class Launcher(ctk.CTk):
    def __init__(self, play_callback):
        super().__init__()
        self.title(f"{APP_NAME} v{CURRENT_VERSION}")
        self.geometry("850x600")
        self.resizable(False, False)
        self.configure(fg_color="#020617")
        
        self.withdraw()
        
        self._set_taskbar_icon()
        
        self.play_service = PlayService(play_callback, self.update_button_state)
        self.auth_handler = MicrosoftAuthHandler(self, AZURE_CLIENT_ID, AZURE_REDIRECT_URI)
        self.advanced_mode = False
        self.logo_img = None
        self.ms_account = None
        self.tray = SystemTray(self)
        
        self._setup_ui()
        self._center_window()
        
        self._load_config_and_show()
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _set_taskbar_icon(self):
        try:
            ico_path = resource_path("assets/favicon.ico")
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
        
        card = ctk.CTkFrame(container, corner_radius=28, fg_color="#0b1220",
                           border_width=2, border_color=PRIMARIO)
        card.pack(fill="both", expand=True)
        card.grid_columnconfigure((0, 1), weight=1)
        card.grid_rowconfigure(0, weight=1)
        
        self._setup_left_panel(card)
        self._setup_right_panel(card)

    def _setup_left_panel(self, parent):
        left_frame = ctk.CTkFrame(parent, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        logo_container = ctk.CTkFrame(left_frame, fg_color="transparent")
        logo_container.pack(expand=True, fill="both")
        
        try:
            ico_path = resource_path("assets/favicon.ico")
            with Image.open(ico_path) as img:
                img = img.resize((220, 220))
                self.logo_img = ctk.CTkImage(img, img, size=(220, 220))
            ctk.CTkLabel(logo_container, image=self.logo_img, text="").pack(pady=(40, 10))
        except:
            ctk.CTkLabel(logo_container, text="NEXO", font=("Segoe UI", 48, "bold"),
                        text_color=PRIMARIO).pack(pady=(40, 10))
        
        buttons_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        buttons_frame.pack(side="bottom", pady=(10, 20))
        
        self.ms_left_button = ctk.CTkButton(
            buttons_frame,
            text="🔐 Iniciar Sesión Microsoft",
            height=44,
            width=280,
            corner_radius=14,
            fg_color="#0b1220",
            border_color=SECUNDARIO,
            border_width=2,
            text_color=SECUNDARIO if MICROSOFT_LOGIN_ENABLED else "#666666",
            font=("Segoe UI Semibold", 13),
            hover_color="#1e293b" if MICROSOFT_LOGIN_ENABLED else "#0b1220",
            command=self._on_microsoft_action,
            state="normal" if MICROSOFT_LOGIN_ENABLED else "disabled"
        )
        self.ms_left_button.pack(pady=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="🎨 Carpeta Shaders",
            height=44,
            width=280,
            corner_radius=14,
            fg_color="#0b1220",
            border_color=PRIMARIO,
            border_width=2,
            text_color=SECUNDARIO,
            font=("Segoe UI Semibold", 13),
            hover_color="#1e293b",
            command=self._open_shaders_folder
        ).pack(pady=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="📦 Carpeta Mods",
            height=44,
            width=280,
            corner_radius=14,
            fg_color="#0b1220",
            border_color=PRIMARIO,
            border_width=2,
            text_color=SECUNDARIO,
            font=("Segoe UI Semibold", 13),
            hover_color="#1e293b",
            command=self._open_mods_folder
        ).pack(pady=5)

    def _setup_right_panel(self, parent):
        right_frame = ctk.CTkFrame(parent, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        right_frame.grid_rowconfigure((0, 8), weight=1)
        
        self.ms_button = ctk.CTkButton(
            right_frame,
            text="🔐 Iniciar sesión con Microsoft",
            height=44,
            width=320,
            corner_radius=14,
            fg_color="#0b1220",
            border_color=PRIMARIO if MICROSOFT_LOGIN_ENABLED else "#444444",
            border_width=2,
            text_color=SECUNDARIO if MICROSOFT_LOGIN_ENABLED else "#666666",
            font=("Segoe UI Semibold", 13),
            hover_color="#1e293b" if MICROSOFT_LOGIN_ENABLED else "#0b1220",
            command=self._on_microsoft_login,
            state="normal" if MICROSOFT_LOGIN_ENABLED else "disabled"
        )
        self.ms_button.grid(row=1, column=0, pady=(0, 5))
        self.ms_button.grid_remove()
        
        self.user = ctk.CTkEntry(
            right_frame,
            placeholder_text="Nombre de usuario",
            height=50,
            width=320,
            corner_radius=16,
            fg_color="#0b1220",
            border_color=PRIMARIO,
            border_width=2,
            text_color=SECUNDARIO,
            placeholder_text_color="#94a3b8",
            font=("Segoe UI Semibold", 16),
            justify="center"
        )
        self.user.grid(row=2, column=0, pady=(5, 10))
        
        self.combo = VersionPicker(right_frame,
                                   on_version_change=lambda _: self.check_version_installed())
        self.combo.grid(row=3, column=0, pady=10)
        self.combo.grid_remove()
        
        self.type_switch = DualToggleSwitch(
            right_frame,
            command=self._on_type_change,
            width=320,
            height=46
        )
        self.type_switch.grid(row=4, column=0, pady=10)
        self.type_switch.grid_remove()
        
        self.status_label = ctk.CTkLabel(right_frame, text="",
                                        font=("Segoe UI", 12), text_color="#AAAAAA")
        self.status_label.grid(row=5, column=0, pady=(10, 0))
        
        self.progress_bar = ctk.CTkProgressBar(right_frame, width=320, height=12,
                                              corner_radius=6, progress_color=PRIMARIO,
                                              fg_color="#1e293b")
        self.progress_bar.set(0)
        self.progress_bar.grid(row=6, column=0, pady=(5, 10))
        self.progress_bar.grid_remove()
        
        self.play_btn = ctk.CTkButton(
            right_frame,
            text="▶ JUGAR",
            height=56,
            width=320,
            corner_radius=18,
            font=("Segoe UI", 20, "bold"),
            fg_color=PRIMARIO,
            hover_color=SECUNDARIO,
            command=self._on_play_click
        )
        self.play_btn.grid(row=7, column=0, pady=10)
        
        self.mode_switch = ToggleSwitch(
            right_frame,
            command=self._toggle_mode,
            text_left="Sencillo",
            text_right="Avanzado",
            width=320,
            height=46
        )
        self.mode_switch.grid(row=8, column=0, pady=(10, 5))
        
        ctk.CTkLabel(
            right_frame,
            text=f"Launcher v{CURRENT_VERSION}",
            font=("Segoe UI", 10),
            text_color="#555555"
        ).grid(row=9, column=0, pady=(5, 0))

    def _on_microsoft_action(self):
        if not MICROSOFT_LOGIN_ENABLED:
            return
        
        if self.ms_account:
            self._logout_microsoft()
        else:
            self.auth_handler.start_login(self._on_login_success)
    
    def _logout_microsoft(self):
        result = messagebox.askyesno(
            "Cerrar sesión",
            f"¿Quieres cerrar la sesión de {self.ms_account.get('name', 'Microsoft')}?"
        )
        
        if result:
            self.ms_account = None
            self.user.configure(state="normal")
            self.user.delete(0, "end")
            self.ms_button.configure(
                text="🔐 Iniciar sesión con Microsoft",
                state="normal",
                border_color=PRIMARIO
            )
            self.ms_left_button.configure(
                text="🔐 Microsoft",
                border_color=PRIMARIO
            )
            
            save_config(
                username="",
                ms_account=False,
                refresh_token=None
            )
            
            messagebox.showinfo("Sesión cerrada", "Has cerrado sesión correctamente")

    def _on_microsoft_login(self):
        if not MICROSOFT_LOGIN_ENABLED:
            return
        self.auth_handler.start_login(self._on_login_success)

    def _on_login_success(self, account_info):
        username = account_info.get("name", "Usuario Microsoft")
        self.ms_account = account_info
        self.user.delete(0, "end")
        self.user.insert(0, username)
        self.user.configure(state="disabled")
        self.ms_button.configure(
            text=f"✓ {username}",
            state="disabled",
            border_color=SECUNDARIO
        )
        self.ms_left_button.configure(
            text="✓ Cerrar sesión",
            border_color=SECUNDARIO
        )
        
        save_config(
            username=username, 
            ms_account=True,
            refresh_token=account_info.get("refresh_token")
        )
        
        messagebox.showinfo("¡Éxito!", f"Sesión iniciada como: {username}")
    
    def _open_shaders_folder(self):
        from app.utils.paths import DIR
        import subprocess
        
        shaders_path = DIR / "shaderpacks"
        shaders_path.mkdir(exist_ok=True)
        
        try:
            if os.name == 'nt':
                os.startfile(shaders_path)
            else:
                subprocess.run(['xdg-open', str(shaders_path)])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{str(e)}")
    
    def _open_mods_folder(self):
        from app.utils.paths import DIR
        import subprocess
        
        mods_path = DIR / "mods"
        mods_path.mkdir(exist_ok=True)
        
        try:
            if os.name == 'nt':
                os.startfile(mods_path)
            else:
                subprocess.run(['xdg-open', str(mods_path)])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{str(e)}")

    def _load_config_and_show(self):
        def load_in_background():
            cfg = load_config()
            
            ms_restored = False
            if cfg.get("ms_account") and cfg.get("refresh_token"):
                result = self.auth_handler.refresh_token(cfg["refresh_token"], timeout=5)
                if result:
                    self.ms_account = result
                    username = result.get("name", "Usuario Microsoft")
                    ms_restored = True
                    
                    self.after(0, lambda: self._apply_config_ui(cfg, ms_restored, username))
                else:
                    self.after(0, lambda: self._apply_config_ui(cfg, False, None))
            else:
                self.after(0, lambda: self._apply_config_ui(cfg, False, None))
        
        threading.Thread(target=load_in_background, daemon=True).start()

    def _apply_config_ui(self, cfg, ms_restored, ms_username):
        if ms_restored and ms_username:
            self.user.delete(0, "end")
            self.user.insert(0, ms_username)
            self.user.configure(state="disabled")
            self.ms_button.configure(
                text=f"✓ {ms_username}",
                state="disabled",
                border_color=SECUNDARIO
            )
            self.ms_left_button.configure(
                text="✓ Cerrar sesión",
                border_color=SECUNDARIO
            )
        elif cfg.get("username"):
            self.user.insert(0, cfg["username"])
        
        latest = VersionService.latest_release()
        if latest:
            self.combo.set(latest)
        
        saved_v = cfg.get("version")
        if saved_v:
            if self.combo.versions is None:
                self.combo._lazy_load_versions()
            if saved_v in self.combo.versions:
                self.combo.set(saved_v)
        
        mode = cfg.get("mode", "simple")
        if mode == "advanced":
            self.mode_switch.set_state(True)
            self.advanced_mode = True
            self.combo.grid()
            self.type_switch.grid()
        else:
            self.mode_switch.set_state(False)
            self.advanced_mode = False
            self.combo.grid_remove()
            self.type_switch.grid_remove()
        
        mod_type = cfg.get("mod_type", "vanilla")
        
        if mod_type in ["optifine", "forge"]:
            self.type_switch.set_position(1)
        else:
            self.type_switch.set_position(0)
        
        self.check_version_installed()
        
        self._check_updates()
        
        self.deiconify()
        self.lift()
        self.focus_force()

    def _check_updates(self):
        def check():
            info = UpdateService.check_for_updates()
            if info:
                self.after(500, lambda: AutoUpdateDialog(self, info, UpdateService))
        threading.Thread(target=check, daemon=True).start()

    def _on_type_change(self):
        self.check_version_installed()
        save_config(mod_type=self.type_switch.get())

    def _toggle_mode(self):
        self.advanced_mode = self.mode_switch.get()
        if self.advanced_mode:
            self.combo.grid()
            self.type_switch.grid()
            latest = VersionService.latest_release()
            if self.combo.get() == "Seleccionar Versión" and latest:
                self.combo.set(latest)
            save_config(mode="advanced")
        else:
            self.combo.grid_remove()
            self.type_switch.grid_remove()
            latest = VersionService.latest_release()
            if latest:
                self.combo.set(latest)
            save_config(mode="simple")
        self.check_version_installed()

    def _on_play_click(self):
        username = self.user.get().strip()
        if not username:
            messagebox.showwarning("Atención", "Escribe un nombre de usuario")
            return
        
        if not self.advanced_mode:
            latest = VersionService.latest_release()
            if latest:
                self.combo.set(latest)
            mod_type = "vanilla"
        else:
            mod_type = self.type_switch.get()
        
        version = self.combo.get()
        save_config(username=username, version=version, mod_type=mod_type)
        self.play_service.launch(username, version, self.ms_account, mod_type)

    def check_version_installed(self):
        if not self.advanced_mode:
            is_installed = self.combo.is_selected_installed()
        else:
            mod_type = self.type_switch.get()
            version = self.combo.get()
            
            if mod_type == "modded":
                is_installed = VersionService.is_optimized_installed(version)
            else:
                is_installed = VersionService.is_installed(version)
        
        self.play_btn.configure(
            text="▶ JUGAR" if is_installed else "🔥 INSTALAR"
        )
        
    def _on_close(self):
        if self.play_service.is_running:
            self.tray.hide_to_tray()
        else:
            self.tray.stop_tray()
            self.quit()

    def update_button_state(self, state, message=None):
        if state == "installing":
            self.combo.set_state("disabled")
            self.user.configure(state="disabled")
            self.ms_button.configure(state="disabled")
            self.ms_left_button.configure(state="disabled")
            self.mode_switch.canvas.unbind("<Button-1>")
            self.progress_bar.grid()
            self.play_btn.configure(
                text="⏳ INSTALANDO...", state="disabled", fg_color="#444444")
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
            self.status_label.configure(text="Preparando archivos...")
        elif state == "hide_to_tray":
            self.after(500, self.tray.hide_to_tray)
        elif state == "playing":
            self.combo.set_state("disabled")
            self.user.configure(state="disabled")
            self.ms_button.configure(state="disabled")
            self.ms_left_button.configure(state="disabled")
            self.mode_switch.canvas.unbind("<Button-1>")
            self.progress_bar.grid_remove()
            self.play_btn.configure(text="🎮 JUGANDO...", state="disabled")
            self.status_label.configure(text="")
        elif state == "ready":
            self.combo.set_state("normal")
            if not self.ms_account and MICROSOFT_LOGIN_ENABLED:
                self.user.configure(state="normal")
                self.ms_button.configure(state="normal")
                self.ms_left_button.configure(state="normal")
            self.mode_switch.canvas.bind(
                "<Button-1>", lambda e: self.mode_switch.toggle())
            self.progress_bar.grid_remove()
            self.status_label.configure(text="")
            self.play_btn.configure(state="normal", fg_color=PRIMARIO)
            self.check_version_installed()
            self.tray.show_window()
        elif state == "error":
            self.combo.set_state("normal")
            if not self.ms_account and MICROSOFT_LOGIN_ENABLED:
                self.user.configure(state="normal")
                self.ms_button.configure(state="normal")
                self.ms_left_button.configure(state="normal")
            self.mode_switch.canvas.bind(
                "<Button-1>", lambda e: self.mode_switch.toggle())
            self.progress_bar.grid_remove()
            self.play_btn.configure(state="normal", fg_color=PRIMARIO)
            self.check_version_installed()
            if message:
                messagebox.showerror("Error", message)
            self.tray.show_window()