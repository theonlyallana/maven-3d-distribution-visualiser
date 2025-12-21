# maven_3d_particle_distributions.py

import os
import glob
import numpy as np
from pytplot import cdf_to_tplot, tplot, tnames, get_data, store_data, options
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# --- CONFIGURATION ---
base_dir = r''

instrument_paths = {
    'swea': os.path.join(base_dir, '_maven.swea.calibrated'),
    'static': os.path.join(base_dir, '_maven.static.c'),
    'sep': os.path.join(base_dir, '_maven.sep.calibrated'),
}

output_dir = os.path.join(base_dir, 'processed_data_3d_improved')
os.makedirs(output_dir, exist_ok=True)

# Number of 3D snapshots to generate (evenly spaced over time)
num_3d_snapshots = 5

# Instrument-specific configurations for better labeling (based on MAVEN documentation)
instrument_configs = {
    'swea': {
        'description': "SWEA svy3d: 3D electron distribution. Dimensions: time x elevation (-60° to +60° in 6 bins) x azimuth (0° to 360° in 16 bins) x energy (64 bins, ~3-4600 eV). Units for flux: eV/cm²-s-sr-eV.",
        'theta_range': (-60, 60),  # elevation/deflection
        'phi_range': (0, 360),  # azimuth/anode
        'energy_desc': "Energy bins (eV)",
        'flux_label': "Diff. Energy Flux [eV/cm² s sr eV]",
        'angle_label1': "Elevation (deflection, degrees)",
        'angle_label2': "Azimuth (anode, degrees)"
    },
    'static': {
        'description': "STATIC d1-32e4d16a8m: High-angular ion distribution. Dimensions: time x mass (8 bins) x energy (32 bins, ~0.1-25 keV) x angle (64 bins = 4 deflections x 16 anodes, ±60° deflection, 22.5° azimuth). Units for flux: eV/cm²-s-sr-eV.",
        'theta_range': (-60, 60),  # deflection
        'phi_range': (0, 360),  # anode
        'energy_desc': "Energy bins (eV/q)",
        'flux_label': "Diff. Energy Flux [eV/cm² s sr eV]",
        'angle_label1': "Deflection (degrees)",
        'angle_label2': "Anode (azimuth, degrees)"
    },
    'sep': {
        'description': "SEP cal-svy-full: Calibrated energetic particle spectra. Dimensions: time x look directions/sensors (6, e.g., F/R/O for ion/electron) x bins (16?) x energy (64 bins, ions ~25 keV-6 MeV, electrons ~25-500 keV). Units for flux: #/cm²-s-sr-keV.",
        'theta_range': (0, 180),  # Approximate for look directions
        'phi_range': (0, 360),
        'energy_desc': "Energy bins (keV)",
        'flux_label': "Particle Flux [#/cm² s sr keV]",
        'angle_label1': "Look Direction 1",
        'angle_label2': "Look Direction 2"
    }
}

def process_instrument(name, path):
    config = instrument_configs.get(name, {})
    print(f"\n=== Processing {name.upper()} ===")
    print(f"Description: {config.get('description', 'No description available')}")
    
    cdf_files = sorted(glob.glob(os.path.join(path, '**', '*.cdf'), recursive=True))
    if not cdf_files:
        print("No files found.")
        return
    
    print(f"Found {len(cdf_files)} files.")
    
    cdf_to_tplot(cdf_files)
    if not tnames():
        print("No variables loaded.")
        return
    
    # Select flux variable
    flux_vars = [v for v in tnames() if any(k in v.lower() for k in ['flux', 'eflux', 'diff_en'])]
    flux_var = flux_vars[0] if flux_vars else tnames()[0]
    print(f"Primary variable: {flux_var}")
    
    data = get_data(flux_var)
    y = data.y
    times = pd.to_datetime(data.times, unit='s')
    shape = y.shape
    print(f"Data shape: {shape}")
    
    # Add better labels to raw plot
    options(flux_var, 'ytitle', config.get('energy_desc', 'Energy'))
    options(flux_var, 'ztitle', config.get('flux_label', 'Flux'))
    tplot(flux_var)
    
    if len(shape) >= 4:  # Multi-dim data
        # Create omni spectrogram
        omni_y = np.nansum(y, axis=(1, 2))  # Sum angles
        omni_var = f'{name}_omni_flux'
        store_data(omni_var, data={'x': data.times, 'y': omni_y})
        options(omni_var, 'ytitle', config.get('energy_desc', 'Energy [eV]'))
        options(omni_var, 'ztitle', config.get('flux_label', 'Flux'))
        tplot(omni_var)
        print(f"Omnidirectional spectrogram plotted (summed over angles).")
        
        # Save omni
        df = pd.DataFrame(omni_y, index=times, columns=[f'Bin_{i}' for i in range(omni_y.shape[1])])
        df.mean(axis=1).to_csv(os.path.join(output_dir, f'{name}_omni_mean_flux.csv'))
        xr.Dataset.from_dataframe(df).to_netcdf(os.path.join(output_dir, f'{name}_omni_spectrogram.nc'))
        
        # 3D snapshots
        n_time = shape[0]
        indices = np.linspace(0, n_time - 1, num_3d_snapshots, dtype=int)
        
        n_theta = shape[1]
        n_phi = shape[2]
        
        theta_vals = np.linspace(config['theta_range'][0], config['theta_range'][1], n_theta)
        phi_vals = np.linspace(config['phi_range'][0], config['phi_range'][1], n_phi, endpoint=False)
        
        Theta, Phi = np.meshgrid(theta_vals, phi_vals, indexing='ij')
        
        for ti in indices:
            print(f"Generating 3D snapshot for time {times[ti]} (index {ti})...")
            
            angular_slice = np.nanmean(y[ti], axis=-1)  # Avg over energy
            
            R = angular_slice
            
            X = R * np.cos(np.deg2rad(Phi)) * np.cos(np.deg2rad(Theta))
            Y = R * np.sin(np.deg2rad(Phi)) * np.cos(np.deg2rad(Theta))
            Z = R * np.sin(np.deg2rad(Theta))
            
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            surf = ax.plot_surface(X, Y, Z, cmap='viridis', linewidth=0)
            fig.colorbar(surf, label=config.get('flux_label', 'Flux'))
            ax.set_title(f'{name.upper()} 3D Angular Distribution\n{times[ti]}')
            ax.set_xlabel(f"{config.get('angle_label2', 'Azimuth')} direction")
            ax.set_ylabel(f"{config.get('angle_label2', 'Azimuth')} direction")
            ax.set_zlabel(f"{config.get('angle_label1', 'Elevation')} direction")
            plt.show()
            print("What this 3D plot shows: Flux distribution in instrument angular coordinates. Radius/color = flux intensity; axes represent projected directions (e.g., towards Sun or planet).")

process_instrument('swea', instrument_paths['swea'])
process_instrument('static', instrument_paths['static'])
process_instrument('sep', instrument_paths['sep'])

print("\nAll done! Check folder:", output_dir)