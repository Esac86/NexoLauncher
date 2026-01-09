import customtkinter as ctk
import threading
import sys
import os
from app.utils.resources import resource_path
from app.services.updater import UpdateService

PRIMARIO = "#FF55FF"
SECUNDARIO = "#55FFFF"

class AutoUpdateDialog(ctk.CTkToplevel):
    def __init__(self, parent, update_info, updater_service):
        super().__init__(parent)

        self.update_info = update_info

        self.title("Actualizando Launcher")
        self.geometry("450x280")
        self.resizable(False, False)
        self.configure(fg_color="#020617")

        try:
            ico = resource_path("assets/updater.ico")
            if os.path.exists(ico):
                self.iconbitmap(ico)
        except:
            pass

        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self._center_window(parent)

        self._setup_ui()
        self._start_update()

    def _center_window(self, parent):
        """Centrar la ventana sobre la ventana padre."""
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        x = px + (pw // 2) - (w // 2)
        y = py + (ph // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_ui(self):
        frame = ctk.CTkFrame(
            self, fg_color="#0b1220", corner_radius=20,
            border_width=2, border_color=PRIMARIO
        )
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="🔄 Actualizando Launcher",
            font=("Segoe UI", 22, "bold"),
            text_color=PRIMARIO
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            frame,
            text=f"Nueva versión: {self.update_info['version']}",
            font=("Segoe UI", 14),
            text_color=SECUNDARIO
        ).pack(pady=(0, 30))

        self.progress = ctk.CTkProgressBar(
            frame, width=350, height=16,
            progress_color=PRIMARIO, fg_color="#1e293b"
        )
        self.progress.set(0)
        self.progress.pack(pady=10)

        self.status = ctk.CTkLabel(
            frame, text="Preparando actualización...",
            font=("Segoe UI", 12), text_color="#AAAAAA"
        )
        self.status.pack(pady=(5, 30))

    def _start_update(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        ok = UpdateService.start_update(
            self.update_info["download_url"]
        )

        if ok:
            self.after(500, lambda: sys.exit(0))
        else:
            self.after(0, lambda: self.status.configure(
                text="❌ Error iniciando actualización"
            ))
