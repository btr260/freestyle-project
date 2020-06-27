import requests
import dotenv
import json
import datetime
import csv
import os
from dotenv import load_dotenv
import time
import pandas as pd

# DEFINE FUNCTIONS ----------------------------------------------------------------------

def spy_pull(api_key):

    spy_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol=SPY&apikey={api_key}"
    spy_response = requests.get(spy_url)

    parsed_spy = json.loads(spy_response.text)

    close_days = list(parsed_spy['Monthly Adjusted Time Series'].keys())

    spy_headers = ['timestamp', 'close',
               'adj close', 'volume', 'div amt']

    spy_filepath = os.path.join(os.path.dirname(os.path.abspath(
        __file__)), '..', 'data', "SPY.csv")

    with open(spy_filepath, 'w') as spy_file:
        writer = csv.DictWriter(spy_file, fieldnames=spy_headers)
        writer.writeheader()

        for k in close_days:

            writer.writerow({
                'timestamp': k,
                'close': parsed_spy['Monthly Adjusted Time Series'][k]['4. close'],
                'adj close': parsed_spy['Monthly Adjusted Time Series'][k]['5. adjusted close'],
                'volume': parsed_spy['Monthly Adjusted Time Series'][k]['6. volume'],
                'div amt': parsed_spy['Monthly Adjusted Time Series'][k]['7. dividend amount']
            })

    spy = pd.read_csv(spy_filepath, parse_dates=['timestamp'])
    spy_sort = spy.sort_values(by=['timestamp'])
    spy_sort['month'] = spy_sort['timestamp'].dt.to_period('M')
    spy_sort = spy_sort.set_index('month')
    spy_sort['spret'] = spy_sort['adj close'].pct_change()
    spy_ret = spy_sort['spret']

    return spy_ret

def fred_pull(api_key):

    fred_url = f'https://api.stlouisfed.org/fred/series/observations?series_id=DGS1&api_key={api_key}&file_type=json'
    fred_response = requests.get(fred_url)

    parsed_fred = json.loads(fred_response.text)

    #fred_data = [{'date':x['date'], 'rate':x['value']} for x in parsed_fred['observations']]

    fred_filepath = os.path.join(os.path.dirname(os.path.abspath(
        __file__)), '..', 'data', "FRED.csv")

    fred_headers = ['date', 'rate']

    with open(fred_filepath, 'w') as fred_file:
        writer = csv.DictWriter(fred_file, fieldnames=fred_headers)
        writer.writeheader()

        for k in parsed_fred['observations']:

            if k['value'] != '.':

                writer.writerow({
                    'date': k['date'],
                    'rate': k['value']
                })

    fred = pd.read_csv(fred_filepath, parse_dates=['date'])
    fred['month'] = fred['date'].dt.to_period('M')
    risk_free = fred.groupby('month')['rate'].mean()
    risk_free = risk_free / 100

    return risk_free


# LOAD ENVIRONMENT VARIABLES ------------------------------------------------------------
load_dotenv()
ap_api_key = os.environ.get('ALPHAVANTAGE_API_KEY')
fred_api_key = os.environ.get('FRED_API_KEY')

spy_join=spy_pull(ap_api_key)
fred_join=fred_pull(fred_api_key)
