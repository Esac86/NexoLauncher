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
from app.ui.update import AutoUpdateDialog
from app.utils.resources import resource_path
from app.utils.tray import SystemTray

PRIMARIO = "#FF55FF"
SECUNDARIO = "#55FFFF"
APP_NAME = "Nexo Abierto Launcher"

class ToggleSwitch(ctk.CTkFrame):
    def __init__(self, parent, command=None, text_left="Sencillo", text_right="Avanzado", width=280, height=46, **kwargs):
        super().__init__(parent, fg_color="transparent", width=width, height=height)
        self.command = command
        self.is_right = False 
        self.is_locked = False
        self._width_total = width 
        
        self.bg_color = "#0b1220"
        self.border_color = PRIMARIO
        self.slider_color = PRIMARIO
        self.text_active = "#FFFFFF"
        self.text_inactive = "#64748b"
        
        self.canvas = ctk.CTkCanvas(self, width=width, height=height, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack()
        
        self.slider_width = width // 2 - 6
        self.slider_height = height - 10
        self.slider_x = 5
        self.slider_y = 5
        
        self._create_rounded_rect(0, 0, width, height, radius=23, fill="", outline=self.border_color, width=2)
        self._create_rounded_rect(3, 3, width-3, height-3, radius=20, fill=self.bg_color, outline="")
        
        self.slider = self.canvas.create_polygon(self._get_rect_coords(self.slider_x), fill=self.slider_color, outline="", smooth=True)
        
        self.text_left_id = self.canvas.create_text(width * 0.25, height // 2, text=text_left, font=("Segoe UI Semibold", 13), fill=self.text_active)
        self.text_right_id = self.canvas.create_text(width * 0.75, height // 2, text=text_right, font=("Segoe UI Semibold", 13), fill=self.text_inactive)
        
        self.canvas.tag_raise(self.text_left_id)
        self.canvas.tag_raise(self.text_right_id)
        self.canvas.bind("<Button-1>", lambda e: self.toggle())
        
        self.animation_steps = 12
        self.animation_speed = 8 

    def _get_rect_coords(self, x):
        radius = 18
        y1, x2 = self.slider_y, x + self.slider_width
        y2, x1 = y1 + self.slider_height, x
        return [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]

    def _create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def set_state(self, is_right):
        self.is_right = is_right
        self.slider_x = (self._width_total - self.slider_width - 5) if self.is_right else 5
        self.canvas.coords(self.slider, *self._get_rect_coords(self.slider_x))
        self._update_colors()

    def toggle(self):
        if self.is_locked: return
        self.is_right = not self.is_right
        self._update_colors()
        self._animate_slider()
        if self.command: self.command()

    def _animate_slider(self):
        end_x = (self._width_total - self.slider_width - 5) if self.is_right else 5
        step_size = (end_x - self.slider_x) / self.animation_steps
        def animate_step(step=0):
            if step < self.animation_steps:
                self.slider_x += step_size
                self.canvas.coords(self.slider, *self._get_rect_coords(self.slider_x))
                self.after(self.animation_speed, lambda: animate_step(step + 1))
            else:
                self.slider_x = end_x
                self.canvas.coords(self.slider, *self._get_rect_coords(self.slider_x))
        animate_step()

    def _update_colors(self):
        if self.is_right:
            self.canvas.itemconfig(self.text_left_id, fill=self.text_inactive)
            self.canvas.itemconfig(self.text_right_id, fill=self.text_active)
        else:
            self.canvas.itemconfig(self.text_left_id, fill=self.text_active)
            self.canvas.itemconfig(self.text_right_id, fill=self.text_inactive)

    def get(self): return self.is_right
    def set_lock(self, state): self.is_locked = state

class VersionPicker(ctk.CTkFrame):
    def __init__(self, parent, on_version_change=None, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.versions = VersionService.get_versions("release")
        self.on_version_change = on_version_change
        self.is_open = False
        self._disabled = False
        self.main_button = ctk.CTkButton(self, text="Seleccionar Versión", height=50, width=320, corner_radius=16, fg_color="#0b1220", border_color=PRIMARIO, border_width=2, text_color=SECUNDARIO, font=("Segoe UI Semibold", 15), hover_color="#1e293b", command=self._toggle_dropdown)
        self.main_button.pack()
        self.dropdown_frame = ctk.CTkScrollableFrame(self.master.master, width=300, height=200, fg_color="#0b1220", border_color=PRIMARIO, border_width=2, corner_radius=12, scrollbar_button_color=PRIMARIO, scrollbar_button_hover_color=SECUNDARIO)
        self._populate_list()

    def set_state(self, state):
        self._disabled = (state == "disabled")
        self.main_button.configure(state=state)
        if self.is_open and self._disabled:
            self._close_dropdown()

    def _populate_list(self):
        for version in self.versions:
            btn = ctk.CTkButton(self.dropdown_frame, text=version, fg_color="transparent", text_color="#FFFFFF", hover_color="#1e293b", font=("Segoe UI", 13), anchor="center", height=35, command=lambda v=version: self._select_version(v))
            btn.pack(fill="x", padx=5, pady=2)

    def _toggle_dropdown(self):
        if self._disabled: 
            return
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
        if not self.is_open: 
            return
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
        ico_path = resource_path("assets/favicon.ico")
        self._set_taskbar_icon(ico_path)
        self.play_service = PlayService(play_callback, self.update_button_state)
        self.advanced_mode = False
        
        self.tray = SystemTray(self)
        
        self._setup_ui()
        self._center_window()
        self._load_config()
        self._check_updates()
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
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
        card = ctk.CTkFrame(container, corner_radius=28, fg_color="#0b1220", border_width=2, border_color=PRIMARIO)
        card.pack(fill="both", expand=True)
        card.grid_columnconfigure((0, 1), weight=1)
        card.grid_rowconfigure(0, weight=1)
        left_frame = ctk.CTkFrame(card, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        try:
            with Image.open(resource_path("assets/favicon.ico")) as img:
                img = img.resize((260, 260))
                self.logo_img = ctk.CTkImage(img, img, size=(260, 260))
            ctk.CTkLabel(left_frame, image=self.logo_img, text="").place(relx=0.5, rely=0.5, anchor="center")
        except:
            ctk.CTkLabel(left_frame, text="NEXO", font=("Segoe UI", 48, "bold"), text_color=PRIMARIO).place(relx=0.5, rely=0.5, anchor="center")
        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        right_frame.grid_rowconfigure((0, 7), weight=1)
        self.user = ctk.CTkEntry(right_frame, placeholder_text="Nombre de usuario", height=50, width=320, corner_radius=16, fg_color="#0b1220", border_color=PRIMARIO, border_width=2, text_color=SECUNDARIO, placeholder_text_color="#94a3b8", font=("Segoe UI Semibold", 16), justify="center")
        self.user.grid(row=1, column=0, pady=10)
        self.combo = VersionPicker(right_frame, on_version_change=lambda _: self.check_version_installed())
        self.combo.grid(row=2, column=0, pady=10)
        self.combo.grid_remove()
        self.status_label = ctk.CTkLabel(right_frame, text="", font=("Segoe UI", 12), text_color="#AAAAAA")
        self.status_label.grid(row=3, column=0, pady=(10, 0))
        self.progress_bar = ctk.CTkProgressBar(right_frame, width=320, height=12, corner_radius=6, progress_color=PRIMARIO, fg_color="#1e293b")
        self.progress_bar.set(0)
        self.progress_bar.grid(row=4, column=0, pady=(5, 10))
        self.progress_bar.grid_remove()
        self.play_btn = ctk.CTkButton(right_frame, text="▶ JUGAR", height=56, width=320, corner_radius=18, font=("Segoe UI", 20, "bold"), fg_color=PRIMARIO, hover_color=SECUNDARIO, command=self._on_play_click)
        self.play_btn.grid(row=5, column=0, pady=10)
        self.mode_switch = ToggleSwitch(right_frame, command=self._toggle_mode, text_left="Sencillo", text_right="Avanzado", width=320, height=46)
        self.mode_switch.grid(row=6, column=0, pady=(10, 5))
        ctk.CTkLabel(right_frame, text=f"Launcher v{CURRENT_VERSION}", font=("Segoe UI", 10), text_color="#555555").grid(row=7, column=0, pady=(5, 0))

    def _toggle_mode(self):
        self.advanced_mode = self.mode_switch.get()
        
        if self.advanced_mode:
            self.combo.grid()
            latest = VersionService.latest_release()
            if self.combo.get() == "Seleccionar Versión" and latest:
                self.combo.set(latest)
            save_config(mode="advanced") 
        else:
            self.combo.grid_remove()
            latest = VersionService.latest_release()
            if latest:
                self.combo.set(latest)
            save_config(mode="simple") 

        self.check_version_installed()

    def _load_config(self):
            cfg = load_config()

            if cfg.get("username"):
                self.user.insert(0, cfg["username"])

            latest = VersionService.latest_release()
            if latest:
                self.combo.set(latest)

            saved_v = cfg.get("version")
            if saved_v in self.combo.versions:
                self.combo.set(saved_v)

            mode = cfg.get("mode", "simple")
            if mode == "advanced":
                self.mode_switch.set_state(True) 
                self.advanced_mode = True
                self.combo.grid() 
            else:
                self.mode_switch.set_state(False)
                self.advanced_mode = False
                self.combo.grid_remove()

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
        if not self.advanced_mode:
            latest = VersionService.latest_release()
            if latest:
                self.combo.set(latest)
        save_config(username=username, version=self.combo.get())
        self.play_service.launch(username, self.combo.get())

    def check_version_installed(self):
        self.play_btn.configure(text="▶ JUGAR" if self.combo.is_selected_installed() else "🔥 INSTALAR")

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
            self.mode_switch.canvas.unbind("<Button-1>")
            self.progress_bar.grid()
            self.play_btn.configure(text="⏳ INSTALANDO...", state="disabled", fg_color="#444444")
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
            self.status_label.configure(text="Preparando archivos...")
        elif state == "hide_to_tray":
            self.after(500, self.tray.hide_to_tray)
        elif state == "playing":
            self.combo.set_state("disabled")
            self.user.configure(state="disabled")
            self.mode_switch.canvas.unbind("<Button-1>")
            self.progress_bar.grid_remove()
            self.play_btn.configure(text="🎮 JUGANDO...", state="disabled")
            self.status_label.configure(text="")
        elif state == "ready":
            self.combo.set_state("normal")
            self.user.configure(state="normal")
            self.mode_switch.canvas.bind("<Button-1>", lambda e: self.mode_switch.toggle())
            self.progress_bar.grid_remove()
            self.status_label.configure(text="")
            self.play_btn.configure(state="normal", fg_color=PRIMARIO)
            self.check_version_installed()
            self.tray.show_window()
            gc.collect()
        elif state == "error":
            self.combo.set_state("normal")
            self.user.configure(state="normal")
            self.mode_switch.canvas.bind("<Button-1>", lambda e: self.mode_switch.toggle())
            self.progress_bar.grid_remove()
            self.play_btn.configure(state="normal", fg_color=PRIMARIO)
            self.check_version_installed()
            if message:
                messagebox.showerror("Error", message)
            self.tray.show_window()