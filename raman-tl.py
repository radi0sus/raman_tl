# -*- coding: utf-8 -*-
'''

# for arPLS baseline correction, please cite:
"Baseline correction using asymmetrically reweighted penalized least squares smoothing"
Sung-June Baek, Aaron Park, Young-Jin Ahna, Jaebum Choo  
Analyst 2015, 140, 250-257
DOI	https://doi.org/10.1039/C4AN01061B

# python adaption based on the code example from:
https://stackoverflow.com/questions/29156532/python-baseline-correction-library
Daniel Casas-Orozco

# Whittaker filter / smoothing adapted from several sources based on:
"A perfect smoother"
Paul H. C. Eilers 
Anal. Chem. 2003, 75, 3631-3636
DOI https://doi.org/10.1021/ac034173t

# Whittaker paper 
"On a new method of gradutation"
E. T. Whittaker
Proceedings of the Edinburgh Mathematical Society 1922, 41, 63-75
DOI: https://doi.org/10.1017/S0013091500077853

# open more than one datat set under windows: 
open powershell: baseline.py (Get-ChildItem *.txt -Name)

'''

import sys                                              #sys files processing
import os                                               #os file processing
import argparse                                         #argument parser
import numpy as np                                      #summation
import matplotlib.pyplot as plt                         #plots
from scipy.signal import find_peaks                     #peak detection
from scipy import sparse                                #for arPLS
from scipy.sparse import linalg                         #for arPLS
from numpy.linalg import norm                           #for arPLS
from scipy.special import expit                         #for arPLS
from scipy.signal import savgol_filter                  #Savitzky–Golay filter 
from matplotlib.backends.backend_pdf import PdfPages    #save summary as PDF

# global constants
#wl = 5                                     #window length for the Savitzky–Golay filter (filtering /smoothing)
#po = 3                                     #polynomal order the Savitzky–Golay filter (filtering /smoothing)
intensities = 0                             #add 0 to intensities
auto_threshold = 0                          #check if auto threshold was activated
threshold_factor = 0.05                     #threshold factor for auto peak detection
peak_distance = 8                           #peak distance for peak detection
arpls_ratio = 1e-6                          #ratio for arPLS
lam = 1000                                  #lamda for the arPLS baseline correction
n_iter = 200                                #number of iterations for arPLS

# plot and data output config section 
y_label = "intensity"                       #label of y-axis 
x_label = r'raman shift /cm$^{-1}$'         #label of the x-axis 
figure_dpi = 300                            #DPI of the picture
save_plots_png = False                      #save PNGs
save_dat = False                            #save data file 
dat_delimiter = " "                         #separator character for data export - "csv"

#global lists and dicts
freqlist=list()                             #frequencies current spectrum
intenslist=list()                           #intensities current spectrum
freqdict=dict()                             #frequencies all spectra
intensdict=dict()                           #intensities all spectra

# arPLS baseline correction
def baseline_arPLS(y, ratio=arpls_ratio, lam=lam, niter=n_iter):
    L = len(y)    
    diag = np.ones(L - 2)
    D = sparse.spdiags([diag, -2*diag, diag], [0, -1, -2], L, L - 2)    
    H = lam * D.dot(D.T)     
    w = np.ones(L)
    W = sparse.spdiags(w, 0, L, L)    
    crit = 1
    count = 0    
    while crit > ratio:
        z = linalg.spsolve(W + H, W * y)
        d = y - z
        dn = d[d < 0]        
        m = np.mean(dn)
        s = np.std(dn)        
        w_new = expit(-2 * (d - (2*s - m))/s)
        crit = norm(w_new - w) / norm(w)        
        w = w_new
        W.setdiag(w)         
        count += 1        
        if count > niter:
            break
    return z

#Whittaker filter (smoothing)
def whittaker(y,lmd = 2, d = 2):
    L = len(y)
    E = sparse.csc_matrix(np.diff(np.eye(L), d))
    W = sparse.spdiags(np.ones(L), 0, L, L)
    Z = W + lmd * E.dot(E.transpose())
    z = sparse.linalg.spsolve(Z, np.ones(L)*y)
    return z

#add +x or subtract -x wave numbers to spectrum
def add_x_to_freq(freqlist,x):
    return np.add(freqlist,x).tolist()

#multiply intensity with x
def mult_y_with_intens(intenslist,y):
    return np.multiply(intenslist,y).tolist()

#add +y or subtract -y to intensities
def add_y_to_intens(intenslist,y):
    return np.add(intenslist,y).tolist()

#argument parser
parser = argparse.ArgumentParser(prog='raman-tl', 
         description='Baseline correction, smoothing and processing of Raman spectra',
         formatter_class=argparse.RawTextHelpFormatter)

#filename is required
parser.add_argument("filename", 
    nargs="+",
    help="filename(s), data - data format is: frequency [space] intensity")

#lambda for baseline
parser.add_argument('-l','--lambda',
    type=int,
    dest='lambda_',
    metavar='LAMBDA',
    default=1000,
    help='lambda for arPLS (baseline) correction\n' +
         'save values start from 1000, '+ 
         'values less than 1000 giver sharper peaks,\n' + 
         'but broader peaks will become part of the baseline\n' + 
         'check output')
    
#parameter for Savitzky–Golay filter
parser.add_argument('-p','--wp',
    type=str,
    metavar=('WINDOWLENGTH : POLYORDER'),
    help='activates the Savitzky–Golay filter (smoothing)\n'+ 
         'window length and polynomial order for the Savitzky–Golay filter (smoothing)\n'+ 
         'window length must be a positive odd number and ' +
         'window length > polynomial order')

#parameter for Whittaker filter
parser.add_argument('-w','--whittaker',
    type=float,
    default=1,
    help='lamda parameter for the Whittaker  filter (smoothing)') 


#start spectra at xmin
parser.add_argument('-xmin','--xmin',
    type=float,
    help='start spectra at xmin wave numbers\n'+ 
         'take care of the collected data range\n' +
         'xmax must be greater than xmin and xmin and xmax ' +
         'should not be equal or to close together')

#end spectra at xmax
parser.add_argument('-xmax','--xmax',
    type=float,
    help='end spectra at xmax wave numbers\n'+ 
         'take care of the collected data range\n' +
         'xmax must be greater than xmin and xmin and xmax ' +
         'should not be equal or to close together')

#threshold for peak annotation
parser.add_argument('-t','--threshold',
    type=int,
    help='threshold for peak detection\n'+ 
         'only peaks with intensities equal or above t will be printed')

#multiply intensities 
parser.add_argument('-m','--multiply',
    type=float,
    help='multiply intensities with m')

#add to wave numbers
parser.add_argument('-a','--add',
    type=float,
    help='add or subtract a to wave numbers\n' +
         'take care of the collected data range ' +
         'and -xmin and -xmax options')

#add to intensities
parser.add_argument('-i','--intensities',
    type=float,
    default = 0,
    help='add or subtract i to intensities\n' +
    'take care of peak detection')

#do not save the pdf
parser.add_argument('-n','--nosave',
    default=1, action='store_false',
    help='do not save summary.pdf')

#save spectra and / or modified data 
parser.add_argument('-s','--save',
    type=str,
    metavar=('p[ng], d[at]'),
    help='save PNG and DAT files of every spectra including summary.png\n'+
         'DAT data are baseline corrected and filtered\n' + 
         'xmin and xmax are active')

#parse arguments
args = parser.parse_args()

#lambda for arPLS baseline correction
lam = args.lambda_

#window-length and poly-order for the Savitzky–Golay filter
#delimiter changed to ":" because of win10 issues
if args.wp:
    wl = int(args.wp.split(':')[0])
    po = int(args.wp.split(':')[1])

#lamda for Whittaker filter / smoothing
whittaker_lmd = args.whittaker

#xmin and xmax for spectra
xmin = args.xmin
xmax = args.xmax

#threshold for peak detection
threshold = args.threshold

#multiply intensities with facor if argument is given
multiply = args.multiply

#add or subtract x to wave numbers if argument is given
add = args.add

#if True save summary.pdf
save_pdf = args.nosave

#check for p or P (png) or d or D (dat) in argument
#save PNGs and DAT data if True
if args.save:
    if "p" in args.save or "P" in args.save:
        save_plots_png = True
    else:
        save_plots_png = False
    if "d" in args.save or "D" in args.save:
        save_dat = True
    else:
        save_dat = False
    
#open one or more files
#check existence
try:
    for filename in args.filename:
        with open(filename, "r") as input_file:
            spectrum_name = os.path.splitext(os.path.basename(filename))[0]
            for line in input_file:
                freqlist.append(float(line.strip().split()[0]))
                intenslist.append(float(line.strip().split()[1]))
        freqdict[spectrum_name]=freqlist
        intensdict[spectrum_name]=intenslist
        freqlist=[]
        intenslist=[]
#file not found -> exit here
except IOError:
    print(f"'{args.filename}'" + " not found")
    sys.exit(1)

#multiply intensities with factor if argument is given
if multiply:
    for key in intensdict.keys():
        intensdict[key]=mult_y_with_intens(intensdict[key],abs(multiply))

#add or subtract x to wave numbers if argument is given
if add:
    print("Warning! The '-a' option can change your results completely. Use it with extra care.")
    for key in freqdict.keys():
        freqdict[key]=add_x_to_freq(freqdict[key],add)

#if True save summary.pdf
if save_pdf:    
    pdf = PdfPages("summary.pdf")

#only one data set
if len(freqdict) == 1:
    
    #prepare plot
    fig, ax = plt.subplots(3,constrained_layout=True)
    
    #get key (name) of spectra and counter - not necessary for only one data set
    for counter, key in enumerate(freqdict.keys()):
        
        # if xmin and xmax parameters are given
        if xmin:
            #get index closest to xmin
            xmin_index = min(range(len(freqdict[key])), key=lambda i: abs(freqdict[key][i]-xmin)) # index closest to xmin
        else:
            #else start at first index
            xmin_index=0
        if xmax:
            #get index closest to xmax
            xmax_index = min(range(len(freqdict[key])), key=lambda i: abs(freqdict[key][i]-xmax)) # index closest to xmax 
        else:
            #else take last index
            xmax_index=-1
        
        #plot raw data
        ax[0].plot(freqdict[key],intensdict[key],color='black',linewidth=1,label='raw data')
        #plot baseline
        ax[0].plot(freqdict[key],baseline_arPLS(intensdict[key],lam=lam),color='red',linewidth=1,
            label='baseline\n'+ r'$\lambda$ = ' + str(lam))
        #baseline correct spectrum (intensities)
        spec_baseline_corr = intensdict[key] - baseline_arPLS(intensdict[key],lam=lam)
        
        #add +y to intensities if arg is given
        if args.intensities:
            spec_baseline_corr = add_y_to_intens(spec_baseline_corr, args.intensities)
        
        #plot baseline corrected spectrum - take care of xmin & xmax - in summary plot
        ax[1].plot(freqdict[key][xmin_index:xmax_index],spec_baseline_corr[xmin_index:xmax_index],color='black',linewidth=1,
            label='baseline corrected data\n'+ r'$\lambda$ = ' + str(lam))
        
        #filter baseline corrected spectrum, savgol parameters wl & po or whittaker lambda
        if args.wp:
            spec_filtered=savgol_filter(spec_baseline_corr,wl,po)
            lbl = 'smoothed data\n' + 'Savitzky-Golay filter\n' + 'window-length = '+ str(wl) + '\npoly-order = ' + str (po)
        elif args.whittaker:
            spec_filtered=whittaker(spec_baseline_corr,lmd=whittaker_lmd)
            lbl = 'Whittaker\n' + r'$\lambda$ = '+ str(whittaker_lmd) 
        else:
            spec_filtered=whittaker(spec_baseline_corr,lmd=1)
            lbl = 'Whittaker\n' + r'$\lambda$ = 1'
            
        #plot baseline corrected, filtered spectrum - take care of xmin & xmax
        ax[2].plot(freqdict[key][xmin_index:xmax_index],spec_filtered[xmin_index:xmax_index],color='black',linewidth=1,
            label=lbl)
        
        #spectrum title, legend and labels
        ax[0].set_title(" ".join(freqdict.keys()))
        ax[0].legend(loc='upper left',fontsize='8')
        ax[1].legend(loc='upper left',fontsize='8')
        ax[2].legend(loc='upper left',fontsize='8')
        ax[0].set_ylabel(y_label)
        ax[1].set_ylabel(y_label)
        ax[2].set_ylabel(y_label)
        ax[2].set_xlabel(x_label)
        
        #peak detection threshold
        if threshold != None and auto_threshold == 0:
            threshold=abs(threshold)
        else:
            #auto threshold
            auto_threshold=1
            try:   
                threshold=(max(spec_filtered[xmin_index:xmax_index])+abs(min(spec_filtered[xmin_index:xmax_index])))*threshold_factor
            except ValueError:
                print('Warning! xmin or xmax are out of range or (almost) equal.')
        
        #peak detection
        peaks , _ = find_peaks(spec_filtered[xmin_index:xmax_index],height=threshold,distance=peak_distance)
        peakz = [freqdict[key][xmin_index:xmax_index][peak] for peak in peaks]
        
        #label peaks
        for index, txt in enumerate(peakz):
            ax[2].annotate(int(np.round(txt)),xy=(txt,spec_filtered[xmin_index:xmax_index][peaks[index]]),ha="center",rotation=90,size=6,
                xytext=(0,5), textcoords='offset points')
        try:    
            #auto y range
            ymax=max(spec_filtered[xmin_index:xmax_index])
            ymin=min(spec_filtered[xmin_index:xmax_index])
            ax[2].set_ylim(ymin-ymax*0.05,ymax+ymax*0.15)
        except ValueError:
            print('Warning! xmin or xmax are out of range or (almost) equal.')
            
#more than one data set   
else:
    #get number of data sets
    number_of_files=len(freqdict)
    #prepare plot
    fig, ax = plt.subplots(3,len(freqdict),constrained_layout=True)
    
    #get key (name) of spectra and counter 
    for counter, key in enumerate(freqdict.keys()):
        #change font size according to the number of spectra
        if number_of_files > 5:
            ax[0,counter].set_title(key,fontsize=5)
        else:
            ax[0,counter].set_title(key,fontsize=8)
        
        # if xmin and xmax parameters are given
        if xmin:
            #get index closest to xmin
            xmin_index = min(range(len(freqdict[key])), key=lambda i: abs(freqdict[key][i]-xmin)) # index closest to xmin
        else:
            #else start at first index
            xmin_index=0
        if xmax:
            #get index closest to xmax
            xmax_index = min(range(len(freqdict[key])), key=lambda i: abs(freqdict[key][i]-xmax)) # index closest to xmax 
        else:
            #else take last index
            xmax_index=-1
            
        #plot raw data
        ax[0,counter].plot(freqdict[key],intensdict[key],color='black',linewidth=1,label='raw data')
        #plot baseline
        ax[0,counter].plot(freqdict[key],baseline_arPLS(intensdict[key],lam=lam),color='red',linewidth=1,
            label='baseline\n'+ r'$\lambda$ = ' + str(lam))
        #baseline correct spectrum (intensities)
        spec_baseline_corr = intensdict[key] - baseline_arPLS(intensdict[key],lam=lam)
        
        #add +y to intensities if arg is given
        if args.intensities:
            spec_baseline_corr = add_y_to_intens(spec_baseline_corr, args.intensities)
            
        #plot baseline corrected spectrum - take care of xmin & xmax - in summary plot
        ax[1,counter].plot(freqdict[key][xmin_index:xmax_index],spec_baseline_corr[xmin_index:xmax_index],color='black',linewidth=1,
            label='baseline corrected data\n'+ r'$\lambda$ = ' + str(lam))
    
        #filter baseline corrected spectrum, savgol parameters wl & po or whittaker lambda
        if args.wp:
            spec_filtered=savgol_filter(spec_baseline_corr,wl,po)
            lbl = 'smoothed data\n' + 'Savitzky-Golay filter\n' + 'window-length = '+ str(wl) + '\npoly-order = ' + str (po)
        elif args.whittaker:
            spec_filtered=whittaker(spec_baseline_corr,lmd=whittaker_lmd)
            lbl = 'smoothed data\n' + 'Whittaker filter\n' + r'$\lambda$ = '+ str(whittaker_lmd) 
        else:
            spec_filtered=whittaker(spec_baseline_corr,lmd=1)
            lbl = 'smoothed data\n' + 'Whittaker filter\n' + r'$\lambda$ = 1'
        
    
        #plot baseline corrected, filtered spectrum - take care of xmin & xmax
        ax[2,counter].plot(freqdict[key][xmin_index:xmax_index],spec_filtered[xmin_index:xmax_index],color='black',linewidth=1,
            label=lbl)
        
        #spectrum title, legend and labels
        ax[0,counter].legend(loc='upper left',fontsize='8')
        ax[1,counter].legend(loc='upper left',fontsize='8')
        ax[2,counter].legend(loc='upper left',fontsize='8')
        ax[2,counter].set_xlabel(x_label)
        ax[0,0].set_ylabel(y_label)
        ax[1,0].set_ylabel(y_label)
        ax[2,0].set_ylabel(y_label)
        
        #peak detection threshold
        if threshold != None and auto_threshold == 0:
            threshold=abs(threshold)
        else:
            #auto threshold
            auto_threshold=1
            try:   
                threshold=(max(spec_filtered[xmin_index:xmax_index])+abs(min(spec_filtered[xmin_index:xmax_index])))*threshold_factor
            except ValueError:
                print('Warning! xmin or xmax are out of range or (almost) equal.')
        
        #peak detection
        peaks , _ = find_peaks(spec_filtered[xmin_index:xmax_index],height=threshold,distance=peak_distance)
        peakz = [freqdict[key][xmin_index:xmax_index][peak] for peak in peaks]
        
        #label peaks
        for index, txt in enumerate(peakz):
            ax[2,counter].annotate(int(np.round(txt)),xy=(txt,spec_filtered[xmin_index:xmax_index][peaks[index]]),ha="center",rotation=90,size=6,
                xytext=(0,5), textcoords='offset points')
        
        try:
            #auto y range
            ymax=max(spec_filtered[xmin_index:xmax_index])
            ymin=min(spec_filtered[xmin_index:xmax_index])
            ax[2,counter].set_ylim(ymin-ymax*0.05,ymax+ymax*0.15)
        except ValueError:
            print('Warning! xmin or xmax are out of range or (almost) equal.')
        


#increase figure size N (number of data sets) x M 
N = len(freqdict)
M = 2
params = plt.gcf()
plSize = params.get_size_inches()
params.set_size_inches((plSize[0]*N, plSize[1]*M))

#save to pdf
if save_pdf:
    pdf.savefig()
#save to png
if save_plots_png:
    plt.savefig('summary.png', dpi=figure_dpi)

#show the summary plot
plt.show()

for counter, key in enumerate(freqdict.keys()):
    #same as above, but for single spectra and saving data 
    fig, ax = plt.subplots()
    
    if xmin:
        xmin_index = min(range(len(freqdict[key])), key=lambda i: abs(freqdict[key][i]-xmin)) # index closest to xmin
    else:
        xmin_index=0
    if xmax:
        xmax_index = min(range(len(freqdict[key])), key=lambda i: abs(freqdict[key][i]-xmax)) # index closest to xmax 
    else:
        xmax_index=-1
    
    spec_baseline_corr = intensdict[key] - baseline_arPLS(intensdict[key],lam=lam)
     
    if args.intensities:
        spec_baseline_corr = add_y_to_intens(spec_baseline_corr, args.intensities)
    
    #filter baseline corrected spectrum, savgol parameters wl & po or whittaker lambda
    if args.wp:
        spec_filtered=savgol_filter(spec_baseline_corr,wl,po)
        #lbl = 'smoothed data\n' + 'Savitzky-Golay filter\n' + 'window-length = '+ str(wl) + '\npoly-order = ' + str (po)
    elif args.whittaker:
        spec_filtered=whittaker(spec_baseline_corr,lmd=whittaker_lmd)
        #lbl = 'smoothed data\n' + 'Whittaker filter\n' + r'$\lambda$ = '+ str(whittaker_lmd) 
    else:
        spec_filtered=whittaker(spec_baseline_corr,lmd=1)
        #lbl = 'smoothed data\n' + 'Whittaker filter\n' + r'$\lambda$ = 1'
    
    ax.plot(freqdict[key][xmin_index:xmax_index],spec_filtered[xmin_index:xmax_index],color='black',linewidth=1,
        label=lbl)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(key)
    
    #peak detection threshold
    if threshold != None and auto_threshold == 0:
        threshold=abs(threshold)
    else:
        #auto threshold
        auto_threshold=1
        try:   
            threshold=(max(spec_filtered[xmin_index:xmax_index])
                +abs(min(spec_filtered[xmin_index:xmax_index])))*threshold_factor
        except ValueError:
            print('Warning! xmin or xmax are out of range or (almost) equal.')
    
    peaks , _ = find_peaks(spec_filtered[xmin_index:xmax_index],height=threshold,distance=peak_distance)
    peakz = [freqdict[key][xmin_index:xmax_index][peak] for peak in peaks]
    
    for index, txt in enumerate(peakz):
        ax.annotate(int(np.round(txt)),xy=(txt,spec_filtered[xmin_index:xmax_index][peaks[index]]),ha="center",rotation=90,size=6,
            xytext=(0,5), textcoords='offset points')
    
    try:    
        ymax=max(spec_filtered[xmin_index:xmax_index])
        ymin=min(spec_filtered[xmin_index:xmax_index])
        ax.set_ylim(ymin-ymax*0.05,ymax+ymax*0.10)
    except ValueError:
        print('Warning! xmin or xmax are out of range or (almost) equal.')
        
    #increase figure size N x M     
    N = 1.5
    M = 1.5
    params = plt.gcf()
    plSize = params.get_size_inches()
    params.set_size_inches((plSize[0]*N, plSize[1]*M))
    
    #save single plots as png
    if save_plots_png:
        plt.savefig(key + ".png", dpi=figure_dpi)
        
    #save single plots to summary.pdf
    if save_pdf:
        pdf.savefig()
    
    #save modified spectra as "csv"
    if save_dat:
        try:
            with open(key + "-mod.dat","w") as output_file:
                for (wn, intens) in zip(freqdict[key][xmin_index:xmax_index],spec_filtered[xmin_index:xmax_index]):
                    output_file.write("{:.3f}".format(wn) + dat_delimiter + "{:.2f}".format(intens) +'\n')    
        #file not found -> exit here
        except IOError:
            print("Write error. Exit.")
            sys.exit(1)

#show the plot(s)
#plt.show()
            
#close summary.pdf
if save_pdf:
    pdf.close()
    
