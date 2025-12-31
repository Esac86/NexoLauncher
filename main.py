from app.ui.launcher_ui import Launcher
from app.services.minecraft import PlayService

def onPlay(username, version):
    pass

if __name__ == "__main__":
    Launcher(onPlay).mainloop()
