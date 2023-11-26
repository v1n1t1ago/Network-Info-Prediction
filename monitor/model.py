import pandas as pd
from django.conf import settings
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from . import constants


ARQUIVO_CSV = settings.BASE_DIR / 'training' / f'data_{constants.INTERFACE_GUID}.csv'

class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class TrainedModel(metaclass=SingletonMeta):

    def __init__(self, arquivo=ARQUIVO_CSV):
        self.arquivo = arquivo
        self.treinado = False
        self.cruzamento_matrizes = None
        self.modelo = LinearRegression()
        self.treinar()

    def __carregar_dados(self):
        data_frame = pd.read_csv(self.arquivo)
        x_data = data_frame[
            [
                'velocidade_upload', 
                'velocidade_download', 
                'perda', 
                'latencia', 
                'forca_sinal',
                'jitter'
            ]
        ]
        y_download = data_frame['velocidade_download']
        y_upload = data_frame['velocidade_upload']
        y_data = pd.concat([y_download, y_upload], axis=1)
        return x_data, y_data

    def treinar(self):
        x_data, y_data = self.__carregar_dados()
        x_train, x_test, y_train, _ = train_test_split(
            x_data, y_data, test_size=0.2, random_state=42
        )
        self.cruzamento_matrizes = x_test
        self.modelo.fit(x_train, y_train)
        self.treinado = True
    
    def prever(self):
        if not self.treinado:
            return (0, 0)
        previsoes = self.modelo.predict(self.cruzamento_matrizes)
        previsao_download = previsoes[:, 0]
        previsao_upload = previsoes[:, 1]
        return previsao_download, previsao_upload 

