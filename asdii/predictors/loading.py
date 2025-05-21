"""
Implementation of the LoadingOptimizer class.

This module provides the LoadingOptimizer class which optimizes drug loading
for a given API-polymer combination.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import logging
import numpy as np

from asdii.core.api import API
from asdii.core.polymer import Polymer
from asdii.core.formulation import ASDFormulation


class LoadingOptimizer:
    """
    Optimizes drug loading for a given API-polymer combination.
    
    Attributes:
        api (API): API object
        polymer (Polymer): Polymer object
        process_method (str): Manufacturing method
        process_parameters (dict): Dictionary of process parameters
        min_loading (float): Minimum drug loading to consider
        max_loading (float): Maximum drug loading to consider
        min_stability (float): Minimum acceptable stability score
    """
    
    def __init__(
        self, 
        api: API, 
        polymer: Polymer, 
        process_method: Optional[str] = None, 
        min_loading: float = 0.1, 
        max_loading: float = 0.5, 
        min_stability: float = 0.7, 
        **process_parameters: Dict[str, Any]
    ) -> None:
        """
        Initialize a LoadingOptimizer object.
        
        Args:
            api (API): API object
            polymer (Polymer): Polymer object
            process_method (str, optional): Manufacturing method
            min_loading (float, optional): Minimum drug loading to consider
            max_loading (float, optional): Maximum drug loading to consider
            min_stability (float, optional): Minimum acceptable stability score
            **process_parameters: Additional process parameters
        
        Raises:
            ValueError: If min_loading or max_loading are not between 0 and 1,
                or if min_loading > max_loading
        """
        if not 0 <= min_loading <= 1:
            raise ValueError("min_loading must be between 0 and 1.")
        if not 0 <= max_loading <= 1:
            raise ValueError("max_loading must be between 0 and 1.")
        if min_loading > max_loading:
            raise ValueError("min_loading must be less than or equal to max_loading.")
        if not 0 <= min_stability <= 1:
            raise ValueError("min_stability must be between 0 and 1.")
        
        self.api = api
        self.polymer = polymer
        self.process_method = process_method
        self.process_parameters = process_parameters
        self.min_loading = min_loading
        self.max_loading = max_loading
        self.min_stability = min_stability
        
        # Initialize results
        self.results = {}
    
    def evaluate_loading(self, loading: float) -> Dict[str, Any]:
        """
        Evaluate a specific drug loading value.
        
        Args:
            loading (float): Drug loading to evaluate
            
        Returns:
            dict: Evaluation results:
                'loading': Drug loading value
                'stability': Stability score
                'thermodynamic_stability': Thermodynamic stability score
                'kinetic_stability': Kinetic stability score
                'glass_transition_temp': Glass transition temperature
                'miscibility': Miscibility score
                'shelf_life_estimate': Estimated shelf life in months
        """
        # Validate loading value
        if not 0 <= loading <= 1:
            raise ValueError("loading must be between 0 and 1.")
        
        # Create formulation with the specified loading
        formulation = ASDFormulation(
            api=self.api,
            polymer=self.polymer,
            drug_loading=loading,
            process_method=self.process_method,
            **self.process_parameters
        )
        
        # Predict stability
        stability = formulation.predict_stability()
        
        # Create result
        result = {
            'loading': loading,
            'stability': stability['score'],
            'thermodynamic_stability': stability['thermodynamic'],
            'kinetic_stability': stability['kinetic'],
            'glass_transition_temp': formulation.predicted_tg,
            'miscibility': formulation.predicted_miscibility,
            'shelf_life_estimate': stability['shelf_life_estimate']
        }
        
        # Store result
        self.results[loading] = result
        
        return result
    
    def find_optimal_loading(self, method: str = 'binary_search') -> float:
        """
        Find the optimal drug loading.
        
        Args:
            method (str, optional): Optimization method:
                'binary_search': Binary search algorithm
                'grid_search': Grid search algorithm
            
        Returns:
            float: Optimal drug loading as weight fraction (0-1)
            
        Raises:
            ValueError: If method is not valid
        """
        if method == 'binary_search':
            return self._binary_search()
        elif method == 'grid_search':
            return self._grid_search()
        else:
            raise ValueError(f"Invalid method: {method}. Valid methods are: 'binary_search', 'grid_search'")
    
    def _binary_search(self) -> float:
        """
        Find the optimal drug loading using a binary search algorithm.
        
        Returns:
            float: Optimal drug loading
        """
        # Define search range
        low = self.min_loading
        high = self.max_loading
        
        # Define convergence criteria
        max_iterations = 10
        tolerance = 0.01
        
        # Initialize results
        optimal_loading = low
        optimal_stability = 0.0
        
        # Evaluate endpoints
        low_result = self.evaluate_loading(low)
        high_result = self.evaluate_loading(high)
        
        # Check if endpoints meet stability requirement
        if low_result['stability'] >= self.min_stability:
            # If low endpoint is stable, check if high endpoint is stable
            if high_result['stability'] >= self.min_stability:
                # Both endpoints are stable, return high endpoint
                return high
            else:
                # Only low endpoint is stable, start binary search
                optimal_loading = low
                optimal_stability = low_result['stability']
        else:
            # Low endpoint is not stable, formulation might not be viable
            # Check high endpoint as a last resort
            if high_result['stability'] >= self.min_stability:
                return high
            else:
                # Neither endpoint is stable, return the one with higher stability
                if low_result['stability'] > high_result['stability']:
                    return low
                else:
                    return high
        
        # Perform binary search
        for _ in range(max_iterations):
            # Check if search range is small enough
            if high - low < tolerance:
                break
            
            # Try middle point
            mid = (low + high) / 2
            mid_result = self.evaluate_loading(mid)
            
            # Update optimal loading if mid point is stable and has higher loading
            if mid_result['stability'] >= self.min_stability and mid > optimal_loading:
                optimal_loading = mid
                optimal_stability = mid_result['stability']
            
            # Update search range
            if mid_result['stability'] >= self.min_stability:
                # Mid point is stable, search in upper half
                low = mid
            else:
                # Mid point is not stable, search in lower half
                high = mid
        
        return optimal_loading
    
    def _grid_search(self) -> float:
        """
        Find the optimal drug loading using a grid search algorithm.
        
        Returns:
            float: Optimal drug loading
        """
        # Define grid
        num_points = 9
        loadings = np.linspace(self.min_loading, self.max_loading, num_points)
        
        # Initialize results
        optimal_loading = self.min_loading
        optimal_stability = 0.0
        
        # Evaluate all points
        for loading in loadings:
            result = self.evaluate_loading(loading)
            
            # Update optimal loading if current point is stable and has higher loading
            if result['stability'] >= self.min_stability and loading > optimal_loading:
                optimal_loading = loading
                optimal_stability = result['stability']
        
        # If no point meets stability requirement, return the one with highest stability
        if optimal_stability < self.min_stability:
            # Find point with highest stability
            max_stability = 0.0
            max_stability_loading = self.min_loading
            
            for loading, result in self.results.items():
                if result['stability'] > max_stability:
                    max_stability = result['stability']
                    max_stability_loading = loading
            
            return max_stability_loading
        
        return optimal_loading
    
    def plot_stability_vs_loading(self) -> Any:
        """
        Plot stability score versus drug loading.
        
        Returns:
            matplotlib.figure.Figure: Figure object with the plot
            
        Raises:
            ImportError: If matplotlib is not available
            ValueError: If no results are available
        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.figure import Figure
        except ImportError:
            raise ImportError("Matplotlib is required for visualization.")
        
        # Check if results are available
        if not self.results:
            raise ValueError("No results available. Run find_optimal_loading() or evaluate_loading() first.")
        
        # Extract data
        loadings = []
        stabilities = []
        thermo_stabilities = []
        kinetic_stabilities = []
        tgs = []
        
        for loading, result in sorted(self.results.items()):
            loadings.append(loading)
            stabilities.append(result['stability'])
            thermo_stabilities.append(result['thermodynamic_stability'])
            kinetic_stabilities.append(result['kinetic_stability'])
            tgs.append(result['glass_transition_temp'])
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [3, 1]})
        
        # Plot stability scores
        ax1.plot(loadings, stabilities, 'o-', color='blue', label='Overall Stability')
        ax1.plot(loadings, thermo_stabilities, 's--', color='green', label='Thermodynamic Stability')
        ax1.plot(loadings, kinetic_stabilities, '^--', color='orange', label='Kinetic Stability')
        
        # Add stability threshold
        ax1.axhline(y=self.min_stability, color='red', linestyle='--', linewidth=1, label=f'Stability Threshold ({self.min_stability})')
        
        # Highlight optimal loading
        optimal_loading = self.find_optimal_loading(method='grid_search')
        ax1.axvline(x=optimal_loading, color='purple', linestyle='--', linewidth=1, label=f'Optimal Loading ({optimal_loading:.2f})')
        
        # Set labels and title
        ax1.set_xlabel('Drug Loading (weight fraction)')
        ax1.set_ylabel('Stability Score')
        ax1.set_title(f'Stability vs. Drug Loading for {self.api.name} in {self.polymer.name}')
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Plot glass transition temperature
        ax2.plot(loadings, tgs, 'o-', color='purple')
        
        # Set labels
        ax2.set_xlabel('Drug Loading (weight fraction)')
        ax2.set_ylabel('Tg (°C)')
        ax2.set_title('Glass Transition Temperature vs. Drug Loading')
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Tight layout
        fig.tight_layout()
        
        return fig
    
    def get_loading_profile(self) -> Dict[str, List[float]]:
        """
        Get the loading profile with stability data.
        
        Returns:
            dict: Dictionary with loading profile data:
                'loadings': List of drug loading values
                'stabilities': List of stability scores
                'thermodynamic_stabilities': List of thermodynamic stability scores
                'kinetic_stabilities': List of kinetic stability scores
                'glass_transition_temps': List of glass transition temperatures
                'shelf_life_estimates': List of shelf life estimates
            
        Raises:
            ValueError: If no results are available
        """
        # Check if results are available
        if not self.results:
            raise ValueError("No results available. Run find_optimal_loading() or evaluate_loading() first.")
        
        # Initialize profile
        profile = {
            'loadings': [],
            'stabilities': [],
            'thermodynamic_stabilities': [],
            'kinetic_stabilities': [],
            'glass_transition_temps': [],
            'shelf_life_estimates': []
        }
        
        # Extract data
        for loading, result in sorted(self.results.items()):
            profile['loadings'].append(loading)
            profile['stabilities'].append(result['stability'])
            profile['thermodynamic_stabilities'].append(result['thermodynamic_stability'])
            profile['kinetic_stabilities'].append(result['kinetic_stability'])
            profile['glass_transition_temps'].append(result['glass_transition_temp'])
            profile['shelf_life_estimates'].append(result['shelf_life_estimate'])
        
        return profile
    
    def generate_report(self, format: str = 'markdown') -> Union[str, Dict[str, Any]]:
        """
        Generate a comprehensive report of the loading optimization results.
        
        Args:
            format (str, optional): Report format ('markdown', 'json')
            
        Returns:
            str or dict: Report content
            
        Raises:
            ValueError: If no results are available or format is not valid
        """
        # Check if results are available
        if not self.results:
            raise ValueError("No results available. Run find_optimal_loading() or evaluate_loading() first.")
        
        # Validate format
        valid_formats = ['markdown', 'json']
        if format not in valid_formats:
            raise ValueError(f"Invalid format: {format}. Valid formats are: {', '.join(valid_formats)}")
        
        # Find optimal loading
        optimal_loading = self.find_optimal_loading(method='grid_search')
        optimal_result = self.results[optimal_loading]
        
        # Generate JSON report
        if format == 'json':
            report = {
                'api': {
                    'name': self.api.name,
                    'molecular_weight': self.api.molecular_weight,
                    'melting_point': self.api.melting_point,
                    'glass_transition_temp': self.api.glass_transition_temp,
                    'log_p': self.api.log_p
                },
                'polymer': {
                    'name': self.polymer.name,
                    'type': self.polymer.type,
                    'molecular_weight': self.polymer.molecular_weight,
                    'glass_transition_temp': self.polymer.glass_transition_temp,
                    'hydrophilicity': self.polymer.hydrophilicity,
                    'hygroscopicity': self.polymer.hygroscopicity
                },
                'constraints': {
                    'min_loading': self.min_loading,
                    'max_loading': self.max_loading,
                    'min_stability': self.min_stability
                },
                'optimal_loading': {
                    'value': optimal_loading,
                    'stability': optimal_result['stability'],
                    'thermodynamic_stability': optimal_result['thermodynamic_stability'],
                    'kinetic_stability': optimal_result['kinetic_stability'],
                    'glass_transition_temp': optimal_result['glass_transition_temp'],
                    'miscibility': optimal_result['miscibility'],
                    'shelf_life_estimate': optimal_result['shelf_life_estimate']
                },
                'loading_profile': self.get_loading_profile()
            }
            
            return report
            
        # Generate Markdown report
        elif format == 'markdown':
            # Begin report
            report = f"# Drug Loading Optimization Report for {self.api.name} in {self.polymer.name}\n\n"
            
            # System information
            report += "## System Information\n\n"
            report += f"- **API**: {self.api.name}\n"
            report += f"- **Polymer**: {self.polymer.name}\n"
            if self.process_method:
                report += f"- **Manufacturing Method**: {self.process_method}\n"
            report += "\n"
            
            # Constraints
            report += "## Optimization Constraints\n\n"
            report += f"- **Minimum Loading**: {self.min_loading:.1%}\n"
            report += f"- **Maximum Loading**: {self.max_loading:.1%}\n"
            report += f"- **Minimum Stability**: {self.min_stability:.2f}\n"
            report += "\n"
            
            # Optimal loading
            report += "## Optimization Results\n\n"
            report += f"- **Optimal Drug Loading**: {optimal_loading:.1%}\n"
            report += f"- **Stability Score**: {optimal_result['stability']:.2f}\n"
            report += f"- **Thermodynamic Stability**: {optimal_result['thermodynamic_stability']:.2f}\n"
            report += f"- **Kinetic Stability**: {optimal_result['kinetic_stability']:.2f}\n"
            report += f"- **Glass Transition Temperature**: {optimal_result['glass_transition_temp']:.1f}°C\n"
            report += f"- **Miscibility Score**: {optimal_result['miscibility']:.2f}\n"
            report += f"- **Estimated Shelf Life**: {optimal_result['shelf_life_estimate']} months\n"
            report += "\n"
            
            # Loading profile
            report += "## Loading Profile\n\n"
            report += "| Loading | Stability | Thermodynamic | Kinetic | Tg (°C) | Shelf Life |\n"
            report += "|---------|-----------|---------------|---------|---------|------------|\n"
            
            for loading, result in sorted(self.results.items()):
                loading_percent = f"{loading:.1%}"
                stability = f"{result['stability']:.2f}"
                thermo = f"{result['thermodynamic_stability']:.2f}"
                kinetic = f"{result['kinetic_stability']:.2f}"
                tg = f"{result['glass_transition_temp']:.1f}"
                shelf_life = f"{result['shelf_life_estimate']}"
                
                report += f"| {loading_percent} | {stability} | {thermo} | {kinetic} | {tg} | {shelf_life} |\n"
            
            report += "\n"
            
            # Recommendations
            report += "## Recommendations\n\n"
            
            if optimal_result['stability'] < self.min_stability:
                report += "⚠️ **Warning**: No drug loading value meets the minimum stability requirement.\n\n"
                report += f"The optimal loading of {optimal_loading:.1%} has a stability score of {optimal_result['stability']:.2f}, "
                report += f"which is below the minimum threshold of {self.min_stability:.2f}.\n\n"
                report += "Consider the following options:\n"
                report += "1. Use a different polymer with better compatibility\n"
                report += "2. Lower the drug loading further\n"
                report += "3. Modify the formulation with stabilizing additives\n"
                report += "4. Use a different manufacturing process\n"
            else:
                if optimal_loading == self.max_loading:
                    report += f"✅ The maximum drug loading of {optimal_loading:.1%} meets the stability requirement.\n\n"
                    report += "You may be able to increase the drug loading beyond the current maximum value while maintaining stability.\n"
                    report += "Consider extending the search range to explore higher drug loadings.\n"
                else:
                    report += f"✅ The optimal drug loading of {optimal_loading:.1%} provides a good balance between drug content and stability.\n\n"
                    
                # Process-specific recommendations
                if self.process_method:
                    if self.process_method == 'hot_melt_extrusion':
                        report += "**Process Recommendations for Hot Melt Extrusion**:\n"
                        report += f"- Processing temperature: {optimal_result['glass_transition_temp'] + 30:.1f}°C (Tg + 30°C)\n"
                        report += "- Ensure uniform mixing for homogeneous dispersion\n"
                    elif self.process_method == 'spray_drying':
                        report += "**Process Recommendations for Spray Drying**:\n"
                        report += "- Optimize solvent selection based on API and polymer solubility\n"
                        report += "- Control process parameters to ensure rapid evaporation and minimal residual solvent\n"
            
            report += "\n"
            
            # Limitations
            report += "## Limitations and Considerations\n\n"
            report += "- Computational predictions should be verified with experimental studies\n"
            report += "- The influence of processing conditions is not fully captured\n"
            report += "- The impact of storage conditions (temperature, humidity) should be evaluated experimentally\n"
            report += "- Additional excipients may affect the optimal drug loading\n"
            
            return report
    
    def __str__(self) -> str:
        """Return a string representation of the LoadingOptimizer object."""
        return (
            f"LoadingOptimizer(API: {self.api.name}, Polymer: {self.polymer.name}, "
            f"Range: {self.min_loading:.1%}-{self.max_loading:.1%}, "
            f"Min Stability: {self.min_stability:.2f})"
        )