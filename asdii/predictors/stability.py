"""
Implementation of the StabilityPredictor class.

This module provides the StabilityPredictor class which predicts the stability
of ASD formulations.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import logging
import os
import json
import numpy as np
import pickle
from datetime import datetime

from asdii.core.api import API
from asdii.core.polymer import Polymer
from asdii.core.formulation import ASDFormulation


class StabilityPredictor:
    """
    Predicts the stability of ASD formulations.
    
    Attributes:
        model_type (str): Type of prediction model
        model_parameters (dict): Dictionary of model parameters
        trained_model: Trained prediction model
    """
    
    # Define valid model types
    VALID_MODEL_TYPES = [
        'rule_based',
        'thermodynamic_only',
        'kinetic_only',
        'combined',
        'ml_random_forest',
        'ml_svm',
        'ml_neural_network'
    ]
    
    def __init__(self, model_type: str = 'rule_based', **model_parameters: Dict[str, Any]) -> None:
        """
        Initialize a StabilityPredictor object.
        
        Args:
            model_type (str, optional): Type of prediction model
            **model_parameters: Additional model parameters
        
        Raises:
            ValueError: If model_type is not valid
        """
        # Validate model type
        if model_type not in self.VALID_MODEL_TYPES:
            raise ValueError(
                f"Invalid model type: {model_type}. "
                f"Valid types are: {', '.join(self.VALID_MODEL_TYPES)}"
            )
        
        self.model_type = model_type
        self.model_parameters = model_parameters
        self.trained_model = None
        
        # Initialize model if it's rule-based (doesn't require training)
        if model_type == 'rule_based':
            self._initialize_rule_based_model()
        elif model_type == 'thermodynamic_only':
            self._initialize_thermodynamic_model()
        elif model_type == 'kinetic_only':
            self._initialize_kinetic_model()
        elif model_type == 'combined':
            self._initialize_combined_model()
    
    def _initialize_rule_based_model(self) -> None:
        """
        Initialize a rule-based stability prediction model.
        """
        # Set default parameters if not provided
        if 'tg_weight' not in self.model_parameters:
            self.model_parameters['tg_weight'] = 0.25
        if 'miscibility_weight' not in self.model_parameters:
            self.model_parameters['miscibility_weight'] = 0.25
        if 'loading_weight' not in self.model_parameters:
            self.model_parameters['loading_weight'] = 0.15
        if 'hygroscopicity_weight' not in self.model_parameters:
            self.model_parameters['hygroscopicity_weight'] = 0.15
        if 'crystallization_weight' not in self.model_parameters:
            self.model_parameters['crystallization_weight'] = 0.10
        if 'process_weight' not in self.model_parameters:
            self.model_parameters['process_weight'] = 0.10
    
    def _initialize_thermodynamic_model(self) -> None:
        """
        Initialize a thermodynamic-only stability prediction model.
        """
        # Set default parameters if not provided
        if 'tg_weight' not in self.model_parameters:
            self.model_parameters['tg_weight'] = 0.40
        if 'miscibility_weight' not in self.model_parameters:
            self.model_parameters['miscibility_weight'] = 0.40
        if 'loading_weight' not in self.model_parameters:
            self.model_parameters['loading_weight'] = 0.20
    
    def _initialize_kinetic_model(self) -> None:
        """
        Initialize a kinetic-only stability prediction model.
        """
        # Set default parameters if not provided
        if 'hygroscopicity_weight' not in self.model_parameters:
            self.model_parameters['hygroscopicity_weight'] = 0.40
        if 'crystallization_weight' not in self.model_parameters:
            self.model_parameters['crystallization_weight'] = 0.40
        if 'process_weight' not in self.model_parameters:
            self.model_parameters['process_weight'] = 0.20
    
    def _initialize_combined_model(self) -> None:
        """
        Initialize a combined stability prediction model.
        """
        # This model uses both thermodynamic and kinetic factors
        # Set default parameters if not provided
        if 'thermodynamic_weight' not in self.model_parameters:
            self.model_parameters['thermodynamic_weight'] = 0.7
        if 'kinetic_weight' not in self.model_parameters:
            self.model_parameters['kinetic_weight'] = 0.3
        
        # Initialize both models
        self._initialize_thermodynamic_model()
        self._initialize_kinetic_model()
    
    @classmethod
    def from_pretrained(cls, model_path: str) -> 'StabilityPredictor':
        """
        Load a pretrained stability prediction model.
        
        Args:
            model_path (str): Path to the pretrained model
            
        Returns:
            StabilityPredictor: A StabilityPredictor object
            
        Raises:
            ValueError: If the model file is not found or invalid
        """
        if not os.path.exists(model_path):
            raise ValueError(f"Model file not found: {model_path}")
        
        try:
            # Load model metadata and parameters
            model_dir = os.path.dirname(model_path)
            metadata_path = os.path.join(model_dir, 'metadata.json')
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                model_type = metadata.get('model_type', 'rule_based')
                model_parameters = metadata.get('model_parameters', {})
            else:
                # Default to rule-based if metadata not found
                model_type = 'rule_based'
                model_parameters = {}
            
            # Create predictor
            predictor = cls(model_type=model_type, **model_parameters)
            
            # Load trained model if applicable
            if model_type in ['ml_random_forest', 'ml_svm', 'ml_neural_network']:
                with open(model_path, 'rb') as f:
                    predictor.trained_model = pickle.load(f)
            
            return predictor
            
        except Exception as e:
            raise ValueError(f"Failed to load model from {model_path}: {e}")
    
    def predict(
        self, 
        formulation: ASDFormulation, 
        conditions: Optional[Dict[str, float]] = None, 
        timeframe: str = 'long_term'
    ) -> Dict[str, Any]:
        """
        Predict the stability of a formulation.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            conditions (dict, optional): Storage conditions
                'temperature': Temperature in Celsius
                'humidity': Relative humidity in percentage
            timeframe (str, optional): Timeframe for prediction
                'short_term': Hours to days
                'intermediate': Weeks to months
                'long_term': Months to years
            
        Returns:
            dict: Dictionary of stability predictions
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
        
        # Validate timeframe
        valid_timeframes = ['short_term', 'intermediate', 'long_term']
        if timeframe not in valid_timeframes:
            raise ValueError(f"Invalid timeframe: {timeframe}. Valid timeframes are: {', '.join(valid_timeframes)}")
        
        # Call appropriate prediction method based on model type
        if self.model_type == 'rule_based':
            return self._predict_rule_based(formulation, conditions, timeframe)
        elif self.model_type == 'thermodynamic_only':
            thermodynamic = self.calculate_thermodynamic_stability(formulation)
            return {
                'score': thermodynamic,
                'thermodynamic': thermodynamic,
                'kinetic': 0.5,  # Default value
                'confidence': 0.6,
                'major_factors': [],  # Not applicable for this model
                'shelf_life_estimate': self._estimate_shelf_life(thermodynamic)
            }
        elif self.model_type == 'kinetic_only':
            kinetic = self.calculate_kinetic_stability(formulation, conditions)
            return {
                'score': kinetic,
                'thermodynamic': 0.5,  # Default value
                'kinetic': kinetic,
                'confidence': 0.6,
                'major_factors': [],  # Not applicable for this model
                'shelf_life_estimate': self._estimate_shelf_life(kinetic)
            }
        elif self.model_type == 'combined':
            return self._predict_combined(formulation, conditions, timeframe)
        elif self.model_type in ['ml_random_forest', 'ml_svm', 'ml_neural_network']:
            return self._predict_ml(formulation, conditions, timeframe)
        else:
            # This should not happen due to the validation in __init__
            raise ValueError(f"Invalid model type: {self.model_type}")
    
    def _predict_rule_based(
        self, 
        formulation: ASDFormulation, 
        conditions: Dict[str, float], 
        timeframe: str
    ) -> Dict[str, Any]:
        """
        Predict stability using a rule-based model.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            conditions (dict): Storage conditions
            timeframe (str): Timeframe for prediction
            
        Returns:
            dict: Dictionary of stability predictions
        """
        api = formulation.api
        polymer = formulation.polymer
        
        # 1. Thermodynamic stability factors
        
        # Factor 1: Tg difference from storage temperature
        # Higher Tg - T difference is better for stability
        tg_factor = 0.5  # Default value
        if formulation.predicted_tg is not None:
            tg_difference = formulation.predicted_tg - conditions['temperature']
            tg_factor = min(1.0, max(0.0, tg_difference / 50.0))
        
        # Factor 2: Miscibility
        # Higher miscibility is better for stability
        miscibility_factor = 0.5  # Default value
        if formulation.predicted_miscibility is not None:
            miscibility_factor = formulation.predicted_miscibility
        
        # Factor 3: Drug loading
        # Lower drug loading generally leads to better stability
        loading_factor = 1.0 - formulation.drug_loading
        
        # 2. Kinetic stability factors
        
        # Factor 4: Hygroscopicity
        # Lower hygroscopicity is better for stability
        hygroscopicity_factor = 0.5  # Default value
        if polymer.hygroscopicity is not None:
            # Adjust based on humidity conditions
            hygroscopicity_impact = polymer.hygroscopicity * conditions['humidity'] / 100.0
            hygroscopicity_factor = 1.0 - hygroscopicity_impact
        
        # Factor 5: API crystallization tendency
        # Lower crystallization tendency is better for stability
        crystallization_factor = 0.5  # Default value
        if hasattr(api, 'crystallization_tendency') and api.crystallization_tendency is not None:
            crystallization_factor = 1.0 - api.crystallization_tendency
        
        # 3. Process factors
        
        # Factor 6: Process appropriateness
        # Some processes are better for certain formulations
        process_factor = 0.7  # Default value
        if formulation.process_method:
            # This is a placeholder and should be replaced with a proper model
            if formulation.process_method == 'hot_melt_extrusion' and api.melting_point and formulation.predicted_tg:
                # Check if HME is appropriate based on melting point and Tg
                if api.melting_point > 250 or formulation.predicted_tg > 100:
                    process_factor = 0.5  # HME may be challenging
                else:
                    process_factor = 0.9  # HME is appropriate
            elif formulation.process_method == 'spray_drying':
                # Spray drying is generally versatile
                process_factor = 0.8
        
        # Get weights from model parameters
        weights = {
            'tg': self.model_parameters.get('tg_weight', 0.25),
            'miscibility': self.model_parameters.get('miscibility_weight', 0.25),
            'loading': self.model_parameters.get('loading_weight', 0.15),
            'hygroscopicity': self.model_parameters.get('hygroscopicity_weight', 0.15),
            'crystallization': self.model_parameters.get('crystallization_weight', 0.10),
            'process': self.model_parameters.get('process_weight', 0.10)
        }
        
        # Calculate thermodynamic stability
        thermo_numerator = (
            weights['tg'] * tg_factor +
            weights['miscibility'] * miscibility_factor +
            weights['loading'] * loading_factor
        )
        thermo_denominator = weights['tg'] + weights['miscibility'] + weights['loading']
        thermodynamic_stability = thermo_numerator / thermo_denominator
        
        # Calculate kinetic stability
        kinetic_numerator = (
            weights['hygroscopicity'] * hygroscopicity_factor +
            weights['crystallization'] * crystallization_factor +
            weights['process'] * process_factor
        )
        kinetic_denominator = weights['hygroscopicity'] + weights['crystallization'] + weights['process']
        kinetic_stability = kinetic_numerator / kinetic_denominator
        
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
        shelf_life = self._estimate_shelf_life(overall_stability)
        
        # Create the stability prediction result
        stability_result = {
            'score': overall_stability,
            'thermodynamic': thermodynamic_stability,
            'kinetic': kinetic_stability,
            'confidence': 0.7,  # Placeholder - rule-based models have moderate confidence
            'major_factors': major_factors,
            'shelf_life_estimate': shelf_life
        }
        
        return stability_result
    
    def _predict_combined(
        self, 
        formulation: ASDFormulation, 
        conditions: Dict[str, float], 
        timeframe: str
    ) -> Dict[str, Any]:
        """
        Predict stability using a combined thermodynamic and kinetic model.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            conditions (dict): Storage conditions
            timeframe (str): Timeframe for prediction
            
        Returns:
            dict: Dictionary of stability predictions
        """
        # Calculate thermodynamic stability
        thermodynamic = self.calculate_thermodynamic_stability(formulation)
        
        # Calculate kinetic stability
        kinetic = self.calculate_kinetic_stability(formulation, conditions)
        
        # Adjust weights based on timeframe
        if timeframe == 'short_term':
            thermodynamic_weight = 0.3
            kinetic_weight = 0.7
        elif timeframe == 'intermediate':
            thermodynamic_weight = 0.5
            kinetic_weight = 0.5
        else:  # long_term
            thermodynamic_weight = 0.7
            kinetic_weight = 0.3
        
        # Calculate overall stability
        overall_stability = (
            thermodynamic_weight * thermodynamic +
            kinetic_weight * kinetic
        )
        
        # Determine major factors (simplified approach)
        # In a production implementation, this should be more sophisticated
        major_factors = []
        
        if thermodynamic < 0.5:
            if formulation.predicted_tg is not None and formulation.predicted_tg < conditions['temperature'] + 20:
                major_factors.append(('Glass transition temperature', 0.4))
            if formulation.predicted_miscibility is not None and formulation.predicted_miscibility < 0.5:
                major_factors.append(('API-polymer miscibility', 0.3))
            if formulation.drug_loading > 0.4:
                major_factors.append(('Drug loading', 0.4))
        
        if kinetic < 0.5:
            if formulation.polymer.hygroscopicity is not None and formulation.polymer.hygroscopicity > 0.7:
                major_factors.append(('Polymer hygroscopicity', 0.3))
            if hasattr(formulation.api, 'crystallization_tendency') and formulation.api.crystallization_tendency > 0.7:
                major_factors.append(('API crystallization tendency', 0.3))
        
        # If we don't have enough factors, add default ones
        while len(major_factors) < 3:
            if ('Glass transition temperature', 0.4) not in major_factors:
                major_factors.append(('Glass transition temperature', 0.5))
            elif ('API-polymer miscibility', 0.3) not in major_factors:
                major_factors.append(('API-polymer miscibility', 0.5))
            elif ('Drug loading', 0.4) not in major_factors:
                major_factors.append(('Drug loading', 0.5))
            else:
                break
        
        # Sort factors by impact (lowest scores have highest impact)
        major_factors.sort(key=lambda x: x[1])
        major_factors = major_factors[:3]
        
        # Estimate shelf life based on stability score
        shelf_life = self._estimate_shelf_life(overall_stability)
        
        # Create the stability prediction result
        stability_result = {
            'score': overall_stability,
            'thermodynamic': thermodynamic,
            'kinetic': kinetic,
            'confidence': 0.75,  # Slightly higher confidence than rule-based
            'major_factors': major_factors,
            'shelf_life_estimate': shelf_life
        }
        
        return stability_result
    
    def _predict_ml(
        self, 
        formulation: ASDFormulation, 
        conditions: Dict[str, float], 
        timeframe: str
    ) -> Dict[str, Any]:
        """
        Predict stability using a machine learning model.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            conditions (dict): Storage conditions
            timeframe (str): Timeframe for prediction
            
        Returns:
            dict: Dictionary of stability predictions
            
        Raises:
            ValueError: If the model is not trained
        """
        if self.trained_model is None:
            raise ValueError("Model is not trained. Please train the model first.")
        
        # This is a placeholder for ML-based prediction
        # In a production implementation, this should extract features and call the ML model
        
        # For now, fall back to rule-based prediction
        logging.warning("ML model not fully implemented. Falling back to rule-based prediction.")
        return self._predict_rule_based(formulation, conditions, timeframe)
    
    def calculate_thermodynamic_stability(self, formulation: ASDFormulation) -> float:
        """
        Calculate thermodynamic stability of a formulation.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            
        Returns:
            float: Thermodynamic stability score (0-1)
        """
        api = formulation.api
        polymer = formulation.polymer
        
        # Factor 1: Tg difference from standard storage temperature (25°C)
        # Higher Tg - T difference is better for stability
        tg_factor = 0.5  # Default value
        if formulation.predicted_tg is not None:
            tg_difference = formulation.predicted_tg - 25.0
            tg_factor = min(1.0, max(0.0, tg_difference / 50.0))
        
        # Factor 2: Miscibility
        # Higher miscibility is better for stability
        miscibility_factor = 0.5  # Default value
        if formulation.predicted_miscibility is not None:
            miscibility_factor = formulation.predicted_miscibility
        
        # Factor 3: Drug loading
        # Lower drug loading generally leads to better stability
        loading_factor = 1.0 - formulation.drug_loading
        
        # Get weights from model parameters
        weights = {
            'tg': self.model_parameters.get('tg_weight', 0.40),
            'miscibility': self.model_parameters.get('miscibility_weight', 0.40),
            'loading': self.model_parameters.get('loading_weight', 0.20)
        }
        
        # Calculate thermodynamic stability
        numerator = (
            weights['tg'] * tg_factor +
            weights['miscibility'] * miscibility_factor +
            weights['loading'] * loading_factor
        )
        denominator = weights['tg'] + weights['miscibility'] + weights['loading']
        thermodynamic_stability = numerator / denominator
        
        return thermodynamic_stability
    
    def calculate_kinetic_stability(
        self, 
        formulation: ASDFormulation, 
        conditions: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate kinetic stability of a formulation.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            conditions (dict, optional): Storage conditions
            
        Returns:
            float: Kinetic stability score (0-1)
        """
        # Set default conditions if not provided
        if conditions is None:
            conditions = {'temperature': 25.0, 'humidity': 60.0}
        
        api = formulation.api
        polymer = formulation.polymer
        
        # Factor 1: Hygroscopicity
        # Lower hygroscopicity is better for stability
        hygroscopicity_factor = 0.5  # Default value
        if polymer.hygroscopicity is not None:
            # Adjust based on humidity conditions
            hygroscopicity_impact = polymer.hygroscopicity * conditions['humidity'] / 100.0
            hygroscopicity_factor = 1.0 - hygroscopicity_impact
        
        # Factor 2: API crystallization tendency
        # Lower crystallization tendency is better for stability
        crystallization_factor = 0.5  # Default value
        if hasattr(api, 'crystallization_tendency') and api.crystallization_tendency is not None:
            crystallization_factor = 1.0 - api.crystallization_tendency
        
        # Factor 3: Process appropriateness
        # Some processes are better for certain formulations
        process_factor = 0.7  # Default value
        if formulation.process_method:
            # This is a placeholder and should be replaced with a proper model
            if formulation.process_method == 'hot_melt_extrusion' and api.melting_point and formulation.predicted_tg:
                # Check if HME is appropriate based on melting point and Tg
                if api.melting_point > 250 or formulation.predicted_tg > 100:
                    process_factor = 0.5  # HME may be challenging
                else:
                    process_factor = 0.9  # HME is appropriate
            elif formulation.process_method == 'spray_drying':
                # Spray drying is generally versatile
                process_factor = 0.8
        
        # Get weights from model parameters
        weights = {
            'hygroscopicity': self.model_parameters.get('hygroscopicity_weight', 0.40),
            'crystallization': self.model_parameters.get('crystallization_weight', 0.40),
            'process': self.model_parameters.get('process_weight', 0.20)
        }
        
        # Calculate kinetic stability
        numerator = (
            weights['hygroscopicity'] * hygroscopicity_factor +
            weights['crystallization'] * crystallization_factor +
            weights['process'] * process_factor
        )
        denominator = weights['hygroscopicity'] + weights['crystallization'] + weights['process']
        kinetic_stability = numerator / denominator
        
        return kinetic_stability
    
    def _estimate_shelf_life(self, stability_score: float) -> int:
        """
        Estimate shelf life based on stability score.
        
        Args:
            stability_score (float): Stability score (0-1)
            
        Returns:
            int: Estimated shelf life in months
        """
        # This is a simplified model for shelf life estimation
        # A more sophisticated model should be implemented in a production library
        
        if stability_score > 0.9:
            shelf_life = 48  # 4 years
        elif stability_score > 0.8:
            shelf_life = 36  # 3 years
        elif stability_score > 0.7:
            shelf_life = 30  # 2.5 years
        elif stability_score > 0.6:
            shelf_life = 24  # 2 years
        elif stability_score > 0.5:
            shelf_life = 18  # 1.5 years
        elif stability_score > 0.4:
            shelf_life = 12  # 1 year
        elif stability_score > 0.3:
            shelf_life = 9   # 9 months
        elif stability_score > 0.2:
            shelf_life = 6   # 6 months
        else:
            shelf_life = 3   # 3 months
        
        return shelf_life
    
    def train(self, training_data: List[Tuple[ASDFormulation, Dict[str, Any]]]) -> bool:
        """
        Train the stability prediction model.
        
        Args:
            training_data (list): List of (formulation, stability) tuples
            
        Returns:
            bool: True if training was successful, False otherwise
            
        Raises:
            ValueError: If model_type is not a machine learning model
        """
        # Check if model type is a machine learning model
        if self.model_type not in ['ml_random_forest', 'ml_svm', 'ml_neural_network']:
            raise ValueError(f"Model type {self.model_type} is not trainable. Use a machine learning model.")
        
        # This is a placeholder for ML model training
        # In a production implementation, this should extract features, train the model, and evaluate it
        
        logging.warning("ML model training not fully implemented.")
        return False
    
    def save_model(self, model_path: str) -> bool:
        """
        Save the trained model to a file.
        
        Args:
            model_path (str): Path to save the model
            
        Returns:
            bool: True if saving was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            model_dir = os.path.dirname(model_path)
            os.makedirs(model_dir, exist_ok=True)
            
            # Save model metadata
            metadata_path = os.path.join(model_dir, 'metadata.json')
            metadata = {
                'model_type': self.model_type,
                'model_parameters': self.model_parameters,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Save trained model if applicable
            if self.model_type in ['ml_random_forest', 'ml_svm', 'ml_neural_network']:
                if self.trained_model is not None:
                    with open(model_path, 'wb') as f:
                        pickle.dump(self.trained_model, f)
                else:
                    logging.warning("No trained model to save.")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to save model to {model_path}: {e}")
            return False
    
    def __str__(self) -> str:
        """Return a string representation of the StabilityPredictor object."""
        return f"StabilityPredictor(model_type='{self.model_type}', trained={self.trained_model is not None})"