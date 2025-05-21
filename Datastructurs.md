# ASDii Core Data Structures

This document outlines the primary Python classes that will represent the main entities in the ASDii library.

## 1. API Class

The `API` class represents an Active Pharmaceutical Ingredient.

```python
class API:
    """
    Represents an Active Pharmaceutical Ingredient (API) in an ASD formulation.
    
    Attributes:
        name (str): Name of the API
        smiles (str): SMILES representation of the API structure
        mol (rdkit.Chem.Mol): RDKit molecule object
        molecular_weight (float): Molecular weight in g/mol
        melting_point (float): Melting point in Celsius
        glass_transition_temp (float): Glass transition temperature in Celsius
        log_p (float): Octanol-water partition coefficient
        solubility_parameters (dict): Hansen solubility parameters
        h_bond_donors (int): Number of hydrogen bond donors
        h_bond_acceptors (int): Number of hydrogen bond acceptors
        rotatable_bonds (int): Number of rotatable bonds
        descriptors (dict): Dictionary of molecular descriptors
    """
    
    def __init__(self, name, smiles=None, mol=None, **properties):
        """
        Initialize an API object.
        
        Args:
            name (str): Name of the API
            smiles (str, optional): SMILES representation of the API structure
            mol (rdkit.Chem.Mol, optional): RDKit molecule object
            **properties: Additional properties of the API
        """
        pass
    
    @classmethod
    def from_smiles(cls, smiles, name=None):
        """
        Create an API object from a SMILES string.
        
        Args:
            smiles (str): SMILES representation of the API structure
            name (str, optional): Name of the API
            
        Returns:
            API: An API object
        """
        pass
    
    @classmethod
    def from_mol(cls, mol, name=None):
        """
        Create an API object from an RDKit molecule object.
        
        Args:
            mol (rdkit.Chem.Mol): RDKit molecule object
            name (str, optional): Name of the API
            
        Returns:
            API: An API object
        """
        pass
    
    @classmethod
    def from_name(cls, name):
        """
        Create an API object from a name by looking up in the database.
        
        Args:
            name (str): Name of the API
            
        Returns:
            API: An API object
        """
        pass
    
    def calculate_properties(self):
        """
        Calculate basic molecular properties.
        
        Returns:
            dict: Dictionary of calculated properties
        """
        pass
    
    def calculate_solubility_parameters(self):
        """
        Calculate Hansen solubility parameters.
        
        Returns:
            dict: Dictionary of solubility parameters (δd, δp, δh, δt)
        """
        pass
    
    def calculate_descriptors(self):
        """
        Calculate molecular descriptors.
        
        Returns:
            dict: Dictionary of molecular descriptors
        """
        pass
    
    def predict_amorphization_tendency(self):
        """
        Predict the tendency of the API to form an amorphous state.
        
        Returns:
            float: Score indicating amorphization tendency (0-1)
        """
        pass
    
    def visualize(self):
        """
        Generate a 2D visualization of the API structure.
        
        Returns:
            matplotlib.figure.Figure: Figure object with the API structure
        """
        pass
```

## 2. Polymer Class

The `Polymer` class represents a polymer used as a carrier in an ASD formulation.

```python
class Polymer:
    """
    Represents a polymer used as a carrier in an ASD formulation.
    
    Attributes:
        name (str): Name of the polymer
        type (str): Type/class of the polymer (e.g., 'cellulosic', 'vinyl')
        molecular_weight (float): Average molecular weight in g/mol
        glass_transition_temp (float): Glass transition temperature in Celsius
        solubility_parameters (dict): Hansen solubility parameters
        functional_groups (dict): Dictionary of functional groups and their counts
        monomer_smiles (str): SMILES representation of the monomer structure
        monomer_mol (rdkit.Chem.Mol): RDKit molecule object of the monomer
        hydrophilicity (float): Measure of hydrophilicity
        hygroscopicity (float): Measure of hygroscopicity
        descriptors (dict): Dictionary of polymer descriptors
    """
    
    def __init__(self, name, type=None, monomer_smiles=None, **properties):
        """
        Initialize a Polymer object.
        
        Args:
            name (str): Name of the polymer
            type (str, optional): Type/class of the polymer
            monomer_smiles (str, optional): SMILES representation of the monomer
            **properties: Additional properties of the polymer
        """
        pass
    
    @classmethod
    def from_name(cls, name):
        """
        Create a Polymer object from a name by looking up in the database.
        
        Args:
            name (str): Name of the polymer
            
        Returns:
            Polymer: A Polymer object
        """
        pass
    
    @classmethod
    def from_monomer(cls, monomer_smiles, name=None, degree_of_polymerization=100):
        """
        Create a Polymer object from a monomer SMILES.
        
        Args:
            monomer_smiles (str): SMILES representation of the monomer
            name (str, optional): Name of the polymer
            degree_of_polymerization (int, optional): Average degree of polymerization
            
        Returns:
            Polymer: A Polymer object
        """
        pass
    
    @classmethod
    def load_common_polymers(cls):
        """
        Load a list of common polymers used in ASD formulations.
        
        Returns:
            list: List of Polymer objects
        """
        pass
    
    def calculate_properties(self):
        """
        Calculate basic polymer properties.
        
        Returns:
            dict: Dictionary of calculated properties
        """
        pass
    
    def calculate_solubility_parameters(self):
        """
        Calculate Hansen solubility parameters for the polymer.
        
        Returns:
            dict: Dictionary of solubility parameters (δd, δp, δh, δt)
        """
        pass
    
    def calculate_functional_groups(self):
        """
        Identify and count functional groups in the polymer.
        
        Returns:
            dict: Dictionary of functional groups and their counts
        """
        pass
    
    def predict_api_compatibility(self, api):
        """
        Predict the compatibility of the polymer with a given API.
        
        Args:
            api (API): API object
            
        Returns:
            float: Compatibility score (0-1)
        """
        pass
```

## 3. ASDFormulation Class

The `ASDFormulation` class represents an amorphous solid dispersion formulation.

```python
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
    
    def __init__(self, api, polymer, drug_loading, process_method=None, **process_parameters):
        """
        Initialize an ASDFormulation object.
        
        Args:
            api (API): API object
            polymer (Polymer): Polymer object
            drug_loading (float): Drug loading as weight fraction (0-1)
            process_method (str, optional): Manufacturing method
            **process_parameters: Additional process parameters
        """
        pass
    
    def predict_glass_transition_temp(self, method='gordon_taylor'):
        """
        Predict the glass transition temperature of the formulation.
        
        Args:
            method (str, optional): Method for Tg prediction ('gordon_taylor', 'fox', 'couchman_karasz')
            
        Returns:
            float: Predicted glass transition temperature in Celsius
        """
        pass
    
    def predict_miscibility(self, method='flory_huggins'):
        """
        Predict the miscibility of the API and polymer.
        
        Args:
            method (str, optional): Method for miscibility prediction ('flory_huggins', 'hansen', 'bagley')
            
        Returns:
            float: Miscibility score (0-1)
        """
        pass
    
    def predict_stability(self, conditions=None, timeframe='long_term'):
        """
        Predict the stability of the formulation.
        
        Args:
            conditions (dict, optional): Storage conditions (temperature, humidity)
            timeframe (str, optional): Timeframe for stability prediction ('short_term', 'long_term')
            
        Returns:
            dict: Dictionary of stability predictions
        """
        pass
    
    def predict_dissolution_profile(self, medium='water', ph=6.8):
        """
        Predict the dissolution profile of the formulation.
        
        Args:
            medium (str, optional): Dissolution medium
            ph (float, optional): pH of the dissolution medium
            
        Returns:
            tuple: Time points and dissolution percentages
        """
        pass
    
    def optimize_drug_loading(self, min_stability=0.7):
        """
        Optimize drug loading for maximum API content while maintaining stability.
        
        Args:
            min_stability (float, optional): Minimum acceptable stability score
            
        Returns:
            float: Optimal drug loading as weight fraction
        """
        pass
    
    def optimize_process_parameters(self):
        """
        Optimize process parameters for the selected manufacturing method.
        
        Returns:
            dict: Optimal process parameters
        """
        pass
    
    def generate_report(self, format='markdown'):
        """
        Generate a comprehensive report of the formulation properties and predictions.
        
        Args:
            format (str, optional): Report format ('markdown', 'pdf', 'json')
            
        Returns:
            str or dict: Report content
        """
        pass
    
    def visualize_stability(self):
        """
        Generate a visualization of stability predictions.
        
        Returns:
            matplotlib.figure.Figure: Figure object with stability visualization
        """
        pass
    
    def visualize_phase_diagram(self):
        """
        Generate a phase diagram for the API-polymer system.
        
        Returns:
            matplotlib.figure.Figure: Figure object with phase diagram
        """
        pass
```

## 4. ProcessParameters Class

The `ProcessParameters` class represents manufacturing process parameters for an ASD formulation.

```python
class ProcessParameters:
    """
    Represents manufacturing process parameters for an ASD formulation.
    
    Attributes:
        method (str): Manufacturing method (e.g., 'hot_melt_extrusion', 'spray_drying')
        parameters (dict): Dictionary of process-specific parameters
    """
    
    def __init__(self, method, **parameters):
        """
        Initialize a ProcessParameters object.
        
        Args:
            method (str): Manufacturing method
            **parameters: Process-specific parameters
        """
        pass
    
    @classmethod
    def for_hot_melt_extrusion(cls, temperature, screw_speed, residence_time, **other_params):
        """
        Create ProcessParameters for hot melt extrusion.
        
        Args:
            temperature (float): Processing temperature in Celsius
            screw_speed (float): Screw speed in RPM
            residence_time (float): Residence time in minutes
            **other_params: Additional HME parameters
            
        Returns:
            ProcessParameters: A ProcessParameters object for HME
        """
        pass
    
    @classmethod
    def for_spray_drying(cls, inlet_temp, outlet_temp, feed_rate, atomization_pressure, **other_params):
        """
        Create ProcessParameters for spray drying.
        
        Args:
            inlet_temp (float): Inlet temperature in Celsius
            outlet_temp (float): Outlet temperature in Celsius
            feed_rate (float): Feed rate in mL/min
            atomization_pressure (float): Atomization pressure in bar
            **other_params: Additional spray drying parameters
            
        Returns:
            ProcessParameters: A ProcessParameters object for spray drying
        """
        pass
    
    def is_valid_for_formulation(self, formulation):
        """
        Check if the process parameters are valid for a given formulation.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            
        Returns:
            bool: True if parameters are valid, False otherwise
        """
        pass
    
    def predict_impact_on_stability(self, formulation):
        """
        Predict the impact of process parameters on formulation stability.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            
        Returns:
            float: Impact on stability score (-1 to 1, negative for detrimental impact)
        """
        pass
    
    def optimize_for_formulation(self, formulation):
        """
        Optimize process parameters for a given formulation.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            
        Returns:
            ProcessParameters: Optimized ProcessParameters object
        """
        pass
```

## 5. MaterialsDatabase Class

The `MaterialsDatabase` class manages a database of APIs and polymers.

```python
class MaterialsDatabase:
    """
    Manages a database of APIs and polymers.
    
    Attributes:
        apis (dict): Dictionary of API objects indexed by name
        polymers (dict): Dictionary of Polymer objects indexed by name
    """
    
    def __init__(self, database_path=None):
        """
        Initialize a MaterialsDatabase object.
        
        Args:
            database_path (str, optional): Path to the database file
        """
        pass
    
    def load_database(self, database_path):
        """
        Load a database from a file.
        
        Args:
            database_path (str): Path to the database file
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    def save_database(self, database_path=None):
        """
        Save the database to a file.
        
        Args:
            database_path (str, optional): Path to the database file
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    def add_api(self, api):
        """
        Add an API to the database.
        
        Args:
            api (API): API object
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    def add_polymer(self, polymer):
        """
        Add a polymer to the database.
        
        Args:
            polymer (Polymer): Polymer object
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    def get_api(self, name):
        """
        Get an API from the database by name.
        
        Args:
            name (str): Name of the API
            
        Returns:
            API: API object
        """
        pass
    
    def get_polymer(self, name):
        """
        Get a polymer from the database by name.
        
        Args:
            name (str): Name of the polymer
            
        Returns:
            Polymer: Polymer object
        """
        pass
    
    def search_apis(self, query):
        """
        Search for APIs in the database.
        
        Args:
            query (str): Search query
            
        Returns:
            list: List of matching API objects
        """
        pass
    
    def search_polymers(self, query):
        """
        Search for polymers in the database.
        
        Args:
            query (str): Search query
            
        Returns:
            list: List of matching Polymer objects
        """
        pass
    
    def get_common_polymers(self):
        """
        Get a list of common polymers used in ASD formulations.
        
        Returns:
            list: List of Polymer objects
        """
        pass
```

## 6. PolymerScreener Class

The `PolymerScreener` class screens polymers for compatibility with a given API.

```python
class PolymerScreener:
    """
    Screens polymers for compatibility with a given API.
    
    Attributes:
        api (API): API object
        polymers (list): List of Polymer objects
        formulations (list): List of ASDFormulation objects
        results (dict): Dictionary of screening results
    """
    
    def __init__(self, api, polymers, drug_loading=0.3):
        """
        Initialize a PolymerScreener object.
        
        Args:
            api (API): API object
            polymers (list): List of Polymer objects
            drug_loading (float, optional): Drug loading for screening formulations
        """
        pass
    
    def screen_all(self):
        """
        Screen all polymers for compatibility with the API.
        
        Returns:
            dict: Dictionary of screening results
        """
        pass
    
    def rank_by_miscibility(self):
        """
        Rank polymers by miscibility with the API.
        
        Returns:
            list: List of (polymer, score) tuples sorted by miscibility
        """
        pass
    
    def rank_by_stability(self):
        """
        Rank polymers by predicted formulation stability.
        
        Returns:
            list: List of (polymer, score) tuples sorted by stability
        """
        pass
    
    def get_top_polymers(self, n=3, criterion='stability'):
        """
        Get the top n polymers based on a specified criterion.
        
        Args:
            n (int, optional): Number of top polymers to return
            criterion (str, optional): Ranking criterion ('stability', 'miscibility')
            
        Returns:
            list: List of top n Polymer objects
        """
        pass
    
    def plot_ranking(self, criterion='stability'):
        """
        Plot the ranking of polymers based on a specified criterion.
        
        Args:
            criterion (str, optional): Ranking criterion ('stability', 'miscibility')
            
        Returns:
            matplotlib.figure.Figure: Figure object with the ranking plot
        """
        pass
```

## 7. LoadingOptimizer Class

The `LoadingOptimizer` class optimizes drug loading for a given API-polymer combination.

```python
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
    
    def __init__(self, api, polymer, process_method=None, min_loading=0.1, max_loading=0.5, min_stability=0.7, **process_parameters):
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
        """
        pass
    
    def evaluate_loading(self, loading):
        """
        Evaluate a specific drug loading value.
        
        Args:
            loading (float): Drug loading to evaluate
            
        Returns:
            dict: Evaluation results
        """
        pass
    
    def find_optimal_loading(self, method='binary_search'):
        """
        Find the optimal drug loading.
        
        Args:
            method (str, optional): Optimization method ('binary_search', 'grid_search')
            
        Returns:
            float: Optimal drug loading
        """
        pass
    
    def plot_stability_vs_loading(self):
        """
        Plot stability score versus drug loading.
        
        Returns:
            matplotlib.figure.Figure: Figure object with the plot
        """
        pass
```

## 8. StabilityPredictor Class

The `StabilityPredictor` class predicts the stability of ASD formulations.

```python
class StabilityPredictor:
    """
    Predicts the stability of ASD formulations.
    
    Attributes:
        model_type (str): Type of prediction model
        model_parameters (dict): Dictionary of model parameters
        trained_model: Trained prediction model
    """
    
    def __init__(self, model_type='rule_based', **model_parameters):
        """
        Initialize a StabilityPredictor object.
        
        Args:
            model_type (str, optional): Type of prediction model
            **model_parameters: Additional model parameters
        """
        pass
    
    @classmethod
    def from_pretrained(cls, model_path):
        """
        Load a pretrained stability prediction model.
        
        Args:
            model_path (str): Path to the pretrained model
            
        Returns:
            StabilityPredictor: A StabilityPredictor object
        """
        pass
    
    def predict(self, formulation, conditions=None, timeframe='long_term'):
        """
        Predict the stability of a formulation.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            conditions (dict, optional): Storage conditions
            timeframe (str, optional): Timeframe for prediction
            
        Returns:
            dict: Dictionary of stability predictions
        """
        pass
    
    def calculate_thermodynamic_stability(self, formulation):
        """
        Calculate thermodynamic stability of a formulation.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            
        Returns:
            float: Thermodynamic stability score (0-1)
        """
        pass
    
    def calculate_kinetic_stability(self, formulation, conditions=None):
        """
        Calculate kinetic stability of a formulation.
        
        Args:
            formulation (ASDFormulation): ASD formulation object
            conditions (dict, optional): Storage conditions
            
        Returns:
            float: Kinetic stability score (0-1)
        """
        pass
    
    def train(self, training_data):
        """
        Train the stability prediction model.
        
        Args:
            training_data (list): List of (formulation, stability) tuples
            
        Returns:
            bool: True if training was successful, False otherwise
        """
        pass
    
    def save_model(self, model_path):
        """
        Save the trained model to a file.
        
        Args:
            model_path (str): Path to save the model
            
        Returns:
            bool: True if saving was successful, False otherwise
        """
        pass
```