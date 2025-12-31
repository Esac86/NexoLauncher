import customtkinter as ctk
from customtkinter import CTkImage
from tkinter import messagebox
import webbrowser
from PIL import Image
from app.ui.versionSelector import VersionComboBox
from app.utils.paths import MC_DIR
import threading

PRIMARIO = "#FF55FF"
SECUNDARIO = "#55FFFF"
APP_NAME = "Nexo Abierto Launcher"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class Launcher(ctk.CTk):
    def __init__(self, on_play):
        super().__init__()
        self.on_play = on_play
        self.title(APP_NAME)
        self.geometry("850x500")
        self.resizable(False, False)
        self.configure(fg_color="#020617")
        self.is_running = False
        self.centrar_ventana()
        self.ui()
        self.check_version_installed()

    def centrar_ventana(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{x}+{y}")

    def ui(self):
        container = ctk.CTkFrame(self, fg_color="#020617")
        container.pack(fill="both", expand=True, padx=30, pady=20)

        card = ctk.CTkFrame(
            container, 
            corner_radius=28, 
            fg_color="#0b1220", 
            border_width=2, 
            border_color=PRIMARIO
        )
        card.pack(fill="both", expand=True)

        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)
        card.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(card, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        try:
            pil_img = Image.open("img/logo.png").resize((280, 280), Image.Resampling.LANCZOS)
            self.logo_img = CTkImage(light_image=pil_img, dark_image=pil_img, size=(280, 280))
            self.logo_label = ctk.CTkLabel(left_frame, image=self.logo_img, text="")
            self.logo_label.grid(row=0, column=0)
            self.logo_label.bind("<Button-1>", lambda e: webbrowser.open("https://discord.nexoabierto.com"))
        except Exception as e:
            ctk.CTkLabel(
                left_frame, 
                text="LOGO", 
                font=("Segoe UI", 48, "bold"),
                text_color=PRIMARIO
            ).grid(row=0, column=0)

        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)
        
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=0)
        right_frame.grid_rowconfigure(2, weight=0)
        right_frame.grid_rowconfigure(3, weight=0)
        right_frame.grid_rowconfigure(4, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        self.user = ctk.CTkEntry(
            right_frame, 
            placeholder_text="Nombre de usuario", 
            height=52, 
            width=320,
            corner_radius=16, 
            fg_color="#0b1220",
            border_color=PRIMARIO,
            border_width=2,
            text_color=SECUNDARIO,
            font=("Segoe UI", 14)
        )
        self.user.grid(row=1, column=0, pady=12)

        self.combo = VersionComboBox(
            right_frame,
            on_version_change=lambda _: self.check_version_installed()
        )
        self.combo.grid(row=2, column=0, pady=12)

        self.play_btn = ctk.CTkButton(
            right_frame, 
            text="▶ JUGAR", 
            height=56,
            width=320,
            corner_radius=18, 
            font=("Segoe UI", 20, "bold"), 
            fg_color=PRIMARIO, 
            hover_color=SECUNDARIO,
            command=self.play
        )
        self.play_btn.grid(row=3, column=0, pady=(24, 0))

    def check_version_installed(self):
        """Verifica si la versión seleccionada está instalada"""
        if self.combo.is_selected_installed():
            self.play_btn.configure(text="▶ JUGAR")
        else:
            self.play_btn.configure(text="📥 INSTALAR")
    
    def update_button_state(self, state):
        """Actualiza el estado del botón según la acción"""
        if state == "installing":
            self.play_btn.configure(
                text="⏳ INSTALANDO...",
                state="disabled",
                fg_color="#666666"
            )
        elif state == "playing":
            self.play_btn.configure(
                text="🎮 JUGANDO...",
                state="disabled",
                fg_color="#666666"
            )
        elif state == "ready":
            self.is_running = False
            self.play_btn.configure(
                state="normal",
                fg_color=PRIMARIO
            )
            self.check_version_installed()

    def play(self):
        if self.is_running:
            return
        
        user = self.user.get().strip()
        version = self.combo.get_selected_version()
        
        if not user:
            return messagebox.showerror("Error", "Usuario requerido")
        
        self.is_running = True
        threading.Thread(
            target=lambda: self.on_play(user, version, self.update_button_state), 
            daemon=True
        ).start()