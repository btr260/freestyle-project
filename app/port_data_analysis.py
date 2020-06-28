import pandas as pd
import os
import dotenv
from dotenv import load_dotenv
import datetime
import numpy as np
import plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from app.other_data_pull import spy_pull, fred_pull
from app.port_data_pull import port_data_pull
from app import APP_ENV

# -------------------------------------------------------------------------------------
# FUNCTIONS ---------------------------------------------------------------------------
# -------------------------------------------------------------------------------------


def to_usd(my_price):
    '''
    Converts a numeric value to usd-formatted string, for printing and display purposes.

    Param: my_price (int or float) like 4000.444444

    Example: to_usd(4000.444444)

    Returns: $4,000.44
    '''
    return f'${my_price:,.2f}'  # > $12,000.71


def pd_describe(mon_len):
    '''
    Converts a specified number of months to a text description of years and months.
    '''
    full_years = int(mon_len / 12)
    resid_months = mon_len % 12

    if full_years > 0 & resid_months > 0:
        join_str = ' and '
    else:
        join_str = ''

    if full_years == 0:
        yr_str = ''
    elif full_years == 1:
        yr_str = f'{full_years} Year'
    else:
        yr_str = f'{full_years} Years'

    if resid_months == 0:
        mon_str = ''
    elif resid_months == 1:
        mon_str = f'{resid_months} Month'
    else:
        mon_str=f'{resid_months} Months'

    pd_detail=f'{yr_str}{join_str}{mon_str}'

    return pd_detail

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

    port_ret = port_ret.join(spy_join)

    port_ret = port_ret.join(fred_join)

    port_ret['spretp1'] = port_ret['spret'] + 1
    port_ret['cum spret'] = port_ret['spretp1'].cumprod()
    port_ret = port_ret.drop(columns=['spretp1'])

    port_ret['exret'] = port_ret['mon ret'] - port_ret['rate']
    port_ret['exspret'] = port_ret['spret'] - port_ret['rate']


    # Calc Portf Return
    months = len(port_ret)
    years = months / 12
    avg_ann_ret = (port_ret.loc[pd_end, 'cum ret'])**(1 / years) - 1
    avg_mon_ret = (port_ret.loc[pd_end, 'cum ret'])**(1 / months) - 1
    avg_ann_spret = (port_ret.loc[pd_end, 'cum spret'])**(1 / years) - 1
    avg_mon_spret = (port_ret.loc[pd_end, 'cum spret'])**(1 / months) - 1


    #Calc Return Std Dev
    mon_sdev = port_ret['mon ret'].std()
    ann_sdev = mon_sdev * (12 ** .5)

    mon_sp_sdev = port_ret['spret'].std()
    ann_sp_sdev = mon_sp_sdev * (12 ** .5)

    beta = port_ret.cov().loc['mon ret', 'spret'] / port_ret.cov().loc['spret', 'spret']

    sharpe_port = (port_ret['exret'].mean() / port_ret['exret'].std()) * (12 ** .5)
    sharpe_sp = (port_ret['exspret'].mean() / port_ret['exspret'].std()) * (12 ** .5)

    ret_calc = {'years_tgt': pd_len, 'years_act': years, 'months_act': months, 'st_date': pd_start.strftime('%Y-%m'),
                'end_date': pd_end.strftime('%Y-%m'), 'ann_ret': avg_ann_ret, 'mon_ret': avg_mon_ret, 'ann_sdev': ann_sdev, 'mon_sdev': mon_sdev, 'ann_spret': avg_ann_spret, 'mon_spret': avg_mon_spret, 'ann_sp_sdev': ann_sp_sdev, 'mon_sp_sdev': mon_sp_sdev, 'beta': beta, 'sharpe_port': sharpe_port, 'sharpe_sp': sharpe_sp}

    tot_ret_data = port_ret[['cum ret', 'cum spret']] - 1
    app_df = pd.DataFrame([[tot_ret_data.index.min() - 1, 0, 0]], columns=['month', 'cum ret', 'cum spret']).set_index('month')
    tot_ret_data=tot_ret_data.append(app_df).sort_index()
    tot_ret_data.index = tot_ret_data.index.to_series().astype(str)
    tot_ret_dict = tot_ret_data.reset_index().to_dict(orient='list')


    return ret_calc, tot_ret_dict, port_ret

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
            __file__)), '..', 'data', "working_spy.csv"), parse_dates=['month'])
        spy_join['month'] = spy_join['month'].dt.to_period('M')
        spy_join=spy_join.set_index('month')

        fred_join = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(
            __file__)), '..', 'data', "working_fred.csv"), parse_dates=['month'])
        fred_join['month'] = fred_join['month'].dt.to_period('M')
        fred_join=fred_join.set_index('month')

        maxomin = sub['month'].min()
        minomax = sub['month'].max()


    else:

        spy_join = spy_pull(ap_api_key)
        fred_join = fred_pull(fred_api_key)

        sub, minomax, maxomin=port_data_pull(portfolio,ap_api_key)

    # Calculate returns
    results = []
    tot_ret=[]

    x = 0
    keep = []
    figs = []

    for i in [1,2,3,5]:
        if x==0:
            temp_returns, temp_tot, temp_review = returns(sub, i, maxomin, minomax)
            results.append(temp_returns)
            tot_ret.append(temp_tot)
            keep.append(i)

            figs.append({'port line': go.Scatter(x=temp_tot['month'], y=temp_tot['cum ret'], name='Portfolio Cumulative Return', line=dict(color='firebrick', width=4)), 'sp line': go.Scatter(x=temp_tot['month'], y=temp_tot['cum spret'], name='S&P 500 Cumulative Return', line=dict(color='royalblue', width=4))})

            if temp_returns['years_tgt'] != temp_returns['years_act']:
                x = 1





    axis_font = dict(size=16, family='Times New Roman')
    tick_font = dict(size=12, family='Times New Roman')
    for i in range(len(figs)):
        fig=go.Figure()
        fig.add_trace(figs[i]['port line'])
        fig.add_trace(figs[i]['sp line'])

        pd_months = results[i]['months_act']

        fig.update_layout(title=dict(text=f'Cumulative Returns ({pd_describe(pd_months)})', font=dict(family='Times New Roman', size=20)))
        fig.update_layout(xaxis=dict(title=dict(text='Month', font=axis_font), ticks='outside', tickfont=tick_font))
        fig.update_layout(yaxis=dict(title=dict(text='Cumulative Monthly Returns (%)', font=axis_font), ticks='outside', tickfont=tick_font, tickformat='.1%'))
        fig.update_layout(legend=dict(orientation='h', font=axis_font, x=0, y=1))
        fig.show()

        riskret_x = [results[i]['ann_sp_sdev'], results[i]['ann_sdev']]
        riskret_y = [results[i]['ann_spret'], results[i]['ann_ret']]

        fig_huh = go.Figure(data=go.Scatter(x=riskret_x, y=riskret_y, mode='markers', marker=dict(size=[20, 20], color=['royalblue', 'firebrick'])))

        fig_huh.show()

    breakpoint()

test_fig = make_subplots(rows=1, cols=2, specs=[[{'type':'scatter'}, {'type':'table'}]])
test_fig.add_trace(figs[3]['port line'], row=1, col=1)
test_fig.add_trace(figs[3]['sp line'], row=1, col=1)


col1 = ['Avg. Annual Return', 'Std. Dev. (Ann.)', 'Sharpe Ratio', 'Beta']
col2 = [results[3]['ann_ret'], results[3]['ann_sdev'], results[3]['sharpe_port'], results[3]['beta']]
col3 = [results[3]['ann_spret'], results[3]['ann_sp_sdev'], results[3]['sharpe_sp'], 1]



test_fig.add_trace(go.Table(header=dict(values=['Statistic', 'Portfolio', 'S&P 500']), cells=dict(values=[col1, col2, col3])),row=1,col=2)
