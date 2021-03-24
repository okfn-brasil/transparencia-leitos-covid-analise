import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from helpers.get_cnes_data import get_all_hospital_data
import json


def preprocess_data(df, UPDATED_DAYS, TS_RUN, get_cnes_data=False):
    try:
        expected_cols = ['_index', '_type', '_id', '_score', 'estado', 'estadoSigla',
           'municipio', 'cnes', 'nomeCnes', 'dataNotificacaoOcupacao',
           'ofertaRespiradores', 'ofertaHospCli', 'ofertaHospUti',
           'ofertaSRAGCli', 'ofertaSRAGUti', 'ocupHospCli', 'ocupHospUti',
           'ocupSRAGCli', 'ocupSRAGUti', 'altas', 'obitos',
           'ocupacaoInformada', 'algumaOcupacaoInformada', 'ts_run']
        df.columns.values.tolist() == expected_cols
    except Exception as e:
        print('df columns different from expected')
        raise ValueError

    # limpar siglas, muitas estão caixa baixa, preservando dado
    df['estadoSigla_original'] = df['estadoSigla']
    df['estadoSigla'] = df['estadoSigla'].str.upper()

    # preencher nans com zeros
    df = df.fillna({
        'ofertaHospCli': 0,
        'ofertaSRAGCli': 0,
        'ofertaHospUti': 0,
        'ofertaSRAGUti': 0,
        'ocupHospCli': 0,
        'ocupSRAGCli': 0,
        'ocupHospUti': 0,
        'ocupSRAGUti': 0,
    })

    # considerando oferta sem ocupação
    df['totalOfertaCli'] = df['ofertaHospCli'] + df['ofertaSRAGCli']
    df['totalOfertaUti'] = df['ofertaHospUti'] + df['ofertaSRAGUti']
    df['totalOcupCli'] = df['ocupHospCli'] + df['ocupSRAGCli']
    df['totalOcupUti'] = df['ocupHospUti'] + df['ocupSRAGUti']

    # considerando oferta como oferta + ocupação
    df['totalOfertaCliAlt'] = df['ofertaHospCli'] + df['ofertaSRAGCli'] + df['ocupHospCli'] + df['ocupSRAGCli']
    df['totalOfertaUtiAlt'] = df['ofertaHospUti'] + df['ofertaSRAGUti'] + df['ocupHospUti'] + df['ocupSRAGUti']

    # tem uti
    df['has_uti_proxy'] = np.where(df['totalOfertaUtiAlt'] > 0, True, False)

    # dados de atualização
    df['dataNotificacaoOcupacao'] = pd.to_datetime(df['dataNotificacaoOcupacao'])
    for d in UPDATED_DAYS:
        df[f'updated_{str(d)}d'] = np.where(df['dataNotificacaoOcupacao'] >= TS_RUN - timedelta(days=d, hours=TS_RUN.hour), True, False)

    for d in UPDATED_DAYS:
        pct_outdated = len(df[df[f'updated_{str(d)}d'] == True]) / len(df)
        # print(f'{round((pct_outdated * 100), 1)}% updated in {str(d)} days')

    if get_cnes_data is True:
        # fazer consultas cnes
        df_hosp, errors = get_all_hospital_data(df)

        # salvar erros
        with open(f'data/hospitais_errors.json', 'w') as outfile:
            json.dump(errors, outfile)

        # salvar dados
        df_hosp.to_json('exports/hospitais_cnes.json', orient='records')

    # ler resultado
    dtypes = {
        'cnes': str  # has left padding zeros
    }
    df_hosp = pd.read_json('exports/hospitais_cnes.json', dtype=dtypes)

    # merge dados api e dados cnes
    df_h = df.merge(df_hosp, on='cnes', suffixes=('', '_cnes'), how='left')

    ### Tentando diferenciar os desativados

    # - Não tem dados CNES & não foram atualizados nos últimos 14 dias
    # - OU Tem dados CNES & CNES == 'desativado' & não foram atualizados nos últimos 14 dias
    df_deactivated = (df_h[
        ((df_h.id.isna()) & (df_h.updated_14d == False))
        |
        ((df_h.id.notna()) & (df_h.deactivated == True) & (df_h.updated_14d == False))
    ])
    # print('% deactivated proxy', len(df_deactivated) / len(df_h))
    df_h['deactivated_proxy'] = np.where(df_h._id.isin(df_deactivated._id.unique()), True, False)

    # leitos cnes
    all_beds = []
    for index, row in df_h[df_h['beds'].notna()].iterrows():
        beds = row['beds']
        for bed in beds:
            bed['cnes'] = row['cnes']
            all_beds.append(bed)

    df_beds = pd.DataFrame(all_beds)
    df_beds['total_beds'] = df_beds['qtExistente'].astype(float)

    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(df_beds[df_beds.dsLeito.str[0:3] == 'UTI'].groupby(['dsLeito', 'dsAtributo']).total_beds.sum().sort_values(ascending=False))

    # leitos tipo UTI
    df_beds['uti'] = (np.where(
        df_beds.dsLeito.str[0:3] == 'UTI',
            np.where(df_beds.dsLeito.str.contains('NEONATAL|QUEIMADOS') == False, True, False)
        , False))

    # somar leitos cnes uti
    cnes_uti = df_beds[df_beds['uti'] == True].groupby('cnes').agg({'total_beds': 'sum'})
    cnes_uti.reset_index(inplace=True)
    cnes_uti.rename(columns={'total_beds': 'uti_beds_via_cnes'}, inplace=True)

    # merge de volta com dados
    df_hb = df_h.merge(cnes_uti, on='cnes', how='left')

    return df_hb
