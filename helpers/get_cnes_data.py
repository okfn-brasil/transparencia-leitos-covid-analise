import pandas as pd
import json
import time
from datetime import datetime, timezone, timedelta
import glob
import requests
from pathlib import Path

STANDARD_HEADERS = {
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'http://cnes.datasus.gov.br/pages/estabelecimentos/consulta.jsp',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
}

DATA_FOLDER = 'data/hospitais'


def get_basic_info_by_cnes(cnes):
    params = (
        ('cnes', cnes),
    )
    r = requests.get('http://cnes.datasus.gov.br/services/estabelecimentos', headers=STANDARD_HEADERS, params=params, verify=False)
    return json.loads(r.content)


def get_detailed_info(id):
    r = requests.get(f'http://cnes.datasus.gov.br/services/estabelecimentos/{id}', headers=STANDARD_HEADERS, verify=False)
    return json.loads(r.content)


def get_beds(id):
    r = requests.get(f'http://cnes.datasus.gov.br/services/estabelecimentos-hospitalar/{id}', headers=STANDARD_HEADERS, verify=False)
    return json.loads(r.content)


def check_if_deactivated(id):
    # returns True is deactivated, false otherwise
    r = requests.get(f'http://cnes.datasus.gov.br/services/estabelecimentos-desativados-local/validar/{id}', headers=STANDARD_HEADERS, verify=False)
    return json.loads(r.content)['existe']


def get_all_info(cnes):
    basic_info = get_basic_info_by_cnes(cnes)
    # display(basic_info)
    first_match = basic_info[0]
    id = str(first_match['id'])

    beds = get_beds(id)
    detailed_info = get_detailed_info(id)
    deactivated = check_if_deactivated(id)

    detailed_info['beds'] = beds
    detailed_info['deactivated'] = deactivated
    return detailed_info


def get_all_hospital_data(df):
    ts_run = datetime.now(timezone.utc)
    cnes_codes = df[:].cnes.unique()
    counter = 1
    errors = []
    start_time = time.time()
    end_time = time.time()

    for cnes in cnes_codes:
        print(cnes, f'{counter}/{len(cnes_codes)}')
        file_path = f'{DATA_FOLDER}/{cnes}.json'
        if Path(file_path).exists():
            print('--->file already exists, skipping')
            continue
        try:
            info = get_all_info(cnes)
            info['ts_run'] = ts_run.isoformat()
            info['error'] = False
            with open(file_path, 'w') as outfile:
                json.dump(info, outfile)
        except Exception as e:
            print('error:', e)
            errors.append(cnes)
            with open(file_path, 'w') as outfile:
                json.dump({'cnes': cnes, 'error': True}, outfile)
        finally:
            counter += 1

    # ler arquivos baixados
    cnes_files = glob.glob('{DATA_FOLDER}/*.json')

    frames = []
    for file_path in cnes_files:
        with open(file_path) as f:
            data = json.load(f)
        if data['error'] == False:
            frames.append(pd.json_normalize(data))

    df_hosp = pd.concat(frames)

    time_elapsed = (end_time - start_time)
    print(time_elapsed)
    return df_hosp, errors
