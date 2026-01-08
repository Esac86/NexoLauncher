import pystray
from PIL import Image
import threading
from app.utils.resources import resource_path

class SystemTray:
    def __init__(self, launcher_window):
        self.launcher = launcher_window
        self.icon = None
        self.is_running = False
        
    def create_tray_icon(self):
        icon_path = resource_path("assets/favicon.ico")
        image = Image.open(icon_path)
        
        menu = pystray.Menu(
            pystray.MenuItem('Abrir Launcher', self.show_window, default=True),
            pystray.MenuItem('Salir', self.quit_app)
        )
        
        self.icon = pystray.Icon(
            "NexoLauncher",
            image,
            "Nexo Launcher",
            menu
        )
        
    def show_window(self, icon=None, item=None):
        self.launcher.after(0, self._show_window_safe)
        
    def _show_window_safe(self):
        self.launcher.deiconify()
        self.launcher.lift()
        self.launcher.focus_force()
        
    def hide_to_tray(self):
        if not self.is_running:
            self.create_tray_icon()
            self.is_running = True
            threading.Thread(target=self._run_tray, daemon=True).start()
        
        self.launcher.withdraw()
        
    def _run_tray(self):
        if self.icon:
            self.icon.run()
            
    def quit_app(self, icon=None, item=None):
        self.stop_tray()
        self.launcher.after(0, self.launcher.quit)
        
    def stop_tray(self):
        if self.icon:
            self.icon.stop()
            self.is_running = False
