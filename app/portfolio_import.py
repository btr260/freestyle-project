# portfolio_import.py

# IMPORT PACKAGES

import csv
import os
from dotenv import load_dotenv

# FUNTIONS

def hasnum(ticker_input_str):
    '''
    Checks string for presence of numeric character
    '''
    return any(char.isdigit() for char in ticker_input_str)


def portfolio_import(file_name):

    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'input', file_name)

    port_import = []

    with open(filepath, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            port_import.append(dict(row))

    #TODO: Data validation on input data

    return port_import


if __name__ == '__main__':

    file_name = os.getenv('PORTFOLIO_FILE_NAME', default='sample.csv')

    portfolio_import(file_name)
