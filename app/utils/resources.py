import sys, os
def resource_path(p):
    return os.path.join(
        getattr(sys, "_MEIPASS", os.getcwd()),
        p
    )