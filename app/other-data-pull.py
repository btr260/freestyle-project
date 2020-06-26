import requests
import dotenv
import json
import datetime
import csv
import os
from dotenv import load_dotenv
import time

# LOAD ENVIRONMENT VARIABLES ------------------------------------------------------------

load_dotenv()
ap_api_key = os.environ.get('ALPHAVANTAGE_API_KEY')
fred_api_key = os.environ.get('FRED_API_KEY')

# DEFINE FUNCTIONS ----------------------------------------------------------------------


#def to_usd(my_price):
#    '''
#    Converts a numeric value to usd-formatted string, for printing and display purposes.
#
#    Param: my_price (int or float) like 4000.444444
#
#    Example: to_usd(4000.444444)
#
#    Returns: $4,000.44
#    '''
#    return f'${my_price:,.2f}'  # > $12,000.71
#
#
#def num_suffix(num_for_suffix):
#    '''
#    Adds st, nd, rd, or th to the end of a day of the month.
#    '''
#    if 4 <= num_for_suffix <= 20 or 24 <= num_for_suffix <= 30:
#        suffix = 'th'
#    else:
#        suffix = ['st', 'nd', 'rd'][num_for_suffix % 10 - 1]
#
#    return suffix
#

spy_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol=SPY&apikey={ap_api_key}"
spy_response = requests.get(spy_url)

# PARSE API DATA -----------------------------------------------------------------------

#print(response.text)
parsed_spy = json.loads(spy_response.text)

close_days = list(parsed_spy['Monthly Adjusted Time Series'].keys())

spy_headers = ['ticker', 'timestamp', 'close',
           'adj close', 'volume', 'div amt']

spy_filepath = os.path.join(os.path.dirname(os.path.abspath(
    __file__)), '..', 'data', "SPY.csv")

with open(spy_filepath, 'w') as spy_file:
    writer = csv.DictWriter(spy_file, fieldnames=spy_headers)
    writer.writeheader()

    for k in close_days:

        writer.writerow({
            'ticker': 'SPY',
            'timestamp': k,
            'close': parsed_spy['Monthly Adjusted Time Series'][k]['4. close'],
            'adj close': parsed_spy['Monthly Adjusted Time Series'][k]['5. adjusted close'],
            'volume': parsed_spy['Monthly Adjusted Time Series'][k]['6. volume'],
            'div amt': parsed_spy['Monthly Adjusted Time Series'][k]['7. dividend amount']
        })

fred_url = f'https://api.stlouisfed.org/fred/series/observations?series_id=DGS1&api_key={fred_api_key}&file_type=json'
fred_response = requests.get(fred_url)

parsed_fred = json.loads(fred_response.text)

fred_data = [{'date':x['date'], 'rate':x['value']} for x in parsed_fred['observations']]

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
