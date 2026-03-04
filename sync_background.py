import os
import time
import shutil

source = r"C:\Users\Micro\Documents\usina_concreto_software"
target = r"C:\Users\Micro\OneDrive\usina_concreto_software"

# Roda silenciosamente
while True:
    try:
        for root, dirs, files in os.walk(source):
            if '.venv' in root or '__pycache__' in root:
                continue
            for file in files:
                if '.pyc' in file:
                    continue
                src = os.path.join(root, file)
                dst = os.path.join(target, os.path.relpath(src, source))
                if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
        time.sleep(3)
    except:
        time.sleep(10)
