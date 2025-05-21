"""
Implementation of the ASDFormulation class.

This module provides the ASDFormulation class which represents an amorphous solid
dispersion formulation combining an API and a polymer.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import logging
import numpy as np
from datetime import datetime

from asdii.core.api import API
from asdii.core.polymer import Polymer
from asdii.calculators.thermal import predict_glass_transition


class ASDFormulation:
    """
    Represents an amorphous solid dispersion formulation.
    
    Attributes:
        api (API): API object
        polymer (Polymer): Polymer object
        drug_loading (float): Drug loading as weight fraction (0-1)
        process_method (str): Manufacturing method (e.g., 'hot_melt_extrusion', 'spray_drying')
        process_parameters (dict): Dictionary of process parameters
        predicted_tg (float): Predicted glass transition temperature of the mixture
        predicted_miscibility (float): Predicted miscibility score (0-1)
        predicted_stability (dict): Dictionary of stability predictions
        interaction_strength (float): Predicted API-polymer interaction strength
        crystallization_tendency (float): Predicted crystallization tendency
    """
    
    def __init__(
        self, 
        api: API, 
        polymer: Polymer, 
        drug_loading: float, 
        process_method: Optional[str] = None, 
        **process_parameters: Dict[str, Any]
    ) -> None:
        """
        Initialize an ASDFormulation object.
        
        Args:
            api (API): API object
            polymer (Polymer): Polymer object
            drug_loading (float): Drug loading as weight fraction (0-1)
            process_method (str, optional): Manufacturing method
            **process_parameters: Additional process parameters
        
        Raises:
            ValueError: If drug_loading is not between 0 and 1
        """
        # Validate inputs
        if not 0 <= drug_loading <= 1:
            raise ValueError("Drug loading must be between 0 and 1.")
        
        self.api = api
        self.polymer = polymer
        self.drug_loading = drug_loading
        self.process_method = process_method
        self.process_parameters = process_parameters
        
        # Initialize predicted properties
        self.predicted_tg = None
        self.predicted_miscibility = None
        self.predicted_stability = {}
        self.interaction_strength = None
        self.crystallization_tendency = None
        
        # Create a formulation ID
        self.id = f"{api.name}_{polymer.name}_{drug_loading:.2f}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate basic properties
        self._calculate_basic_properties()
    
    def _calculate_basic_properties(self) -> None:
        """
        Calculate basic properties of the formulation.
        """
        # Predict glass transition temperature
        try:
            self.predicted_tg = self.predict_glass_transition_temp()
        except Exception as e:
            logging.warning(f"Failed to predict glass transition temperature: {e}")
        
        # Predict miscibility
        try:
            self.predicted_miscibility = self.predict_miscibility()
        except Exception as e:
            logging.warning(f"Failed to predict miscibility: {e}")
    
    def predict_glass_transition_temp(self, method: str = 'gordon_taylor') -> float:
        """
        Predict the glass transition temperature of the formulation.
        
        Args:
            method (str, optional): Method for Tg prediction:
                'gordon_taylor': Gordon-Taylor equation
                'fox': Fox equation
                'couchman_karasz': Couchman-Karasz equation
            
        Returns:
            float: Predicted glass transition temperature in Celsius
            
        Raises:
            ValueError: If required properties are not available or method is invalid
        """
        # Check if required properties are available
        if self.api.glass_transition_temp is None:
            raise ValueError("API glass transition temperature is required.")
        if self.polymer.glass_transition_temp is None:
            raise ValueError("Polymer glass transition temperature is required.")
        
        # Call the thermal property calculator
        tg = predict_glass_transition(
            self.api.glass_transition_temp,
            self.polymer.glass_transition_temp,
            self.drug_loading,
            method=method
        )
        
        # Update the object property
        self.predicted_tg = tg
        
        return tg
    
    def predict_miscibility(self, method: str = 'flory_huggins') -> float:
        """
        Predict the miscibility of the API and polymer.
        
        Args:
            method (str, optional): Method for miscibility prediction:
                'flory_huggins': Flory-Huggins interaction parameter
                'hansen': Hansen solubility parameter distance
                'bagley': Bagley plot approach
            
        Returns:
            float: Miscibility score (0-1)
            
        Raises:
            ValueError: If required properties are not available or method is invalid
        """
        # For now, implement a simplified version based on Hansen solubility parameters
        if not self.api.solubility_parameters or not self.polymer.solubility_parameters:
            raise ValueError("Solubility parameters are required for both API and polymer.")
        
        # Calculate Hansen distance in solubility parameter space
        api_hsp = self.api.solubility_parameters
        polymer_hsp = self.polymer.solubility_parameters
        
        # Check if we have all required parameters
        required_params = ['dispersive', 'polar', 'hydrogen']
        for param in required_params:
            if param not in api_hsp or param not in polymer_hsp:
                raise ValueError(f"Missing solubility parameter: {param}")
        
        # Calculate Hansen distance
        distance_squared = (
            4 * (polymer_hsp['dispersive'] - api_hsp['dispersive'])**2 +
            (polymer_hsp['polar'] - api_hsp['polar'])**2 +
            (polymer_hsp['hydrogen'] - api_hsp['hydrogen'])**2
        )
        hansen_distance = np.sqrt(distance_squared)
        
        # Convert to miscibility score (0-1)
        # Typically, Hansen distances < 5 indicate good miscibility
        max_distance = 10.0  # Maximum distance to consider
        miscibility = max(0.0, 1.0 - hansen_distance / max_distance)
        
        # Update the object property
        self.predicted_miscibility = miscibility
        
        return miscibility
    
    def predict_stability(
        self, 
        conditions: Optional[Dict[str, float]] = None, 
        timeframe: str = 'long_term'
    ) -> Dict[str, Any]:
        """
        Predict the stability of the formulation.
        
        Args:
            conditions (dict, optional): Storage conditions:
                'temperature': Temperature in Celsius
                'humidity': Relative humidity in percentage
            timeframe (str, optional): Timeframe for stability prediction:
                'short_term': Hours to days
                'intermediate': Weeks to months
                'long_term': Months to years
            
        Returns:
            dict: Dictionary of stability predictions:
                'score': Overall stability score (0-1)
                'thermodynamic': Thermodynamic stability score (0-1)
                'kinetic': Kinetic stability score (0-1)
                'confidence': Confidence in the prediction (0-1)
                'major_factors': List of factors affecting stability
                'shelf_life_estimate': Estimated shelf life in months
        """
        # Set default conditions if not provided
        if conditions is None:
            conditions = {'temperature': 25.0, 'humidity': 60.0}
        
        # Check for required properties
        if self.predicted_tg is None:
            try:
                self.predicted_tg = self.predict_glass_transition_temp()
            except Exception as e:
                logging.warning(f"Failed to predict glass transition temperature: {e}")
                self.predicted_tg = None
        
        if self.predicted_miscibility is None:
            try:
                self.predicted_miscibility = self.predict_miscibility()
            except Exception as e:
                logging.warning(f"Failed to predict miscibility: {e}")
                self.predicted_miscibility = None
        
        # For now, implement a simplified rule-based prediction
        # This should be replaced with a more sophisticated model in the future
        
        # 1. Thermodynamic stability factors
        
        # Factor 1: Tg difference from storage temperature
        # Higher Tg - T difference is better for stability
        tg_factor = 0.5  # Default value
        if self.predicted_tg is not None:
            tg_difference = self.predicted_tg - conditions['temperature']
            tg_factor = min(1.0, max(0.0, tg_difference / 50.0))
        
        # Factor 2: Miscibility
        # Higher miscibility is better for stability
        miscibility_factor = 0.5  # Default value
        if self.predicted_miscibility is not None:
            miscibility_factor = self.predicted_miscibility
        
        # Factor 3: Drug loading
        # Lower drug loading generally leads to better stability
        loading_factor = 1.0 - self.drug_loading
        
        # 2. Kinetic stability factors
        
        # Factor 4: Hygroscopicity
        # Lower hygroscopicity is better for stability
        hygroscopicity_factor = 0.5  # Default value
        if self.polymer.hygroscopicity is not None:
            # Adjust based on humidity conditions
            hygroscopicity_impact = self.polymer.hygroscopicity * conditions['humidity'] / 100.0
            hygroscopicity_factor = 1.0 - hygroscopicity_impact
        
        # Factor 5: API crystallization tendency
        # Lower crystallization tendency is better for stability
        crystallization_factor = 0.5  # Default value
        if hasattr(self.api, 'crystallization_tendency') and self.api.crystallization_tendency is not None:
            crystallization_factor = 1.0 - self.api.crystallization_tendency
        
        # 3. Process factors
        
        # Factor 6: Process appropriateness
        # Some processes are better for certain formulations
        process_factor = 0.7  # Default value
        if self.process_method:
            # This is a placeholder and should be replaced with a proper model
            if self.process_method == 'hot_melt_extrusion' and self.api.melting_point and self.predicted_tg:
                # Check if HME is appropriate based on melting point and Tg
                if self.api.melting_point > 250 or self.predicted_tg > 100:
                    process_factor = 0.5  # HME may be challenging
                else:
                    process_factor = 0.9  # HME is appropriate
            elif self.process_method == 'spray_drying':
                # Spray drying is generally versatile
                process_factor = 0.8
        
        # Combine factors to calculate overall stability
        
        # Weights for different factors (should be optimized based on real data)
        weights = {
            'tg': 0.25,
            'miscibility': 0.25,
            'loading': 0.15,
            'hygroscopicity': 0.15,
            'crystallization': 0.10,
            'process': 0.10
        }
        
        # Calculate thermodynamic stability
        thermodynamic_stability = (
            weights['tg'] * tg_factor +
            weights['miscibility'] * miscibility_factor +
            weights['loading'] * loading_factor
        ) / (weights['tg'] + weights['miscibility'] + weights['loading'])
        
        # Calculate kinetic stability
        kinetic_stability = (
            weights['hygroscopicity'] * hygroscopicity_factor +
            weights['crystallization'] * crystallization_factor +
            weights['process'] * process_factor
        ) / (weights['hygroscopicity'] + weights['crystallization'] + weights['process'])
        
        # Calculate overall stability
        # For long-term stability, thermodynamic factors are more important
        # For short-term stability, kinetic factors are more important
        if timeframe == 'short_term':
            thermodynamic_weight = 0.3
            kinetic_weight = 0.7
        elif timeframe == 'intermediate':
            thermodynamic_weight = 0.5
            kinetic_weight = 0.5
        else:  # long_term
            thermodynamic_weight = 0.7
            kinetic_weight = 0.3
        
        overall_stability = (
            thermodynamic_weight * thermodynamic_stability +
            kinetic_weight * kinetic_stability
        )
        
        # Determine major factors affecting stability
        factor_scores = {
            'Glass transition temperature': tg_factor,
            'API-polymer miscibility': miscibility_factor,
            'Drug loading': loading_factor,
            'Polymer hygroscopicity': hygroscopicity_factor,
            'API crystallization tendency': crystallization_factor,
            'Manufacturing process': process_factor
        }
        
        # Sort factors by impact (lowest scores have highest impact)
        major_factors = sorted(factor_scores.items(), key=lambda x: x[1])[:3]
        
        # Estimate shelf life based on stability score
        # This is a very simplified approach and should be refined
        if overall_stability > 0.8:
            shelf_life = 36  # 3 years
        elif overall_stability > 0.6:
            shelf_life = 24  # 2 years
        elif overall_stability > 0.4:
            shelf_life = 12  # 1 year
        elif overall_stability > 0.2:
            shelf_life = 6   # 6 months
        else:
            shelf_life = 3   # 3 months
        
        # Create the stability prediction result
        stability_result = {
            'score': overall_stability,
            'thermodynamic': thermodynamic_stability,
            'kinetic': kinetic_stability,
            'confidence': 0.7,  # Placeholder - should be model-based
            'major_factors': major_factors,
            'shelf_life_estimate': shelf_life
        }
        
        # Update the object property
        self.predicted_stability = stability_result
        
        return stability_result
    
    def predict_dissolution_profile(
        self, 
        medium: str = 'water', 
        ph: float = 6.8
    ) -> Tuple[List[float], List[float]]:
        """
        Predict the dissolution profile of the formulation.
        
        Args:
            medium (str, optional): Dissolution medium
            ph (float, optional): pH of the dissolution medium
            
        Returns:
            tuple: Time points (hours) and dissolution percentages
        """
        # This is a placeholder implementation
        # A more sophisticated model should be implemented
        
        # Generate time points (0 to 24 hours)
        time_points = np.linspace(0, 24, 25)
        
        # Generate dissolution percentages
        # This is a simplified model that generates a first-order dissolution curve
        
        # Base dissolution rate depends on API properties
        if self.api.log_p is not None:
            # Higher logP means slower dissolution
            base_rate = max(0.1, 1.0 - self.api.log_p / 10.0)
        else:
            base_rate = 0.3  # Default value
        
        # Adjust for polymer properties
        if self.polymer.hydrophilicity is not None:
            # Higher hydrophilicity means faster dissolution
            polymer_factor = 1.0 + self.polymer.hydrophilicity
        else:
            polymer_factor = 1.5  # Default value
        
        # Adjust for drug loading
        # Higher loading can lead to slower dissolution due to saturation effects
        loading_factor = 1.0 - 0.5 * self.drug_loading
        
        # Adjust for pH (simplified model)
        # Assume optimal dissolution at pH 7, decreasing in either direction
        ph_factor = 1.0 - 0.1 * abs(ph - 7.0)
        
        # Calculate dissolution rate
        dissolution_rate = base_rate * polymer_factor * loading_factor * ph_factor
        
        # Generate dissolution curve
        # First-order dissolution model: D(t) = Dmax * (1 - exp(-k*t))
        dmax = 100  # Maximum dissolution percentage
        k = dissolution_rate / 2.0  # Rate constant (h^-1)
        dissolution = dmax * (1 - np.exp(-k * time_points))
        
        return time_points.tolist(), dissolution.tolist()
    
    def optimize_drug_loading(self, min_stability: float = 0.7) -> float:
        """
        Optimize drug loading for maximum API content while maintaining stability.
        
        Args:
            min_stability (float, optional): Minimum acceptable stability score (0-1)
            
        Returns:
            float: Optimal drug loading as weight fraction (0-1)
        """
        # This is a placeholder implementation
        # A more sophisticated optimization algorithm should be implemented
        
        # Start with a grid search to identify the optimal region
        loadings = np.linspace(0.1, 0.9, 9)
        stabilities = []
        
        for loading in loadings:
            # Create a temporary formulation with the test loading
            temp_formulation = ASDFormulation(
                self.api, 
                self.polymer, 
                loading, 
                self.process_method, 
                **self.process_parameters
            )
            
            # Predict stability
            stability = temp_formulation.predict_stability()['score']
            stabilities.append(stability)
        
        # Find the highest loading that meets the stability requirement
        optimal_loading = 0.1  # Default value
        for loading, stability in zip(loadings, stabilities):
            if stability >= min_stability and loading > optimal_loading:
                optimal_loading = loading
        
        # If all loadings fail to meet the stability requirement,
        # return the one with the highest stability
        if optimal_loading == 0.1 and stabilities[0] < min_stability:
            best_index = np.argmax(stabilities)
            optimal_loading = loadings[best_index]
        
        return optimal_loading
    
    def optimize_process_parameters(self) -> Dict[str, Any]:
        """
        Optimize process parameters for the selected manufacturing method.
        
        Returns:
            dict: Optimal process parameters
            
        Raises:
            ValueError: If process_method is not set
        """
        if not self.process_method:
            raise ValueError("Process method must be set before optimizing parameters.")
        
        # This is a placeholder implementation
        # A more sophisticated optimization algorithm should be implemented
        
        # Default parameters for different process methods
        if self.process_method == 'hot_melt_extrusion':
            # For HME, optimize temperature, screw speed, and residence time
            
            # Temperature should be above Tg but below degradation temperature
            # As a simple rule, set it to Tg + 30°C
            if self.predicted_tg is not None:
                temperature = self.predicted_tg + 30
            else:
                temperature = 150  # Default value
            
            # Screw speed and residence time depend on formulation properties
            # These are placeholder values
            screw_speed = 100  # RPM
            residence_time = 2  # minutes
            
            return {
                'temperature': temperature,
                'screw_speed': screw_speed,
                'residence_time': residence_time
            }
            
        elif self.process_method == 'spray_drying':
            # For spray drying, optimize inlet temperature, outlet temperature,
            # feed rate, and atomization pressure
            
            # Temperatures depend on solvent properties and API stability
            # These are placeholder values
            inlet_temp = 120  # °C
            outlet_temp = 60  # °C
            
            # Feed rate and atomization pressure affect particle size
            # These are placeholder values
            feed_rate = 10  # mL/min
            atomization_pressure = 2.0  # bar
            
            return {
                'inlet_temperature': inlet_temp,
                'outlet_temperature': outlet_temp,
                'feed_rate': feed_rate,
                'atomization_pressure': atomization_pressure
            }
            
        else:
            # For other process methods, return a generic message
            return {'message': f"Optimization for {self.process_method} not implemented yet."}
    
    def generate_report(self, format: str = 'markdown') -> Union[str, Dict[str, Any]]:
        """
        Generate a comprehensive report of the formulation properties and predictions.
        
        Args:
            format (str, optional): Report format ('markdown', 'json')
            
        Returns:
            str or dict: Report content
        """
        # Ensure we have the latest predictions
        if not self.predicted_stability:
            self.predict_stability()
        
        if format == 'json':
            # Generate JSON report
            report = {
                'formulation_id': self.id,
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
                'formulation': {
                    'drug_loading': self.drug_loading,
                    'process_method': self.process_method,
                    'process_parameters': self.process_parameters,
                    'predicted_tg': self.predicted_tg,
                    'predicted_miscibility': self.predicted_miscibility
                },
                'stability': self.predicted_stability
            }
            
            return report
            
        else:  # markdown format
            # Generate Markdown report
            report = f"# ASD Formulation Report: {self.api.name} with {self.polymer.name}\n\n"
            
            # Formulation details
            report += "## Formulation Details\n\n"
            report += f"- **API**: {self.api.name}\n"
            report += f"- **Polymer**: {self.polymer.name}\n"
            report += f"- **Drug Loading**: {self.drug_loading:.1%}\n"
            if self.process_method:
                report += f"- **Manufacturing Method**: {self.process_method}\n"
                if self.process_parameters:
                    report += "- **Process Parameters**:\n"
                    for param, value in self.process_parameters.items():
                        report += f"  - {param}: {value}\n"
            report += "\n"
            
            # API properties
            report += "## API Properties\n\n"
            report += f"- **Molecular Weight**: {self.api.molecular_weight:.2f} g/mol\n" if self.api.molecular_weight else ""
            report += f"- **Melting Point**: {self.api.melting_point:.1f}°C\n" if self.api.melting_point else ""
            report += f"- **Glass Transition Temperature**: {self.api.glass_transition_temp:.1f}°C\n" if self.api.glass_transition_temp else ""
            report += f"- **LogP**: {self.api.log_p:.2f}\n" if self.api.log_p else ""
            if self.api.solubility_parameters:
                report += "- **Solubility Parameters**:\n"
                for param, value in self.api.solubility_parameters.items():
                    report += f"  - {param}: {value:.2f}\n"
            report += "\n"
            
            # Polymer properties
            report += "## Polymer Properties\n\n"
            report += f"- **Type**: {self.polymer.type}\n" if self.polymer.type else ""
            report += f"- **Molecular Weight**: {self.polymer.molecular_weight:.0f} g/mol\n" if self.polymer.molecular_weight else ""
            report += f"- **Glass Transition Temperature**: {self.polymer.glass_transition_temp:.1f}°C\n" if self.polymer.glass_transition_temp else ""
            report += f"- **Hydrophilicity**: {self.polymer.hydrophilicity:.2f}\n" if self.polymer.hydrophilicity else ""
            report += f"- **Hygroscopicity**: {self.polymer.hygroscopicity:.2f}\n" if self.polymer.hygroscopicity else ""
            if self.polymer.solubility_parameters:
                report += "- **Solubility Parameters**:\n"
                for param, value in self.polymer.solubility_parameters.items():
                    report += f"  - {param}: {value:.2f}\n"
            report += "\n"
            
            # Predicted properties
            report += "## Predicted Formulation Properties\n\n"
            report += f"- **Glass Transition Temperature**: {self.predicted_tg:.1f}°C\n" if self.predicted_tg else ""
            report += f"- **Miscibility Score**: {self.predicted_miscibility:.2f}\n" if self.predicted_miscibility else ""
            report += "\n"
            
            # Stability prediction
            if self.predicted_stability:
                report += "## Stability Prediction\n\n"
                report += f"- **Overall Stability Score**: {self.predicted_stability['score']:.2f}\n"
                report += f"- **Thermodynamic Stability**: {self.predicted_stability['thermodynamic']:.2f}\n"
                report += f"- **Kinetic Stability**: {self.predicted_stability['kinetic']:.2f}\n"
                report += f"- **Estimated Shelf Life**: {self.predicted_stability['shelf_life_estimate']} months\n"
                report += f"- **Prediction Confidence**: {self.predicted_stability['confidence']:.2f}\n"
                
                if self.predicted_stability.get('major_factors'):
                    report += "- **Major Factors Affecting Stability**:\n"
                    for factor, score in self.predicted_stability['major_factors']:
                        report += f"  - {factor}: {score:.2f}\n"
                report += "\n"
            
            # Recommendations
            report += "## Recommendations\n\n"
            
            # Drug loading recommendation
            if self.predicted_stability and self.predicted_stability['score'] < 0.7 and self.drug_loading > 0.3:
                report += "- **Consider reducing drug loading** to improve stability.\n"
            
            # Process recommendation
            if self.process_method:
                if self.process_method == 'hot_melt_extrusion' and self.api.melting_point and self.api.melting_point > 200:
                    report += "- **Consider spray drying** as an alternative to hot melt extrusion due to the high melting point of the API.\n"
                
                # Recommend process parameters if not specified
                if not self.process_parameters:
                    report += "- **Optimize process parameters** for improved formulation quality.\n"
            else:
                # Recommend a process method if not specified
                report += "- **Select an appropriate manufacturing method** based on formulation properties:\n"
                if self.api.melting_point and self.api.melting_point < 180:
                    report += "  - Hot melt extrusion is suitable for this API.\n"
                else:
                    report += "  - Spray drying may be preferable for this API.\n"
            
            # Add recommendations based on stability factors
            if self.predicted_stability and self.predicted_stability.get('major_factors'):
                for factor, score in self.predicted_stability['major_factors']:
                    if score < 0.5:
                        if 'Glass transition' in factor:
                            report += "- **Consider a polymer with higher Tg** to improve stability.\n"
                        elif 'miscibility' in factor:
                            report += "- **Consider a polymer with more similar solubility parameters** to improve miscibility.\n"
                        elif 'hygroscopicity' in factor:
                            report += "- **Consider using a less hygroscopic polymer** or adding a desiccant to the packaging.\n"
                        elif 'crystallization' in factor:
                            report += "- **Consider adding a crystallization inhibitor** to improve stability.\n"
            
            report += "\n"
            
            # Disclaimer
            report += "## Disclaimer\n\n"
            report += "This report is based on computational predictions and should be validated with experimental studies. "
            report += "Predictions are estimates and actual formulation performance may vary. "
            report += "Always follow good formulation practices and conduct appropriate stability studies."
            
            return report
    
    def visualize_stability(self) -> Any:
        """
        Generate a visualization of stability predictions.
        
        Returns:
            matplotlib.figure.Figure: Figure object with stability visualization
            
        Raises:
            ImportError: If matplotlib is not available
        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.figure import Figure
            
            # Ensure we have stability predictions
            if not self.predicted_stability:
                self.predict_stability()
            
            # Create figure
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Plot 1: Stability score components
            stability_components = {
                'Overall': self.predicted_stability['score'],
                'Thermodynamic': self.predicted_stability['thermodynamic'],
                'Kinetic': self.predicted_stability['kinetic']
            }
            
            bars = ax1.bar(
                stability_components.keys(),
                stability_components.values(),
                color=['blue', 'green', 'orange']
            )
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + 0.02,
                    f'{height:.2f}',
                    ha='center'
                )
            
            ax1.set_ylim(0, 1.1)
            ax1.set_ylabel('Stability Score')
            ax1.set_title('Stability Components')
            
            # Plot 2: Factors affecting stability
            if self.predicted_stability.get('major_factors'):
                factors = [f[0] for f in self.predicted_stability['major_factors']]
                scores = [f[1] for f in self.predicted_stability['major_factors']]
                
                bars = ax2.barh(factors, scores, color='skyblue')
                
                # Add value labels inside bars
                for bar in bars:
                    width = bar.get_width()
                    ax2.text(
                        width - 0.1,
                        bar.get_y() + bar.get_height() / 2,
                        f'{width:.2f}',
                        ha='right',
                        va='center',
                        color='white',
                        fontweight='bold'
                    )
                
                ax2.set_xlim(0, 1)
                ax2.set_xlabel('Factor Score')
                ax2.set_title('Factors Affecting Stability')
                
                # Add threshold line
                ax2.axvline(x=0.5, color='red', linestyle='--', linewidth=1)
                ax2.text(0.51, ax2.get_ylim()[0], '0.5 (Threshold)', color='red')
            
            plt.tight_layout()
            
            return fig
            
        except ImportError:
            raise ImportError("Matplotlib is required for visualization.")
    
    def visualize_phase_diagram(self) -> Any:
        """
        Generate a phase diagram for the API-polymer system.
        
        Returns:
            matplotlib.figure.Figure: Figure object with phase diagram
            
        Raises:
            ImportError: If matplotlib is not available
        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.figure import Figure
            import numpy as np
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Generate data for phase diagram
            # This is a simplified Flory-Huggins phase diagram
            
            # Temperature range: Tg - 50°C to Tg + 100°C
            if self.predicted_tg:
                t_min = max(0, self.predicted_tg - 50)
                t_max = self.predicted_tg + 100
            else:
                t_min = 0
                t_max = 200
            
            # Create temperature and composition arrays
            temperatures = np.linspace(t_min, t_max, 100)
            compositions = np.linspace(0, 1, 100)
            T, X = np.meshgrid(temperatures, compositions)
            
            # Calculate free energy of mixing (simplified model)
            # This is a placeholder and should be replaced with a proper model
            
            # Estimate interaction parameter (chi)
            chi = 0.5
            if self.predicted_miscibility:
                # Convert miscibility score to chi parameter (higher miscibility = lower chi)
                chi = 0.5 * (1 - self.predicted_miscibility)
            
            # Calculate free energy
            R = 8.314  # Gas constant
            
            # Volume fractions
            phi1 = X
            phi2 = 1 - X
            
            # Degree of polymerization
            n1 = 1  # API (small molecule)
            n2 = 100  # Polymer
            
            # Free energy of mixing
            delta_G = R * T * (phi1 * np.log(phi1) / n1 + phi2 * np.log(phi2) / n2 + chi * phi1 * phi2)
            
            # Plot phase diagram
            contour = ax.contourf(X, T, delta_G, 20, cmap='viridis')
            fig.colorbar(contour, ax=ax, label='Free Energy of Mixing (J/mol)')
            
            # Add current formulation point
            ax.plot(self.drug_loading, 25, 'ro', markersize=10, label='Current Formulation')
            
            # Add labels and title
            ax.set_xlabel('API Weight Fraction')
            ax.set_ylabel('Temperature (°C)')
            ax.set_title('Phase Diagram: API-Polymer System')
            ax.legend()
            
            # Add a note
            ax.text(
                0.5, 0.02,
                "This is a simplified phase diagram and should be validated experimentally",
                transform=ax.transAxes,
                ha='center',
                fontsize=9,
                bbox=dict(facecolor='white', alpha=0.8)
            )
            
            return fig
            
        except ImportError:
            raise ImportError("Matplotlib and NumPy are required for visualization.")
    
    def __repr__(self) -> str:
        """Return a string representation of the ASDFormulation object."""
        process_str = f", process='{self.process_method}'" if self.process_method else ""
        return f"ASDFormulation(api='{self.api.name}', polymer='{self.polymer.name}', drug_loading={self.drug_loading:.2f}{process_str})"
    
    def __str__(self) -> str:
        """Return a user-friendly string representation of the ASDFormulation object."""
        stability_str = ""
        if self.predicted_stability and 'score' in self.predicted_stability:
            stability_str = f", Stability: {self.predicted_stability['score']:.2f}"
        
        process_str = f", Process: {self.process_method}" if self.process_method else ""
        
        return f"{self.api.name} ({self.drug_loading:.1%}) in {self.polymer.name}{process_str}{stability_str}"