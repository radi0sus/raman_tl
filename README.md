# raman-tl.py
A Python 3 script for baseline correction, smoothing, processing and plotting of Raman spectra. Data must be in the format `wavenumber [space] intensity`. The baseline correction uses the asymmetrically reweighted penalized least squares smoothing algorithm (arPLS). The [Savitzky–Golay](https://en.wikipedia.org/wiki/Savitzky–Golay_filter) filter is applied for smoothing. Data of the processed spectra can be saved as "csv"-like data files in the format `wavenumber [delimiter] intensity`. Plots can be saved as PNG bitmap files and as PDF.

If you use the arPLS algorithm to process your spectra, please cite:

> "Baseline correction using asymmetrically reweighted penalized least squares smoothing"
> 
> Sung-June Baek, Aaron Park, Young-Jin Ahna, Jaebum Choo  
> *Analyst*, **2015**, *140*, 250-257
> 
> DOI:	https://doi.org/10.1039/C4AN01061B



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

In all cases a file `summary.pdf` will be created which contains the following plots:

On the first page:
- raw spectrum with base line plot
- baseline corrected spectrum
- smoothed spectrum with peak annotation 

On the following page(s):
- smoothed or filtered spectrum with peak annotation 

## Command-line options
