from app.ui.main import Launcher
from app.services.discord_rpc import DiscordRPC
from app.services.config import save_config
from app.services.updater import CURRENT_VERSION
from app.utils.bootstrap import ensure_running_from_appdata

ensure_running_from_appdata()
save_config(launcher_version=CURRENT_VERSION)

discord_rpc = DiscordRPC()

def onPlay():
    pass

if __name__ == "__main__":
    Launcher(onPlay).mainloop()