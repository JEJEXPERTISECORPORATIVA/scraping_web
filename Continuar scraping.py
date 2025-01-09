from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time

def procurar_aba_ativa():
    # Configuração do WebDriver para o Edge
    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
    driver.maximize_window()

    # Abrir o Google Maps em uma nova aba
    driver.get("https://www.google.com.br/maps")
    time.sleep(3)  # Espera o carregamento da página

    # Obter todas as abas abertas
    abas = driver.window_handles
    aba_encontrada = False

    # Procurar por uma aba que tenha "google.com.br/maps" no URL
    for aba in abas:
        driver.switch_to.window(aba)
        current_url = driver.current_url
        print(f"Aba atual URL: {current_url}")

        if "google.com.br/maps" in current_url:
            aba_encontrada = True
            break  # Encontrou a aba, podemos parar a busca

    if aba_encontrada:
        print("Aba com o Google Maps encontrada e ativada!")
    else:
        print("Nenhuma aba com o Google Maps foi encontrada.")

    # Manter a aba ativa por 5 segundos para demonstração
    time.sleep(5)

    driver.quit()

if __name__ == "__main__":
    procurar_aba_ativa()
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
from threading import Thread

app = Flask(__name__)

def executar_scraping():
    # Configuração do WebDriver para o Edge
    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
    driver.maximize_window()

    # Abrir o Google Maps em uma nova aba
    driver.get("https://www.google.com.br/maps")
    time.sleep(3)  # Espera o carregamento da página

    # Obter todas as abas abertas
    abas = driver.window_handles
    aba_encontrada = False

    # Procurar por uma aba que tenha "google.com.br/maps" no URL
    for aba in abas:
        driver.switch_to.window(aba)
        current_url = driver.current_url
        print(f"Aba atual URL: {current_url}")

        if "google.com.br/maps" in current_url:
            aba_encontrada = True
            break  # Encontrou a aba, podemos parar a busca

    if aba_encontrada:
        print("Aba com o Google Maps encontrada e ativada!")
    else:
        print("Nenhuma aba com o Google Maps foi encontrada.")

    # Manter a aba ativa por 5 segundos para demonstração
    time.sleep(5)

    driver.quit()

@app.route('/continuar_scraping', methods=['POST'])
def continuar_scraping():
    # Executar o scraping em uma thread separada para não bloquear o servidor
    thread = Thread(target=executar_scraping)
    thread.start()

    return jsonify({"status": "Scraping iniciado com sucesso!"}), 200

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
