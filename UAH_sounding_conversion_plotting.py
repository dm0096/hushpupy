"""UAH Sounding Converter / Plotter

Preston Pangle and Dean Meyer 2020

This program takes in UAH sounding data, quality-controls the data, and 
outputs into 3 different formats:
- Research-Ready, easy to read data
- SHARPpy formatted data
- Raob formatted data

This program is designed for easy use and minimizing errors in the field. 
If you encounter bugs, please contact Preston Pangle or Dean Meyer at 
preston.pangle@uah.edu and dm0096@uah.edu, respectively.

Plots made with SHARPpy - https://sharppy.github.io/SHARPpy/
"""

from os import path
from UAH_windsond_program import convert_windsond
from UAH_imet_program import convert_imet

def verify_number(num):
    try:
        int(num)
        float(num)
    except Exception:
        raise TypeError('\nExpected a numeric entry!\n')
        
def verify_length(num, length):
    if len(num) != length:
        raise ValueError

def get_date():
    while True:
        date = str(input('Enter the launch date in UTC (YYYYMMDD): '))
        try:
            verify_number(date)
            verify_length(date, 8)
        except TypeError:
            print('\nExpected a numeric entry!\n')
            continue
        except ValueError:
            print('\nDate entry must be 8 digits long!\n')
            continue
        else:
            return date
            break
        
def get_time():
    while True:
        time = str(input('Enter the launch time in UTC (HHMM): '))
        try:
            verify_number(time)
            verify_length(time, 4)
        except TypeError:
            print('\nExpected a numeric entry!\n')
            continue
        except ValueError:
            print('\nTime entry must be 4 digits long!\n')
            continue
        else:
            return time
            break
        
def get_location():
    while True:
        location = str(input('Enter the launch site name (e.g. Huntsville): '))
        try:
            verify_length(location, 0)
        except ValueError:
            return location
            break
        else:
            print('\nLocation entry cannot be blank!\n')
            continue
        
def get_state():
    while True:
        st = str(input('Enter the launch state (e.g. AL): '))
        try:
            verify_length(st, 2)
        except ValueError:
            print('\nState entry must be two characters long!\n')
            continue
        else:
            return st
            break
        
def get_elevation():
    while True:
        elev = str(input('Enter the launch elevation in meters above MSL: '))
        try:
            verify_number(elev)
        except TypeError:
            print('\nExpected a numeric entry!\n')
            continue
        else:
            return elev
            break

while True:
    file = str(input('Drag and drop an iMet "TSPOTINT" or Windsond "raw_history" file here: '))
    file = file.replace('"', '')
    
    if path.basename(file).split(sep='.')[-2] == 'raw_history':
        print('\nWindsond file detected!\n')
        date = get_date()
        time = get_time()
        location = get_location()
        st = get_state()
        convert_windsond(file, date, time, location, st)
        print('\n\n\n')
        continue
        
    elif path.basename(file).split('.')[-2].split('_')[-1] == 'TSPOTINT':
        print('\niMet file detected!\n')
        date = get_date()
        time = get_time()
        location = get_location()
        st = get_state()
        elev = get_elevation()
        convert_imet(file, date, time, location, st, elev)
        print('\n\n\n')
        continue
        
    else:
        print('\nExpected an iMet "TSPOTINT" or Windsond "raw_history" file!\n')
        continue