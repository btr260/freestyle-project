import pandas as pd
import os
import dotenv
from dotenv import load_dotenv
import datetime
import numpy as np
from app.other_data_pull import spy_pull, fred_pull
from app.port_data_pull import port_data_pull
from app import APP_ENV

# -------------------------------------------------------------------------------------
# FUNCTIONS ---------------------------------------------------------------------------
# -------------------------------------------------------------------------------------

def returns(dataset,period_length,min_start,max_end):

    working_data = dataset
    working_data['mret'] = working_data.groupby('ticker')['adj close'].pct_change()
    working_data['mretp1'] = working_data['mret'] + 1

    working_data['sh val'] = working_data['qty'] * working_data['close']

    pd_len = period_length
    pd_end = max_end
    pd_start = max(max_end - (pd_len * 12), min_start)

    # Start Value of Assets
    pd_start_val = working_data.loc[working_data['month'] == pd_start]
    pd_start_val = pd_start_val.set_index('ticker')
    pd_start_val = pd_start_val['sh val'].rename('start val')

    # Cum Return of Assets
    cum_ret_set = working_data.loc[(working_data['month'] > pd_start) & (working_data['month'] <= pd_end)]
    cum_ret_set = cum_ret_set.set_index('ticker')
    cum_ret_set['cumret'] = cum_ret_set.groupby('ticker')['mretp1'].cumprod()
    cum_ret_set = cum_ret_set.join(pd_start_val, on='ticker')
    cum_ret_set['mon val'] = cum_ret_set['start val'] * cum_ret_set['cumret']

    port_ret = cum_ret_set.groupby('month')[['start val', 'mon val']].sum()
    port_ret['cum ret'] = port_ret['mon val'] / port_ret['start val']
    port_ret['mon ret'] = port_ret['mon val'].pct_change()

    port_ret.loc[pd_start + 1,
                 'mon ret'] = port_ret.loc[pd_start + 1, 'cum ret'] - 1

    # Calc Portf Return
    tot_pd_ret = port_ret.loc[pd_end, 'cum ret'] - 1
    months = len(port_ret)
    years = months / 12
    avg_ann_ret = (1 + tot_pd_ret)**(1 / years) - 1
    avg_mon_ret = (1 + tot_pd_ret)**(1 / months) - 1

    #Calc Return Std Dev
    mon_sdev = port_ret['mon ret'].std()
    ann_sdev = mon_sdev * (12 ** .5)

    ret_calc = {'years_tgt': pd_len, 'years_act': years, 'months_act': months, 'st_date': f'{pd_start.year}-{pd_start.month}',
                'end_date': f'{pd_end.year}-{pd_end.month}', 'ann_ret': avg_ann_ret, 'mon_ret': avg_mon_ret, 'ann_sdev': ann_sdev, 'mon_sdev': mon_sdev}

    return ret_calc, port_ret

# -------------------------------------------------------------------------------------
# CODE --------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------

if __name__=='__main__':

    handling = "good"

    if handling == "good":

        portfolio = [{'id': 1, 'tck': 'ABBV', 'qty': 225.000},
                    {'id': 2, 'tck': 'AZO', 'qty': 5.000},
                    {'id': 3, 'tck': 'STZ', 'qty': 100.000},
                    {'id': 4, 'tck': 'CCI', 'qty': 39.000},
                    {'id': 5, 'tck': 'CVS', 'qty': 200.000},
                    {'id': 6, 'tck': 'DE', 'qty': 26.000},
                    {'id': 7, 'tck': 'ENB', 'qty': 116.000},
                    {'id': 8, 'tck': 'HD', 'qty': 22.000},
                    {'id': 9, 'tck': 'JPM', 'qty': 35.000},
                    {'id': 10, 'tck': 'KKR', 'qty': 185.000},
                    {'id': 11, 'tck': 'MPC', 'qty': 450.000},
                    {'id': 12, 'tck': 'MRK', 'qty': 72.000},
                    {'id': 13, 'tck': 'MET', 'qty': 90.000},
                    {'id': 14, 'tck': 'NXST', 'qty': 55.000},
                    {'id': 15, 'tck': 'PNR', 'qty': 60.000},
                    {'id': 16, 'tck': 'RTX', 'qty': 46.000},
                    {'id': 17, 'tck': 'SNY', 'qty': 100.000}]

    else:
        portfolio = [{'id': 1, 'tck': 'ABBV', 'qty': 225.000},
                    {'id': 2, 'tck': 'AZO', 'qty': 5.000},
                    {'id': 3, 'tck': 'STZ', 'qty': 100.000},
                    {'id': 4, 'tck': 'CCI', 'qty': 39.000},
                    {'id': 5, 'tck': 'CVS', 'qty': 200.000},
                    {'id': 6, 'tck': 'BOOB', 'qty': 26.000},
                    {'id': 7, 'tck': 'ENB', 'qty': 116.000}]

    # LOAD ENVIRONMENT VARIABLES ------------------------------------------------------------

    load_dotenv()
    ap_api_key = os.environ.get('ALPHAVANTAGE_API_KEY')
    fred_api_key = os.environ.get('FRED_API_KEY')


    # Pull in sp500 and rf rate data

    # Pull in portfolio data
    if APP_ENV == 'development':

        sub = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(
            __file__)), '..', 'data', "working_port.csv"), parse_dates=['timestamp', 'month'])
        sub['month']=sub['month'].dt.to_period('M')

        spy_join = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(
            __file__)), '..', 'data', "working_spy.csv"),index_col='month')

        fred_join = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(
            __file__)), '..', 'data', "working_fred.csv"), index_col='month')

        maxomin = sub['month'].min()
        minomax = sub['month'].max()


    else:

        spy_join = spy_pull(ap_api_key)
        fred_join = fred_pull(fred_api_key)

        sub, minomax, maxomin=port_data_pull(portfolio,ap_api_key)

    # Calculate returns
    results = []

    for i in [1,2,3,5]:

        temp_returns, temp_review = returns(sub, i, maxomin, minomax)

        results.append(temp_returns)


breakpoint()
