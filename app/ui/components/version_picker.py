import customtkinter as ctk
from app.services.versions import VersionService

PRIMARIO = "#FF55FF"
SECUNDARIO = "#55FFFF"


class VersionPicker(ctk.CTkFrame):
    def __init__(self, parent, on_version_change=None, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.versions = None
        self.on_version_change = on_version_change
        self.is_open = False
        self._disabled = False
        self.dropdown_frame = None
        
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

    def _lazy_load_versions(self):
        if self.versions is None:
            self.versions = VersionService.get_versions("release")
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
        if self._disabled:
            return
        if self.is_open:
            self._close_dropdown()
        else:
            self._open_dropdown()

    def _open_dropdown(self):
        self._lazy_load_versions()
        self.main_button.update_idletasks()
        parent_frame = self.master.master
        x = self.main_button.winfo_rootx() - parent_frame.winfo_rootx()
        y = self.main_button.winfo_rooty() - parent_frame.winfo_rooty() + \
            self.main_button.winfo_height()
        self.dropdown_frame.place(x=x, y=y)
        self.dropdown_frame.lift()
        self.main_button.configure(border_color=SECUNDARIO)
        self.is_open = True
        self.master.winfo_toplevel().bind("<Button-1>", self._check_click_outside, add="+")

    def _close_dropdown(self):
        if self.dropdown_frame:
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