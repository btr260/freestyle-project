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


def to_pct(dec):
    '''
    Converts a numeric value to formatted string for printing and display purposes.

    Param: dec (int or float) like 0.403321

    Example: to_pct(0.403321)

    Returns: 40.33%
    '''
    return f'{dec:.2%}'


def two_dec(dec):
    '''
    Converts a numeric value to formatted string for printing and display purposes.

    Param: dec (int or float) like 4000.444444

    Example: two_dec(4000.444444)

    Returns: 4,000.44
    '''
    return f'{dec:,.2f}'

def pd_describe(mon_len):
    '''
    Converts a specified number of months to a text description of years and months.

    Param: mon_len (int) like 17

    Example: mon_len(17)

    Returns: 1 Year and 5 Months
    '''
    full_years = int(mon_len / 12)
    resid_months = mon_len % 12

    if (full_years > 0 and resid_months > 0):
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

def returns(dataset, period_length, min_start, max_end):

    '''
    Calculates various portfolio performance measures and prepares data for data visualization.
    '''
    # Calculate percent returns of individual portfolio positions
    working_data = dataset
    working_data['mret'] = working_data.groupby('ticker')['adj close'].pct_change()
    working_data['mretp1'] = working_data['mret'] + 1

    # Calculate share values over time (used to pull analysis period starting portfolio values)
    working_data['sh val'] = working_data['qty'] * working_data['close']

    # Define analysis period length.  For now, analysis period start date is
    # based on the data availability of the individual positions.  The most recent
    # first monthly data point for a given stock in the portfolio becomes the analysis
    # start date.  This is a limitation of the data/API.
    pd_len = period_length
    pd_end = max_end
    pd_start = max(max_end - (pd_len * 12), min_start)

    # Create dataset of asset values by position at the analysis start date
    pd_start_val = working_data.loc[working_data['month'] == pd_start]
    pd_start_val = pd_start_val.set_index('ticker')
    pd_start_val = pd_start_val['sh val'].rename('start val')

    # Caclulate cumulative returns and corresponding monthly values of individual
    # portfolio positions over time
    cum_ret_set = working_data.loc[(working_data['month'] > pd_start) & (working_data['month'] <= pd_end)]
    cum_ret_set = cum_ret_set.set_index('ticker')
    cum_ret_set['cumret'] = cum_ret_set.groupby('ticker')['mretp1'].cumprod()
    cum_ret_set = cum_ret_set.join(pd_start_val, on='ticker')
    cum_ret_set['mon val'] = cum_ret_set['start val'] * cum_ret_set['cumret']

    # Calculate monthly returns on the total portfolio over time
    port_ret = cum_ret_set.groupby('month')[['start val', 'mon val']].sum()
    port_ret['cum ret'] = port_ret['mon val'] / port_ret['start val']
    port_ret['mon ret'] = port_ret['mon val'].pct_change()

    # Replace analysis period start month portfolio return (was na due to
    # pct_change() function)
    port_ret.loc[pd_start + 1,
                 'mon ret'] = port_ret.loc[pd_start + 1, 'cum ret'] - 1

    # Merge in S&P 500 data from other_data_pull module
    port_ret = port_ret.join(spy_join)

    # Merge in 1Y constant maturity treasury data from other_data_pull module
    port_ret = port_ret.join(fred_join)

    # Calculate S&P 500 returns and cumulative return over analysis period
    port_ret['spretp1'] = port_ret['spret'] + 1
    port_ret['cum spret'] = port_ret['spretp1'].cumprod()
    port_ret = port_ret.drop(columns=['spretp1'])

    # Calculate portfolio and S&P 500 excess returns over risk free rate
    port_ret['exret'] = port_ret['mon ret'] - port_ret['rate']
    port_ret['exspret'] = port_ret['spret'] - port_ret['rate']

    # Calculate average annual and monthly returns
    months = len(port_ret)
    years = months / 12
    avg_ann_ret = (port_ret.loc[pd_end, 'cum ret'])**(1 / years) - 1
    avg_mon_ret = (port_ret.loc[pd_end, 'cum ret'])**(1 / months) - 1
    avg_ann_spret = (port_ret.loc[pd_end, 'cum spret'])**(1 / years) - 1
    avg_mon_spret = (port_ret.loc[pd_end, 'cum spret'])**(1 / months) - 1

    #Calculate return standard deviations
    mon_sdev = port_ret['mon ret'].std()
    ann_sdev = mon_sdev * (12 ** .5)

    mon_sp_sdev = port_ret['spret'].std()
    ann_sp_sdev = mon_sp_sdev * (12 ** .5)

    # Calculate portfolio beta (covariance of portfolio and S&P 500 divided by
    # volatility of S&P 500)
    beta = port_ret.cov().loc['mon ret', 'spret'] / port_ret.cov().loc['spret', 'spret']

    # Calculate sharpe ratios
    sharpe_port = (port_ret['exret'].mean() / port_ret['exret'].std()) * (12 ** .5)
    sharpe_sp = (port_ret['exspret'].mean() / port_ret['exspret'].std()) * (12 ** .5)

    # Assemble dictionary of calculation results
    ret_calc = {'years_tgt': pd_len, 'years_act': years, 'months_act': months, 'st_date': pd_start.strftime('%Y-%m'),
                'end_date': pd_end.strftime('%Y-%m'), 'ann_ret': avg_ann_ret, 'mon_ret': avg_mon_ret, 'ann_sdev': ann_sdev, 'mon_sdev': mon_sdev, 'ann_spret': avg_ann_spret, 'mon_spret': avg_mon_spret, 'ann_sp_sdev': ann_sp_sdev, 'mon_sp_sdev': mon_sp_sdev, 'beta': beta, 'sharpe_port': sharpe_port, 'sharpe_sp': sharpe_sp}

    # Create total (cumulative) returns dataset for data visualization
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

    # Testing error handling with portfolio definition

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
                    {'id': 6, 'tck': 'FAIL', 'qty': 26.000},
                    {'id': 7, 'tck': 'ENB', 'qty': 116.000}]

    # Loan environment variables

    load_dotenv()
    ap_api_key = os.environ.get('ALPHAVANTAGE_API_KEY')
    fred_api_key = os.environ.get('FRED_API_KEY')

    # Pull in portfolio data depending on app environment (to avoid unnecessary and
    # time consumingAPI calls)
    if APP_ENV == 'development':

        # Requires that each of other_data_pull and port_data_pull modules be
        # run separately/individually (i.e., not called from within this program)
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

        # Call on other_data_pull module for S&P 500 and risk free rate data from
        # Alpha Vantage and FRED (Federal Reserve Economic Data) APIs
        spy_join = spy_pull(ap_api_key)
        fred_join = fred_pull(fred_api_key)

        # Call on port_data_pull module for monthly data on individual portfolio stocks
        # from Alpha Vantage API
        sub, minomax, maxomin=port_data_pull(portfolio,ap_api_key)

    # Collect and store results, datasets, and chart elements for 1, 2, 3, and 5 year analysis periods
    # (but only if sufficient data exists for all portfolio positions).  If data are insufficient,
    # only store results for complete or near complete periods.  For example, if the longest data
    # sampling period for one stock in the portfolio is 2 years and 7 months, then the 3-year
    # analysis period will record results for a period of 2 years and 7 months, and the loop
    # will not bother with the 5-year calculations.
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




    # MAKE CHARTS/TABLES!
    axis_font = dict(size=16, family='Times New Roman')
    tick_font = dict(size=12, family='Times New Roman')
    for i in range(len(figs)):
        fig = make_subplots(rows=2, cols=1, vertical_spacing=0.03, row_width=[0.75,0.25], specs=[[{'type':'table'}], [{'type':'scatter'}]])
        fig.add_trace(figs[i]['port line'], row=2, col=1)
        fig.add_trace(figs[i]['sp line'], row=2, col=1,)

        pd_months = results[i]['months_act']

        fig.update_layout(title=dict(text=f'Portfolio Performance Report: Monthly Returns over Last {pd_describe(pd_months)}', font=dict(family='Times New Roman', size=20)))
        fig.update_layout(xaxis=dict(title=dict(text='Month', font=axis_font), ticks='outside', tickfont=tick_font))
        fig.update_layout(yaxis=dict(title=dict(text='Cumulative Monthly Returns (%)', font=axis_font), ticks='outside', tickfont=tick_font, tickformat='.1%'))
        fig.update_layout(legend=dict(orientation='h', font=axis_font))

        col1 = ['Avg. Annual Return', 'Std. Dev. (Ann.)', 'Sharpe Ratio', 'Beta']
        col2 = [to_pct(results[i]['ann_ret']), to_pct(results[i]['ann_sdev']), two_dec(results[i]['sharpe_port']), two_dec(results[i]['beta'])]
        col3 = [to_pct(results[i]['ann_spret']), to_pct(results[i]['ann_sp_sdev']), two_dec(results[i]['sharpe_sp']), two_dec(1.00)]

        fig.add_trace(go.Table(header=dict(values=['Statistic', 'Portfolio', 'S&P 500']), cells=dict(values=[col1, col2, col3])),row=1,col=1)

        fig.show()
