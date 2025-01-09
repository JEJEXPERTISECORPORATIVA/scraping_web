import logging
from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import socket

# Configuração do Flask
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Configuração do log
logging.basicConfig(filename='login.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Função para pegar o UUID da máquina local
def obter_uuid_maquina():
    return socket.gethostname()

# Função para carregar dados de login da planilha
def carregar_dados_login():
    caminho_planilha = 'dados_login.xlsx'  # Substitua pelo caminho correto
    dados = pd.read_excel(caminho_planilha)
    if 'Usuario_Coluna' in dados.columns:
        dados.rename(columns={'Usuario_Coluna': 'Usuario', 'Senha_Coluna': 'Senha', 'UUID_Coluna': 'UUID'}, inplace=True)
    return dados

# Rota para a página de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        machine_uuid = obter_uuid_maquina()

        # Carregar dados de login da planilha
        dados_login = carregar_dados_login()

        # Verifique as credenciais (usuário, senha e UUID)
        usuario_valido = dados_login['Usuario'] == username
        senha_valida = dados_login['Senha'] == password
        uuid_valido = dados_login['UUID'] == machine_uuid

        # Verifica se pelo menos uma linha das condições foi atendida
        if (usuario_valido & senha_valida & uuid_valido).any():  # Se qualquer linha for válida
            logging.info(f'Login bem-sucedido: Usuário: {username}, UUID: {machine_uuid}')
            return redirect('http://127.0.0.1:5002')  # Redireciona para o servidor Flask na porta 5000
        else:
            logging.warning(f'Falha no login: Usuário: {username}, UUID: {machine_uuid} - Credenciais inválidas')
            error_message = f"UUID: {machine_uuid} - Credenciais inválidas"
            return render_template('login.html', error=error_message)

    return render_template('login.html')

# Rota para a página principal
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Roda o Flask na porta 5001
