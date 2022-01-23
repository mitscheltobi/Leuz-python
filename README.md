# A Python Implementation of Leuz Measures
Leuz, Christian & Nanda, Dhananjay & Wysocki, Peter. (2002). Earnings Management and Investor Protection: An International Comparison. Journal of Financial Economics. 69. 505-527. 10.1016/S0304-405X(03)00121-1. 
https://www.researchgate.net/publication/222699072_Earnings_Management_and_Investor_Protection_An_International_Comparison

## Application
This application can be used to iterate over, process and consolidate financial data to calculate Leuz measures, a statistical approach of measuring earnings smoothing and discretion.

Make sure to follow include all neccassary data for the calculation. To see relevant Orbis categories see [_data/_orbisRaw/Export default.xlsx](./_data/_orbisRaw/Export%20default.xlsx) for reference. Headers do not need to be in order. Currently only xlsx files in the from provided by the Orbis database are supported.

## Usage
To process data and calculate EM measures follow these steps:
  1. use [CSVtoJSON.py](CSVtoJSON.py) to convert your data to JSON serialized python objects. Use `CSVtoJSON.py -h` for help on arguments and flags. You can automatically save your file and execute the script that calculates the EM measures by adding the flag -c when executing the script. 
  2. You can also execute [leuz.py](leuz.py) manually afterwards to calculate the EM measures for your specified data & timeframe. Upon completion results will be printed to the terminal and saved to [/_results](/_results). Use `leuz.py -h` for help on arguments and flags.
  
## Dependencies
Please use Python 3.10 or later to run scripts.
This project uses a number of built-in python modules as well as the following 3rd party modules:
  1. jsonpickle // https://github.com/jsonpickle/jsonpickle
  2. numpy // https://github.com/numpy/numpy
  3. scipy // https://github.com/scipy/scipy
  4. pandas // https://github.com/pandas-dev/pandas

Please install all dependencies prior to running any script to avoid runtime errors.

## Further development:
- command line arguments for custom data structure / different headers
- support for conversion of data from other Databases such as SEC EDGER
