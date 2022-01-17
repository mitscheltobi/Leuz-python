# A Python Implementation of Leuz Measures
Leuz, Christian & Nanda, Dhananjay & Wysocki, Peter. (2002). Earnings Management and Investor Protection: An International Comparison. Journal of Financial Economics. 69. 505-527. 10.1016/S0304-405X(03)00121-1. 
https://www.researchgate.net/publication/222699072_Earnings_Management_and_Investor_Protection_An_International_Comparison

## Application
This application can be used to iterate over, process and consolidate financial data to calculate Leuz measures, a statistical approach of measuring earnings smoothing and discretion.

Data can only be processed following a static format.
The structure must follow the guidelines of the [_data/data.csv](_data/data.csv) file. Currently only csv files in the from provided by the ORBIS database are supported.

## Usage
To process data and calculate EM measures follow these steps:
  1. use [CSVtoJSON.py](CSVtoJSON.py) to convert your data to JSON serialized python objects. The script will overwrite [/_data/python_objects.json](_data/python_objects.json) with the generated objects. Use `CSVtoJSON.py -h` for help on arguments and flags.
  3. use [leuz.py](leuz.py) to calculate the EM measures for your specified data & timeframe. Upon completion results will be printed to the terminal. Use `leuz.py -h` for help on arguments and flags.
  
## Dependencies
Please use Python 3.6 or later to run scripts.
This project uses a number of built-in python modules as well as the following 3rd party modules:
  1. jsonpickle // https://github.com/jsonpickle/jsonpickle
  2. numpy // https://github.com/numpy/numpy
  3. scipy // https://github.com/scipy/scipy

Please install all dependencies prior to running any script to avoid runtime errors.

## Further development:
- command line arguments for Data structure and custom behaviour
- support for conversion of data from other Databases such as SEC EDGER
