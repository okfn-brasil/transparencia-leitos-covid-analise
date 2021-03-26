# Painel de Leitos - Análise

## Fontes de dados

- [API Leitos DataSUS - Registro de Ocupação Hospitalar COVID-19](https://opendatasus.saude.gov.br/dataset/registro-de-ocupacao-hospitalar)
- [CNES](http://cnes.datasus.gov.br/pages/estabelecimentos/consulta.jsp)
- Dados Painéis Secretarias Estaduais de Saúde (vários, ver planilha [ses/dados_secretarias.csv](ses/dados_secretarias.csv))

## Setup

    virtualenv -p python3 python-env
    source python-env/bin/activate
    pip install -r requirements.txt
