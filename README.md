# MAVEN 3D Particle Distribution Visualiser

One Python script, `maven_3d_particle_distributions.py`, that reads calibrated MAVEN CDF files you already have on disk for SWEA, STATIC, and SEP. When the selected array has four or more dimensions, it sums two axes, writes that sum to CSV and NetCDF, and draws a spherical surface.

It does not download data, and it does not turn the files into pitch-angle or Sun/Mars coordinates.

## What the script does

`base_dir` at the top of the script defaults to an empty string. Output and CDF search paths are then relative to the working directory. On startup it creates `processed_data_3d_improved/`.

It searches these directories recursively for `*.cdf`:

- `_maven.swea.calibrated/`
- `_maven.static.c/`
- `_maven.sep.calibrated/`

The leading underscore is part of the path in the script. These are not the PDS bundle ids (`maven.swea.calibrated`, `maven.static.c`, `maven.sep.calibrated`).

For each instrument:

1. Load every CDF in that directory with `cdf_to_tplot`.
2. Choose a variable: the first loaded name containing `flux`, `eflux`, or `diff_en`, otherwise the first loaded name.
3. Show that variable with `tplot`. The colour-scale text is the hardcoded `flux_label` in `instrument_configs`, not the CDF `UNITS` attribute. Nothing is written to an image file.
4. If the array rank is below 4, stop for that instrument. No CSV, NetCDF, or 3D figure is produced.
5. If the rank is at least 4, treat axis 1 and axis 2 as angles and the last axis as energy:
   - Replace the array with an unweighted `numpy.nansum` over axes 1 and 2. This is not a solid-angle-weighted omnidirectional flux.
   - Show that sum with `tplot`. The y axis is the bin index. Energy coordinates are not read from the CDF.
   - Write `processed_data_3d_improved/{instrument}_omni_mean_flux.csv`: the mean of the summed array across bins, one value per time. Times are `pandas.to_datetime(..., unit='s')` applied to the tplot time array.
   - Write `processed_data_3d_improved/{instrument}_omni_spectrogram.nc`: the summed array (time × `Bin_0` …), not the original distribution.
   - Draw `num_3d_snapshots` surfaces (the constant is `5` unless you edit it). Indices are `linspace` from the first to the last time, so they repeat when there are fewer times than snapshots. Radius and colour are the mean along the last axis. Elevation and azimuth are evenly spaced across the hardcoded `theta_range` and `phi_range`, not an angle table from the CDF. Each figure is shown with `plt.show()` and is not saved.

The SWEA note in the script describes time × elevation × azimuth × energy, which matches that axis assumption. The STATIC and SEP notes describe different orders (mass/energy/angle, and look direction/bins/energy). The script still uses the same sum and the same sphere for those files, and it prints a warning when it does.

There is no command-line interface. Change `base_dir` and `num_3d_snapshots` in the script.

## Install

`pytplot-mpl-temp` requires Python 3.9 or newer. It is the package that provides `import pytplot` at version 2 and later, including `cdf_to_tplot`, `tplot`, `get_data`, `store_data`, and `options`.

```bash
pip install -r requirements.txt
```

Do not install the PyPI project named `pytplot` for this script. That distribution stops at 1.7.x and is a different plotting library, so a requirement of `pytplot>=2.0` cannot be installed.

This script does not import `pyspedas`. PySPEDAS 2.0 and later moved these plotting routines into the `pyspedas` package; this repository has not been updated to that import style.

## Run

Put CDF files in the three directories above (or edit `base_dir` / `instrument_paths`), then from the directory that contains those folders:

```bash
python maven_3d_particle_distributions.py
```

If a directory has no CDFs, the script prints `No files found.` and continues with the next instrument. With the default empty `base_dir` and no local files, that is the whole run.

`tplot` and `plt.show()` open on-screen figures. On a non-interactive Matplotlib backend they return without saving a file.

## Data you have to obtain separately

Calibrated MAVEN CDFs are distributed by NASA's Planetary Data System PPI node. The script will load whatever `*.cdf` files are in the folders above; it does not check the product id.

- SWEA search: https://pds-ppi.igpp.ucla.edu/search/?sc=MAVEN&i=SWEA
- STATIC search: https://pds-ppi.igpp.ucla.edu/search/?sc=MAVEN&i=STATIC
- SEP search: https://pds-ppi.igpp.ucla.edu/search/?sc=MAVEN&i=SEP
- PDS data search: https://pds.nasa.gov/datasearch/data-search/

The script comment for SWEA refers to survey 3D data (`svy3d`). The STATIC comment names the CDF filename token `d1-32e4d16a8m` (collection `urn:nasa:pds:maven.static.c:data.d1_32e4d16a8m`, files such as `mvn_sta_l2_d1-32e4d16a8m_*.cdf`). `d0_32e4d16a8m` is a different STATIC collection; this script does not treat it separately. The SEP comment refers to `cal-svy-full` and is uncertain about one bin count (`16?`).

## Licence

This repository does not include a licence file.
