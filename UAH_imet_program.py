#A program for converting and plotting iMet data
#Dean Meyer and Preston Pangle 2020

import pandas as pd
import numpy as np
import os
import shutil
from UAH_sounding_plotting import plot_sounding
from sounding_formats import write_sharppy, write_raob, write_research

def convert_imet(file, date, time, location, st, elev):
    #parse out date and time from user input
    yr = date[0:4]
    yrshort = date[2:4]
    mo = date[4:6]
    day = date[6:8]
    
    #read the file into a Pandas DataFrame with a datetime index
    df = pd.read_csv(file, header=0, skiprows=[1,2], delim_whitespace=True)
    df = df.set_index(pd.to_datetime(df['UTC_Time']))
    
    ##### Output raw data #####
    
    #convert wind speed to kt
    df['WSpeed'] = df['WSpeed'] * 1.944
    
    #find first lat/lon
    lat = str(np.round(df['Lat/N'].loc[df['Lat/N'].first_valid_index()], 3))
    lon = str(np.round(df['Long/E'].loc[df['Long/E'].first_valid_index()], 3))
    
    #perform final rounding on all float columns
    df['Lat/N'] = np.round(df['Lat/N'], 5)
    df['Long/E'] = np.round(df['Long/E'], 5)
    df['Alt_AGL'] = np.round(df['Alt_AGL'], 3)
    df['Press'] = np.round(df['Press'], 2)
    df['Temp'] = np.round(df['Temp'], 2)
    df['DP'] = np.round(df['DP'], 3)
    df['RelHum'] = np.round(df['RelHum'], 2)
    df['WSpeed'] = np.round(df['WSpeed'], 3)
    
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
    research_cols = ['Lat/N', 'Long/E', 'UTC_Time', 'Alt_AGL', 
                     'Press', 'Temp', 'RelHum',
                     'DP', 'WSpeed', 'WDirn']
    df_research = df[research_cols]
    sharppy_cols = ['Press', 'Alt_AGL', 'Temp', 
                    'DP', 'WDirn', 'WSpeed']
    df_sharppy = df[sharppy_cols]
    raob_cols = ['Press', 'Temp', 'DP', 
                 'WDirn', 'WSpeed', 'Alt_AGL']
    df_raob = df[raob_cols]
    
    fname = 'upperair.UAH_Sonde.' + yr + mo + day + time + '.' + location + '_' + st
    write_research(fname, df_research, location, st, yr, mo, day, time, str(elev))
    print('Raw research file created')
    write_sharppy(fname + '_sharppy', df_sharppy, location, st, lat, lon, yrshort, mo, day, time)
    print('Raw SHARPpy file created')
    write_raob(fname + '_raob', df_raob, lat, lon, elev)
    print('Raw RAOB file created')
    
    ##### Output QC data #####
    
    #resample data to 10 second intervals
    df = df.resample('10s').bfill()
    df = df.sort_values(by=['Alt_AGL']) #fix wrong order if crossing midnight
    
    #removing duplicate heights
    df = df.drop_duplicates(subset='Alt_AGL', keep='last')
    
    #fill NAN's with linearly interpolated values
    df = df.interpolate(method='linear')
    df = df.fillna(method='bfill')
    
    #write out files
    df_research = df[research_cols]
    df_sharppy = df[sharppy_cols]
    df_raob = df[raob_cols]
    
    fname = 'upperair.UAH_Sonde.' + yr + mo + day + time + '.' + location + '_' + st
    write_research(fname + '_QC', df_research, location, st, yr, mo, day, time, str(elev))
    print('QC research file created')
    write_sharppy(fname + '_sharppy_QC', df_sharppy, location, st, lat, lon, yrshort, mo, day, time)
    print('QC SHARPpy file created')
    write_raob(fname + '_raob_QC', df_raob, lat, lon, elev)
    print('QC RAOB file created')
    
    #move back to the original working directory
    os.chdir(cwd)
    
    #plot the sounding
    print('Plotting ...')
    plot_sounding(path + '/' + fname + '_sharppy_QC.txt', path + '/' + fname + '.png')