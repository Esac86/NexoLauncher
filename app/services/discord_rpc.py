import threading
import time

CLIENT_ID = "1456139803211993176"

class DiscordRPC:
    def __init__(self):
        self.rpc = None
        self._running = False
        self._thread = None
        self._start_rpc()

    def _start_rpc(self):
        if self._thread is None or not self._thread.is_alive():
            self._running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def _run(self):
        try:
            from pypresence import Presence
            self.rpc = Presence(CLIENT_ID)
            self.rpc.connect()
            self.update_status("Jugando a Nexo Abierto Launcher", "Abierto")
            
            while self._running:
                time.sleep(30)  
        except Exception as e:
            print("Discord no disponible:", e)
            self.rpc = None

    def update_status(self, details: str, state: str):
        if self.rpc:
            try:
                self.rpc.update(
                    details=details,
                    state=state,
                    large_image="logo",
                    start=int(time.time())
                )
            except Exception:
                pass

    def close(self):
        self._running = False
        if self.rpc:
            try:
                self.rpc.close()
            except Exception:
                pass
            self.rpc = None