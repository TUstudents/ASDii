"""
Example script for loading and using test data for the ASDii library.

This script demonstrates how to load the test data files and use them with the ASDii library
to validate the functionality of the core components.
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np

from asdii import API, Polymer, ASDFormulation
from asdii import PolymerScreener, StabilityPredictor, LoadingOptimizer
from asdii.utils import save_json, load_json
from asdii.visualization import (
    plot_solubility_parameters, 
    plot_bagley_diagram, 
    plot_glass_transition_composition,
    save_visualization
)


def load_test_data(data_dir=None):
    """
    Load test data from JSON files.
    
    Args:
        data_dir (str, optional): Directory containing test data files.
            If None, uses the default 'asdii/data' directory.
    
    Returns:
        tuple: (test_apis, test_polymers, test_formulations, test_correlations)
    """
    # Set default data directory if not provided
    if data_dir is None:
        # Try to locate the package directory
        try:
            import asdii
            package_dir = os.path.dirname(asdii.__file__)
            data_dir = os.path.join(package_dir, 'data')
        except (ImportError, AttributeError):
            # Fall back to a relative path
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'asdii', 'data')
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    # Load test APIs
    apis_path = os.path.join(data_dir, 'test_apis.json')
    test_apis = load_json(apis_path)
    if test_apis is None:
        raise FileNotFoundError(f"Test APIs file not found: {apis_path}")
    
    # Load test polymers
    polymers_path = os.path.join(data_dir, 'test_polymers.json')
    test_polymers = load_json(polymers_path)
    if test_polymers is None:
        raise FileNotFoundError(f"Test polymers file not found: {polymers_path}")
    
    # Load test formulations
    formulations_path = os.path.join(data_dir, 'test_formulations.json')
    test_formulations = load_json(formulations_path)
    if test_formulations is None:
        raise FileNotFoundError(f"Test formulations file not found: {formulations_path}")
    
    # Load test correlations
    correlations_path = os.path.join(data_dir, 'test_correlations.json')
    test_correlations = load_json(correlations_path)
    if test_correlations is None:
        raise FileNotFoundError(f"Test correlations file not found: {correlations_path}")
    
    return test_apis, test_polymers, test_formulations, test_correlations


def create_apis_from_test_data(test_apis):
    """
    Create API objects from test data.
    
    Args:
        test_apis (dict): Dictionary of API data
    
    Returns:
        dict: Dictionary of API objects
    """
    apis = {}
    
    for name, data in test_apis.items():
        # Create API object
        api = API(
            name=name,
            smiles=data.get('smiles'),
            molecular_weight=data.get('molecular_weight'),
            melting_point=data.get('melting_point'),
            glass_transition_temp=data.get('glass_transition_temp'),
            log_p=data.get('log_p'),
            solubility_parameters=data.get('solubility_parameters', {}),
            crystallization_tendency=data.get('crystallization_tendency')
        )
        
        apis[name] = api
    
    return apis


def create_polymers_from_test_data(test_polymers):
    """
    Create Polymer objects from test data.
    
    Args:
        test_polymers (dict): Dictionary of polymer data
    
    Returns:
        dict: Dictionary of Polymer objects
    """
    polymers = {}
    
    for name, data in test_polymers.items():
        # Create Polymer object
        polymer = Polymer(
            name=name,
            type=data.get('type'),
            monomer_smiles=data.get('monomer_smiles'),
            molecular_weight=data.get('molecular_weight'),
            glass_transition_temp=data.get('glass_transition_temp'),
            solubility_parameters=data.get('solubility_parameters', {}),
            hydrophilicity=data.get('hydrophilicity'),
            hygroscopicity=data.get('hygroscopicity'),
            functional_groups=data.get('functional_groups', {})
        )
        
        polymers[name] = polymer
    
    return polymers


def create_formulations_from_test_data(test_formulations, apis, polymers):
    """
    Create ASDFormulation objects from test data.
    
    Args:
        test_formulations (dict): Dictionary of formulation data
        apis (dict): Dictionary of API objects
        polymers (dict): Dictionary of Polymer objects
    
    Returns:
        dict: Dictionary of ASDFormulation objects
    """
    formulations = {}
    
    for formulation_data in test_formulations.get('formulations', []):
        # Get API and polymer
        api_name = formulation_data.get('api')
        polymer_name = formulation_data.get('polymer')
        
        if api_name not in apis or polymer_name not in polymers:
            print(f"Warning: API '{api_name}' or polymer '{polymer_name}' not found. Skipping formulation {formulation_data.get('id')}.")
            continue
        
        api = apis[api_name]
        polymer = polymers[polymer_name]
        
        # Create formulation
        try:
            formulation = ASDFormulation(
                api=api,
                polymer=polymer,
                drug_loading=formulation_data.get('drug_loading'),
                process_method=formulation_data.get('process_method'),
                **formulation_data.get('process_parameters', {})
            )
            
            # Store experimental results as attributes
            for key, value in formulation_data.get('experimental_results', {}).items():
                setattr(formulation, f"experimental_{key}", value)
            
            formulations[formulation_data.get('id')] = formulation
            
        except Exception as e:
            print(f"Error creating formulation {formulation_data.get('id')}: {e}")
    
    return formulations


def compare_predicted_vs_experimental(formulations, property_name, ax=None):
    """
    Compare predicted vs. experimental property values.
    
    Args:
        formulations (dict): Dictionary of ASDFormulation objects
        property_name (str): Name of the property to compare
        ax (matplotlib.axes.Axes, optional): Axes to plot on
    
    Returns:
        matplotlib.axes.Axes: Axes with the plot
    """
    # Create axes if not provided
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 6))
    
    # Collect predicted and experimental values
    predicted_values = []
    experimental_values = []
    labels = []
    
    for form_id, formulation in formulations.items():
        # Get predicted value
        if property_name == 'glass_transition_temp':
            try:
                predicted = formulation.predict_glass_transition_temp()
            except Exception:
                continue
        elif property_name == 'miscibility':
            try:
                predicted = formulation.predict_miscibility()
            except Exception:
                continue
        elif property_name == 'stability':
            try:
                stability = formulation.predict_stability()
                predicted = stability['score']
            except Exception:
                continue
        else:
            # Unknown property
            continue
        
        # Get experimental value
        experimental_attr = f"experimental_{property_name}"
        if hasattr(formulation, experimental_attr):
            experimental = getattr(formulation, experimental_attr)
            
            predicted_values.append(predicted)
            experimental_values.append(experimental)
            labels.append(form_id)
    
    # Create scatter plot
    ax.scatter(experimental_values, predicted_values, s=80, alpha=0.7)
    
    # Add 45-degree line
    min_val = min(min(predicted_values), min(experimental_values))
    max_val = max(max(predicted_values), max(experimental_values))
    padding = (max_val - min_val) * 0.1
    ax.plot([min_val - padding, max_val + padding], [min_val - padding, max_val + padding], 'k--', alpha=0.5)
    
    # Add labels to points
    for i, label in enumerate(labels):
        ax.annotate(label, (experimental_values[i], predicted_values[i]),
                    xytext=(5, 5), textcoords='offset points')
    
    # Set axis limits
    ax.set_xlim(min_val - padding, max_val + padding)
    ax.set_ylim(min_val - padding, max_val + padding)
    
    # Calculate metrics
    n = len(predicted_values)
    if n > 0:
        # Mean Absolute Error
        mae = sum(abs(p - e) for p, e in zip(predicted_values, experimental_values)) / n
        
        # Root Mean Squared Error
        rmse = (sum((p - e) ** 2 for p, e in zip(predicted_values, experimental_values)) / n) ** 0.5
        
        # Coefficient of Determination (R²)
        mean_experimental = sum(experimental_values) / n
        ss_total = sum((e - mean_experimental) ** 2 for e in experimental_values)
        ss_residual = sum((e - p) ** 2 for e, p in zip(experimental_values, predicted_values))
        r2 = 1 - (ss_residual / ss_total) if ss_total > 0 else 0
        
        # Add metrics to plot
        metrics_text = f"MAE: {mae:.3f}\nRMSE: {rmse:.3f}\nR²: {r2:.3f}"
        ax.text(0.05, 0.95, metrics_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', alpha=0.1))
    
    # Set labels and title
    property_label = property_name.replace('_', ' ').title()
    ax.set_xlabel(f"Experimental {property_label}")
    ax.set_ylabel(f"Predicted {property_label}")
    ax.set_title(f"Predicted vs. Experimental {property_label}")
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.5)
    
    return ax


def plot_loading_effect(test_correlations, apis, polymers):
    """
    Plot the effect of drug loading on glass transition temperature
    using test correlation data.
    
    Args:
        test_correlations (dict): Test correlation data
        apis (dict): Dictionary of API objects
        polymers (dict): Dictionary of Polymer objects
    
    Returns:
        matplotlib.figure.Figure: Figure with the plot
    """
    # Get glass transition data
    gt_data = test_correlations.get('glass_transition_gordon_taylor', {})
    api_polymer_pairs = gt_data.get('api_polymer_pairs', [])
    
    # Create figure
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    axs = axs.flatten()
    
    # Plot each API-polymer pair
    for i, pair_data in enumerate(api_polymer_pairs[:4]):
        api_name = pair_data.get('api')
        polymer_name = pair_data.get('polymer')
        k_parameter = pair_data.get('k_parameter')
        experimental_data = pair_data.get('experimental_data', [])
        
        # Skip if we don't have the API or polymer
        if api_name not in apis or polymer_name not in polymers:
            continue
        
        # Get API and polymer
        api = apis[api_name]
        polymer = polymers[polymer_name]
        
        # Extract experimental data
        exp_loadings = [point.get('drug_loading') for point in experimental_data]
        exp_tgs = [point.get('tg') for point in experimental_data]
        
        # Plot glass transition composition
        ax = axs[i]
        plot_glass_transition_composition(
            material_1_name=api_name,
            material_2_name=polymer_name,
            material_1_tg=api.glass_transition_temp,
            material_2_tg=polymer.glass_transition_temp,
            k=k_parameter,
            experimental_data=list(zip(exp_loadings, exp_tgs)),
            ax=ax
        )
        
        # Set title
        ax.set_title(f"{api_name} - {polymer_name}")
    
    # Adjust layout
    plt.tight_layout()
    
    return fig


def main():
    """
    Main function to demonstrate loading and using test data.
    """
    # Create output directory
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading test data...")
    test_apis, test_polymers, test_formulations, test_correlations = load_test_data()
    
    print(f"Loaded {len(test_apis)} APIs, {len(test_polymers)} polymers, "
          f"{len(test_formulations.get('formulations', []))} formulations")
    
    print("\nCreating objects from test data...")
    # Create objects
    apis = create_apis_from_test_data(test_apis)
    polymers = create_polymers_from_test_data(test_polymers)
    formulations = create_formulations_from_test_data(test_formulations, apis, polymers)
    
    print(f"Created {len(apis)} API objects, {len(polymers)} Polymer objects, "
          f"{len(formulations)} ASDFormulation objects")
    
    # Choose a specific API and polymer for testing
    api = apis.get('ibuprofen')
    polymer = polymers.get('PVP K30')
    
    if api and polymer:
        print("\nTesting property predictions...")
        
        # Create a formulation
        formulation = ASDFormulation(
            api=api,
            polymer=polymer,
            drug_loading=0.3,
            process_method="hot_melt_extrusion"
        )
        
        # Predict glass transition temperature
        tg = formulation.predict_glass_transition_temp()
        print(f"Predicted Glass Transition Temperature: {tg:.1f}°C")
        
        # Predict miscibility
        miscibility = formulation.predict_miscibility()
        print(f"Predicted Miscibility: {miscibility:.2f}")
        
        # Predict stability
        stability = formulation.predict_stability()
        print(f"Predicted Stability Score: {stability['score']:.2f}")
        print(f"Thermodynamic Stability: {stability['thermodynamic']:.2f}")
        print(f"Kinetic Stability: {stability['kinetic']:.2f}")
        print(f"Estimated Shelf Life: {stability['shelf_life_estimate']} months")
    
    print("\nComparing predicted vs. experimental values...")
    # Create comparison plots
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))
    
    # Tg comparison
    compare_predicted_vs_experimental(formulations, 'glass_transition_temp', axs[0])
    
    # Miscibility comparison (if available)
    try:
        compare_predicted_vs_experimental(formulations, 'miscibility', axs[1])
    except Exception as e:
        print(f"Error comparing miscibility: {e}")
    
    # Stability comparison
    compare_predicted_vs_experimental(formulations, 'stability', axs[2])
    
    # Save figure
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'prediction_comparison.png'), dpi=300)
    
    print("\nPlotting Hansen solubility parameters...")
    # Plot Hansen solubility parameters
    api_materials = []
    polymer_materials = []
    api_names = []
    polymer_names = []
    
    # Collect data
    for name, api in apis.items():
        if hasattr(api, 'solubility_parameters') and api.solubility_parameters:
            api_materials.append(api.solubility_parameters)
            api_names.append(name)
    
    for name, polymer in polymers.items():
        if hasattr(polymer, 'solubility_parameters') and polymer.solubility_parameters:
            polymer_materials.append(polymer.solubility_parameters)
            polymer_names.append(name)
    
    # Create 3D plot
    fig = plot_solubility_parameters(
        api_materials + polymer_materials,
        api_names + polymer_names
    )
    
    # Save figure
    fig.savefig(os.path.join(output_dir, 'hansen_parameters_3d.png'), dpi=300)
    
    print("\nPlotting Bagley diagram...")
    # Create Bagley plot
    fig = plot_bagley_diagram(
        api_materials + polymer_materials,
        api_names + polymer_names
    )
    
    # Save figure
    fig.savefig(os.path.join(output_dir, 'bagley_diagram.png'), dpi=300)
    
    print("\nPlotting glass transition temperature vs. composition...")
    # Plot glass transition temperature vs. composition
    fig = plot_loading_effect(test_correlations, apis, polymers)
    
    # Save figure
    fig.savefig(os.path.join(output_dir, 'tg_vs_loading.png'), dpi=300)
    
    print("\nAnalysis complete! Output saved to:", output_dir)


if __name__ == "__main__":
    main()