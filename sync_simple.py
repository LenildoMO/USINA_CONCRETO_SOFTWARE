import os
import time
import shutil
import sys

source = r"C:\Users\Micro\Documents\usina_concreto_software"
target = r"C:\Users\Micro\OneDrive\usina_concreto_software"

print("Sincronização automática ativa!")
print(f"Origem: {source}")
print(f"Destino: {target}")

while True:
    try:
        # Percorre todos os arquivos
        for root, dirs, files in os.walk(source):
            # Ignora .venv e __pycache__
            if '.venv' in root or '__pycache__' in root:
                continue
            
            for file in files:
                # Ignora arquivos temporários
                if file.endswith('.pyc'):
                    continue
                
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, source)
                dst_path = os.path.join(target, rel_path)
                
                # Verifica se precisa copiar
                if not os.path.exists(dst_path):
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                    print(f"[NOVO] {rel_path}")
                else:
                    # Compara datas de modificação
                    src_time = os.path.getmtime(src_path)
                    dst_time = os.path.getmtime(dst_path)
                    
                    if src_time > dst_time:
                        shutil.copy2(src_path, dst_path)
                        print(f"[ATUALIZADO] {rel_path}")
        
        # Aguarda 2 segundos
        time.sleep(2)
        
    except KeyboardInterrupt:
        print("\nSincronização interrompida.")
        break
    except Exception as e:
        print(f"Erro: {e}")
        time.sleep(5)
