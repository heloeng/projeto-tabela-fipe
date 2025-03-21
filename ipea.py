import ipeadatapy as ipea
import pandas as pd
from datetime import datetime

def calcular_precos_ao_longo_tempo(preco_final, mes_inicio, ano_inicio, mes_fim, ano_fim):
    """
    Calcula o preço do carro ao longo do tempo entre as duas datas, aplicando as taxas de inflação mensais ao contrário.
    :param preco_final: Preço do carro na data final (float)
    :param mes_inicio: Mês da data inicial (int)
    :param ano_inicio: Ano da data inicial (int)
    :param mes_fim: Mês da data final (int)
    :param ano_fim: Ano da data final (int)
    :return: Data e preço do carro ao longo do tempo
    """
    
    mes_fim=2
    ano_fim = 2025
    # Código da série para o IPCA (Inflação)
    codigo_serie = 'BM12_IPCAEXP1212'
    
    # Buscar todos os dados da série
    df = ipea.timeseries(codigo_serie)
    
    # Converter a coluna de data para datetime para facilitar o filtro
    df['RAW DATE'] = pd.to_datetime(df['RAW DATE'], utc=True)

    #Converter janeiro em 1...
    meses = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
        "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }
    
    # Criar o filtro para incluir apenas os meses 
    data_inicio = pd.Timestamp(f"{ano_inicio}-{mes_inicio:02d}-01", tz='UTC')
    data_fim = pd.Timestamp(f"{ano_fim}-{mes_fim:02d}-01", tz='UTC')
    
    df_filtrado = df[(df['RAW DATE'] >= data_inicio) & (df['RAW DATE'] <= data_fim)]
    
    # Obter a inflação mensal em decimal (dividido por 100)
    inflation = df_filtrado['VALUE ((% a.a.))'] / 100
    
    # Fator de inflação total
    fator_total = 1.0
    precos = []
    datas = []
    
    for i in range(len(inflation)-1, -1, -1):  # Começar do fim em direção ao início
        fator_mensal = (1 + inflation.iloc[i]) ** (1 / 12)  # Converter a taxa anual para mensal
        fator_total *= fator_mensal  # Acumular o fator mensal

        # Divide o preço final pelo fator acumulado
        preco = float(preco_final) / fator_total
        datas.append(df_filtrado.iloc[i]['RAW DATE'])
        precos.append(preco)


    return datas, precos

# Exemplo de uso
# preco_final = 75000  # Preço em fevereiro de 2025
# ano_inicio = 2004
# mes_inicio = 2  # Fevereiro de 2004
# ano_fim = 2025
# mes_fim = 2  # Fevereiro de 2025
