#A container for various radiosonde data file formats
#Dean Meyer and Preston Pangle 2020

def write_sharppy(fname, df, location, state, lat, lon, yrshort, mo, day, time):
    """Write radiosonde data to a SHARPpy--compatible text file.

    Parameters
    ----------
    fname : str
        Name of the output file.
    df : DataFrame
        DataFrame with radiosonde data filed under format-compatible columns.
        SHARPpy requires these columns in this order:
            | Pressure (hPa) | Height (m) | Temperature (C) | Dewpoint Temp (C)
            | Wind Direction (deg) | Wind Speed (kt) |
    location : str
        The launch location (e.g. Huntsville).
    state : str
        The abbreviated launch state (e.g. AL).
    lat : str
        The launch site latitude.
    lon : str
        The launch site longitude.
    yrshort : str
        The launch year minus the century (ex. 2019 -> 19).
    mo : str
        The two-digit launch month (ex. April -> 04).
    day : str
        The two-digit UTC launch day (e.g. 02).
    time : str
        The UTC launch time in HHMM format (e.g. 1830).

    Returns
    -------
    A formatted .txt data file in the same directory.

    """
    with open(fname + '.txt', 'w') as f:
        f.write('%TITLE%\n')
        f.write(location + '_' + state + '_' + lat + '/' + lon + ' ' + yrshort + mo + day + '/' + time + '\n\n')
        f.write('LEVEL  HGHT  TEMP  DWPT WDIR  WSPD\n')
        f.write('----------------------------------\n')
        f.write('%RAW%\n')
        f.write(df.to_csv(header=False, index=False))
        f.write('%END%')
        f.close()

def write_research(fname, df, location, state, yr, mo, day, time, elev):
    """Write radiosonde data to a research--compatible text file.

    Parameters
    ----------
    fname : str
        Name of the output file.
    df : DataFrame
        DataFrame with radiosonde data filed under format-compatible columns.
        The research format requires these columns in this order:
            | latitude (deg) | longitude (deg) | UTC time (HH:MM:SS) 
            | height (m AGL) | pressure (mb) | temp (deg C) | RH (%) 
            | dewpoint (deg C) | wind speed (kts) | wind direction (deg) |
    location : str
        The launch location (e.g. Huntsville).
    state : str
        The abbreviated launch state (e.g. AL).
    yr : str
        The launch year (e.g. 2020).
    mo : str
        The two-digit launch month (ex. April -> 04).
    day : str
        The two-digit UTC launch day (e.g. 02).
    time : str
        The UTC launch time in HHMM format (e.g. 1830).
    elev : str
        The launch elevation in meters above MSL.

    Returns
    -------
    A formatted .txt data file in the same directory.

    """
    with open(fname + '.txt', 'w') as f:
        f.write('# UAH Radiosonde Data\n')
        f.write('# ' + yr + mo + day + ', ' + time + ' UTC, ' + location + ', ' + state + ', ' + elev + ' m\n')
        f.write('latitude (deg), longitude (deg),UTC (HH:MM:SS),height (m AGL),pressure(mb),temp (deg C),RH (%),dewpoint (deg C),wind speed (kts),wind direction (deg)\n')
        f.write(df.to_csv(header=False, index=False))
        f.write('%END%')
        f.close()
        
def write_raob(fname, df, lat, lon, elev): 
    """Write radiosonde data to a Raob--compatible text file.

    Parameters
    ----------
    fname : str
        Name of the output file.
    df : DataFrame
        DataFrame with radiosonde data filed under format-compatible columns.
        Raob requires these columns in this order:
            | Pressure (hPa) | Temperature (C) | Dewpoint Temp (C)
            | Wind Direction (deg) | Wind Speed (kt) | Altitude (m) |
    lat : str
        The launch site latitude.
    lon : str
        The launch site longitude.
    elev : str
        The launch site elevation in meters above MSL.

    Returns
    -------
    A formatted .txt data file in the same directory.

    """
    with open(fname + '.txt', 'w') as f:
        f.write('RAOB/CSV\n')
        f.write('LAT ' + lat + ', N\n')
        f.write('LON ' + lon + ', W\n')
        f.write('ELEV ' + str(elev) + ', M\n')
        f.write('MOISTURE, TD\n')
        f.write('WIND, kts\n')
        f.write('GPM, AGL\n')
        f.write('MISSING, -999\n')
        f.write('SORT, YES\n')
        f.write('RAOB/DATA\n')
        f.write('PRES, TEMP, TD, WIND, SPEED, GPM\n')
        f.write(df.to_csv(header=False, index=False))
        f.close()
        
    