# The Freestyle Project - Portfolio Performance Analyzer

## Program Overview

  1. Take portfolio information (ticker, quantity) from a CSV file prepared by the user and placed in the input folder of the repository.
  2. Send list of tickers to Alpha Vantage API and retrieve historical market data.
  3. Request S&P 500 data from Alpha Vantage API and risk free rate data (1Y t-bill rates) from Federal Reserve Economic Data (FRED) API.
  4. Save all market data as CSV files.
  5. Process data into a dataset of portfolio and benchmark returns.
  6. Use calculated returns to take various portfolio performance measurements.
  7. Present portfolio performance measurements using data visualization tools.


### Repo Setup

Use the GitHub.com online interface to create a new remote project repository called something like "portfolio-analyzer". When prompted by the GitHub.com online interface, add a "README.md" file and a Python-flavored ".gitignore" file (and also a "LICENSE") during the repo creation process. After this process is complete, you should be able to view the repo on GitHub.com at an address like `https://github.com/YOUR_USERNAME/portfolio-analyzer`.

After creating the remote repo, use GitHub Desktop software or the command-line to download or "clone" it onto your computer. Choose a familiar download location like the Desktop.

After cloning the repo, navigate there from the command-line:

```sh
cd ~/Desktop/portfolio-analyzer
```

Create and activate a new Anaconda virtual environment:

```sh
conda create -n portfolio-env python=3.7 # (first time only)
conda activate portfolio-env
```

From within the virtual environment, install the required packages specified in the "requirements.txt" file:

```sh
pip install -r requirements.txt
```

If not already present in the folders, add .gitignore files to the data and input subfolders.  They should read as follows:

data:
```sh
# data/.gitignore

# ignore all files in this directory:
*

# except this gitignore file:
!.gitignore
```

input:
```sh
# input/.gitignore

# ignore all files in this directory:
*

# except this gitignore and the sample portfolio files:
!.gitignore
!sample.csv
```

### Portfolio CSV File

In the input folder, you will find a sample portfolio CSV file.  Create your own portfolio CSV file following the same format as the sample file.  [Note - the .gitignore will keep your portfolio information from being uploaded to GitHub.]

Please take care with this step as ticker and portfolio data validations have not been incorporated into this version of the software.  [In this version, the program will notify you if a ticker was not found on Alpha Vantage and exit the program.]


### Setting Environment Variables

In the directory, create a .env file.  In the .env file, add the following:

```sh
ALPHAVANTAGE_API_KEY="abc123"

FRED_API_KEY="xyz789"

PORTFOLIO_FILE_NAME='sample.csv'

APP_ENV='production'
```

In the .env file, you MUST specify your API keys (i.e., replacing abc123 in the text shown above).  You can obtain an API keys from:
1. [AlphaVantage API](https://www.alphavantage.co).
2. [Federal Reserve (FRED) API] (https://fred.stlouisfed.org/docs/api/fred/)


In the .env file, you must also specify the file name of a CSV file that contains your portfolio information.  By default, this variable is set to the name of the sample CSV file.

Finally, set the APP_ENV variable to 'production'.  If set to something else "e.g. development", the program will bypass the API data retrieval process.  More detail on this to follow.


### Running the app

From within the virtual environment, run the Python app from the command-line:

```sh
python -m app.port_data_analysis
```

All supporting modules will be imported into this one app.

The app will first import your portfolio from the input folder.  The relevant code can be found in the portfolio_import module (see portfolio_import.py in the app folder).

Then, the app will pull S&P 500 data from the Alpha Vantage API and 1Y T-Bill rates from the FRED API.  These data will be saved down in the data folder and prepared for later use.  The relevant code can be found in the spy_pull and fred_pull modules (see other_data_input.py in the app folder).

Next, the portfolio will retrieve data from the Alpha Vantage API for the tickers provided in the portfolio input file.  As mentioned above, if there are issues with your portfolio input tickers, the program will list the faulty tickers and ask you to try again before ending.  If the tickers are successfully found, the program will proceed with its analysis.  PLEASE NOTE: the data  retrieval step can take several minutes depending on the number of tickers included in your portfolio.  Alpha Vantage only allows 5 API calls per minute, so the app will look at the number of tickers in your portfolio file and batch them into groups of five, running each batch with a one minute (and 10 second) delay in between.  The relevant code can be found in the port_data_pull module (see port_data_pull.py in the app folder).

Once the data have been collected, returns are calculated, datasets are combined, and other statistics are measured.  Results are shown for periods of 1, 2, 3, and 5 years if sufficient data exists for each of the portfolio positions.  If a position has a data history shorter than 5 years, then adjustments are made to the period lengths.  For example, if a portfolio stock only has 2 years and 6 months of data, then the program will analyze the portfolio's performance over 1, 2, and 2.5 year periods (i.e., abbreviating the 3 year measurement and skipping the 5th year measurement).  The relevant code can be found in the port_data_analysis module (see port_data_analysis.py in the app folder).

Once the analysis has been performed for each period, the results are shown in a portfolio report (opened automatically via your browser) using Plotly data visualization tools.


### Running the app in a development environment

If you are interested in testing or expanding upon the portfolio analysis portion of the code, you may wish to avoid re-pulling data from the Alpha Vantage API with each run.  To do so, you can set the APP_ENV environment variable to "development" (or some string other than "production").  HOWEVER, before running the app in the development environment, you MUST run each of the other_data_pull and port_data_pull apps SEPARATELY and INDEPENDENTLY from the command-line:

```sh
python -m app.other_data_pull
python -m app.port_data_pull
```

Running these on their own will prepare working datasets and save them in the CSV folder.  The port_data_analysis app will then pull from these files rather than calling on the port_data_pull and other_data_pull modules.
