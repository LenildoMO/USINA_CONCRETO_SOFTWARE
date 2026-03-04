from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Betto Mix Web - SISTEMA FUNCIONANDO!</h1><p>Acesse: <a href=\
/dashboard\>Dashboard</a></p>'

@app.route('/dashboard')
def dashboard():
    return '<h1>Dashboard</h1><p>Sistema em operação!</p>'

if __name__ == '__main__':
    print('Sistema iniciado! Acesse: http://localhost:5000')
    app.run(debug=True, port=5000)
