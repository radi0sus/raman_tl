# raman-tl.py
A Python 3 script for baseline correction, smoothing, processing and plotting of Raman spectra. Data must be in the format `wavenumber [space] intensity`. The baseline correction uses the asymmetrically reweighted penalized least squares smoothing algorithm (arPLS). The Savitzky–Golay filter is applied for smoothing. Data of the processed spectra can be saved as "csv"-like data files in the format `wavenumber [space] intensity`. Plots can be saved as PNG bitmap files and as PDF.

## External modules
 `numpy`,  `scipy`,  `matplotlib`
 
## Quick start
 Start the script with:
```console
python3 raman-tl.py filename
```
to open a single file.

Start the script with:
```console
python3 raman-tl.py *.txt
```
to process all files with the extension  `.txt` in the folder.

Under Windows you have to open `PowerShell` first and start the script with:
```console
python raman-tl.py (Get-ChildItem *.txt -Name)
```

In all cases
