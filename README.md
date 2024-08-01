# Análise de Valor Agregado (EVA)

Este projeto realiza uma Análise de Valor Agregado (EVA) usando funções sigmoides para prever valores planejados, custos reais e valores agregados ao longo de um período de tempo. O objetivo é calcular métricas importantes para monitorar e analisar o desempenho de projetos.

## Descrição

O script Python realiza os seguintes cálculos:

1. **Geração de Datas**:
   - Cria uma lista de datas representando o último dia de cada mês a partir de uma data inicial.

2. **DataFrame e Cálculos Iniciais**:
   - Gera um DataFrame com datas e calcula a diferença em dias desde a data inicial.
   - Adiciona colunas para valores planejados, custos reais e valor agregado usando funções sigmoides.

3. **Cálculos de EVA**:
   - Calcula métricas como:
     - **IDC** (Índice de Desempenho de Custo)
     - **IDP** (Índice de Desempenho Planejado)
     - **EPT** (Eficiência Planejada Total)
     - **ENT** (Estimativa de Custo Total)
     - **VNT** (Variação do Valor Total)
   - Estima datas e valores futuros com base nos cálculos realizados.

4. **Cálculos Adicionais**:
   - Estima valores futuros de custo real e valor agregado com base no valor planejado.
   - Calcula variações simples de valor planejado e outras métricas relacionadas.

## Requisitos

- Python 3.x
- Bibliotecas:
  - pandas
  - numpy
  - math
  - datetime
  - dateutil

Para instalar as bibliotecas necessárias, execute:
```bash
pip install pandas numpy
