"""
Implementation of the ProcessParameters class.

This module provides the ProcessParameters class which represents manufacturing
process parameters for an amorphous solid dispersion formulation.
"""

from typing import Dict, List, Optional, Union, Any
import logging


class ProcessParameters:
    """
    Represents manufacturing process parameters for an ASD formulation.
    
    Attributes:
        method (str): Manufacturing method (e.g., 'hot_melt_extrusion', 'spray_drying')
        parameters (dict): Dictionary of process-specific parameters
    """
    
    # Define valid process methods
    VALID_METHODS = [
        'hot_melt_extrusion',
        'spray_drying',
        'freeze_drying',
        'co_precipitation',
        'kinetisol',
        'co_milling',
        'solvent_evaporation'
    ]
    
    # Define required parameters for each method
    REQUIRED_PARAMETERS = {
        'hot_melt_extrusion': ['temperature', 'screw_speed'],
        'spray_drying': ['inlet_temperature', 'outlet_temperature', 'feed_rate'],
        'freeze_drying': ['freezing_temperature', 'drying_temperature', 'drying_pressure'],
        'co_precipitation': ['solvent', 'anti_solvent', 'solvent_ratio'],
        'kinetisol': ['processing_temperature', 'processing_time', 'rpm'],
        'co_milling': ['milling_time', 'rotation_speed'],
        'solvent_evaporation': ['solvent', 'evaporation_temperature']
    }
    
    def __init__(self, method: str, **parameters: Dict[str, Any]) -> None:
        """
        Initialize a ProcessParameters object.
        
        Args:
            method (str): Manufacturing method
            **parameters: Process-specific parameters
        
        Raises:
            ValueError: If method is not valid or required parameters are missing
        """
        # Validate method
        if method not in self.VALID_METHODS:
            raise ValueError(
                f"Invalid method: {method}. "
                f"Valid methods are: {', '.join(self.VALID_METHODS)}"
            )
        
        self.method = method
        self.parameters = parameters
        
        # Check for required parameters
        missing_params = []
        for param in self.REQUIRED_PARAMETERS.get(method, []):
            if param not in parameters:
                missing_params.append(param)
        
        if missing_params:
            raise ValueError(
                f"Missing required parameters for {method}: {', '.join(missing_params)}"
            )
    
    @classmethod
    def for_hot_melt_extrusion(
        cls, 
        temperature: float, 
        screw_speed: float, 
        residence_time: Optional[float] = None, 
        **other_params: Dict[str, Any]
    ) -> 'ProcessParameters':
        """
        Create ProcessParameters for hot melt extrusion.
        
        Args:
            temperature (float): Processing temperature in Celsius
            screw_speed (float): Screw speed in RPM
            residence_time (float, optional): Residence time in minutes
            **other_params: Additional HME parameters
                'feed_rate': Feed rate in kg/h
                'torque': Torque percentage
                'die_temperature': Die temperature in Celsius
                'zone_temperatures': List of zone temperatures in Celsius
            
        Returns:
            ProcessParameters: A ProcessParameters object for HME
        """
        params = {
            'temperature': temperature,
            'screw_speed': screw_speed
        }
        
        if residence_time is not None:
            params['residence_time'] = residence_time
        
        # Add other parameters
        params.update(other_params)
        
        return cls(method='hot_melt_extrusion', **params)
    
    @classmethod
    def for_spray_drying(
        cls, 
        inlet_temperature: float, 
        outlet_temperature: float, 
        feed_rate: float, 
        atomization_pressure: Optional[float] = None, 
        **other_params: Dict[str, Any]
    ) -> 'ProcessParameters':
        """
        Create ProcessParameters for spray drying.
        
        Args:
            inlet_temperature (float): Inlet temperature in Celsius
            outlet_temperature (float): Outlet temperature in Celsius
            feed_rate (float): Feed rate in mL/min
            atomization_pressure (float, optional): Atomization pressure in bar
            **other_params: Additional spray drying parameters
                'aspirator_rate': Aspirator rate in %
                'gas_flow': Gas flow rate in L/min
                'nozzle_size': Nozzle size in mm
                'solvent': Solvent used
                'solid_concentration': Solid concentration in %
            
        Returns:
            ProcessParameters: A ProcessParameters object for spray drying
        """
        params = {
            'inlet_temperature': inlet_temperature,
            'outlet_temperature': outlet_temperature,
            'feed_rate': feed_rate
        }
        
        if atomization_pressure is not None:
            params['atomization_pressure'] = atomization_pressure
        
        # Add other parameters
        params.update(other_params)
        
        return cls(method='spray_drying', **params)
    
    @classmethod
    def for_freeze_drying(
        cls, 
        freezing_temperature: float, 
        drying_temperature: float, 
        drying_pressure: float, 
        **other_params: Dict[str, Any]
    ) -> 'ProcessParameters':
        """
        Create ProcessParameters for freeze drying.
        
        Args:
            freezing_temperature (float): Freezing temperature in Celsius
            drying_temperature (float): Drying temperature in Celsius
            drying_pressure (float): Drying pressure in mbar
            **other_params: Additional freeze drying parameters
                'freezing_time': Freezing time in hours
                'primary_drying_time': Primary drying time in hours
                'secondary_drying_time': Secondary drying time in hours
                'solvent': Solvent used
            
        Returns:
            ProcessParameters: A ProcessParameters object for freeze drying
        """
        params = {
            'freezing_temperature': freezing_temperature,
            'drying_temperature': drying_temperature,
            'drying_pressure': drying_pressure
        }
        
        # Add other parameters
        params.update(other_params)
        
        return cls(method='freeze_drying', **params)
    
    @classmethod
    def for_co_precipitation(
        cls, 
        solvent: str, 
        anti_solvent: str, 
        solvent_ratio: float, 
        **other_params: Dict[str, Any]
    ) -> 'ProcessParameters':
        """
        Create ProcessParameters for co-precipitation.
        
        Args:
            solvent (str): Solvent used
            anti_solvent (str): Anti-solvent used
            solvent_ratio (float): Solvent to anti-solvent ratio
            **other_params: Additional co-precipitation parameters
                'temperature': Process temperature in Celsius
                'stirring_speed': Stirring speed in RPM
                'addition_rate': Anti-solvent addition rate in mL/min
                'solid_concentration': Solid concentration in %
            
        Returns:
            ProcessParameters: A ProcessParameters object for co-precipitation
        """
        params = {
            'solvent': solvent,
            'anti_solvent': anti_solvent,
            'solvent_ratio': solvent_ratio
        }
        
        # Add other parameters
        params.update(other_params)
        
        return cls(method='co_precipitation', **params)
    
    def is_valid_for_formulation(self, formulation: 'ASDFormulation') -> bool:
        """
        Check if the process parameters are valid for a given formulation.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            
        Returns:
            bool: True if parameters are valid, False otherwise
        """
        # This is a simplified implementation
        # A more sophisticated validation should be implemented
        
        api = formulation.api
        polymer = formulation.polymer
        
        # Check if parameters are valid for hot melt extrusion
        if self.method == 'hot_melt_extrusion':
            # Check if temperature is appropriate
            if 'temperature' in self.parameters:
                # Temperature should be above Tg but below degradation temperature
                temp = self.parameters['temperature']
                
                # Check API melting point
                if api.melting_point and temp > api.melting_point:
                    return False
                
                # Check API degradation temperature
                if hasattr(api, 'degradation_temp') and api.degradation_temp and temp > api.degradation_temp:
                    return False
                
                # Check polymer degradation temperature
                if hasattr(polymer, 'degradation_temp') and polymer.degradation_temp and temp > polymer.degradation_temp:
                    return False
                
                # Check formulation Tg
                if formulation.predicted_tg and temp < formulation.predicted_tg:
                    # Temperature should be above Tg
                    return False
        
        # Check if parameters are valid for spray drying
        elif self.method == 'spray_drying':
            # Check if inlet temperature is appropriate
            if 'inlet_temperature' in self.parameters:
                inlet_temp = self.parameters['inlet_temperature']
                
                # Check API degradation temperature
                if hasattr(api, 'degradation_temp') and api.degradation_temp and inlet_temp > api.degradation_temp:
                    return False
                
                # Check polymer degradation temperature
                if hasattr(polymer, 'degradation_temp') and polymer.degradation_temp and inlet_temp > polymer.degradation_temp:
                    return False
        
        # For other methods, return True for now
        return True
    
    def predict_impact_on_stability(self, formulation: 'ASDFormulation') -> float:
        """
        Predict the impact of process parameters on formulation stability.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            
        Returns:
            float: Impact on stability score (-1 to 1, negative for detrimental impact)
        """
        # This is a simplified implementation
        # A more sophisticated prediction model should be implemented
        
        api = formulation.api
        polymer = formulation.polymer
        
        # Initialize impact score
        impact_score = 0.0
        
        # Assess impact for hot melt extrusion
        if self.method == 'hot_melt_extrusion':
            # Impact of temperature
            if 'temperature' in self.parameters:
                temp = self.parameters['temperature']
                
                # Check API melting point
                if api.melting_point:
                    # If temperature is close to melting point, it might be beneficial
                    # but if it's too high, it might be detrimental
                    temp_ratio = temp / api.melting_point
                    if temp_ratio < 0.8:
                        # Too low temperature - may not achieve proper mixing
                        impact_score -= 0.3
                    elif temp_ratio < 0.95:
                        # Good temperature range
                        impact_score += 0.3
                    else:
                        # Too high temperature - may cause degradation
                        impact_score -= 0.5
                
                # Check formulation Tg
                if formulation.predicted_tg:
                    # Temperature should be sufficiently above Tg
                    tg_difference = temp - formulation.predicted_tg
                    if tg_difference < 20:
                        # Too close to Tg - may not achieve proper mixing
                        impact_score -= 0.2
                    elif tg_difference < 50:
                        # Good temperature range
                        impact_score += 0.2
                    else:
                        # Too high above Tg - may cause degradation
                        impact_score -= 0.2
            
            # Impact of residence time
            if 'residence_time' in self.parameters:
                time = self.parameters['residence_time']
                
                # Longer residence time may improve mixing but also increase degradation risk
                if time < 1.0:
                    # Too short - may not achieve proper mixing
                    impact_score -= 0.2
                elif time < 5.0:
                    # Good range
                    impact_score += 0.2
                else:
                    # Too long - may cause degradation
                    impact_score -= 0.3
            
            # Impact of screw speed
            if 'screw_speed' in self.parameters:
                speed = self.parameters['screw_speed']
                
                # Higher screw speed may improve mixing but also increase shear stress
                if speed < 50:
                    # Too slow - may not achieve proper mixing
                    impact_score -= 0.1
                elif speed < 150:
                    # Good range
                    impact_score += 0.1
                else:
                    # Too fast - may cause degradation due to shear stress
                    impact_score -= 0.2
        
        # Assess impact for spray drying
        elif self.method == 'spray_drying':
            # Impact of inlet temperature
            if 'inlet_temperature' in self.parameters:
                inlet_temp = self.parameters['inlet_temperature']
                
                # Higher inlet temperature leads to faster drying but may increase degradation risk
                if inlet_temp < 80:
                    # Too low - may not achieve proper drying
                    impact_score -= 0.2
                elif inlet_temp < 150:
                    # Good range
                    impact_score += 0.2
                else:
                    # Too high - may cause degradation
                    impact_score -= 0.3
            
            # Impact of outlet temperature
            if 'outlet_temperature' in self.parameters:
                outlet_temp = self.parameters['outlet_temperature']
                
                # Outlet temperature affects residual moisture and stability
                if outlet_temp < 40:
                    # Too low - high residual moisture may reduce stability
                    impact_score -= 0.3
                elif outlet_temp < 80:
                    # Good range
                    impact_score += 0.2
                else:
                    # Too high - may not be achievable and may cause sticking
                    impact_score -= 0.1
            
            # Impact of feed rate
            if 'feed_rate' in self.parameters:
                feed_rate = self.parameters['feed_rate']
                
                # Feed rate affects particle size and residual moisture
                # This is a simplified assessment
                if 'solid_concentration' in self.parameters:
                    solid_conc = self.parameters['solid_concentration']
                    
                    # Higher feed rate with high solid concentration may reduce stability
                    if feed_rate > 10 and solid_conc > 10:
                        impact_score -= 0.2
                    elif feed_rate < 5 and solid_conc < 5:
                        # Very low feed rate and concentration - inefficient process
                        impact_score -= 0.1
                    else:
                        # Balanced parameters
                        impact_score += 0.1
        
        # For other methods, return a neutral impact for now
        
        # Ensure the impact score is in the range [-1, 1]
        impact_score = max(-1.0, min(1.0, impact_score))
        
        return impact_score
    
    def optimize_for_formulation(self, formulation: 'ASDFormulation') -> 'ProcessParameters':
        """
        Optimize process parameters for a given formulation.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            
        Returns:
            ProcessParameters: Optimized ProcessParameters object
        """
        # This is a simplified implementation
        # A more sophisticated optimization algorithm should be implemented
        
        api = formulation.api
        polymer = formulation.polymer
        
        # Initialize optimized parameters with current parameters
        optimized_params = self.parameters.copy()
        
        # Optimize for hot melt extrusion
        if self.method == 'hot_melt_extrusion':
            # Optimize temperature
            if 'temperature' in self.parameters and formulation.predicted_tg:
                # Set temperature to Tg + 30°C
                # This is a simple rule of thumb and should be refined
                optimized_params['temperature'] = formulation.predicted_tg + 30
                
                # Ensure temperature is below API melting point if available
                if api.melting_point:
                    max_temp = api.melting_point - 10  # 10°C safety margin
                    optimized_params['temperature'] = min(optimized_params['temperature'], max_temp)
            
            # Optimize residence time
            if 'residence_time' in self.parameters:
                # Set residence time to 2 minutes
                # This is a reasonable default value
                optimized_params['residence_time'] = 2.0
            
            # Optimize screw speed
            if 'screw_speed' in self.parameters:
                # Set screw speed to 100 RPM
                # This is a reasonable default value
                optimized_params['screw_speed'] = 100
        
        # Optimize for spray drying
        elif self.method == 'spray_drying':
            # Optimize inlet temperature
            if 'inlet_temperature' in self.parameters:
                # Set inlet temperature to 120°C
                # This is a reasonable default value
                optimized_params['inlet_temperature'] = 120
                
                # Adjust based on solvent
                if 'solvent' in self.parameters:
                    solvent = self.parameters['solvent'].lower()
                    
                    # Adjust temperature based on solvent boiling point
                    if solvent in ['water']:
                        optimized_params['inlet_temperature'] = 150
                    elif solvent in ['ethanol', 'methanol']:
                        optimized_params['inlet_temperature'] = 110
                    elif solvent in ['acetone']:
                        optimized_params['inlet_temperature'] = 100
                    elif solvent in ['dichloromethane', 'chloroform']:
                        optimized_params['inlet_temperature'] = 90
                
                # Ensure temperature is below degradation temperature if available
                if hasattr(api, 'degradation_temp') and api.degradation_temp:
                    max_temp = api.degradation_temp - 20  # 20°C safety margin
                    optimized_params['inlet_temperature'] = min(optimized_params['inlet_temperature'], max_temp)
            
            # Optimize outlet temperature
            if 'outlet_temperature' in self.parameters:
                # Set outlet temperature to 60°C
                # This is a reasonable default value
                optimized_params['outlet_temperature'] = 60
                
                # Adjust based on inlet temperature
                if 'inlet_temperature' in optimized_params:
                    inlet_temp = optimized_params['inlet_temperature']
                    optimized_params['outlet_temperature'] = max(50, inlet_temp - 60)
            
            # Optimize feed rate
            if 'feed_rate' in self.parameters:
                # Set feed rate to 10 mL/min
                # This is a reasonable default value
                optimized_params['feed_rate'] = 10
                
                # Adjust based on solid concentration
                if 'solid_concentration' in self.parameters:
                    solid_conc = self.parameters['solid_concentration']
                    
                    # Lower feed rate for higher solid concentration
                    if solid_conc > 10:
                        optimized_params['feed_rate'] = 8
                    elif solid_conc > 20:
                        optimized_params['feed_rate'] = 5
            
            # Optimize atomization pressure
            if 'atomization_pressure' in self.parameters:
                # Set atomization pressure to 2.0 bar
                # This is a reasonable default value
                optimized_params['atomization_pressure'] = 2.0
        
        # Return optimized parameters
        return ProcessParameters(method=self.method, **optimized_params)
    
    def __repr__(self) -> str:
        """Return a string representation of the ProcessParameters object."""
        params_str = ", ".join([f"{k}={v}" for k, v in self.parameters.items()])
        return f"ProcessParameters(method='{self.method}', {params_str})"
    
    def __str__(self) -> str:
        """Return a user-friendly string representation of the ProcessParameters object."""
        params_str = ", ".join([f"{k}: {v}" for k, v in self.parameters.items()])
        return f"{self.method.replace('_', ' ').title()}: {params_str}"