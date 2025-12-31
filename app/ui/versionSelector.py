import customtkinter as ctk
from minecraft_launcher_lib import utils
import os
from app.utils.paths import MC_DIR

PRIMARIO = "#FF55FF"
SECUNDARIO = "#55FFFF"

class VersionSelector:    
    @staticmethod
    def get_versions(version_type="release"):
        all_versions = utils.get_version_list()
        
        if version_type == "all":
            return [v["id"] for v in all_versions]
        else:
            return [v["id"] for v in all_versions if v["type"] == version_type]
    
    @staticmethod
    def is_version_installed(version):
        path_version = os.path.join(MC_DIR, "versions", version)
        return os.path.exists(path_version)
    
    @staticmethod
    def get_latest_version():
        versions = VersionSelector.get_versions("release")
        return versions[0] if versions else None

class VersionComboBox(ctk.CTkComboBox):    
    def __init__(self, parent, on_version_change=None, **kwargs):
        self.versions = VersionSelector.get_versions("release")
        self.on_version_change = on_version_change
        
        default_config = {
            "values": self.versions,
            "height": 52,
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
        
        default_config.update(kwargs)
        
        super().__init__(parent, **default_config)
        
        if self.versions:
            self.set(self.versions[0])
    
    def _on_select(self, choice):
        if self.on_version_change:
            self.on_version_change(choice)
    
    def get_selected_version(self):
        return self.get()
    
    def is_selected_installed(self):
        return VersionSelector.is_version_installed(self.get())
    
    def refresh_versions(self, version_type="release"):
        self.versions = VersionSelector.get_versions(version_type)
        self.configure(values=self.versions)
        if self.versions:
            self.set(self.versions[0])