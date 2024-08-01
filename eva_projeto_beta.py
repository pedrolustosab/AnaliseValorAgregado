# -*- coding: utf-8 -*-
"""EVA (2).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qqoPynX528VXBGo2bQ3Pq1CH5e9p1wb3
"""

import pandas as pd
import numpy as np
import math
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

def date_range_monthly(start_date, n):
    dates = []
    current_date = start_date

    # Encontrar o último dia do mês da data inicial
    end_of_month = (current_date + relativedelta(day=1, months=1) - relativedelta(days=1))
    dates.append(end_of_month)

    for _ in range(n - 1):
        # Mover para o primeiro dia do próximo mês
        current_date = end_of_month + relativedelta(days=1)
        # Encontrar o último dia do próximo mês
        end_of_month = (current_date + relativedelta(day=1, months=1) - relativedelta(days=1))
        dates.append(end_of_month)

    return dates

# Exemplo de uso:
start_date = date(2023, 10, 1)
n = 20  # Número de datas desejadas
date_list = date_range_monthly(start_date, n)

# Criar um DataFrame com a coluna 'Medicao'
df = pd.DataFrame({'DataMedicao': date_list})

df.index.name = 'Medicao'
df.index += 1
df.reset_index(inplace=True)

# Função para calcular a diferença em dias
def calculate_days(date_medicao):
    return (date_medicao - start_date).days + 1

# Adiciona a coluna 'Dia' usando apply
df['Dia'] = df['DataMedicao'].apply(calculate_days)

# Função sigmoidal
def sigmoid(x, L, k, x0):
    return L / (1 + np.exp(-k * (x - x0)))

# Calcular valores planejados, reais e agregados
df['ValorPlanejado'] = sigmoid(df['Medicao'], 12345678, 0.48, 7.8).round(2)
df['CustoReal'] = sigmoid(df['Medicao'], 14345678, 0.52, 8).round(2)
df['ValorAgregado'] = sigmoid(df['Medicao'], 9345678, 0.47, 8.5).round(2)

# Ajuste para valores NaN
df.loc[df['Medicao'] > 10, ['CustoReal', 'ValorAgregado']] = np.nan

# Calcular variações
df['VariacaoCusto'] = df['ValorAgregado'] - df['CustoReal']
df['VariacaoPrazo'] = df['ValorAgregado'] - df['ValorPlanejado']

# Cálculo de IDC, IDP
df['IDC'] = df['ValorAgregado'] / df['CustoReal']
df['IDP'] = df['ValorAgregado'] / df['ValorPlanejado']

# Últimos valores
ultimo_custo_real = df['CustoReal'].dropna().iloc[-1]
ultimo_valor_agregado = df['ValorAgregado'].dropna().iloc[-1]
valor_planejado = df['ValorPlanejado'].iloc[-1]
indice = df[df['ValorAgregado'] == ultimo_valor_agregado].index[0]
valor_planejado_indice = df.loc[indice, 'ValorPlanejado']
ultimo_data_real = df.loc[indice, 'DataMedicao']
ultimo_dia_real = df.loc[indice, 'Dia']
ultimo_dia_planejado = df['Dia'].iloc[-1]

# Cálculo dos Pontos
IDC = (ultimo_valor_agregado / ultimo_custo_real).round(2)
IDP = (ultimo_valor_agregado / valor_planejado_indice).round(2)
EPT = ((valor_planejado - ultimo_valor_agregado) / IDC).round(2)
ENT = EPT + ultimo_custo_real
VNT = (ENT - valor_planejado).round(2)
DPT = math.ceil((ultimo_dia_planejado / IDP - ultimo_dia_real + 1))
DNT = math.ceil(ultimo_dia_planejado/IDP)
VD = DNT - ultimo_dia_planejado

def estimar_data(Dia):
  if Dia >= ultimo_dia_real:
    intervalo_origem = ultimo_dia_planejado - ultimo_dia_real
    intervalo_destino = DNT - ultimo_dia_real
    DiaPlanejado = intervalo_destino * (Dia - ultimo_dia_real) / intervalo_origem + ultimo_dia_real
  else:
    DiaPlanejado = 0
  return math.ceil(DiaPlanejado)

def estimar_CR(valor_planejado_):
  if valor_planejado_ >= valor_planejado_indice:
    intervalo_origem = valor_planejado - valor_planejado_indice
    intervalo_destino = ENT - ultimo_custo_real
    CR_Estimado = (intervalo_destino * (valor_planejado_ - valor_planejado_indice) / intervalo_origem + ultimo_custo_real).round(2)
  else:
    CR_Estimado = 0
  return CR_Estimado

def estimar_VA(valor_planejado_):
  if valor_planejado_ >= valor_planejado_indice:
    intervalo_origem = valor_planejado - valor_planejado_indice
    intervalo_destino = valor_planejado - ultimo_valor_agregado
    VA_Estimado = (intervalo_destino * (valor_planejado_ - valor_planejado_indice) / intervalo_origem + ultimo_valor_agregado).round(2)
  else:
    VA_Estimado = 0
  return VA_Estimado

def calcular_data_estimada(row_index, DiaEstimado):
    if row_index > indice:
        return start_date + pd.to_timedelta(DiaEstimado, unit='D')
    elif row_index == indice:
        return ultimo_data_real
    else:
        return np.nan

df['DiaEstimado'] = df['Dia'].apply(estimar_data)
df['DataEstimada'] = [calcular_data_estimada(index, row['DiaEstimado']) for index, row in df.iterrows()]
df['CR_Estimado'] = df['ValorPlanejado'].apply(estimar_CR)
df['VA_Estimado'] = df['ValorPlanejado'].apply(estimar_VA)

def calcular_vp_simples(row_index, valor_planejado, valor_planejado_anterior):
    if row_index <= indice:
        return valor_planejado - valor_planejado_anterior
    else:
        return np.nan

df['VP_Simples'] = [calcular_vp_simples(index, row['ValorPlanejado'], df['ValorPlanejado'].shift(1)[index])
                   for index, row in df.iterrows()]
df.loc[0, 'VP_Simples'] = df.loc[0, 'ValorPlanejado']

ultimo_VP_Simples = df['VP_Simples'].dropna().iloc[-1]
penultimo_VP_Simples = df['VP_Simples'].dropna().iloc[-2]
acum_VP_Simples = df['VP_Simples'].sum() - ultimo_VP_Simples
VariacaoPrazo = (ultimo_VP_Simples + (acum_VP_Simples - ultimo_valor_agregado)).round(2)
VariacaoTempo = math.floor(((acum_VP_Simples - ultimo_valor_agregado)/penultimo_VP_Simples*(df.loc[indice - 1, 'Dia'] - df.loc[indice - 2, 'Dia'])) + (df.loc[indice, 'Dia'] - df.loc[indice - 1, 'Dia'])+0.5)
# Criando o DataFrame
df_pontos = pd.DataFrame({
    'Indicador': ['IDC', 'IDP', 'EPT', 'ENT', 'VNT', 'DPT', 'DNT', 'VD','VariacaoPrazo','VariacaoTempo'],
    'Valor': [IDC, IDP, EPT, ENT, VNT, DPT, DNT, VD, VariacaoPrazo, VariacaoTempo ]
})
df_pontos

df

# Converter colunas para listas
lista_data_medicao = df['DataMedicao'].tolist()
lista_data_estimada = df['DataEstimada'].tolist()

# Mesclar as duas listas
lista_datas = lista_data_medicao + lista_data_estimada

# Remover valores NaN e duplicatas
lista_datas = [data for data in lista_datas if pd.notna(data)]  # Remove NaNs
lista_datas = list(set(lista_datas))  # Remove duplicatas

# Ordenar as datas
lista_datas = sorted(lista_datas)

# Criar DataFrame a partir da lista de datas mescladas
df_datas = pd.DataFrame({'Data': lista_datas})

# Criar DataFrame que contém todas as colunas desejadas
df_dados_reais = df[['DataMedicao', 'ValorPlanejado', 'CustoReal', 'ValorAgregado','VariacaoCusto','VariacaoPrazo' , 'IDC', 'IDP']]
df_dados_reais = df_dados_reais.rename(columns={'DataMedicao': 'Data'})

df_dados_estimado = df[['DataEstimada', 'CR_Estimado', 'VA_Estimado']]
df_dados_estimado = df_dados_estimado.rename(columns={'DataEstimada': 'Data'})

# Merge com left join
df_merged = pd.merge(df_datas, df_dados_reais, on='Data', how='left')
df_merged = pd.merge(df_merged, df_dados_estimado, on='Data', how='left')

# Exibir o DataFrame resultante
df_merged