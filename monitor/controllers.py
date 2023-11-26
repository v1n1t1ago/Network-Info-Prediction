import re, subprocess, statistics, time, asyncio
from ping3 import ping
from speedtest import Speedtest
from . import constants
from abc import ABC, abstractclassmethod

class AsynchronousDataController(ABC):

    @abstractclassmethod
    async def get_data_async(self):
        pass
    
    def get_data(self):
        loop = asyncio.get_event_loop()
        resultado = loop.run_until_complete(self.get_data_async())
        return resultado
    
class ConnectionController(AsynchronousDataController):

    def __init__(self, interface):
        self.interface = interface

    async def get_forca_sinal(self):
        scan_results = self.interface.scan_results()
        if scan_results:
            return scan_results[0].signal
        return ''
    
    async def get_largura_banda(self):
        test = Speedtest()
        async def testar_download():
            return test.download()

        async def testar_upload():
            return test.upload()
        
        velocidade_download = await testar_download()
        velocidade_upload = await testar_upload() 
        return velocidade_download, velocidade_upload

    async def get_jitter(self):
        previous_time = time.time()
        for _ in range(5):
            await asyncio.sleep(1)
            jitter = await self.calculate_jitter(previous_time)
            if jitter is not None:
                return jitter 
            previous_time = time.time()
        return ''

    async def calculate_jitter(self, previous_time):
        current_time = time.time()
        if previous_time is not None:
            jitter = current_time - previous_time
            return jitter
        return None

    async def get_canal_wifi(self):
        try:
            resultado_str = subprocess.check_output(["netsh", "wlan", "show", "interface"],encoding='latin1')
            padrao_canal = re.compile(r"Canal\s*:\s*(\d+)", re.IGNORECASE)
            correspondencias_canal = padrao_canal.search(resultado_str)
            if correspondencias_canal:
                return int(correspondencias_canal.group(1))
        except Exception: 
            pass
        return ''

    async def get_data_async(self):
        forca_sinal = await self.get_forca_sinal()
        velocidade_download, velocidade_upload = await self.get_largura_banda()
        jitter = await self.get_jitter()
        canal = await self.get_canal_wifi()
        return {
            "forca_sinal": forca_sinal,
            "velocidade_download": velocidade_download,
            "velocidade_upload": velocidade_upload, 
            "jitter": jitter,
            "canal": canal,
        }

class PingHostController(AsynchronousDataController):

    def __init__(self, numero_de_pings, host=constants.HOSTGATOR):
        self.numero_de_pings = numero_de_pings
        self.host = host

    async def get_latencia_ms(self, host):
        latencia_ms = ping(host, unit='ms')
        return latencia_ms

    async def calcular_latencia_media(self):
        try:
            latencias = []
            for _ in range(self.numero_de_pings):
                latencia_ms = await self.get_latencia_ms(self.host)
                latencias.append(latencia_ms) 
            return statistics.mean(latencias)
        except Exception:
            pass
        return ''
        
    async def calcular_perda_de_pacotes(self):
        try:
            padrao = r'Perdidos.*(\d+(\.\d+)?)%'
            process = subprocess.Popen(['ping','-n', f'{self.numero_de_pings}', self.host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, _ = process.communicate()
            perdas = []
            perda_media = None
            for fragmento in stdout.decode('latin-1').split('\n'):
                dados_perda = re.search(padrao, fragmento)
                if dados_perda:
                    perdas.append(float(re.search("(\d+(\.\d+)?)%", dados_perda.string).group(1)))
            if perdas:
                perda_media = statistics.mean(perdas)
            return perda_media
        except Exception:
            pass
        return ''
    
    async def get_data_async(self):
        latencia = await self.calcular_latencia_media()
        perda = await self.calcular_perda_de_pacotes()
        return {"latencia": latencia, "perda": perda}


def construir_controllers():
    ping_controller = PingHostController(3)
    interface = constants.INTERFACE_PADRAO 
    connection_controller = ConnectionController(interface=interface)
    return ping_controller, connection_controller


def coletar_dados_conexao(ping_controller, connection_controller):
    async def coleta_async():
        return {
            **await ping_controller.get_data_async(),
            **await connection_controller.get_data_async(),
        }
    return asyncio.run(coleta_async())

if __name__ == "__main__":
    # python -m monitor.controllers
    dados = coletar_dados_conexao(*construir_controllers())
    print(dados)