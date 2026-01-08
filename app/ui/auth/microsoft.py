import threading
import webbrowser
from tkinter import messagebox
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import customtkinter as ctk
import minecraft_launcher_lib as mll
from app.services.config import save_config

PRIMARIO = "#FF55FF"
SECUNDARIO = "#55FFFF"

class MicrosoftAuthHandler:    
    def __init__(self, parent, client_id, redirect_uri):
        self.parent = parent
        self.client_id = client_id
        self.redirect_uri = redirect_uri

    def start_login(self, on_success_callback):
        def login_thread():
            try:
                login_url, state, code_verifier = mll.microsoft_account.get_secure_login_data(
                    self.client_id,
                    self.redirect_uri
                )
                self.parent.after(0, lambda: self._start_local_server_and_login(
                    login_url, state, code_verifier, on_success_callback))
            except Exception as e:
                self.parent.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Error al iniciar sesión: {str(e)}"
                ))
        
        threading.Thread(target=login_thread, daemon=True).start()

    def _start_local_server_and_login(self, login_url, state, code_verifier, on_success_callback):
        captured_data = {"code": None, "error": None, "cancelled": False}
        
        class CallbackHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass
            
            def do_GET(handler_self):
                parsed = urlparse(handler_self.path)
                params = parse_qs(parsed.query)
                
                if "code" in params:
                    captured_data["code"] = params["code"][0]
                    handler_self._send_success_page()
                elif "error" in params:
                    captured_data["error"] = params.get("error_description", ["Error desconocido"])[0]
                    handler_self._send_error_page()
            
            def _send_success_page(handler_self):
                handler_self.send_response(200)
                handler_self.send_header("Content-type", "text/html; charset=utf-8")
                handler_self.end_headers()
                html = self._get_success_html()
                handler_self.wfile.write(html.encode())
            
            def _send_error_page(handler_self):
                handler_self.send_response(200)
                handler_self.send_header("Content-type", "text/html; charset=utf-8")
                handler_self.end_headers()
                html = self._get_error_html()
                handler_self.wfile.write(html.encode())
        
        status_window = self._create_status_window(captured_data)
        
        threading.Thread(
            target=self._run_server,
            args=(CallbackHandler, captured_data, status_window, state, code_verifier, on_success_callback, login_url),
            daemon=True
        ).start()

    def _create_status_window(self, captured_data):
        status_window = ctk.CTkToplevel(self.parent)
        status_window.title("Esperando inicio de sesión...")
        status_window.geometry("450x300")
        status_window.resizable(False, False)
        status_window.configure(fg_color="#020617")
        
        self.parent.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 225
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 150
        status_window.geometry(f"450x300+{x}+{y}")
        status_window.transient(self.parent)
        status_window.grab_set()
        
        main_frame = ctk.CTkFrame(
            status_window, 
            fg_color="#0b1220",
            corner_radius=20, 
            border_width=2, 
            border_color=PRIMARIO
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="🔐", font=("Segoe UI", 64)).pack(pady=(30, 10))
        
        ctk.CTkLabel(
            main_frame,
            text="Esperando inicio de sesión...",
            font=("Segoe UI", 18, "bold"),
            text_color=PRIMARIO
        ).pack(pady=10)
        
        ctk.CTkLabel(
            main_frame,
            text="Se abrió tu navegador.\n\nInicia sesión con tu cuenta de Microsoft.\n\n"
                 "El launcher detectará automáticamente\ncuando completes el inicio de sesión.",
            font=("Segoe UI", 12),
            text_color="#CCCCCC",
            justify="center"
        ).pack(pady=15)
        
        ctk.CTkButton(
            main_frame,
            text="✕ Cancelar",
            height=40,
            width=150,
            corner_radius=12,
            fg_color="#0b1220",
            border_width=2,
            border_color="#666666",
            text_color="#999999",
            hover_color="#1e293b",
            font=("Segoe UI Semibold", 13),
            command=lambda: [setattr(captured_data, 'cancelled', True), status_window.destroy()]
        ).pack(pady=15)
        
        return status_window

    def _run_server(self, handler_class, captured_data, status_window, state, code_verifier, 
                    on_success_callback, login_url):
        try:
            server = HTTPServer(('localhost', 25566), handler_class)
            server.timeout = 0.5
            webbrowser.open(login_url)
            
            while (captured_data["code"] is None and 
                   captured_data["error"] is None and 
                   not captured_data.get('cancelled', False)):
                server.handle_request()
            
            server.server_close()
            self.parent.after(0, status_window.destroy)
            
            if captured_data["code"]:
                callback_url = f"{self.redirect_uri}?code={captured_data['code']}&state={state}"
                threading.Thread(
                    target=self._complete_login,
                    args=(callback_url, state, code_verifier, on_success_callback),
                    daemon=True
                ).start()
            elif captured_data["error"]:
                self.parent.after(0, lambda: messagebox.showerror(
                    "Error de autenticación",
                    f"Error: {captured_data['error']}"
                ))
        except OSError as e:
            if "address already in use" in str(e).lower():
                self.parent.after(0, lambda: messagebox.showerror(
                    "Error",
                    "El puerto 25566 ya está en uso.\n\n"
                    "Cierra otras instancias del launcher e intenta nuevamente."
                ))
            else:
                self.parent.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"No se pudo iniciar el servidor local:\n{str(e)}"
                ))
            self.parent.after(0, status_window.destroy)
        except Exception as e:
            self.parent.after(0, lambda: messagebox.showerror(
                "Error",
                f"Error inesperado:\n{str(e)}"
            ))
            self.parent.after(0, status_window.destroy)

    def _complete_login(self, auth_url, state, code_verifier, on_success_callback):
        try:
            auth_code = mll.microsoft_account.parse_auth_code_url(auth_url, state)
            
            account_info = mll.microsoft_account.complete_login(
                self.client_id,
                None,  
                self.redirect_uri,
                auth_code,
                code_verifier
            )
            
            if "refresh_token" in account_info:
                print(f"✓ Refresh token obtenido y guardado")
                save_config(
                    refresh_token=account_info["refresh_token"],
                    ms_account=True
                )
            else:
                print("⚠ No se recibió refresh token en la respuesta")
            
            self.parent.after(0, lambda: on_success_callback(account_info))
            
        except mll.exceptions.AzureAppNotPermitted:
            self._show_app_not_permitted_error()
        except mll.exceptions.InvalidRefreshToken:
            self._show_invalid_token_error()
        except mll.exceptions.AccountNotOwnMinecraft:
            self._show_no_license_error()
        except KeyError as e:
            self._show_key_error(e)
        except Exception as e:
            self._show_generic_error(e)

    def refresh_token(self, refresh_token, timeout=5):
        try:            
            account_info = mll.microsoft_account.complete_refresh(
                self.client_id,
                None, 
                self.redirect_uri,
                refresh_token
            )
            
            if "refresh_token" in account_info:
                save_config(
                    refresh_token=account_info["refresh_token"],
                    ms_account=True
                )
            else:
                account_info["refresh_token"] = refresh_token
                
            return account_info
            
        except mll.exceptions.InvalidRefreshToken as e:
            print(f"❌ Refresh token inválido o expirado: {e}")
            save_config(refresh_token=None, ms_account=False)
            return None
        except mll.exceptions.AzureAppNotPermitted as e:
            print(f"❌ Aplicación de Azure sin permisos: {e}")
            save_config(refresh_token=None, ms_account=False)
            return None
        except Exception as e:
            print(f"❌ Error refrescando token: {e}")
            import traceback
            traceback.print_exc()
            save_config(refresh_token=None, ms_account=False)
            return None

    def _show_app_not_permitted_error(self):
        self.parent.after(0, lambda: messagebox.showwarning(
            "Aplicación pendiente de aprobación",
            "Tu aplicación de Azure aún no ha sido aprobada por Microsoft.\n\n"
            "Este proceso puede tardar varios días.\n\n"
            "Recibirás un correo cuando sea aprobada.\n"
            "Mientras tanto, puedes jugar en modo offline."
        ))

    def _show_invalid_token_error(self):
        self.parent.after(0, lambda: messagebox.showerror(
            "Sesión expirada",
            "Tu sesión ha expirado. Por favor, inicia sesión nuevamente."
        ))

    def _show_no_license_error(self):
        self.parent.after(0, lambda: messagebox.showerror(
            "Sin licencia de Minecraft",
            "Esta cuenta de Microsoft no tiene una licencia de Minecraft.\n\n"
            "Por favor, compra Minecraft o usa una cuenta diferente."
        ))

    def _show_key_error(self, e):
        self.parent.after(0, lambda: messagebox.showerror(
            "Error de autenticación",
            f"La respuesta del servidor no contiene el campo esperado: {str(e)}\n\n"
            "Esto puede ocurrir si:\n"
            "1. La aplicación de Azure no está configurada correctamente\n"
            "2. Faltan permisos en la aplicación de Azure\n"
            "3. El redirect URI no coincide exactamente\n\n"
            "Verifica la configuración en el portal de Azure."
        ))

    def _show_generic_error(self, e):
        import traceback
        error_msg = str(e)
        trace = traceback.format_exc()
        
        if "permission" in error_msg.lower() or "not permitted" in error_msg.lower():
            self._show_app_not_permitted_error()
        else:
            self.parent.after(0, lambda: messagebox.showerror(
                "Error de autenticación",
                f"No se pudo completar el inicio de sesión:\n\n{error_msg}\n\n"
                f"Detalles técnicos:\n{trace[:200]}"
            ))

    def _get_success_html(self):
        return """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="utf-8">
            <title>¡Éxito!</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #FF55FF 0%, #55FFFF 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 400px;
                }
                h1 {
                    color: #FF55FF;
                    margin: 0 0 20px 0;
                }
                p {
                    color: #666;
                    font-size: 16px;
                }
                .emoji {
                    font-size: 64px;
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="emoji">✅</div>
                <h1>¡Inicio de sesión exitoso!</h1>
                <p>Ya puedes cerrar esta ventana y volver al launcher.</p>
                <p>Tu sesión se ha configurado correctamente.</p>
            </div>
            <script>
                setTimeout(function() {
                    window.close();
                }, 3000);
            </script>
        </body>
        </html>
        """

    def _get_error_html(self):
        return """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="utf-8">
            <title>Error</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    background: #f44336;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 400px;
                }
                h1 {
                    color: #f44336;
                    margin: 0 0 20px 0;
                }
                p {
                    color: #666;
                    font-size: 16px;
                }
                .emoji {
                    font-size: 64px;
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="emoji">❌</div>
                <h1>Error de autenticación</h1>
                <p>Puedes cerrar esta ventana e intentar nuevamente.</p>
            </div>
        </body>
        </html>
        """