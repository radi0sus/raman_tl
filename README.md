# raman-tl.py
A Python 3 script for baseline correction, smoothing, processing and plotting of Raman spectra. Data must be in the format `wavenumber [space] intensity`. The baseline correction uses the *asymmetrically reweighted penalized least squares smoothing algorithm* (arPLS). The Whittaker filter is (by default) applied for smoothing. Optionally, the [Savitzky–Golay](https://en.wikipedia.org/wiki/Savitzky–Golay_filter) filter can be used. Data of the processed spectra can be saved as "csv"-like data files in the format `wavenumber [delimiter] intensity`. Plots can be saved as PNG bitmap files and as PDF.

If you use the arPLS algorithm to process your spectra, please cite:

> "Baseline correction using asymmetrically reweighted penalized least squares smoothing"
> 
> Sung-June Baek, Aaron Park, Young-Jin Ahna, Jaebum Choo, *Analyst* **2015**, *140*, 250-257
> 
> DOI:	https://doi.org/10.1039/C4AN01061B

The Whittaker algorithm is adapted from:

> "A perfect smoother"
> 
> Paul H. C. Eilers, *Anal. Chem.* **2003**, *75*, 3631-3636
> 
> DOI https://doi.org/10.1021/ac03417

which is based on:

>"On a new method of gradutation"
>
>E. T. Whittaker, *Proceedings of the Edinburgh Mathematical Society* **1922**, *41*, 63-75
>
>DOI: https://doi.org/10.1017/S0013091500077853


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
- smoothed / filtered spectrum with peak annotation 

On the following page(s):
- smoothed / filtered spectrum with peak annotation 

## Command-line options
- `filename` , required: filename(s), input file(s) in the format `wavenumber [space] intensity`
- `-l` `N`, optional: the lambda parameter for the arPLS algorithm (default is `N = 1000`)
- `-p` `N:M`, optional: invokes the Savitzky–Golay filter, `N:M` are the window length and polynomial order of the Savitzky–Golay filter 
- `-w` `N`,  optional: the lambda parameter for the Whittaker filter (default is `N = 1`)
- `-xmin` `N` , optional: start spectra at `N` wave numbers
- `-xmax` `N` , optional: end spectra at `N` wave numbers
- `-t` `N` , optional: threshold for peak detection, with `N` being the intensity (default is 5% from the maximum intensity)
- `-m` `N` , optional: multiply intensities with `N` (default is `N = 1`)
- `-a` `N` , optional: add or subtract `N` to / from wave numbers (default is `N = 0`)
- `-i` `N` , optional: add or subtract `N` to / from intensities (default is `N = 0`)
- `-n` , optional: do not save `summary.pdf`
- `-s` `p,d` , optional: save P(NG) and / or D(ATA) files. The filenames are `filename.png` and / or `filename-mod.dat`. Data files are in the format `wavenumber [delimiter] intensity`. The delimiter can be set in the script. The default delimiter is [space].

## Remarks
- The save values for the arPLS parameter `lambda` start from 1000. Smaller values will give sharper peaks, but broader peaks become part of the baseline. Check the red baseline curve in the summary page.
- There is no way to turn off smoothing directly, but with two Savitzky-Golay parameters close together, e.g. `-p3:2` or a Whittaker parameter `-w0.01` filtering is ineffective. 
- The window length for the Savitzky–Golay filter must be an odd number and the window length must be greater than the polynomial order.
- Polynomial based filters, such as the Savitzky–Golay filter, sometimes tend to overshoot in negative regions, especially with sharp signals in the Raman spectrum. Reduce the filtering (see above) is one way to solve this problem. 
- `xmin` and or `xmax` values outside the experimental wave number range will result in errors or strange outputs.
- `-a` changes the range for `xmin` and `xmax`
- `-i` and `-m` change the range for  `-t` 
- The  `.dat` file contains the data of the processed spectrum in the given range as it is shown in the last plot.
- The delimiter  in the `.dat` file can be changed in the script: `dat_delimiter = " "` or `dat_delimiter = " ; "` for example.

## Examples
![show](/examples/show-use4.gif)

Remember, under Windows you have to open `PowerShell` first and start the script with:
```console
python raman-tl.py (Get-ChildItem *.txt -Name)
```
to open more than one file at once.

### Example 1
```console
python3 raman-tl.py s*.txt
```
Process all files starting with `s` and the extension `.txt`.

Summary:

<img src="/examples/summary2n.png" width=600>

Single spectra:

<img src="/examples/sample-A2.png" width=600>
<img src="/examples/sample-B2n.png" width=600>

### Example 2
```console
python3 raman-tl.py sample-A.txt -xmin 600 -xmax 800 -spd 
```
Process spectrum `sample-A.txt` in the range from `xmin = 600` to `xmax = 800` cm<sup>-1</sup> and save the PNG and DATA files (`-spd`).

Summary:

<img src="/examples/summary3.png" width=600>

Single spectrum:

<img src="/examples/sample-A3.png" width=600>

### Example 3
```console
python3 raman-tl.py sample-A.txt -l10000 -p7:4 -xmin 600 -xmax 800 -t50 -spd 
```
Process spectrum `sample-A.txt` with `lambda = 10000` (baseline parameter), `window length = 7` and `polynomial order = 4` (smoothing parameters) in the range from `xmin = 600` to `xmax = 800` cm<sup>-1</sup>, annotate peaks with intensities equal or greater than `t = 50` and save the PNG and DATA files (`-spd`).
