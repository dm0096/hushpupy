#A program for creating summaries of radiosonde flights
#Dean Meyer 2020



def print_summary(file, save_path, station, lat, lon, elev_sfc, p_sfc, temp, 
                  rh, wspd, wdir, ascent_rate, p_min, elev_max, sonde_type, 
                  serial='/////'):
    print(f'FLIGHT SUMMARY FOR "{file}"')
    print('+++++++++++++++++++++++++++++++++++++++++++++\n')
    print(f'Station     Name              > {station}')
    print(f'.           Latitude          > {lat} N')
    print(f'.           Longitude         > {lon} W')
    print(f'.           Elevation         > {elev_sfc} m\n')
    print(f'Sonde       Type              > {sonde_type}')
    print(f'.           Serial Number     > {serial}\n')
    print(f'Surface     Pressure          > {p_sfc} mb')
    print(f'.           Temperature       > {temp} C')
    print(f'.           Humidity          > {rh}%')
    print(f'.           Wind Speed        > {wspd} m/s')
    print(f'.           Wind Direction    > {wdir} deg\n')
    print(f'Flight      Minimum Pressure  > {p_min} mb')
    print(f'.           Maximum Altitude  > {elev_max} m')
    print(f'.           Ascent Rate       > {ascent_rate} m/s')

def save_summary(file, save_path, station, lat, lon, elev_sfc, p_sfc, temp, 
                  rh, wspd, wdir, ascent_rate, p_min, elev_max, sonde_type, 
                  serial='/////'):
    with open(f'{save_path}/{file}_SUMMARY.txt', 'w') as f:
        f.write(f'FLIGHT SUMMARY FOR "{file}"\n')
        f.write('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n')
        f.write(f'Station     Name              > {station}\n')
        f.write(f'.           Latitude          > {lat} N\n')
        f.write(f'.           Longitude         > {lon} W\n')
        f.write(f'.           Elevation         > {elev_sfc} m\n\n')
        f.write(f'Sonde       Type              > {sonde_type}\n')
        f.write(f'.           Serial Number     > {serial}\n\n')
        f.write(f'Surface     Pressure          > {p_sfc} mb\n')
        f.write(f'.           Temperature       > {temp} C\n')
        f.write(f'.           Humidity          > {rh} %\n')
        f.write(f'.           Wind Speed        > {wspd} m/s\n')
        f.write(f'.           Wind Direction    > {wdir} deg\n\n')
        f.write(f'Flight      Minimum Pressure  > {p_min} mb\n')
        f.write(f'.           Maximum Altitude  > {elev_max} m\n')
        f.write(f'.           Ascent Rate       > {ascent_rate} m/s')
        f.close()