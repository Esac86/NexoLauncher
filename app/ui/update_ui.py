import customtkinter as ctk
import threading
import sys
import os
from app.utils.helpers import resource_path

PRIMARIO = "#FF55FF"
SECUNDARIO = "#55FFFF"

class AutoUpdateDialog(ctk.CTkToplevel):
    def __init__(self, parent, update_info, updater_service):
        super().__init__(parent)
        self.update_info = update_info
        self.updater_service = updater_service
        
        self.title("Actualizando Launcher")
        self.geometry("450x280")
        self.resizable(False, False)
        self.configure(fg_color="#020617")
        
        try:
            ico_path = resource_path("img/favicon.ico")
            if os.path.exists(ico_path):
                self.after(10, lambda: self.iconbitmap(ico_path))
        except:
            pass
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 225
        y = (self.winfo_screenheight() // 2) - 140
        self.geometry(f"450x280+{x}+{y}")
        
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        
        self._setup_ui()
        self._start_update()
    
    def _setup_ui(self):
        container = ctk.CTkFrame(self, fg_color="#0b1220", corner_radius=20,
                                 border_width=2, border_color=PRIMARIO)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(container, text="🔄 Actualizando Launcher",
                            font=("Segoe UI", 22, "bold"), text_color=PRIMARIO)
        title.pack(pady=(30, 10))
        
        version_text = f"Nueva versión: {self.update_info['version']}"
        version_label = ctk.CTkLabel(container, text=version_text,
                                     font=("Segoe UI", 14), text_color=SECUNDARIO)
        version_label.pack(pady=(0, 30))
        
        self.progress_bar = ctk.CTkProgressBar(container, width=350, height=16,
                                              corner_radius=8, progress_color=PRIMARIO,
                                              fg_color="#1e293b")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(10, 10))
        
        self.status_label = ctk.CTkLabel(container, text="Preparando descarga...",
                                        font=("Segoe UI", 12), text_color="#AAAAAA")
        self.status_label.pack(pady=(5, 30))
    
    def _start_update(self):
        download_url = self.update_info.get('download_url')
        if not download_url:
            self.status_label.configure(text="❌ Error: No se encontró el archivo")
            self.after(3000, self.destroy)
            return
        
        threading.Thread(target=self._download_update, args=(download_url,), daemon=True).start()
    
    def _download_update(self, download_url):
        def on_progress(current, total):
            progress = current / total
            mb_current = current / (1024 * 1024)
            mb_total = total / (1024 * 1024)
            self.after(0, lambda: self.progress_bar.set(progress))
            self.after(0, lambda: self.status_label.configure(
                text=f"Descargando: {mb_current:.1f} MB / {mb_total:.1f} MB"
            ))
        
        success = self.updater_service.download_and_install(
            download_url, 
            self.update_info['version'],
            on_progress
        )
        
        if success:
            self.after(0, lambda: self.status_label.configure(
                text="✅ Actualización completada. Reiniciando..."
            ))
            self.after(0, lambda: self.progress_bar.set(1))
            self.after(1500, lambda: sys.exit(0))
        else:
            self.after(0, lambda: self.status_label.configure(
                text="❌ Error al descargar. Reiniciando launcher..."
            ))
            self.after(3000, self.destroy)