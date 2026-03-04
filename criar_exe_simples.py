print("=== CRIADOR DE APLICACAO WINDOWS ===")
import os
os.system("pip install pyinstaller")
os.system('pyinstaller --onefile --windowed --name "UsinaBettoMix" main.py')
print("✅ Pronto! Verifique a pasta 'dist'")
input("Pressione Enter...")
