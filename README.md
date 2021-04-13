# Análise - Transparência de Leitos Covid

Análise em Jupyter Notebook da transparência do Censo Hospitalar, que registra a disponibilidade e ocupação de leitos hospitalares no Brasil.

Veja a [nota de lançamento](https://www.ok.org.br/noticia/estudo-revela-que-quase-70-dos-dados-de-ocupacao-de-leitos-do-pais-tem-problemas/) e o [estudo completo em formato PDF](https://transparenciacovid19.ok.org.br/files/ESPECIAL_Transparencia-Covid19_OcupacaoLeitos_01.pdf).

## Análise completa

O [código completo da análise](Analysis.ipynb) está disponível em formato Jupyter Notebook. Os dados também estão incluídos neste repositório, para que qualquer um possa reproduzir a análise.

## Fontes de dados

- [API Leitos DataSUS - Registro de Ocupação Hospitalar COVID-19](https://opendatasus.saude.gov.br/dataset/registro-de-ocupacao-hospitalar)
- [CNES](http://cnes.datasus.gov.br/pages/estabelecimentos/consulta.jsp)
- Dados Painéis Secretarias Estaduais de Saúde (várias fontes, ver planilha [ses/dados_secretarias.csv](ses/dados_secretarias.csv))

## Setup

Você precisa ter Python 3 instalado para rodar a análise. Recomendamos fazer o setup de um ambiente virtual usando conda ou virtualenv, por exemplo rodando:

~~~shell
virtualenv -p python3 python-env
source python-env/bin/activate
pip install -r requirements.txt
~~~

Depois, é só rodar `jupyter notebook` e abrir o arquivo `Analysis.ipynb` para ver a análise completa.
