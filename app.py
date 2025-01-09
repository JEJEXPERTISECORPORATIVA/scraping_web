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
    # Aqui, retornamos um identificador fixo (pode ser alterado conforme necessário)
    return "DESKTOP-TR3IHL0"  # Ajuste conforme o identificador correto da máquina

# Função para verificar login bem-sucedido no arquivo login.log
def validar_login():
    log_file = "login.log"
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            linhas = file.readlines()
            for linha in linhas:
                if "Login bem-sucedido" in linha:
                    # Parse do timestamp completo (data + hora)
                    timestamp_str = linha.split(' - ')[0]
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')

                    # Verifica se a data do log é igual à data de hoje
                    data_atual = datetime.now().date()  # Apenas a data (ano-mês-dia)
                    if timestamp.date() == data_atual:  # Comparar apenas a data
                        uuid_log = linha.split('UUID: ')[1].strip()

                        # Log de depuração para ver o UUID
                        print(f"UUID do log: {uuid_log}")

                        # Obtém o UUID da máquina real
                        uuid_maquina = obter_uuid_maquina()

                        # Log de depuração para ver o UUID da máquina
                        print(f"UUID da máquina: {uuid_maquina}")

                        # Verifica se o UUID da máquina bate com o do log
                        if uuid_maquina == uuid_log:
                            # Adiciona a linha no log conforme solicitado
                            logging.info(f"Login bem-sucedido: Data: {data_atual}, UUID da máquina: {uuid_maquina}, UUID do log: {uuid_log}")
                            return True
                        else:
                            # Log de falha no arquivo com detalhamento e UUID
                            logging.warning(f"Falha no login: Data: {data_atual}, UUID da máquina: {uuid_maquina}, UUID do log: {uuid_log}. UUID da máquina não corresponde ao UUID do log.")
                            return False
                    else:
                        # Log de falha no arquivo com detalhamento e UUID
                        logging.warning(f"Falha no login: Data: {data_atual}, UUID da máquina: {obter_uuid_maquina()}. A data do log não corresponde à data atual.")
                        return False
    else:
        logging.error("Arquivo login.log não encontrado.")
    return False

# Rota principal para a página inicial
@app.route('/')
def index():
    if not validar_login():
        # Log detalhado para falha de acesso
        uuid_maquina = obter_uuid_maquina()
        logging.warning(f"Falha de acesso: Data: {datetime.now().date()}, UUID da máquina: {uuid_maquina}. Acesso não autorizado.")
        return "Acesso não autorizado. Login necessário.", 403

    dias_restantes = verificar_tempo_de_uso()
    return render_template('index.html', dias_restantes=dias_restantes)

# Rota para iniciar o scraping e download dos arquivos
@app.route('/iniciar_scraping')
def iniciar_scraping():
    if not validar_login():
        # Log detalhado para falha de acesso
        uuid_maquina = obter_uuid_maquina()
        logging.warning(f"Falha de acesso: Data: {datetime.now().date()}, UUID da máquina: {uuid_maquina}. Acesso não autorizado.")
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
        # Log detalhado para falha de acesso
        uuid_maquina = obter_uuid_maquina()
        logging.warning(f"Falha de acesso: Data: {datetime.now().date()}, UUID da máquina: {uuid_maquina}. Acesso não autorizado.")
        return "Acesso não autorizado. Login necessário.", 403

    if arquivo_tipo == "excel":
        return send_from_directory(directory='data/EXCEL', filename=os.path.basename(caminho_excel), as_attachment=True)
    elif arquivo_tipo == "csv":
        return send_from_directory(directory='data/CSV', filename=os.path.basename(caminho_csv), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
