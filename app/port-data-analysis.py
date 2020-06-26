import pandas as pd
import os
import dotenv
from dotenv import load_dotenv
import datetime
import numpy as np

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


# GET FIRST AND LAST MONTHS

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


# CALCULATE RETURNS (this and others from https://www.codingfinance.com/post/2018-04-03-calc-returns-py/)

sub['mret'] = sub.groupby('ticker')['adj close'].pct_change()
sub['mretp1'] = sub['mret'] + 1

sub['sh val'] = sub['qty'] * sub['close']

pd_len = 5
pd_end = minomax
pd_start = max(minomax - (pd_len * 12), maxomin)


# Start Value of Assets
pd_start_val = sub.loc[sub['month']==pd_start]
pd_start_val = pd_start_val.set_index('ticker')
pd_start_val=pd_start_val['sh val'].rename('start val')

# Cum Return of Assets
cum_ret_set = sub.loc[(sub['month'] > pd_start) & (sub['month'] <= pd_end)]
cum_ret_set = cum_ret_set.set_index('ticker')
cum_ret_set['cumret'] = cum_ret_set.groupby('ticker')['mretp1'].cumprod()
cum_ret_set = cum_ret_set.join(pd_start_val, on='ticker')
cum_ret_set['mon val'] = cum_ret_set['start val'] * cum_ret_set['cumret']

port_ret = cum_ret_set.groupby('month')[['start val', 'mon val']].sum()
port_ret['cum ret'] = port_ret['mon val'] / port_ret['start val']
port_ret['mon ret'] = port_ret['mon val'].pct_change()

port_ret.loc[pd_start + 1, 'mon ret'] = port_ret.loc[pd_start + 1, 'cum ret'] - 1

# Calc Portf Return
tot_pd_ret = port_ret.loc[pd_end,'cum ret'] - 1
months = len(port_ret)
years = months / 12
avg_ann_ret = (1 + tot_pd_ret)**(1 / years) - 1
avg_mon_ret = (1 + tot_pd_ret)**(1 / months) - 1


breakpoint()

#Calc Return Std Dev
mon_sdev = cum_ret_set.groupby('ticker')['mret'].std()
ann_sdev = mon_sdev * (12 ** .5)

ret_calc = {'years_tgt': pd_len, 'years_act': years, 'st_date': pd_start, 'end_date': pd_end, 'ann_ret': avg_ann_ret, 'mon_ret': avg_mon_ret,'ann_sdev':ann_sdev, 'mon_sdev':mon_sdev}

breakpoint()
