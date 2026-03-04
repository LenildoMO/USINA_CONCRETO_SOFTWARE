import os
print("Criando sistema Betto Mix Web...")
os.makedirs("BettoWeb", exist_ok=True)
os.chdir("BettoWeb")

app_code = '''
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Betto Mix Web</h1><p>Sistema funcionando!</p>"

@app.route("/dashboard")
def dashboard():
    return "<h1>Dashboard</h1><p>150 Clientes</p><p>42 Pesagens hoje</p>"

if __name__ == "__main__":
    print("Acesse: http://localhost:5000")
    app.run(debug=True, port=5000)
'''

with open("app.py", "w") as f:
    f.write(app_code)

import subprocess
subprocess.run(["pip", "install", "flask"])

print("Sistema criado!")
print("Execute: python app.py")
print("Acesse: http://localhost:5000")
