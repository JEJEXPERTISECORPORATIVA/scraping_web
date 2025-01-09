import uuid
from flask import Flask, render_template, send_from_directory
import os
from datetime import datetime
import logging
from scraping import capturar_dados_google_maps, verificar_tempo_de_uso, configurar_driver

# Configuração do Flask
app = Flask(__name__)

# Configuração de logging
logging.basicConfig(filename='login.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

# Função para pegar o UUID da máquina (no formato desejado)
def obter_uuid_maquina():
    return "DESKTOP-TR3IHL0"  # Ajuste conforme o identificador correto da máquina

# Função para verificar login bem-sucedido no arquivo login.log
def validar_login():
    log_file = "login.log"
    uuid_maquina = obter_uuid_maquina()
    data_hoje = datetime.now().strftime('%Y-%m-%d')
    ultima_linha_valida = None

    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            linhas = file.readlines()

        # Verifica todas as linhas e encontra a mais recente com "Login bem-sucedido"
        for linha in linhas:
            if "Login bem-sucedido" in linha:
                # Parse do timestamp e UUID na linha
                try:
                    timestamp_str = linha.split(' - ')[0]
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                    uuid_log = linha.split('UUID do log: ')[1].strip()
                except (IndexError, ValueError):
                    continue  # Pula linhas que não seguem o formato esperado

                # Atualiza a última linha válida se a data bater
                if timestamp.strftime('%Y-%m-%d') == data_hoje and uuid_log == uuid_maquina:
                    ultima_linha_valida = linha

        if ultima_linha_valida:
            # Adiciona log de sucesso
            logging.info(f"Login bem-sucedido: Data: {data_hoje}, UUID da máquina: {uuid_maquina}, UUID do log: {uuid_maquina}")
            return True
        else:
            # Caso nenhuma linha válida seja encontrada, loga a falha com detalhes
            logging.warning(f"Falha no login: Data: {data_hoje}, UUID da máquina: {uuid_maquina}. Nenhum login válido encontrado no log.")
    else:
        logging.error(f"Arquivo {log_file} não encontrado.")

    return False

# Rota principal para a página inicial
@app.route('/')
def index():
    if not validar_login():
        return "Acesso não autorizado. Login necessário.", 403

    dias_restantes = verificar_tempo_de_uso()
    return render_template('index.html', dias_restantes=dias_restantes)

# Rota para iniciar o scraping e download dos arquivos
@app.route('/iniciar_scraping')
def iniciar_scraping():
    if not validar_login():
        return "Acesso não autorizado. Login necessário.", 403

    try:
        driver = configurar_driver()
        driver.get("https://www.google.com/maps")
        caminho_excel, caminho_csv = capturar_dados_google_maps(driver)

        # Enviar os arquivos para download
        return render_template('download.html', caminho_excel=caminho_excel, caminho_csv=caminho_csv)
    except Exception as e:
        return f"Ocorreu um erro: {e}"

# Rota para download dos arquivos
@app.route('/download/<arquivo_tipo>')
def download(arquivo_tipo):
    if not validar_login():
        return "Acesso não autorizado. Login necessário.", 403

    if arquivo_tipo == "excel":
        return send_from_directory(directory='data/EXCEL', filename=os.path.basename(caminho_excel), as_attachment=True)
    elif arquivo_tipo == "csv":
        return send_from_directory(directory='data/CSV', filename=os.path.basename(caminho_csv), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
