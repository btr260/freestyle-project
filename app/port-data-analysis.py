import pandas as pd
import os
import dotenv
from dotenv import load_dotenv
import datetime
import numpy as np

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

    return ret_calc

# -------------------------------------------------------------------------------------
# CODE --------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------

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


tck_list = [t['tck'] for t in portfolio]


# Import saved data and combine --------------------------------------------------------

start_path = os.path.join(os.path.dirname(os.path.abspath(
    __file__)), '..', 'data', f"{tck_list[0]}.csv")

full = pd.read_csv(start_path, parse_dates=['timestamp'])


if len(tck_list) == 2:

    next_path = os.path.join(os.path.dirname(os.path.abspath(
        __file__)), '..', 'data', f"{tck_list[1]}.csv")

    temp_data = pd.read_csv(next_path, parse_dates=['timestamp'])

    full=full.append(temp_data)

else:

    for t in tck_list[1:len(tck_list)]:

        temp_path = os.path.join(os.path.dirname(os.path.abspath(
            __file__)), '..', 'data', f"{t}.csv")

        temp_data = pd.read_csv(temp_path, parse_dates=['timestamp'])
        #print(temp_data)

        full=full.append(temp_data)


full_sort = full.sort_values(by=['ticker', 'timestamp'])

# CREATE MONTH VARIABLE
full_sort['month'] = full_sort['timestamp'].dt.to_period('M')  # SOURCE: https://stackoverflow.com/questions/45304531/extracting-the-first-day-of-month-of-a-datetime-type-column-in-pandas

# Resize data for consistent periods -------------------------------------------------------

maxomin = full_sort.groupby('ticker')['month'].min()
#print(maxomin)
maxomin = maxomin.max()
#print(maxomin)

minomax = full_sort.groupby('ticker')['month'].max()
#print(minomax)
minomax = minomax.min()
#print(minomax)

# SUBSET DATA FOR FIRST/LAST MONTH
sub = full_sort.loc[(full_sort['month'] <= minomax) & (full_sort['month'] >= maxomin)]

sub = sub.sort_values(by=['ticker', 'month'])


# CALCULATE RETURNS
results = []

for i in [1,2,3,5]:
    results.append(returns(sub, i, maxomin, minomax))
