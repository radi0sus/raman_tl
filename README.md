# raman-tl.py
A Python 3 script for baseline correction, smoothing, processing and plotting of Raman spectra. Data must be in the format `wavenumber [space] intensity`. The baseline correction uses the *asymmetrically reweighted penalized least squares smoothing algorithm* (arPLS). The [Savitzky–Golay](https://en.wikipedia.org/wiki/Savitzky–Golay_filter) filter is applied for smoothing. Data of the processed spectra can be saved as "csv"-like data files in the format `wavenumber [delimiter] intensity`. Plots can be saved as PNG bitmap files and as PDF.

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

Under Windows, you have to open `PowerShell` first and start the script with:
```console
python raman-tl.py (Get-ChildItem *.txt -Name)
```
to process all files with the extension  `.txt` in the folder.

In all cases a file `summary.pdf` will be created which contains the following plots:

On the first page:
- raw spectrum with baseline plot (red)
- baseline corrected spectrum
- smoothed spectrum with peak annotation 

On the following page(s):
- smoothed or filtered spectrum with peak annotation 

## Command-line options
- `filename` , required: filename(s), input file(s) in the format `wavenumber [space] intensity`
- `-l` `N`, optional: the lambda parameter for the arPLS algorithm (default is `N = 1000`)
- `-p` `N:M`, optional: window length and polynomial order of the Savitzky–Golay filter (default is `N = 5, M = 3`)
- `-xmin` `N` , optional: start spectra at `N` wave numbers
- `-xmax` `N` , optional: end spectra at `N` wave numbers
- `-t` `N` , optional: threshold for peak detection, with `N` being the intensity (default is 5% from the maximum intensity)
- `-m` `N` , optional: multiply intensities with `N` (default is `N = 1`)
- `-a` `N` , optional: add or subtract `N` to / from wave numbers (default is `N = 0`)
- `-i` `N` , optional: add or subtract `N` to / from intensities (default is `N = 0`)
- `-n` , optional: do not save `summary.pdf`
- `-s` `p,d` , optional: save P(NG) and / or D(ATA) files. The filenames are `filename.png` and / or `filename-mod.dat`. Data files are in the format `wavenumber [delimiter] intensity`. The delimiter can be set in the script. The default delimiter is [space].

## Remarks
- The save values for `lambda` start from 1000. Smaller values will give sharper peaks, but broader peaks become part of the baseline. Check the red baseline curve in the summary page.
- There is no way to turn off the smoothing filter directly, but with two parameters close together, e.g. `-p3:2`, filtering is ineffective. 
- Polynomial based filters, such as the Savitzky–Golay filter, sometimes tend to overshoot in negative regions, especially with sharp signals in the Raman spectrum. Reduce the filtering (see above) is one way to solve this problem. 
- `xmin` and or `xmax` values outside the experimental wave number range will result in errors or strange outputs.
- `-a` changes the range for `xmin` and `xmax`
- `-i` and `-m` change the range for  `-t` 
- The  `.dat` file contains the data of the processed spectrum in the given range as it is shown in the last plot.
- The delimiter  in the `.dat` file can be changed in the script: `dat_delimiter = " "` or `dat_delimiter = " ; "` for example.

## Examples
![show](/examples/show-use3.gif)

### Example 1
```console
python3 raman-tl.py s*.txt
```
Process all files starting with `s` and the extension `.txt`.

Summary:

<img src="/examples/summary2.png" width=600>

Single spectra:

<img src="/examples/sample-A.png" width=600>
<img src="/examples/sample-B2.png" width=600>

### Example 2
```console
python3 raman-tl.py sample-A.txt -l10000 -p7:4 -xmin 600 -xmax 800 -t50 -spd 
```
Process spectrum `sample-A.txt` with `lambda = 10000` (baseline parameter), `window length = 7` and `polynomial order = 4` (smoothing parameters) in the range from `xmin = 600` to `xmax = 800` cm<sup>-1</sup>, annotate peaks with intensities equal or greater than `t = 50` and save the PNG and DATA files (`-spd`).

Summary:

<img src="/examples/summary-3.png" width=600>

Single spectrum:

<img src="/examples/sample-A-3.png" width=600>
