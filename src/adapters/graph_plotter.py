import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import make_interp_spline
from typing import List
from src.interfaces import IGraphGenerator
from src.domain.models import EnergySeries

class GraphPlotter(IGraphGenerator):
    """
    Generates visualizations for energy data using matplotlib.
    """
    def generate_graphs(self, series: EnergySeries, output_dir: str, output_file: str = None, 
                       smoothing_method: str = None, smoothing_param: float = None) -> List[str]:
        """
        Generates graphs and saves them to the specified directory.

        Supports smoothing methods:
        - 'rolling': Rolling mean smoothing.
        - 'spline': Cubic spline interpolation.

        Also calculates and displays total import/export values in the graph title and legend.

        Args:
            series (EnergySeries): The energy data to visualize.
            output_dir (str): The directory to save the generated graphs.
            output_file (str, optional): The filename for the output graph. Defaults to None.
            smoothing_method (str, optional): The smoothing method to apply ('rolling' or 'spline'). Defaults to None.
            smoothing_param (float, optional): Parameter for the smoothing method (e.g., window size for rolling). Defaults to None.

        Returns:
            List[str]: A list of file paths to the generated graphs.
        """
        if series.df.empty:
            return []
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = []
        
        # Prepare data
        x = series.df['timestamp']
        y_import = series.df['import_energy']
        y_export = series.df['export_energy']
        
        # Apply smoothing if requested
        if smoothing_method == 'rolling':
            # Param is window size (int)
            window = int(smoothing_param) if smoothing_param else 3
            y_import = y_import.rolling(window=window, center=True).mean()
            y_export = y_export.rolling(window=window, center=True).mean()
        elif smoothing_method == 'spline':
            # Param is smoothing factor (not directly used in make_interp_spline, but we can use it for something else or ignore)
            # Actually, make_interp_spline is for interpolation.
            # For smoothing, we might want UnivariateSpline or just interpolation on a denser grid.
            # Let's use make_interp_spline to create a smooth curve on a denser grid.
            
            # Convert timestamps to numbers for spline
            x_nums = np.arange(len(x))
            
            # Create denser grid
            x_new = np.linspace(x_nums.min(), x_nums.max(), 300)
            
            # Spline (k=3 for cubic)
            try:
                spl_import = make_interp_spline(x_nums, y_import, k=3)
                spl_export = make_interp_spline(x_nums, y_export, k=3)
                
                y_import_smooth = spl_import(x_new)
                y_export_smooth = spl_export(x_new)
                
                # We need to map x_new back to timestamps for plotting?
                # Or just plot against x_new and label properly?
                # Easier: just plot against x_new, but we lose date labels on X axis unless we interpolate them too.
                # Let's interpolate timestamps too.
                x_timestamps_nums = np.linspace(x.iloc[0].value, x.iloc[-1].value, 300)
                x_smooth = pd.to_datetime(x_timestamps_nums)
                
                # Update data for plotting
                x = x_smooth
                y_import = y_import_smooth
                y_export = y_export_smooth
            except Exception as e:
                print(f"Spline smoothing failed: {e}. Falling back to raw data.")

        # Calculate totals
        total_import = series.df['import_energy'].sum()
        total_export = series.df['export_energy'].sum()

        # Plot 1: Daily Usage (Import vs Export)
        plt.figure(figsize=(10, 6))
        plt.plot(x, y_import, label=f'Import (Total: {total_import:.2f} kWh)')
        plt.plot(x, y_export, label=f'Export (Total: {total_export:.2f} kWh)')
        plt.xlabel('Time')
        plt.ylabel('Energy (kWh)')
        plt.title(f'Energy Import vs Export Over Time ({smoothing_method or "Raw"})\nTotal Import: {total_import:.2f} kWh | Total Export: {total_export:.2f} kWh')
        plt.legend()
        plt.grid(True)
        
        if output_file:
            # If output_file is provided, use it. 
            # If it's just a filename, join with output_dir.
            # If it's a path, use it as is?
            # Let's assume it's a filename relative to output_dir for simplicity, or absolute.
            # But the user asked for "output filename", so maybe they want to override the default "energy_over_time.png".
            output_path = os.path.join(output_dir, output_file)
        else:
            output_path = os.path.join(output_dir, 'energy_over_time.png')
            
        plt.savefig(output_path)
        plt.close()
        generated_files.append(output_path)
        
        return generated_files
