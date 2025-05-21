"""
Property visualization for the ASDii library.

This module provides functions for visualizing properties of APIs, polymers,
and ASD formulations.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import logging
import numpy as np
import os

try:
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("Matplotlib not available. Visualization functionality will be limited.")

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    logging.warning("Seaborn not available. Some visualization functionality will be limited.")


def check_visualization_dependencies() -> bool:
    """
    Check if the required dependencies for visualization are available.
    
    Returns:
        bool: True if available, False otherwise
    """
    if not MATPLOTLIB_AVAILABLE:
        logging.error("Matplotlib is required for visualization.")
        return False
    
    return True


def plot_solubility_parameters(
    materials: List[Dict[str, Any]], 
    names: Optional[List[str]] = None, 
    markers: Optional[List[str]] = None, 
    colors: Optional[List[str]] = None
) -> Optional[Figure]:
    """
    Plot Hansen solubility parameters in 3D space.
    
    Args:
        materials (list): List of dictionaries with solubility parameters
            Each dictionary should have keys 'dispersive', 'polar', and 'hydrogen'
        names (list, optional): List of names for the materials
        markers (list, optional): List of markers for the materials
        colors (list, optional): List of colors for the materials
        
    Returns:
        matplotlib.figure.Figure or None: Figure object if successful, None otherwise
    """
    if not check_visualization_dependencies():
        return None
    
    try:
        # Create figure
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Set default names, markers, and colors if not provided
        if names is None:
            names = [f"Material {i+1}" for i in range(len(materials))]
        
        if markers is None:
            available_markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'h', 'x', '+']
            markers = [available_markers[i % len(available_markers)] for i in range(len(materials))]
        
        if colors is None:
            if SEABORN_AVAILABLE:
                colors = sns.color_palette("husl", len(materials))
            else:
                colors = [f"C{i}" for i in range(len(materials))]
        
        # Plot each material
        for i, material in enumerate(materials):
            # Extract solubility parameters
            dispersive = material.get('dispersive')
            polar = material.get('polar')
            hydrogen = material.get('hydrogen')
            
            # Skip if any parameter is missing
            if dispersive is None or polar is None or hydrogen is None:
                logging.warning(f"Solubility parameters missing for {names[i]}. Skipping.")
                continue
            
            # Plot point
            ax.scatter(
                dispersive, 
                polar, 
                hydrogen, 
                marker=markers[i], 
                color=colors[i], 
                s=100, 
                label=names[i]
            )
            
            # Add text label
            ax.text(dispersive, polar, hydrogen, names[i], fontsize=8)
        
        # Set labels and title
        ax.set_xlabel('Dispersive (δd)')
        ax.set_ylabel('Polar (δp)')
        ax.set_zlabel('Hydrogen Bonding (δh)')
        ax.set_title('Hansen Solubility Parameters')
        
        # Add legend
        ax.legend()
        
        # Add grid
        ax.grid(True)
        
        return fig
    
    except Exception as e:
        logging.error(f"Failed to plot solubility parameters: {e}")
        return None


def plot_bagley_diagram(
    materials: List[Dict[str, Any]], 
    names: Optional[List[str]] = None, 
    markers: Optional[List[str]] = None, 
    colors: Optional[List[str]] = None
) -> Optional[Figure]:
    """
    Plot a Bagley diagram for solubility parameters.
    
    A Bagley diagram plots (δh) vs. (δd + δp) to simplify the 3D Hansen space.
    
    Args:
        materials (list): List of dictionaries with solubility parameters
            Each dictionary should have keys 'dispersive', 'polar', and 'hydrogen'
        names (list, optional): List of names for the materials
        markers (list, optional): List of markers for the materials
        colors (list, optional): List of colors for the materials
        
    Returns:
        matplotlib.figure.Figure or None: Figure object if successful, None otherwise
    """
    if not check_visualization_dependencies():
        return None
    
    try:
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Set default names, markers, and colors if not provided
        if names is None:
            names = [f"Material {i+1}" for i in range(len(materials))]
        
        if markers is None:
            available_markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'h', 'x', '+']
            markers = [available_markers[i % len(available_markers)] for i in range(len(materials))]
        
        if colors is None:
            if SEABORN_AVAILABLE:
                colors = sns.color_palette("husl", len(materials))
            else:
                colors = [f"C{i}" for i in range(len(materials))]
        
        # Plot each material
        for i, material in enumerate(materials):
            # Extract solubility parameters
            dispersive = material.get('dispersive')
            polar = material.get('polar')
            hydrogen = material.get('hydrogen')
            
            # Skip if any parameter is missing
            if dispersive is None or polar is None or hydrogen is None:
                logging.warning(f"Solubility parameters missing for {names[i]}. Skipping.")
                continue
            
            # Calculate Bagley parameters
            x = dispersive + polar
            y = hydrogen
            
            # Plot point
            ax.scatter(
                x, 
                y, 
                marker=markers[i], 
                color=colors[i], 
                s=100, 
                label=names[i]
            )
            
            # Add text label
            ax.text(x, y, names[i], fontsize=8)
        
        # Set labels and title
        ax.set_xlabel('δd + δp')
        ax.set_ylabel('δh')
        ax.set_title('Bagley Diagram')
        
        # Add legend
        ax.legend()
        
        # Add grid
        ax.grid(True)
        
        return fig
    
    except Exception as e:
        logging.error(f"Failed to plot Bagley diagram: {e}")
        return None


def plot_teas_diagram(
    materials: List[Dict[str, Any]], 
    names: Optional[List[str]] = None, 
    markers: Optional[List[str]] = None, 
    colors: Optional[List[str]] = None
) -> Optional[Figure]:
    """
    Plot a Teas diagram for solubility parameters.
    
    A Teas diagram is a triangular plot showing the fractional contribution
    of each Hansen parameter to the total.
    
    Args:
        materials (list): List of dictionaries with solubility parameters
            Each dictionary should have keys 'dispersive', 'polar', and 'hydrogen'
        names (list, optional): List of names for the materials
        markers (list, optional): List of markers for the materials
        colors (list, optional): List of colors for the materials
        
    Returns:
        matplotlib.figure.Figure or None: Figure object if successful, None otherwise
    """
    if not check_visualization_dependencies():
        return None
    
    try:
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Set default names, markers, and colors if not provided
        if names is None:
            names = [f"Material {i+1}" for i in range(len(materials))]
        
        if markers is None:
            available_markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'h', 'x', '+']
            markers = [available_markers[i % len(available_markers)] for i in range(len(materials))]
        
        if colors is None:
            if SEABORN_AVAILABLE:
                colors = sns.color_palette("husl", len(materials))
            else:
                colors = [f"C{i}" for i in range(len(materials))]
        
        # Draw triangular grid
        # Draw triangular outline
        ax.plot([0, 1, 0.5, 0], [0, 0, np.sqrt(3)/2, 0], 'k-')
        
        # Draw grid lines
        grid_spacing = 0.1
        for i in range(1, 10):
            # Horizontal lines
            y = i * grid_spacing * np.sqrt(3)/2
            x_left = 0.5 - (i * grid_spacing) / 2
            x_right = 0.5 + (i * grid_spacing) / 2
            ax.plot([x_left, x_right], [y, y], 'k-', alpha=0.2)
            
            # Left to right diagonal lines
            ax.plot([i * grid_spacing, 1], [0, 0], 'k-', alpha=0.2)
            
            # Right to left diagonal lines
            ax.plot([i * grid_spacing, 0], [0, 0], 'k-', alpha=0.2)
        
        # Plot each material
        for i, material in enumerate(materials):
            # Extract solubility parameters
            dispersive = material.get('dispersive')
            polar = material.get('polar')
            hydrogen = material.get('hydrogen')
            
            # Skip if any parameter is missing
            if dispersive is None or polar is None or hydrogen is None:
                logging.warning(f"Solubility parameters missing for {names[i]}. Skipping.")
                continue
            
            # Calculate fractional parameters
            total = dispersive + polar + hydrogen
            fd = dispersive / total
            fp = polar / total
            fh = hydrogen / total
            
            # Convert to Cartesian coordinates for plotting
            x = 0.5 * (2 * fp + fh) / (fd + fp + fh)
            y = (np.sqrt(3) / 2) * fh / (fd + fp + fh)
            
            # Plot point
            ax.scatter(
                x, 
                y, 
                marker=markers[i], 
                color=colors[i], 
                s=100, 
                label=names[i]
            )
            
            # Add text label
            ax.text(x, y, names[i], fontsize=8)
        
        # Label corners
        ax.text(0, 0, 'Dispersive (δd)', fontsize=12, ha='right')
        ax.text(1, 0, 'Polar (δp)', fontsize=12, ha='left')
        ax.text(0.5, np.sqrt(3)/2, 'Hydrogen Bonding (δh)', fontsize=12, ha='center', va='bottom')
        
        # Set title
        ax.set_title('Teas Diagram')
        
        # Add legend
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
        
        # Remove axes
        ax.set_axis_off()
        
        return fig
    
    except Exception as e:
        logging.error(f"Failed to plot Teas diagram: {e}")
        return None


def plot_glass_transition_composition(
    material_1_name: str,
    material_2_name: str,
    material_1_tg: float,
    material_2_tg: float,
    compositions: Optional[List[float]] = None,
    experimental_data: Optional[List[Tuple[float, float]]] = None,
    model: str = 'gordon_taylor',
    k: Optional[float] = None
) -> Optional[Figure]:
    """
    Plot glass transition temperature as a function of composition.
    
    Args:
        material_1_name (str): Name of the first material
        material_2_name (str): Name of the second material
        material_1_tg (float): Glass transition temperature of the first material
        material_2_tg (float): Glass transition temperature of the second material
        compositions (list, optional): List of compositions to evaluate
        experimental_data (list, optional): List of (composition, Tg) tuples
        model (str, optional): Model for Tg prediction ('gordon_taylor', 'fox')
        k (float, optional): Gordon-Taylor parameter
        
    Returns:
        matplotlib.figure.Figure or None: Figure object if successful, None otherwise
    """
    if not check_visualization_dependencies():
        return None
    
    try:
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate compositions if not provided
        if compositions is None:
            compositions = np.linspace(0, 1, 101)
        
        # Convert temperatures to Kelvin for calculations
        material_1_tg_k = material_1_tg + 273.15
        material_2_tg_k = material_2_tg + 273.15
        
        # Calculate Tg for each composition
        tgs = []
        for w1 in compositions:
            w2 = 1 - w1
            
            # Gordon-Taylor
            if model == 'gordon_taylor':
                # Estimate K if not provided
                if k is None:
                    k = material_1_tg_k / material_2_tg_k
                
                tg_k = (w1 * material_1_tg_k + k * w2 * material_2_tg_k) / (w1 + k * w2)
            
            # Fox
            elif model == 'fox':
                tg_k = 1 / (w1 / material_1_tg_k + w2 / material_2_tg_k)
            
            # Convert back to Celsius
            tg = tg_k - 273.15
            tgs.append(tg)
        
        # Plot predicted Tg
        ax.plot(compositions, tgs, 'b-', label=f'{model.title()} Model')
        
        # Plot experimental data if provided
        if experimental_data:
            exp_comps, exp_tgs = zip(*experimental_data)
            ax.scatter(exp_comps, exp_tgs, color='red', marker='o', s=50, label='Experimental Data')
        
        # Set labels and title
        ax.set_xlabel(f'{material_1_name} Weight Fraction')
        ax.set_ylabel('Glass Transition Temperature (°C)')
        ax.set_title(f'Glass Transition Temperature vs. Composition ({model.title()} Model)')
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add material labels at x=0 and x=1
        ax.text(0, material_2_tg, f'{material_2_name}\nTg = {material_2_tg:.1f}°C', ha='left', va='bottom')
        ax.text(1, material_1_tg, f'{material_1_name}\nTg = {material_1_tg:.1f}°C', ha='right', va='bottom')
        
        # Add equation as a text box
        if model == 'gordon_taylor':
            k_value = k if k is not None else material_1_tg_k / material_2_tg_k
            equation = f"Tg = \\frac{{w_1 \\cdot Tg_1 + K \\cdot w_2 \\cdot Tg_2}}{{w_1 + K \\cdot w_2}}\nK = {k_value:.2f}"
        elif model == 'fox':
            equation = "\\frac{1}{Tg} = \\frac{w_1}{Tg_1} + \\frac{w_2}{Tg_2}"
        
        ax.text(0.05, 0.95, equation, transform=ax.transAxes, 
                bbox=dict(facecolor='white', alpha=0.8),
                verticalalignment='top', horizontalalignment='left',
                usetex=False)  # Using raw strings for better math rendering in most environments
        
        # Add legend
        ax.legend()
        
        return fig
    
    except Exception as e:
        logging.error(f"Failed to plot glass transition vs. composition: {e}")
        return None


def plot_stability_map(
    api_property: List[float],
    polymer_property: List[float],
    stability_scores: List[List[float]],
    api_label: str,
    polymer_label: str,
    api_values: Optional[List[float]] = None,
    polymer_values: Optional[List[float]] = None,
    highlight_point: Optional[Tuple[float, float]] = None
) -> Optional[Figure]:
    """
    Plot a stability map as a function of API and polymer properties.
    
    Args:
        api_property (list): List of API property values (x-axis)
        polymer_property (list): List of polymer property values (y-axis)
        stability_scores (list): 2D list of stability scores
        api_label (str): Label for the API property
        polymer_label (str): Label for the polymer property
        api_values (list, optional): List of specific API values to mark
        polymer_values (list, optional): List of specific polymer values to mark
        highlight_point (tuple, optional): Point to highlight (x, y)
        
    Returns:
        matplotlib.figure.Figure or None: Figure object if successful, None otherwise
    """
    if not check_visualization_dependencies():
        return None
    
    try:
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create a meshgrid for contour plot
        X, Y = np.meshgrid(api_property, polymer_property)
        
        # Create contour plot
        contour = ax.contourf(X, Y, stability_scores, levels=20, cmap='viridis')
        
        # Add contour lines
        contour_lines = ax.contour(X, Y, stability_scores, levels=10, colors='white', alpha=0.5, linewidths=0.5)
        
        # Add stability threshold line
        threshold = 0.7
        threshold_contour = ax.contour(X, Y, stability_scores, levels=[threshold], colors='red', linestyles='dashed', linewidths=2)
        ax.clabel(threshold_contour, inline=True, fontsize=10, fmt=f'Stability = {threshold}')
        
        # Add colorbar
        cbar = fig.colorbar(contour)
        cbar.set_label('Stability Score')
        
        # Mark specific values if provided
        if api_values is not None and polymer_values is not None:
            for api_value in api_values:
                ax.axvline(x=api_value, color='gray', linestyle='--', alpha=0.5)
            
            for polymer_value in polymer_values:
                ax.axhline(y=polymer_value, color='gray', linestyle='--', alpha=0.5)
        
        # Highlight specific point if provided
        if highlight_point is not None:
            ax.plot(highlight_point[0], highlight_point[1], 'ro', markersize=10, label='Current Formulation')
        
        # Set labels and title
        ax.set_xlabel(api_label)
        ax.set_ylabel(polymer_label)
        ax.set_title('Stability Map')
        
        # Add legend if highlight point is provided
        if highlight_point is not None:
            ax.legend()
        
        return fig
    
    except Exception as e:
        logging.error(f"Failed to plot stability map: {e}")
        return None


def save_visualization(fig: Figure, file_path: str, dpi: int = 300) -> bool:
    """
    Save a visualization to a file.
    
    Args:
        fig (matplotlib.figure.Figure): Figure to save
        file_path (str): Path to save the file
        dpi (int, optional): DPI for the saved figure
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Save figure
        fig.savefig(file_path, dpi=dpi, bbox_inches='tight')
        
        return True
    except Exception as e:
        logging.error(f"Failed to save visualization: {e}")
        return False