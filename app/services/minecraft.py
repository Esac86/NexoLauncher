import os
import subprocess
import threading
import minecraft_launcher_lib as mll
from app.utils.paths import MC_DIR

class PlayService:
    def __init__(self, on_play_callback, on_state_change):
        self.on_play_callback = on_play_callback
        self.on_state_change = on_state_change
        self.is_running = False

    def launch(self, username, version):
        if self.is_running:
            return
        if not username:
            self.on_state_change("error", "Usuario requerido")
            return
        self.is_running = True
        threading.Thread(target=self._run, args=(username, version), daemon=True).start()

    def _first_run_setup(self):
        options_path = os.path.join(MC_DIR, "options.txt")
        if os.path.exists(options_path):
            return
        with open(options_path, "w", encoding="utf-8") as f:
            f.write(
                "lang:es_mx\n"
                "narrator:0\n"
                "tutorialStep:none\n"
                "onboardAccessibility:false\n"
            )

    def _run(self, username, version):
        try:
            self.on_state_change("installing")
            path_version = os.path.join(MC_DIR, "versions", version)
            if not os.path.exists(path_version):
                mll.install.install_minecraft_version(version, MC_DIR)
            self._first_run_setup()
            self.on_state_change("playing")
            options = {
                "username": username,
                "uuid": "",
                "token": "",
                "jvmArguments": ["-Xmx2G"]
            }
            cmd = mll.command.get_minecraft_command(version, MC_DIR, options)
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            subprocess.run(cmd, cwd=MC_DIR, creationflags=creationflags)
            self.on_state_change("ready")
        except Exception as e:
            self.on_state_change("error", str(e))
        finally:
            self.is_running = False
