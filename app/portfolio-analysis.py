# IMPORT PACKAGES -----------------------------------------------------------------------

import requests
import dotenv
import json
import datetime
import csv
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
import operator

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


# SET PORTFOLIO -------------------------------------------------------------------------

portfolio = os.environ.get('PORTF')

# PULL AND WRITE DATA -------------------------------------------------------------------

failed_tickers = []

tck_list = [p['tck'] for p in portfolio]

for tkr in tck_list:

    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={tkr}&apikey={api_key}"
    response = requests.get(request_url)

    # PARSE API DATA -----------------------------------------------------------------------

    parsed_response = json.loads(response.text)

    error_check_list = list(parsed_response.keys())
    error_check = error_check_list[0]

    if error_check == 'Meta Data':  # IF TICKER IS ABLE TO PULL ACTUAL DATA

        ## PULL LAST REFRESH DATE FROM DATA ------------------------------------------------------------------

        #last_refreshed = parsed_response['Meta Data']['3. Last Refreshed']

        #last_ref_dt = datetime.datetime.fromisoformat(last_refreshed)

        ## PULL SYMBOL FROM DATA ------------------------------------------------------------------

        #symbol = parsed_response['Meta Data']['2. Symbol']

        ## PULL LATEST CLOSE FROM DATA ------------------------------------------------------------

        close_days = list(parsed_response['Time Series (Daily)'].keys())
        #latest_day = close_days[0]
        #px_last = parsed_response['Time Series (Daily)'][latest_day]['4. close']

        ## PULL HIGH AND LOW FROM DATA----------------------------------------------------------------

        #highlow_pd = min(100, len(close_days))

        #high_px = []

        #for d in close_days[0:highlow_pd]:
        #    high_px.append(
        #        float(parsed_response['Time Series (Daily)'][d]['2. high']))

        #recent_high = max(high_px)

        #low_px = []

        #for d in close_days[0:highlow_pd]:
        #    low_px.append(
        #        float(parsed_response['Time Series (Daily)'][d]['3. low']))

        #recent_low = min(low_px)

        ## PULL MOST RECENT DATE OF HIGH/LOW PRICE FOR USE IN CHART--------------------------------
        #high_date = []
        #low_date = []

        #for k, d in parsed_response['Time Series (Daily)'].items():

        #    if float(d['2. high']) == recent_high:
        #        high_date.append(k)

        #    elif float(d['3. low']) == recent_low:
        #        low_date.append(k)

        #recent_high_dt = datetime.datetime.fromisoformat(high_date[0])

        #recent_low_dt = datetime.datetime.fromisoformat(low_date[0])

        ## WRITE CSV DATA ------------------------------------------------------------------------

        headers = ['timestamp', 'open', 'high', 'low', 'close', 'adj close', 'volume', 'div amt', 'split coeff']

        csv_filepath = os.path.join(os.path.dirname(os.path.abspath(
            __file__)), '..', 'data', f"{tkr}.csv")

        #chart_data = []

        with open(csv_filepath, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()

            for k in close_days:
                writer.writerow({
                    'timestamp': k,
                    'open': parsed_response['Time Series (Daily)'][k]['1. open'],
                    'high': parsed_response['Time Series (Daily)'][k]['2. high'],
                    'low': parsed_response['Time Series (Daily)'][k]['3. low'],
                    'close': parsed_response['Time Series (Daily)'][k]['4. close'],
                    'adj close': parsed_response['Time Series (Daily)'][k]['5. adjusted close'],
                    'volume': parsed_response['Time Series (Daily)'][k]['6. volume'],
                    'div amt': parsed_response['Time Series (Daily)'][k]['7. dividend amount'],
                    'split coeff': parsed_response['Time Series (Daily)'][k]['8. split coefficient']
                })

                #chart_data.append({
                #    'timestamp': k,
                #    'open': parsed_response['Time Series (Daily)'][k]['1. open'],
                #    'high': parsed_response['Time Series (Daily)'][k]['2. high'],
                #    'low': parsed_response['Time Series (Daily)'][k]['3. low'],
                #    'close': parsed_response['Time Series (Daily)'][k]['4. close'],
                #    'volume': parsed_response['Time Series (Daily)'][k]['5. volume']
                #})

        # RECOMMENDATION ------------------------------------------------------------------------

        #rec_criteria = float(px_last) / float(recent_low)

        #if rec_criteria >= 1.2:
        #    rec = f"DO NOT BUY {symbol}!"
        #    reason = f"{symbol} most recently closed at or above 20% of its recent low."
        #    rec_cht = f"Do Not Buy: currently trading at or above 20% of its recent low"

        #else:
        #    rec = f"BUY {symbol}!"
        #    reason = f"{symbol} most recently closed within 20% of its recent low"
        #    rec_cht = f"Buy: currently trading within 20% of recent low"

        # PRINT INFORMATION ---------------------------------------------------------------------

        print("-------------------------")
        print(f"SELECTED SYMBOL: {tkr}")
        print("-------------------------")
        #print(
        #    f"LATEST DAY: {last_ref_dt.strftime('%A, %B %#d')}{date_suffix(last_ref_dt)}, {last_ref_dt.strftime('%Y')}")
        #print(f"LATEST CLOSE: {to_usd(float(px_last))}")
        #print(f"RECENT HIGH: {to_usd(recent_high)}")
        #print(f"RECENT LOW: {to_usd(recent_low)}")
        #print("-------------------------")
        #print(
        #    f"ANALYSIS: {symbol} is trading at {(100*rec_criteria):.1f}% of its recent low")
        #print(f"RECOMMENDATION: {rec}")
        #print(f"RECOMMENDATION REASON: {reason}")
        print("-------------------------")
        print(f"WRITING DATA TO CSV: {os.path.abspath(csv_filepath)}")
        print("-------------------------")

        #PREP CHART----------------------------------------------------------------------------------

        #sorted_chart_data = sorted(
        #    chart_data, key=operator.itemgetter('timestamp'), reverse=False)

        ##print(sorted_chart_data)

        #cht_timestamp = [p['timestamp'] for p in sorted_chart_data]
        #cht_close = [p['close'] for p in sorted_chart_data]
        #cht_open = [p['open'] for p in sorted_chart_data]
        #cht_high = [p['high'] for p in sorted_chart_data]
        #cht_low = [p['low'] for p in sorted_chart_data]
        ##print(cht_timestamp)

        #anno = [dict(x=last_ref_dt, y=px_last, xref='x', yref='y', text=f"Last Close: {to_usd(float(px_last))}", showarrow=True, arrowhead=7, ax=-40, ay=80),
        #        dict(x=recent_high_dt, y=recent_high, xref='x', yref='y',
        #             text=f"Recent High: {to_usd(recent_high)}", showarrow=True, arrowhead=7, ax=-40, ay=-40),
        #        dict(x=recent_low_dt, y=recent_low, xref='x', yref='y',
        #             text=f"Recent Low: {to_usd(recent_low)}", showarrow=True, arrowhead=7, ax=-40, ay=40),
        #        dict(x=last_ref_dt, y=(1.2*recent_low), xref='x', yref='y', text=f"Price Threshhold for Purchase: {to_usd(1.2*recent_low)}", showarrow=False, yanchor='bottom', xanchor='right')]

        #thresh = [dict(x0=min(cht_timestamp), x1=max(cht_timestamp), y0=(
        #    1.2*recent_low), y1=(1.2*recent_low), xref='x', yref='y', line_width=1)]

        ##print(anno)
        #fig = go.Figure(data=[go.Candlestick(
        #    x=cht_timestamp, open=cht_open, high=cht_high, low=cht_low, close=cht_close)],
        #    layout=go.Layout(title=go.layout.Title(text=f"{symbol} - {rec_cht}"), shapes=thresh, annotations=anno, yaxis_title="Price per Share (USD)"))

        #fig.show()

    else:  # IF TICKER NOT FOUND ON API

        if error_check == "Error Message":
            failed_tickers.append(
                {'ticker': tkr, 'err_type': 'Invalid API Call'})

        elif error_check == "Note":
            failed_tickers.append(
                {'ticker': tkr, 'err_type': 'Exceeds API Call Limit (5 per minute and 500 per day)'})

        else:
            failed_tickers.append({'ticker': tkr, 'err_type': 'Other'})

breakpoint()
