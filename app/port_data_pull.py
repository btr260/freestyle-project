# IMPORT PACKAGES -----------------------------------------------------------------------

import requests
import dotenv
import json
import datetime
import csv
import os
from dotenv import load_dotenv
import time
import pandas as pd
from app.portfolio_import import portfolio_import

# DEFINE FUNCTIONS ----------------------------------------------------------------------

def num_suffix(num_for_suffix):
    '''
    Adds st, nd, rd, or th to the end of a day of the month.
    '''
    if 4 <= num_for_suffix <= 20 or 24 <= num_for_suffix <= 30:
        suffix = 'th'
    else:
        suffix = ['st', 'nd', 'rd'][num_for_suffix % 10 - 1]

    return suffix

def port_data_pull(portfolio,api_key):

    failed_tickers = []

    tck_list = [p['tck'] for p in portfolio]

    batch = int(len(tck_list) / 5) + (len(tck_list) % 5 > 0)

    if len(tck_list) > 5:
        print('-----------------------------------------------', flush=True)
        print(f'WARNING! DUE TO NUMBER OF TICKERS IN YOUR PORTFOLIO,\nTHE DATA COLLECTION PROCESS MAY TAKE APPROXIMATELY {batch} MINUTES TO COMPLETE!', flush=True)
        print('-----------------------------------------------', flush=True)

    for i in range(0,batch,1):
        start = i * 5
        end = min(len(tck_list), start + 5)

        # Wait 1 minute and 10 seconds to avoid hitting 5 call per minute API limit
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
                print(f'DATA FROM {close_days[-1]} TO {close_days[0]}')
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
            print('Data download complete.  Compiling portfolio dataset now.', flush=True)
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

        return exit()

    else:

        start_path = os.path.join(os.path.dirname(os.path.abspath(
            __file__)), '..', 'data', f"{tck_list[0]}.csv")


        full = pd.read_csv(start_path, parse_dates=['timestamp'])


        if len(tck_list) == 2:

            next_path = os.path.join(os.path.dirname(os.path.abspath(
                __file__)), '..', 'data', f"{tck_list[1]}.csv")

            temp_data = pd.read_csv(next_path, parse_dates=['timestamp'])

            full = full.append(temp_data)

        else:

            for t in tck_list[1:len(tck_list)]:

                temp_path = os.path.join(os.path.dirname(os.path.abspath(
                    __file__)), '..', 'data', f"{t}.csv")

                temp_data = pd.read_csv(temp_path, parse_dates=['timestamp'])
                #print(temp_data)

                full = full.append(temp_data)


        full_sort = full.sort_values(by=['ticker', 'timestamp'])

        # CREATE MONTH VARIABLE
        # SOURCE: https://stackoverflow.com/questions/45304531/extracting-the-first-day-of-month-of-a-datetime-type-column-in-pandas
        full_sort['month'] = full_sort['timestamp'].dt.to_period('M')

        # Resize data for consistent periods (data/API limitation) ----------------------------

        maxomin = full_sort.groupby('ticker')['month'].min()
        #print(maxomin)
        maxomin = maxomin.max()
        #print(maxomin)

        minomax = full_sort.groupby('ticker')['month'].max()
        #print(minomax)
        minomax = minomax.min()
        #print(minomax)

        # SUBSET DATA FOR FIRST/LAST MONTH
        sub = full_sort.loc[(full_sort['month'] <= minomax) &
                            (full_sort['month'] >= maxomin)]

        sub = sub.sort_values(by=['ticker', 'month'])

        return sub, minomax, maxomin


if __name__=='__main__':

    # LOAD ENVIRONMENT VARIABLES ------------------------------------------------------------

    load_dotenv()
    ap_api_key = os.environ.get('ALPHAVANTAGE_API_KEY')
    port_file_name=os.environ.get('PORTFOLIO_FILE_NAME')

    portfolio = portfolio_import(port_file_name)


    print('-----------------------------------------------', flush=True)
    print(f'You have specified a portfolio of {len(portfolio)} tickers.\nThe program will now retrieve data from the Alpha Vantage API.', flush=True)
    print('-----------------------------------------------', flush=True)

    pull, minomax, maxomin = port_data_pull(portfolio, ap_api_key)


    print(pull)
    print(f'minomax: {minomax}')
    print(f'maxomin: {maxomin}')
    pull.to_csv(os.path.join(os.path.dirname(os.path.abspath(
        __file__)), '..', 'data', "working_port.csv"),index=False)
