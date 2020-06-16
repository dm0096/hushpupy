#A program for converting and plotting windsond data
#Dean Meyer and Preston Pangle 2020

import pandas as pd
import numpy as np
import os
import shutil
import plot_sounding #separate script for plotting SHARPpy soundings
from sounding_formats import write_sharppy, write_raob, write_research

import warnings # silence Pandas warnings
warnings.filterwarnings("ignore")

def convert_windsond(file, date, time, location, st):
    #parse out date and time from user input
    yr = date[0:4]
    yrshort = date[2:4]
    mo = date[4:6]
    day = date[6:8]
    
    #read the file into a Pandas DataFrame with a datetime index
    df = pd.read_csv(file, na_values=['  ', ' '])
    df = df.set_index(pd.to_datetime(df['UTC time']))
    
    ##### Output raw data #####
    
    #convert pressure to hPa
    df['Pressure (hPa)'] = df[' Pressure (Pascal)'] / 100
    
    #convert speed to kt
    df['Speed (kt)'] = df[' Speed (m/s)'] * 1.944
    
    #calculate Td from T and RH using Bolton's equation
    df['Dewpoint (C)'] = (243.5*(np.log(df[' Relative humidity (%)']/100)+(17.67*df[' Temperature (C)']/(243.5+df[' Temperature (C)']))))/(17.67-np.log(df[' Relative humidity (%)']/100)-(17.67*df[' Temperature (C)']/(243.5+df[' Temperature (C)'])))
    df['Dewpoint (C)'] = np.round(df['Dewpoint (C)'], 3)
    
    #find first lat/lon
    lat = str(np.round(df[' Latitude'].loc[df[' Latitude'].first_valid_index()], 3))
    lon = str(np.round(df[' Longitude'].loc[df[' Longitude'].first_valid_index()], 3))
    
    #find first elevation
    elev = df[' Altitude (m MSL)'][0]
    
    #perform final rounding on all float columns
    df[' Latitude'] = np.round(df[' Latitude'], 5)
    df[' Longitude'] = np.round(df[' Longitude'], 5)
    df['Pressure (hPa)'] = np.round(df['Pressure (hPa)'], 2)
    df[' Temperature (C)'] = np.round(df[' Temperature (C)'], 2)
    df['Dewpoint (C)'] = np.round(df['Dewpoint (C)'], 3)
    df[' Relative humidity (%)'] = np.round(df[' Relative humidity (%)'], 2)
    df['Speed (kt)'] = np.round(df['Speed (kt)'], 2)
    df[' Heading (degrees)'] = np.round(df[' Heading (degrees)'], 1)
    
    #get current working directory
    cwd = os.getcwd()
    
    #create output directory if it exists and move to it
    # folder = os.path.expanduser('~/Desktop') + '\Converted_Sounding_Files'
    folder = 'C:/Converted_Soundings'
    if not os.path.exists(folder):
    	os.mkdir(folder)
    path = folder + '/' + yr + mo + day + '_' + time
    if not os.path.exists(path):
    	os.mkdir(path)
    os.chdir(path)
    
    #copy original file to the new folder
    try:
        shutil.copy(file, path)
    except shutil.SameFileError:
        print('')
    
    #write out files
    research_cols = [' Latitude', ' Longitude', 'UTC time', ' Altitude (m AGL)', 
                     'Pressure (hPa)', ' Temperature (C)', ' Relative humidity (%)',
                     'Dewpoint (C)', 'Speed (kt)', ' Heading (degrees)']
    df_research = df[research_cols]
    sharppy_cols = ['Pressure (hPa)', ' Altitude (m MSL)', ' Temperature (C)', 
                    'Dewpoint (C)', ' Heading (degrees)', 'Speed (kt)']
    df_sharppy = df[sharppy_cols]
    raob_cols = ['Pressure (hPa)', ' Temperature (C)', 'Dewpoint (C)', 
                 ' Heading (degrees)', 'Speed (kt)', ' Altitude (m AGL)']
    df_raob = df[raob_cols]
    
    fname = 'upperair.UAH_Sonde.' + yr + mo + day + time + '.' + location + '_' + st
    write_research(fname, df_research, location, st, yr, mo, day, time, str(elev))
    print('Raw research file created')
    write_sharppy(fname + '_sharppy', df_sharppy, location, st, lat, lon, yrshort, mo, day, time)
    print('Raw SHARPpy file created')
    write_raob(fname + '_raob', df_raob, lat, lon, elev)
    print('Raw RAOB file created')
    
    
    ##### Output QC data #####
    
    #remove rows with duplicate timestamps, keeping first point
    df = df.loc[~df.index.duplicated(keep='first')]
    
    #correct negative AGL heights
    df[' Altitude (m AGL)'] = df[' Altitude (m AGL)'] + df[' Altitude (m AGL)'][0] * -1
    
    #find index where rise speed is first > 0.5 m/s
    try:
        idx = df.loc[df[' Rise speed (m/s)'] > 0.5].index[0]
    except IndexError:
        print('\nOops! The balloon never reached 0.5 m/s. No QC files produced!\n')
        return None
        
    #subset dataframe after that index
    df = df[idx:df.index[-1]]
    
    #only get rows where height is monotonically increasing
    mon_inc = df[' Altitude (m MSL)'].cummax().diff() > 0
    df = df[mon_inc]
    
    #correct "flipped winds" problem
    #
    #raw wind data is direction winds "go to," but hodograph needs the
    #direction winds "come from."
    #Therefore, add 180 degrees for headings < 180 and subtract 180 for
    #headings > 180
    condlist = [df[' Heading (degrees)'] < 180., 
                df[' Heading (degrees)'] > 180.]
    choicelist = [df[' Heading (degrees)'] + 180.,
                  df[' Heading (degrees)'] - 180.]
    df[' Heading (degrees)'] = np.select(condlist, choicelist)
    #replace bad zero values with the next nonzero observation
    df[' Heading (degrees)'] = df[' Heading (degrees)'].replace(to_replace=0, method='bfill')
    
    #exponentially weighted moving window mean on wind dir and speed data
    df[' Heading (degrees)'] = df[' Heading (degrees)'].ewm(30).mean()
    df['Speed (kt)'] = df['Speed (kt)'].ewm(30).mean()
    df[' Heading (degrees)'][0] = np.nan #first value is bad
    
    #fill NAN's with linearly interpolated values
    df = df.interpolate(method='linear')
    df = df.fillna(method='bfill')
    
    #resample data to 10 second intervals
    df = df.resample('10s').bfill()
    df = df.sort_values(by=[' Altitude (m MSL)']) #fix wrong order if crossing midnight
    
    #removing duplicate heights
    df = df.drop_duplicates(subset=' Altitude (m MSL)', keep='last')
    
    #find lat/lon of launch
    lat = str(np.round(df[' Latitude'][0], 3))
    lon = str(np.round(df[' Longitude'][0], 3))
    
    #perform final rounding on all float columns
    df[' Latitude'] = np.round(df[' Latitude'], 5)
    df[' Longitude'] = np.round(df[' Longitude'], 5)
    df['Pressure (hPa)'] = np.round(df['Pressure (hPa)'], 2)
    df[' Temperature (C)'] = np.round(df[' Temperature (C)'], 2)
    df['Dewpoint (C)'] = np.round(df['Dewpoint (C)'], 3)
    df[' Relative humidity (%)'] = np.round(df[' Relative humidity (%)'], 2)
    df['Speed (kt)'] = np.round(df['Speed (kt)'], 2)
    df[' Heading (degrees)'] = np.round(df[' Heading (degrees)'], 1)
    
    #write out files
    df_research = df[research_cols]
    df_sharppy = df[sharppy_cols]
    df_raob = df[raob_cols]
    
    fname = 'upperair.UAH_Sonde.' + yr + mo + day + time + '.' + location + '_' + st
    write_research(fname + '_calc', df_research, location, st, yr, mo, day, time, str(elev))
    print('QC research file created')
    write_sharppy(fname + '_sharppy_calc', df_sharppy, location, st, lat, lon, yrshort, mo, day, time)
    print('QC SHARPpy file created')
    write_raob(fname + '_raob_calc', df_raob, lat, lon, elev)
    print('QC RAOB file created')
    
    #move back to the original working directory for plotting
    os.chdir(cwd)
    
    #plot the sounding
    print('Plotting ...')
    plot_sounding.plot(path + '/' + fname + '_sharppy_calc.txt', path)