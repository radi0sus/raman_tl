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

  -h --help            show this help message and exit
  -l LAMBDA, --lambda LAMBDA
                        lambda for arPLS (baseline) correction
                        save values start from 1000, values less than 1000 giver sharper peaks,
                        but broader peaks will become part of the baseline
                        check output
  -p WINDOWLENGTH : POLYORDER, --wp WINDOWLENGTH : POLYORDER
                        window length and polynomial order for the Savitzky–Golay filter (smoothing)
                        window length must be a positive odd number and window length > polynomial order
  -xmin XMIN, --xmin XMIN
                        start spectra at xmin wave numbers
                        take care of the collected data range
                        xmax must be greater than xmin and xmin and xmax should not be equal or to close together
  -xmax XMAX, --xmax XMAX
                        end spectra at xmax wave numbers
                        take care of the collected data range
                        xmax must be greater than xmin and xmin and xmax should not be equal or to close together
  -t THRESHOLD, --threshold THRESHOLD
                        threshold for peak detection
                        only peaks with intensities equal or above t will be printed
  -m MULTIPLY, --multiply MULTIPLY
                        multiply intensities with m
  -a ADD, --add ADD     add or subtract a to wave numbers
                        take care of the collected data range and -xmin and -xmax options
  -i INTENSITIES, --intensities INTENSITIES
                        add or subtract i to intensities
                        take care of peak detection
  -n, --nosave          do not save summary.pdf
  -s P(NG), D(AT), --save P(NG), D(AT)
                        save PNG and DAT files of every spectra including summary.png
                        DAT data are baseline corrected and filtered
                        xmin and xmax are active
