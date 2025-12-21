# MAVEN 3D Particle Distribution Visualizer

A Python tool to load calibrated MAVEN particle data (SWEA, STATIC, SEP), generate omnidirectional spectrograms, and create intuitive **3D angular distribution plots** of differential energy flux in instrument coordinates.

## Why This Tool Is Useful

Understanding 3D particle velocity distributions is key to studying plasma processes around Mars, such as:
- Solar wind interaction with the Martian atmosphere
- Ionospheric electron/ion escape
- Pitch angle distributions and beam/anisotropy features
- Energetic particle events

Standard 2D spectrograms (energy vs. time) lose angular information. This script:
- Sums over angles for clean **omnidirectional spectrograms**
- Projects angular flux onto a 3D spherical surface (radius/color = flux intensity) for selected time snapshots
- Provides clear labeling based on official MAVEN instrument documentation
- Saves processed data as CSV (quick inspection) and NetCDF (standard scientific format)

It's especially helpful for quick-look analysis, student projects, or preparing figures for publications — without needing complex SPEDAS setups or manual coordinate transformations.

## Features

- Supports SWEA (3D electrons), STATIC (high-resolution ions), and SEP (energetic particles)
- Automatic omnidirectional flux calculation
- 3D surface plots showing flux distribution in elevation/azimuth
- Outputs: interactive plots, CSV mean flux, NetCDF full spectrograms
- Configurable number of 3D snapshots

## Requirements

Python 3.8+ and the following packages (install via `pip install -r requirements.txt`):

- numpy
- pandas
- xarray
- matplotlib
- pytplot (>=2.0)
- pyspedas (for easy data download — optional if you already have local CDF files)

## Data Sources

MAVEN calibrated CDF files are publicly available from NASA's Planetary Data System (PDS) Planetary Plasma Interactions (PPI) Node:

- **SWEA**: Search/download from https://pds-ppi.igpp.ucla.edu/search/?sc=MAVEN&i=SWEA (look for "calibrated" bundles, especially `svy_3d` for 3D distributions)
- **STATIC**: https://pds-ppi.igpp.ucla.edu/search/?sc=MAVEN&i=STATIC (e.g., `d0_32e4d16a8m` or similar high-angular resolution products)
- **SEP**: https://pds-ppi.igpp.ucla.edu/search/?sc=MAVEN&i=SEP (cal-svy-full)

Alternative: Use **pyspedas** to automatically download files (recommended for reproducibility — see below).

Full PDS search: https://pds.nasa.gov/datasearch/data-search/

pyspedas documentation: https://pyspedas.readthedocs.io/en/latest/getting_started.html
