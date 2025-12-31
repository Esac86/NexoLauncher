import os
import sys

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

from app.ui import Launcher
from app.services.onPlay import onPlay

def main():
    Launcher(onPlay).mainloop()
    
if __name__ == "__main__":
    main()