from flask import Flask, render_template, session
import os
from datetime import datetime
import logging
from scraping import capturar_dados_google_maps, verificar_tempo_de_uso, configurar_driver

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

logging.basicConfig(filename='login.log', level=logging.INFO, format='%(asctime)s - %(message)s')

@app.route('/')
def index():
    if not session.get('authenticated'):
        return "Acesso não autorizado. Faça login.", 403

    dias_restantes = verificar_tempo_de_uso()
    return render_template('index.html', dias_restantes=dias_restantes)

@app.route('/iniciar_scraping')
def iniciar_scraping():
    if not session.get('authenticated'):
        return "Acesso não autorizado. Faça login.", 403

    try:
        driver = configurar_driver()
        driver.get("https://www.google.com/maps")
        caminho_excel, caminho_csv = capturar_dados_google_maps(driver)
        return render_template('download.html', caminho_excel=caminho_excel, caminho_csv=caminho_csv)
    except Exception as e:
        return f"Ocorreu um erro: {e}"

if __name__ == '__main__':
    app.run(debug=True, port=5002)
