"""
Plotting a sounding with indices and a hodograph
================================================

"""

import warnings # Silence the warnings from SHARPpy
warnings.filterwarnings("ignore")
import os
import sharppy.plot.skew as skew
from matplotlib.ticker import ScalarFormatter, MultipleLocator
from matplotlib.collections import LineCollection
import matplotlib.transforms as transforms
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.patheffects as pe
from datetime import datetime
import numpy as np
from matplotlib import gridspec
from sharppy.sharptab import winds, utils, params, thermo, interp, profile
from sharppy.io.spc_decoder import SPCDecoder
import pandas as pd
from matplotlib import cm
from matplotlib.colors import ListedColormap

# Bounds of the pressure axis 
# pb_plot=1050
# pt_plot=300
# dp_plot=10
# plevs_plot = np.arange(pb_plot,pt_plot-1,-dp_plot)

def decode(filename):

    dec = SPCDecoder(filename)

    if dec is None:
        raise IOError("Could not figure out the format of '%s'!" % filename)

    # Returns the set of profiles from the file that are from the "Profile" class.
    profs = dec.getProfiles()
    stn_id = dec.getStnId()

    for k in list(profs._profs.keys()):
        all_prof = profs._profs[k]
        dates = profs._dates
        for i in range(len(all_prof)):
            prof = all_prof[i]
            new_prof = profile.create_profile(pres=prof.pres, hght=prof.hght, tmpc=prof.tmpc, dwpc=prof.dwpc, wspd=prof.wspd, \
                                              wdir=prof.wdir, strictQC=False, profile='convective', date=dates[i])
            return new_prof, dates[i], stn_id 
 
#routine to plot significant levels
def plot_sig_levels(ax, prof):
    # Plot LCL, LFC, EL labels (if it fails, inform the user.)
    trans = transforms.blended_transform_factory(ax.transAxes, ax.transData)
    try:    
        ax.text(0.90, prof.mupcl.lclpres, '- LCL', verticalalignment='center', transform=trans, color='lime')
    except:
        print("couldn't plot LCL")

    if np.isfinite(prof.mupcl.lfcpres):
        ax.text(0.90, prof.mupcl.lfcpres, '- LFC', verticalalignment='center', transform=trans, color='yellow')
    else:    
        print("couldn't plot LFC")

    try:
        ax.text(0.90, prof.mupcl.elpres, '- EL', verticalalignment='center', transform=trans, color='magenta')
    except:
        print("couldn't plot EL")

    return ax

def draw_mixing_ratio_lines(ax, spacing=[6,10,14,18,22,26,30,34], color='g', lw=.7):
# def draw_mixing_ratio_lines(ax, spacing=[2,4,10,12,14,16,18,20], color='g', lw=.7):
    # plot the mixing ratio lines
    for w in spacing:
        line = thermo.temp_at_mixrat(w, np.arange(1000,600,-1))
        ax.semilogy(line, np.arange(1000,600,-1), '--', color=color, lw=lw)
        x = line[-1]
        y = 600
        ax.annotate(str(w), xy=(x,y), color='g', size=7,
                    xytext=(-2,2), textcoords="offset points")
    return ax

#routine to draw the inset for the hodograph data
def draw_hodo_inset(ax, prof):
    # Draw the hodograph axes on the plot.
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    inset_axes = inset_axes(ax,width=4.5, # width = 30% of parent_bbox
                                        height=4.5, # height : 1 inch
                                        loc='center')
    inset_axes.get_xaxis().set_visible(False)
    inset_axes.get_yaxis().set_visible(False)

    # Draw the range rings around the hodograph.
    for i in range(10,120,10):
        circle = Circle((0,0),i,color='silver',alpha=.3, fill=False)
        if i % 10 == 0 and i <= 70:
            inset_axes.text(-i,-8,str(i), fontsize=8, horizontalalignment='center', color='w')
        inset_axes.add_artist(circle)
    inset_axes.set_xlim(-80,80)
    inset_axes.set_ylim(-80,80)
    inset_axes.axhline(y=0, color='w')
    inset_axes.axvline(x=0, color='w')
    inset_axes.spines['left'].set_color('w')
    inset_axes.spines['right'].set_color('w')
    inset_axes.spines['bottom'].set_color('w')
    inset_axes.spines['top'].set_color('w')
    #srwind = tab.params.bunkers_storm_motion(prof)
    inset_axes.set_facecolor('k')
    return inset_axes

# Routine to plot the hodograph in segments (0-3 km, 3-6 km, etc.)
def plotHodo(axes, h, u, v, color='k'):
    for color, min_hght in zip(['r', 'lime', 'yellow', 'cyan'], [3000,6000,9000,12000]):
        below_12km = np.where((h <= min_hght) & (h >= min_hght - 3000))[0]
        if len(below_12km) == 0:
            continue
        # below_12km = np.append(below_12km, below_12km[-1] + 1)
        # Try except to ensure missing data doesn't cause this routine to fail.
        try:
            axes.plot(u[below_12km][~u.mask[below_12km]],v[below_12km][~v.mask[below_12km]], color, lw=2, ls='-')
        except Exception as e:
            print(e)
            continue
        
# Routine to plot the axes for the wind profile
def plot_wind_axes(axes, pb_plot, pt_plot, plevs_plot):
    # plot wind barbs
    draw_wind_line(axes, plevs_plot)
    axes.set_axis_off()
    axes.axis([-1,1,pb_plot,pt_plot])

# Small routine to find error between (a)ctual and (e)xpected values
def error(a, e):
    err = np.abs((a-e)/e)
    return err

# Routine to plot the wind barbs.
def plot_wind_barbs(axes, p, u, v, pt_plot):
    # for i in np.arange(0,len(p)):
    #     if (p[i] > pt_plot):
    #         if np.ma.is_masked(v[i]) is True:
    #             continue
            
#            C = np.sqrt(u**2 + v**2)
#            cmap = plt.cm.viridis
#            axes.barbs(0,p[i],u[i],v[i], C, length=7, clip_on=False, linewidth=1, flagcolor='k', cmap=cmap)

            # axes.barbs(0,p[i],u[i],v[i], length=7, clip_on=False, linewidth=1, barbcolor='w', flagcolor='k')
    
    #custom colormap
    hsv = cm.get_cmap('hsv_r', 256)
    newcolors = hsv(np.linspace(0, 1, 256))[128:,:]
    newcmp = ListedColormap(newcolors)
    
    df = pd.DataFrame({'p':p,'u':u,'v':v})
    df = df[df['p'] > pt_plot]
    
    #determining how many barbs to plot
    window = np.abs(1050-pt_plot)
    plot = np.abs(df['p'].iloc[0]-df['p'].iloc[-1])
    frac = 1 - error(plot, window)
    numBarbs = round(frac * 20) #number of barbs to be displayed, max 20
    idx = np.round(np.linspace(0, len(df) - 1, numBarbs))
    df = df.iloc[idx]
    
    C = np.sqrt(df['u']**2 + df['v']**2)
    # df = df[np.ma.is_masked(df['v']) == False]
    axes.barbs(np.zeros(len(df['p'])),df['p'],df['u'],df['v'], C, length=7, clip_on=False, linewidth=1, cmap=newcmp, flagcolor='k')
    

# Routine to draw the line for the wind barbs
def draw_wind_line(axes, plevs_plot):
    wind_line = []
    for p in plevs_plot:
        wind_line.append(0)
    axes.semilogy(wind_line, plevs_plot, color='w', linewidth=.5)
    
# Find an ideal temperature range based on the standard SHARPpy plot
def trange(p):
    rat = 9.5 #ratio between pressure range and temp range on a SHARPpy plot
    tran = round((1050-p)/rat)
    return tran

# Function to ask the user for the sharppy data file name
def get_file():
    file = str(input('Drag and drop a SHARPpy format data file here: '))
    file = file.replace('"', '')
    file = file.replace("'", '')
    return file

# Function to ask the user what limits they want for the skew-T
def ask_limits(pres, td):
    pmin = pres[-1]
    tdfirst = td[0]
    
    if pmin > 700.:
        auto_tl = round(tdfirst - (trange(pmin - 25.)*0.3))
        auto_tu = round(tdfirst + (trange(pmin - 25.)*0.5))
    else:
        auto_tl = round(tdfirst - (trange(pmin - 25.)*0.6))
        auto_tu = round(tdfirst + (trange(pmin - 25.)*0.35))
    
    print('\n Skew-T Options\n')
    print(f'     Auto:       1050 to {pmin - 25} mb, {auto_tl} to {auto_tu} deg C   (default)\n')
    print('     SHARPpy:    1050 to 100 mb, -50 to 50 deg C            \n')
    print('     Zoomed:     1050 to 300 mb, -20 to 40 deg C            \n')
    print('     Custom:     1050 to ? mb, ? to ? deg C                 \n')
    while True:
        print(f'Your data ends at {pmin} mb')
        res = str(input('Use default limits for the Skew-T? (y/n) '))
        if res == 'y':
            pu = pmin - 25.
            tl = auto_tl
            tu = auto_tu
            break
        if res == 'n':
            while True:
                pu = float(input('Upper pressure limit (standard is 100): '))
                tl = float(input('Lower temperature limit (standard is -50): '))
                tu = float(input('Upper temperature limit (standard is 50): '))
                sure = str(input('Are you sure? (y/n) '))
                if sure == 'y':
                    break
                if sure == 'n':
                    continue
            break
        else:
            continue
    return pu, tl, tu

#FILENAME = 'testsdg.txt'

def plot_sounding(file, imgName):
    try:
        prof, time, location = decode(file)
    except Exception as e:
        print("\n Oops! Couldn't decode the sounding data. No plot produced!\n")
        print(e)
        # return None
        
    # Open up the text file with the data in columns (e.g. the sample OAX file distributed with SHARPpy)
    locInfo = location.split('_')
    title = locInfo[0] + ' ' + locInfo[1] + ' ' + locInfo[2] + '   ' + time.strftime('%Y%m%d/%H%M') + '   (Observed)'
    
    # Set up the figure in matplotlib.
    fig = plt.figure(figsize=(14, 7.25))
    gs = gridspec.GridSpec(4,6, width_ratios=[1,5,1,0.5,3,3])
    ax = plt.subplot(gs[0:3, 0:2], projection='skewx')
    plt.title(title, fontsize=14, loc='left', color='w')
    ax.set_facecolor('k')
    ax.spines['left'].set_color('w')
    ax.spines['right'].set_color('w')
    ax.spines['bottom'].set_color('w')
    ax.spines['top'].set_color('w')
    
    #     xticks = ax.xaxis.get_major_ticks() #mute a tick label outside plot
    #     xticks[-4].label1.set_visible(False)
        
    ax.tick_params(axis='both', colors='w', grid_color='silver')
    ax.ticklabel_format(style='plain')
    
    # ax.xaxis.label.set_color('w')
    # ax.yaxis.label.set_color('w')
    ax.grid(True)
    plt.grid(True)
    
    # Ask user for default limits or custom limits
    pt_plot, t_lower, t_upper = ask_limits(prof.pres[~prof.dwpc.mask],
                                           prof.dwpc[~prof.dwpc.mask])
    
    # Bounds of the pressure axis 
    pb_plot=1050
    dp_plot=10
    plevs_plot = np.arange(pb_plot,pt_plot-1,-dp_plot)
    
    # Plot the background variables
    # presvals = np.arange(1000, 0, -10)
    
    #draw mixing ratio lines
    draw_mixing_ratio_lines(ax)
    
    ax.semilogy(prof.tmpc[~prof.tmpc.mask], prof.pres[~prof.tmpc.mask], 'r', lw=2)
    ax.semilogy(prof.dwpc[~prof.dwpc.mask], prof.pres[~prof.dwpc.mask], 'lime', lw=2)
    ax.semilogy(prof.vtmp[~prof.dwpc.mask], prof.pres[~prof.dwpc.mask], 'r--', lw=1)
    ax.semilogy(prof.wetbulb[~prof.dwpc.mask], prof.pres[~prof.dwpc.mask], 'cyan', '-', lw=1)
    
    #write sfc temp and dewpoint in F
    sfcT = prof.tmpc[~prof.tmpc.mask][0]
    sfcTd = prof.dwpc[~prof.dwpc.mask][0]
    sfcW = prof.wetbulb[~prof.dwpc.mask][0]
    sfcP = prof.pres[~prof.tmpc.mask][0]
    ax.annotate(str(int(sfcW * (9/5) + 32)), (sfcW, sfcP), xytext=(-6,-9), 
                textcoords='offset points', color='cyan', weight='black', size=8,
                path_effects=[pe.withStroke(linewidth=2, foreground="black")])
    ax.annotate(str(int(sfcT * (9/5) + 32)), (sfcT, sfcP), xytext=(-2,-9), 
                textcoords='offset points', color='r', weight='black', size=8,
                path_effects=[pe.withStroke(linewidth=2, foreground="black")])
    ax.annotate(str(int(sfcTd * (9/5) + 32)), (sfcTd, sfcP), xytext=(-12,-9), 
                textcoords='offset points', color='lime', weight='black', size=8,
                path_effects=[pe.withStroke(linewidth=2, foreground="black")])
    
    #plot significant levels
    plot_sig_levels(ax, prof)
    
    # Plot the parcel trace, but this may fail.  If it does so, inform the user.
    try:
        ax.semilogy(prof.mupcl.ttrace, prof.mupcl.ptrace, 'w--')
    except:
        print("Couldn't plot parcel traces...")
    
    # Highlight the 0 C and -20 C isotherms.
    l = ax.axvline(0, color='b', ls='--')
    l = ax.axvline(-20, color='b', ls='--')
    
    #plot dry adiabats
    skew.draw_dry_adiabats(ax, color='silver')
    
    #draw heights
    skew.draw_heights(ax, prof)
    
    # Disables the log-formatting that comes with semilogy
    ax.yaxis.set_major_formatter(ScalarFormatter())
    pmin = prof.pres[~prof.dwpc.mask][-1]
    if pmin > 700.:
        ax.set_yticks(np.arange(100,1000,50))
    else:
        ax.set_yticks(np.linspace(100,1000,10))
    ax.set_ylim(pb_plot,pt_plot)
    
    # Plot the hodograph data.
    # inset_axes = draw_hodo_inset(ax, prof)
    hodoAx = plt.subplot(gs[0:3,3:])
    hodoAx.set_facecolor('k')
    hodoAx.axis('off')
    hodoAx = draw_hodo_inset(hodoAx, prof)
    
    # plotHodo(inset_axes, prof.hght, prof.u, prof.v, color='r')
    plotHodo(hodoAx, prof.hght, prof.u, prof.v, color='r')
    
    #plot bunkers motion unless the most unstable EL does not exist
    srwind = params.bunkers_storm_motion(prof)
    if isinstance(prof.mupcl.elpres, np.float64):
        hodoAx.text(srwind[0], srwind[1], 'RM', color='w', fontsize=8)
        hodoAx.text(srwind[2], srwind[3], 'LM', color='w', fontsize=8)
    else:
        print("couldn't plot Bunkers vectors")
    
    # inset_axes.text(srwind[0], srwind[1], 'RM', color='r', fontsize=8)
    # inset_axes.text(srwind[2], srwind[3], 'LM', color='b', fontsize=8)
    
    #mask out barbs above the top of the plot
    below_pmin = np.where(prof.pres >= pt_plot)[0]
    
    # Draw the wind barbs axis and everything that comes with it.
    if pmin > 700.:
        ax.xaxis.set_major_locator(MultipleLocator(5))
    else:
        ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.set_xlim(t_lower, t_upper)
    
    ax2 = plt.subplot(gs[0:3,2])
    ax3 = plt.subplot(gs[3,0:3])
    plot_wind_axes(ax2, pb_plot, pt_plot, plevs_plot)
    
    #setting the stride for how many wind barbs plot
    # st = 15
    
    # plot_wind_barbs(ax2, prof.pres[below_pmin][~prof.pres.mask[below_pmin]][::st], 
    #                 prof.u[below_pmin][~prof.u.mask[below_pmin]][::st], 
    #                 prof.v[below_pmin][~prof.v.mask[below_pmin]][::st],
    #                 pt_plot)
    plot_wind_barbs(ax2, prof.pres[below_pmin][~prof.pres.mask[below_pmin]], 
                    prof.u[below_pmin][~prof.u.mask[below_pmin]], 
                    prof.v[below_pmin][~prof.v.mask[below_pmin]],
                    pt_plot)
    
    gs.update(left=0.05, bottom=0.05, top=0.95, right=1, wspace=0.025)
    
    # Calculate indices to be shown.  More indices can be calculated here using the tutorial and reading the params module.
    p1km = interp.pres(prof, interp.to_msl(prof, 1000.))
    p6km = interp.pres(prof, interp.to_msl(prof, 6000.))
    sfc = prof.pres[prof.sfc]
    sfc_1km_shear = winds.wind_shear(prof, pbot=sfc, ptop=p1km)
    sfc_6km_shear = winds.wind_shear(prof, pbot=sfc, ptop=p6km)
    srh3km = winds.helicity(prof, 0, 3000., stu = srwind[0], stv = srwind[1])
    srh1km = winds.helicity(prof, 0, 1000., stu = srwind[0], stv = srwind[1])
    scp = params.scp(prof.mupcl.bplus, prof.right_esrh[0], prof.ebwspd)
    stp_cin = params.stp_cin(prof.mlpcl.bplus, prof.right_esrh[0], prof.ebwspd, prof.mlpcl.lclhght, prof.mlpcl.bminus)
    stp_fixed = params.stp_fixed(prof.sfcpcl.bplus, prof.sfcpcl.lclhght, srh1km[0], utils.comp2vec(prof.sfc_6km_shear[0], prof.sfc_6km_shear[1])[1])
    ship = params.ship(prof)
    
    # A routine to perform the correct formatting when writing the indices out to the figure.
    def fmt(value, fmt='int'):
        if fmt == 'int':
            try:
                val = int(value)
            except:
                val = str("M")
        else:
            try:
                val = round(value,1)
            except:
                val = "M"
        return val
    
    # Setting a dictionary that is a collection of all of the indices we'll be showing on the figure.
    # the dictionary includes the index name, the actual value, and the units.
    indices = {'SBCAPE': [fmt(prof.sfcpcl.bplus), 'J/kg'],\
               'SBCIN': [fmt(prof.sfcpcl.bminus), 'J/kg'],\
               'SBLCL': [fmt(prof.sfcpcl.lclhght), 'm AGL'],\
               'SBLFC': [fmt(prof.sfcpcl.lfchght), 'm AGL'],\
               'SBEL': [fmt(prof.sfcpcl.elhght), 'm AGL'],\
               'SBLI': [fmt(prof.sfcpcl.li5), 'C'],\
               'MLCAPE': [fmt(prof.mlpcl.bplus), 'J/kg'],\
               'MLCIN': [fmt(prof.mlpcl.bminus), 'J/kg'],\
               'MLLCL': [fmt(prof.mlpcl.lclhght), 'm AGL'],\
               'MLLFC': [fmt(prof.mlpcl.lfchght), 'm AGL'],\
               'MLEL': [fmt(prof.mlpcl.elhght), 'm AGL'],\
               'MLLI': [fmt(prof.mlpcl.li5), 'C'],\
               'MUCAPE': [fmt(prof.mupcl.bplus), 'J/kg'],\
               'MUCIN': [fmt(prof.mupcl.bminus), 'J/kg'],\
               'MULCL': [fmt(prof.mupcl.lclhght), 'm AGL'],\
               'MULFC': [fmt(prof.mupcl.lfchght), 'm AGL'],\
               'MUEL': [fmt(prof.mupcl.elhght), 'm AGL'],\
               'MULI': [fmt(prof.mupcl.li5), 'C'],\
               '0-1 km SRH': [fmt(srh1km[0]), 'm2/s2'],\
               '0-1 km Shear': [fmt(utils.comp2vec(sfc_1km_shear[0], sfc_1km_shear[1])[1]), 'kts'],\
               '0-3 km SRH': [fmt(srh3km[0]), 'm2/s2'],\
               '0-6 km Shear': [fmt(utils.comp2vec(sfc_6km_shear[0], sfc_6km_shear[1])[1]), 'kts'],\
               'Eff. SRH': [fmt(prof.right_esrh[0]), 'm2/s2'],\
               'EBWD': [fmt(prof.ebwspd), 'kts'],\
               'PWV': [round(prof.pwat, 2), 'inch'],\
               'K-index': [fmt(params.k_index(prof)), ''],\
               'STP(fix)': [fmt(stp_fixed, 'flt'), ''],\
               'SHIP': [fmt(ship, 'flt'), ''],\
               'SCP': [fmt(scp, 'flt'), ''],\
               'STP(cin)': [fmt(stp_cin, 'flt'), '']}
    
    # List the indices within the indices dictionary on the side of the plot.
    trans = transforms.blended_transform_factory(ax.transAxes,ax.transData)
    
    # Write out all of the indices to the figure.
    #print("##############")
    #print("   INDICES    ")
    #print("##############")
    string = ''
    keys = np.sort(list(indices.keys()))
    x = 0
    counter = 0
    for key in keys:
        string = string + key + ': ' + str(indices[key][0]) + ' ' + indices[key][1] + '\n'
    #    print((key + ": " + str(indices[key][0]) + ' ' + indices[key][1]))
        if counter < 7:
            counter += 1
            continue
        else:
            counter = 0
            ax3.text(x, 1, string, verticalalignment='top', transform=ax3.transAxes, fontsize=11, color='w')
            string = ''
            x += 0.3
    ax3.text(x, 1, string, verticalalignment='top', transform=ax3.transAxes, fontsize=11, color='w')
    ax3.set_axis_off()
    
    # Show SARS matches (edited for Keith Sherburn)
    #try:
    #    supercell_matches = prof.supercell_matches
    #    hail_matches = prof.matches 
    #except:
    #    supercell_matches = prof.right_supercell_matches
    #    hail_matches = prof.right_matches
    
    #print()
    #print("#############")
    #print(" SARS OUTPUT ")
    #print("#############")
    #for mtype, matches in zip(['Supercell', 'Hail'], [supercell_matches, hail_matches]):
    #    print(mtype)
    #    print('-----------')
    #    if len(matches[0]) == 0:
    #        print("NO QUALITY MATCHES")
    #    for i in range(len(matches[0])):
    #        print(matches[0][i] + ' ' + matches[1][i])
    #    print("Total Loose Matches:", matches[2])
    #    print("# of Loose Matches that met Criteria:", matches[3])
    #    print("SVR Probability:", matches[4])
    #    print() 
    
    #plot logos
    im = plt.imread('logo.png')
    #left, bottom, width, height = [0.25, 0.6, 0.2, 0.2]
    #left, bottom, width, height = [0.1, 0.175, 0.4, 0.4] #bottom left
    left, bottom, width, height = [0.035, 0.65, 0.4, 0.4]
    # ax4 = fig.add_axes([left, bottom, width, height])
    ax4 = plt.subplot(gs[3,4])
    implot = ax4.imshow(im, alpha=0.99)
    ax4.axis('off')
    ax4.set_facecolor('k')
    
    im2 = plt.imread('essc_logo.png')
    ax5 = plt.subplot(gs[3,5])
    implot = ax5.imshow(im2, alpha=0.99)
    ax5.axis('off')
    ax5.set_facecolor('k')
    
    #plot SHARPpy acknowledgement
    # plt.text(1, 1, 'Plotted with SHARPpy', horizontalalignment='right', 
    #             verticalalignment='top', transform=ax.transAxes, color='w')
    hodoAx.annotate('Plotted with SHARPpy - https://sharppy.github.io/SHARPpy/', 
                    (0.7,0.96), xycoords='figure fraction', 
                    va='center', color='w')
    
    #filename for the plot
    # plotName = os.path.splitext(file)[0] + '.png'
    
    # Finalize the image formatting and alignments, and save the image to the file.
    #gs.tight_layout(fig)
    plt.style.use('dark_background')
    fn = time.strftime('%Y%m%d.%H%M') + '_' + locInfo[0] + '_' + locInfo[1] + '.png'
    fn = fn.replace('/', '')
    print('SHARPpy quick-look image output at: ' + imgName)
    #plt.savefig(fn, bbox_inches='tight', dpi=180)
    plt.savefig(imgName, dpi=180)
    
if __name__ == '__main__':
    while True:
        file = get_file()
        plot_sounding(file)
        print('\n\n\n')
        continue