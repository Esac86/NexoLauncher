import os
import subprocess
import tkinter.messagebox as mb
import minecraft_launcher_lib
from app.utils.paths import MC_DIR


def onPlay(user, version, callback_update):
    try:
        path_version = os.path.join(MC_DIR, "versions", version)

        if not os.path.exists(path_version):
            callback_update("installing")
            minecraft_launcher_lib.install.install_minecraft_version(
                version, MC_DIR
            )

        callback_update("playing")

        options = {
            "username": user,
            "uuid": "",
            "token": "",
            "jvmArguments": ["-Xmx2G"],
        }

        cmd = minecraft_launcher_lib.command.get_minecraft_command(
            version, MC_DIR, options
        )

        subprocess.run(cmd, cwd=MC_DIR)
        callback_update("ready")

    except Exception as e:
        mb.showerror("Error", str(e))
        callback_update("ready")
