import plotext as plt
from typing import List, Dict

class Visualizer:
    def __init__(self):
        pass

    def plot_metric(self, data: List[Dict], metric_name: str, threshold: float):
        """
        Plots a given metric from a list of data points.
        """
        # Extract data for plotting
        values = [d.get(metric_name, 0) for d in data]
        timestamps = range(len(values))

        plt.clc() # clear canvas
        plt.plot(timestamps, values, label=f'{metric_name}')
        
        # Draw threshold line if it's within the plot limits
        min_val, max_val = min(values) if values else 0, max(values) if values else 0
        if min_val <= threshold <= max_val:
            plt.axhline(y=threshold, color='red', linestyle='--', label=f'Threshold ({threshold})')

        plt.title(f'Metric: {metric_name}')
        plt.xlabel('Time (snapshot)')
        plt.ylabel('Value')
        plt.show() 