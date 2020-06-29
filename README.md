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
```
# data/.gitignore

# ignore all files in this directory:
*

# except this gitignore file:
!.gitignore
```
input:
```
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

Finally, set the APP_ENV variable to 'production'.  If set to something else "e.g. development", the program will bypass the API data retrieval process and pull previously downloaded data from the data folder.  To run the program in a development environment, you must run following apps independently:
```
python -m app.port_data_pull
python -m app.other_data_pull
```

From within the virtual environment, run the Python script from the command-line:

```sh
python app/robo_advisor.py
```
