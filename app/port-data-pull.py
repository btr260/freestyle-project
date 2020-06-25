# IMPORT PACKAGES -----------------------------------------------------------------------

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
api_key = os.environ.get('ALPHAVANTAGE_API_KEY')

# DEFINE FUNCTIONS ----------------------------------------------------------------------

def to_usd(my_price):
    '''
    Converts a numeric value to usd-formatted string, for printing and display purposes.

    Param: my_price (int or float) like 4000.444444

    Example: to_usd(4000.444444)

    Returns: $4,000.44
    '''
    return f'${my_price:,.2f}'  # > $12,000.71

def num_suffix(num_for_suffix):
    '''
    Adds st, nd, rd, or th to the end of a day of the month.
    '''
    if 4 <= num_for_suffix <= 20 or 24 <= num_for_suffix <= 30:
        suffix = 'th'
    else:
        suffix = ['st', 'nd', 'rd'][num_for_suffix % 10 - 1]

    return suffix

def api_data_pull(portfolio):

    failed_tickers = []

    tck_list = [p['tck'] for p in portfolio]

    batch = int(len(tck_list) / 5) + (len(tck_list) % 5 > 0)

    if len(tck_list) > 5:
        print('-----------------------------------------------', flush=True)
        print(f'WARNING! DUE TO NUMBER OF TICKERS IN YOUR PORTFOLIO,\nTHE DATA COLLECTION PROCESS MAY TAKE APPROXIMATELY {batch-1} MINUTES TO COMPLETE!', flush=True)
        print('-----------------------------------------------', flush=True)

    for i in range(0,batch,1):
        start = i * 5
        end = min(len(tck_list), start + 5)
        if i > 0:
            time.sleep(70)

        for tkr in tck_list[start:end]:

            request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={tkr}&apikey={api_key}"
            response = requests.get(request_url)

            # PARSE API DATA -----------------------------------------------------------------------

            #print(response.text)
            parsed_response = json.loads(response.text)

            error_check_list = list(parsed_response.keys())
            error_check = error_check_list[0]

            if error_check == 'Meta Data':  # IF TICKER IS ABLE TO PULL ACTUAL DATA

                quant=[q['qty'] for q in portfolio if q['tck']==tkr][0]

                ## PULL LATEST CLOSE FROM DATA ------------------------------------------------------------

                close_days = list(parsed_response['Monthly Adjusted Time Series'].keys())

                ## WRITE CSV DATA ------------------------------------------------------------------------

                headers = ['ticker', 'qty', 'timestamp', 'close', 'adj close', 'volume', 'div amt']

                csv_filepath = os.path.join(os.path.dirname(os.path.abspath(
                    __file__)), '..', 'data', f"{tkr}.csv")

                with open(csv_filepath, 'w') as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=headers)
                    writer.writeheader()

                    for k in close_days:

                        writer.writerow({
                            'ticker': tkr,
                            'qty': quant,
                            'timestamp': k,
                            'close': parsed_response['Monthly Adjusted Time Series'][k]['4. close'],
                            'adj close': parsed_response['Monthly Adjusted Time Series'][k]['5. adjusted close'],
                            'volume': parsed_response['Monthly Adjusted Time Series'][k]['6. volume'],
                            'div amt': parsed_response['Monthly Adjusted Time Series'][k]['7. dividend amount']
                        })

                # PRINT STATUS ---------------------------------------------------------------------

                print('-----------------------------------------------', flush=True)
                print(f"DOWNLOADING DATA FOR: {tkr}", flush=True)
                print(f"WRITING DATA TO CSV: {os.path.abspath(csv_filepath)}", flush=True)
                print('-----------------------------------------------', flush=True)

            else:  # IF TICKER NOT FOUND ON API

                if error_check == "Error Message":
                    failed_tickers.append(
                        {'ticker': tkr, 'err_type': 'Invalid API Call'})

                elif error_check == "Note":
                    failed_tickers.append(
                        {'ticker': tkr, 'err_type': 'Exceeds API Call Limit (5 per minute and 500 per day)'})

                else:
                    failed_tickers.append({'ticker': tkr, 'err_type': 'Other'})

        if i < (batch - 1):
            print('-----------------------------------------------',flush=True)
            print(f'The {i+1}{num_suffix(i+1)} Batch of Downloads is Complete!', flush=True)
            print('Waiting 1 minute to download next batch of data', flush=True)
            print(f'Estimated remaining download time is approximately {batch-i-1} minutes.', flush=True)
            print('-----------------------------------------------', flush=True)

        else:
            print('-----------------------------------------------', flush=True)
            print('Data download complete', flush=True)
            print('-----------------------------------------------', flush=True)

    # ERROR SUMMARY -----------------------------------------------------------------
    if len(failed_tickers) > 0:
        if len(failed_tickers) == len(tck_list):
            print("-------------------------")
            print("UNABLE TO GENERATE REPORT FOR THE SPECIFIED TICKER(S).\nSEE ERROR SUMMARY")
            print("-------------------------")

        print("-------------------------")
        print("ERROR SUMMARY:")
        print("The program was unable to pull data from the API for the following ticker(s):")
        for t in failed_tickers:
            print(f"----{t['ticker']}: {t['err_type']}")
        print("Please check the accuracy of the ticker(s) and try again.")

        return False

    else:
        return True


if __name__=='__main__':

    portfolio = [{'id': 1, 'tck': 'ABBV', 'qty': 225.000},
                 {'id': 2, 'tck': 'AZO', 'qty': 5.000},
                 {'id': 3, 'tck': 'STZ', 'qty': 100.000},
                 {'id': 4, 'tck': 'CCI', 'qty': 39.000},
                 {'id': 5, 'tck': 'CVS', 'qty': 200.000},
                 {'id': 6, 'tck': 'DE', 'qty': 26.000},
                 {'id': 7, 'tck': 'DELL', 'qty': 108.000},
                 {'id': 8, 'tck': 'ENB', 'qty': 116.000},
                 {'id': 9, 'tck': 'HD', 'qty': 22.000},
                 {'id': 10, 'tck': 'JPM', 'qty': 35.000},
                 {'id': 11, 'tck': 'KKR', 'qty': 185.000},
                 {'id': 12, 'tck': 'MPC', 'qty': 450.000},
                 {'id': 13, 'tck': 'MRK', 'qty': 72.000},
                 {'id': 14, 'tck': 'MET', 'qty': 90.000},
                 {'id': 15, 'tck': 'NXST', 'qty': 55.000},
                 {'id': 16, 'tck': 'NVT', 'qty': 60.000},
                 {'id': 17, 'tck': 'PNR', 'qty': 60.000},
                 {'id': 18, 'tck': 'RTX', 'qty': 46.000},
                 {'id': 19, 'tck': 'SNY', 'qty': 100.000}]


    print('-----------------------------------------------', flush=True)
    print(f'You have specified a portfolio of {len(portfolio)} tickers.\nThe program will now retrieve data from the Alpha Vantage API.', flush=True)
    print('-----------------------------------------------', flush=True)

    pull = api_data_pull(portfolio)
    #print(pull)