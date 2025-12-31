import os

MC_DIR = os.path.abspath(os.path.join(os.getcwd(), ".minecraft"))
os.makedirs(MC_DIR, exist_ok=True)