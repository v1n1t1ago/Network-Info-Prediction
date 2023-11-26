
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import csv
import subprocess
import time
import speedtest
import pandas as pd 
import pywifi
from . import constants
from .controllers import PingController



def collect_data_1():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    download_speed, upload_speed=get_bandwidth()

    ping_controller = PingController(5)
    latencia = ping_controller.calcular_latencia_media()
    perda_de_pacotes = ping_controller.calcular_perda_de_pacotes()

    intensidade_do_sinal=get_signal_strength(iface)
    jitter=get_jitter()
    
    return {
        'upload_speed': upload_speed,
        'download_speed': download_speed, 
        'perda_de_pacotes': perda_de_pacotes,
        'latencia': latencia,
        'intensidade_do_sinal': intensidade_do_sinal,
        'jitter': jitter
    }

def save_data_to_csv(data, csv_file_path='data.csv'):
    data=collect_data_1()
    with open(csv_file_path, 'a', newline='') as file:
        fieldnames = ['upload_speed', 'download_speed', 'perda_de_pacotes', 'latencia', 'intensidade_do_sinal','jitter']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Se o arquivo estiver vazio, escreva o cabeçalho
        if file.tell() == 0:
            writer.writeheader()

        # Escreve os dados no arquivo
        writer.writerow({
            'upload_speed': data['upload_speed'],
            'download_speed': data['download_speed'],
            'perda_de_pacotes': data['perda_de_pacotes'],
            'latencia': data['latencia'],
            'intensidade_do_sinal': data['intensidade_do_sinal'],
            'jitter': data['jitter']
        })

def collect_and_save_data_continuously():
    while True:
        data = collect_data_1()
        save_data_to_csv(data)
        time.sleep(1)

def train_and_predict_multi_output(wait_for_data=True, max_wait_time=30):
    start_time = time.time()
    
    # Espera por dados por 5 segundos
    while wait_for_data and time.time() - start_time < max_wait_time:
        try:
            # Tente ler os dados do arquivo CSV
            df = pd.read_csv('data.csv')
            if not df.empty:
                break
            else:
                print("Arquivo CSV vazio. Aguardando dados...")
        except Exception as e:
            print(f"Erro ao ler o arquivo CSV: {str(e)}")
        
        time.sleep(1)
    
    # Se ainda estiver vazio após a espera, imprima uma mensagem
    if df.empty:
        print("Tempo limite atingido. Não há dados disponíveis.")
        return None, None

    # Carrega os dados do dataframe
    X_data = df[['upload_speed', 'download_speed', 'perda_de_pacotes', 'latencia', 'intensidade_do_sinal','jitter']]
    y_download = df['download_speed']
    y_upload = df['upload_speed']
    
    # Combina as saídas em uma única matriz para usar como saída y
    y_data = pd.concat([y_download, y_upload], axis=1)

    # Dividindo os dados em conjunto de treinamento e teste
    X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.2, random_state=42)

    # Criando o modelo de regressão linear múltipla
    model = LinearRegression()

    # Treinando o modelo com os dados de treinamento
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    # Dividindo as previsões em download e upload
    predictions_download = y_pred[:, 0]
    predictions_upload = y_pred[:, 1]

    return predictions_download, predictions_upload, y_test
