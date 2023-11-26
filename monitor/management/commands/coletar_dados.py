import csv
from django.core.management.base import BaseCommand
from ...controllers import coletar_dados_conexao, construir_controllers
from ...utils import ignore_keys
from ...model import ARQUIVO_CSV

class Command(BaseCommand):
    help = "Este comando serve para manter em treino constante o modelo de previsão de internet."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controllers = construir_controllers()

    def handle(self, *args, **options):
        while True:
            self.coletar_dados_csv()

    def coletar_dados_csv(self):
        cabecalho = ['forca_sinal', 'velocidade_download', 'velocidade_upload', 'jitter', 'latencia', 'perda']
        dados = coletar_dados_conexao(*self.controllers)
        print(f'\n{dados}')
        valores_vazios = any(map(lambda item: item == '', dados.values()))
        if valores_vazios:
            self.stdout.write(self.style.ERROR("Problema ao coletar dados (Conexão Instável)"))
            return
        with open(ARQUIVO_CSV, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=cabecalho)
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(ignore_keys(dados, ['canal']))
        self.stdout.write(self.style.SUCCESS("Dados coletados com sucesso."))