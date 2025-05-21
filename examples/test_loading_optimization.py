"""
Example script for testing the LoadingOptimizer functionality with test data.

This script demonstrates how to use the LoadingOptimizer class to find the optimal
drug loading for different API-polymer combinations.
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np
from test_data_loader import (
    load_test_data,
    create_apis_from_test_data,
    create_polymers_from_test_data
)

from asdii import API, Polymer, ASDFormulation, LoadingOptimizer


def run_loading_optimization(
    api_name, 
    polymer_name, 
    apis, 
    polymers, 
    min_loading=0.1, 
    max_loading=0.5, 
    min_stability=0.7,
    process_method="hot_melt_extrusion"
):
    """
    Run drug loading optimization for a given API-polymer pair.
    
    Args:
        api_name (str): Name of the API
        polymer_name (str): Name of the polymer
        apis (dict): Dictionary of API objects
        polymers (dict): Dictionary of Polymer objects
        min_loading (float, optional): Minimum drug loading to consider
        max_loading (float, optional): Maximum drug loading to consider
        min_stability (float, optional): Minimum acceptable stability score
        process_method (str, optional): Manufacturing method
        
    Returns:
        tuple: (optimizer, optimal_loading, optimization_result)
    """
    # Get API and polymer
    if api_name not in apis:
        raise ValueError(f"API '{api_name}' not found.")
    if polymer_name not in polymers:
        raise ValueError(f"Polymer '{polymer_name}' not found.")
    
    api = apis[api_name]
    polymer = polymers[polymer_name]
    
    # Create optimizer
    optimizer = LoadingOptimizer(
        api=api,
        polymer=polymer,
        process_method=process_method,
        min_loading=min_loading,
        max_loading=max_loading,
        min_stability=min_stability
    )
    
    # Run optimization
    print(f"Optimizing drug loading for {api_name} in {polymer_name}...")
    optimal_loading = optimizer.find_optimal_loading()
    
    # Get result for optimal loading
    optimization_result = optimizer.results[optimal_loading]
    
    return optimizer, optimal_loading, optimization_result


def analyze_optimization_results(optimizer, optimal_loading, optimization_result):
    """
    Analyze and print optimization results.
    
    Args:
        optimizer (LoadingOptimizer): LoadingOptimizer object
        optimal_loading (float): Optimal drug loading
        optimization_result (dict): Result for the optimal loading
    """
    print(f"\nOptimal Drug Loading: {optimal_loading:.1%}")
    print(f"Stability Score: {optimization_result['stability']:.2f}")
    print(f"Glass Transition Temperature: {optimization_result['glass_transition_temp']:.1f}°C")
    print(f"Estimated Shelf Life: {optimization_result['shelf_life_estimate']} months")
    
    # Generate report
    print("\nGenerating optimization report...")
    report = optimizer.generate_report()
    
    # Print the first 500 characters of the report
    print("\nExcerpt from the optimization report:")
    print(report[:500] + "...")


def create_visualization(optimizer, output_dir):
    """
    Create and save visualizations of optimization results.
    
    Args:
        optimizer (LoadingOptimizer): LoadingOptimizer object
        output_dir (str): Directory to save visualizations
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot stability vs. loading
    fig = optimizer.plot_stability_vs_loading()
    fig.savefig(os.path.join(output_dir, 'stability_vs_loading.png'), dpi=300)
    plt.close(fig)
    
    # Create a loading profile visualization
    try:
        loading_profile = optimizer.get_loading_profile()
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
        
        # Plot stability and thermal properties
        loadings = loading_profile['loadings']
        stabilities = loading_profile['stabilities']
        tgs = loading_profile['glass_transition_temps']
        shelf_lives = loading_profile['shelf_life_estimates']
        
        # Plot stability and components
        ax1.plot(loadings, stabilities, 'o-', color='blue', label='Overall Stability')
        if 'thermodynamic_stabilities' in loading_profile:
            thermo_stabilities = loading_profile['thermodynamic_stabilities']
            ax1.plot(loadings, thermo_stabilities, 's--', color='green', label='Thermodynamic')
        if 'kinetic_stabilities' in loading_profile:
            kinetic_stabilities = loading_profile['kinetic_stabilities']
            ax1.plot(loadings, kinetic_stabilities, '^--', color='orange', label='Kinetic')
        
        # Add stability threshold
        ax1.axhline(y=optimizer.min_stability, color='red', linestyle='--', linewidth=1,
                   label=f'Stability Threshold ({optimizer.min_stability})')
        
        # Set labels and title
        ax1.set_xlabel('Drug Loading (weight fraction)')
        ax1.set_ylabel('Stability Score')
        ax1.set_title('Stability vs. Drug Loading')
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Find optimal loading
        optimal_loading = optimizer.find_optimal_loading()
        ax1.axvline(x=optimal_loading, color='purple', linestyle='--', linewidth=1,
                    label=f'Optimal Loading ({optimal_loading:.2f})')
        
        # Plot glass transition temperature
        ax2.plot(loadings, tgs, 'o-', color='red', label='Glass Transition Temp')
        
        # Add a second y-axis for shelf life
        ax2_twin = ax2.twinx()
        ax2_twin.plot(loadings, shelf_lives, 's--', color='green', label='Shelf Life')
        
        # Set labels and title
        ax2.set_xlabel('Drug Loading (weight fraction)')
        ax2.set_ylabel('Glass Transition Temperature (°C)')
        ax2_twin.set_ylabel('Shelf Life (months)')
        ax2.set_title('Thermal Properties vs. Drug Loading')
        
        # Combine legends
        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2_twin.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper center')
        
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Add optimal loading line
        ax2.axvline(x=optimal_loading, color='purple', linestyle='--', linewidth=1)
        
        plt.tight_layout()
        
        # Save figure
        fig.savefig(os.path.join(output_dir, 'loading_properties.png'), dpi=300)
        plt.close(fig)
        
    except Exception as e:
        print(f"Error creating loading profile visualization: {e}")
    
    # Save report
    report = optimizer.generate_report()
    with open(os.path.join(output_dir, 'optimization_report.md'), 'w') as f:
        f.write(report)


def test_multiple_formulations(apis, polymers, output_dir="optimization_results"):
    """
    Run drug loading optimization for multiple API-polymer combinations and save the results.
    
    Args:
        apis (dict): Dictionary of API objects
        polymers (dict): Dictionary of Polymer objects
        output_dir (str, optional): Base directory to save results
    """
    # List of API-polymer pairs to test
    test_formulations = [
        {'api': 'ibuprofen', 'polymer': 'PVP K30', 'process': 'hot_melt_extrusion'},
        {'api': 'ibuprofen', 'polymer': 'HPMC', 'process': 'hot_melt_extrusion'},
        {'api': 'indomethacin', 'polymer': 'PVP K30', 'process': 'hot_melt_extrusion'},
        {'api': 'felodipine', 'polymer': 'HPMCAS-MG', 'process': 'spray_drying'},
        {'api': 'ketoconazole', 'polymer': 'Soluplus', 'process': 'hot_melt_extrusion'}
    ]
    
    # Test each formulation
    for formulation in test_formulations:
        api_name = formulation['api']
        polymer_name = formulation['polymer']
        process_method = formulation['process']
        
        if api_name not in apis:
            print(f"API '{api_name}' not found. Skipping.")
            continue
        if polymer_name not in polymers:
            print(f"Polymer '{polymer_name}' not found. Skipping.")
            continue
        
        print(f"\n====== Testing {api_name} - {polymer_name} ({process_method}) ======\n")
        
        # Create formulation-specific output directory
        form_output_dir = os.path.join(output_dir, f"{api_name}_{polymer_name.replace(' ', '_')}")
        os.makedirs(form_output_dir, exist_ok=True)
        
        try:
            # Run optimization
            optimizer, optimal_loading, optimization_result = run_loading_optimization(
                api_name=api_name,
                polymer_name=polymer_name,
                apis=apis,
                polymers=polymers,
                process_method=process_method
            )
            
            # Analyze results
            analyze_optimization_results(optimizer, optimal_loading, optimization_result)
            
            # Create visualizations
            create_visualization(optimizer, form_output_dir)
            
            print(f"\nResults saved to: {form_output_dir}")
            
        except Exception as e:
            print(f"Error testing formulation '{api_name} - {polymer_name}': {e}")


def main():
    """
    Main function to test the LoadingOptimizer functionality.
    """
    print("Loading test data...")
    test_apis, test_polymers, _, _ = load_test_data()
    
    print(f"Loaded {len(test_apis)} APIs, {len(test_polymers)} polymers")
    
    print("\nCreating objects from test data...")
    # Create objects
    apis = create_apis_from_test_data(test_apis)
    polymers = create_polymers_from_test_data(test_polymers)
    
    print(f"Created {len(apis)} API objects, {len(polymers)} Polymer objects")
    
    # Test multiple formulations
    test_multiple_formulations(apis, polymers)
    
    print("\nDrug loading optimization tests complete!")


if __name__ == "__main__":
    main()