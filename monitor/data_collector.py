# monitor/train_model.py Esse modelo ainda vai sofrer alterações como retirar funções que não retornam os dados que são necessários,anexar novas funções que retornem mais dados necessários e etc
import pywifi
import subprocess
import re
import speedtest


#Função para obter a força do sinal

def get_signal_strength(interface):
    scan_results = interface.scan_results()

    if scan_results:
        signal_strength = scan_results[0].signal
        return signal_strength
    else:
        return None


#Função para obter a interface wifi e posteriormente chamar na função para obter a frequência


def get_wifi_interface():
    try:
        # No Windows
        resultado = subprocess.check_output(["netsh", "wlan", "show", "interfaces"])

        # Decodifique a saída para string usando 'latin-1'
        resultado_str = resultado.decode("latin-1")

        # Use expressões regulares para extrair o nome da interface Wi-Fi
        padroes_interface = [
            re.compile(r"Nome da Interface\s*:\s*(.+)", re.IGNORECASE),
            re.compile(r"Interface Name\s*:\s*(.+)", re.IGNORECASE),
            re.compile(r"Nome\s*:\s*(.+)", re.IGNORECASE),
            # Adicione mais padrões conforme necessário
        ]

        for padrao_interface in padroes_interface:
            correspondencias = padrao_interface.search(resultado_str)
            if correspondencias:
                # Retorna o nome da interface Wi-Fi
                return correspondencias.group(1).strip()

        # Se nenhum padrão corresponder, imprima a saída completa e retorne None
        print(f"Padrão de interface não encontrado. Saída completa:\n{resultado_str}")
        return None

    except Exception as e:
        return f"Erro ao obter informações de interfaces Wi-Fi: {str(e)}"



#Função que retorna o canal wifi
def get_wifi_channel():
    try:
        # Executa o comando netsh wlan show interface
        resultado_str = subprocess.check_output(["netsh", "wlan", "show", "interface"],encoding='latin1')

        # Decodifica a saída para string
        
        # Utiliza expressões regulares para extrair o canal
        padrao_canal = re.compile(r"Canal\s*:\s*(\d+)", re.IGNORECASE)
        correspondencias_canal = padrao_canal.search(resultado_str)

        if correspondencias_canal:
            # Retorna o canal como número inteiro
            canal = int(correspondencias_canal.group(1))
            return canal
        else:
            print("Canal não encontrado na saída do comando.")
            return None

    except Exception as e:
        print(f"Erro ao obter informações de canal: {str(e)}")
        return None


    
#Função para pegar a frequência do wifi


def get_wifi_frequency():
    canal=get_wifi_channel()
    if 1 <= canal <= 14:
        # Fórmula para a faixa de 2.4 GHz
        frequencia = 2.412 + (canal - 1) * 0.005
        return frequencia
    elif 36 <= canal <= 165:
        # Fórmula para a faixa de 5 GHz
        frequencia = 5.18 + 0.006 * (canal - 36)
        return frequencia
    else:
        return None


    
def collect_data():
       # Mede a potência do sinal Wi-Fi usando a biblioteca pywifi
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    signal_strength= get_signal_strength(iface)
    frequency=get_wifi_frequency()

    # Mede a velocidade de upload e download usando a biblioteca psutil
    channel = get_wifi_channel()
    st=speedtest.Speedtest()
    upload_speed = st.upload()
    download_speed = st.download()
        
    return {
        'upload_speed': upload_speed,
        'download_speed': download_speed,
        'signal_strength': signal_strength,
        'frequency': frequency,
        'channel': channel,
    }

