"""
Example script for testing the PolymerScreener functionality with test data.

This script demonstrates how to use the PolymerScreener class to screen multiple
polymers for a given API and analyze the results.
"""

import os
import json
import matplotlib.pyplot as plt
from test_data_loader import (
    load_test_data,
    create_apis_from_test_data,
    create_polymers_from_test_data
)

from asdii import API, Polymer, ASDFormulation, PolymerScreener


def run_polymer_screening(api_name, apis, polymers, drug_loading=0.3):
    """
    Run polymer screening for a given API.
    
    Args:
        api_name (str): Name of the API to screen
        apis (dict): Dictionary of API objects
        polymers (dict): Dictionary of Polymer objects
        drug_loading (float, optional): Drug loading to use for screening
        
    Returns:
        tuple: (screener, polymer_list, stability_ranking, miscibility_ranking)
    """
    # Get API
    if api_name not in apis:
        raise ValueError(f"API '{api_name}' not found.")
    
    api = apis[api_name]
    
    # Convert polymers dict to list
    polymer_list = list(polymers.values())
    
    # Create screener
    screener = PolymerScreener(
        api=api,
        polymers=polymer_list,
        drug_loading=drug_loading
    )
    
    # Run screening
    print(f"Screening {len(polymer_list)} polymers for {api_name}...")
    screener.screen_all()
    
    # Get rankings
    stability_ranking = screener.rank_by_stability()
    miscibility_ranking = screener.rank_by_miscibility()
    
    return screener, polymer_list, stability_ranking, miscibility_ranking


def analyze_screening_results(screener, stability_ranking, miscibility_ranking):
    """
    Analyze and print screening results.
    
    Args:
        screener (PolymerScreener): PolymerScreener object
        stability_ranking (list): List of (polymer_name, score) tuples sorted by stability
        miscibility_ranking (list): List of (polymer_name, score) tuples sorted by miscibility
    """
    print("\nStability Ranking:")
    for i, (polymer_name, score) in enumerate(stability_ranking):
        print(f"{i+1}. {polymer_name}: {score:.2f}")
    
    print("\nMiscibility Ranking:")
    for i, (polymer_name, score) in enumerate(miscibility_ranking):
        print(f"{i+1}. {polymer_name}: {score:.2f}")
    
    # Get top polymers
    top_polymers = screener.get_top_polymers(n=3, criterion='stability')
    
    print("\nTop 3 Polymers by Stability:")
    for i, polymer in enumerate(top_polymers):
        print(f"{i+1}. {polymer.name}")
    
    # Generate report
    print("\nGenerating screening report...")
    report = screener.generate_report()
    
    # Print the first 500 characters of the report
    print("\nExcerpt from the screening report:")
    print(report[:500] + "...")


def create_visualization(screener, output_dir):
    """
    Create and save visualizations of screening results.
    
    Args:
        screener (PolymerScreener): PolymerScreener object
        output_dir (str): Directory to save visualizations
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot stability ranking
    fig_stability = screener.plot_ranking(criterion='stability')
    fig_stability.savefig(os.path.join(output_dir, 'stability_ranking.png'), dpi=300)
    plt.close(fig_stability)
    
    # Plot miscibility ranking
    fig_miscibility = screener.plot_ranking(criterion='miscibility')
    fig_miscibility.savefig(os.path.join(output_dir, 'miscibility_ranking.png'), dpi=300)
    plt.close(fig_miscibility)
    
    # Create a comparison visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    
    # Get stability and miscibility rankings
    stability_ranking = screener.rank_by_stability()
    miscibility_ranking = screener.rank_by_miscibility()
    
    # Convert to dataframes for easier manipulation
    import pandas as pd
    
    stability_df = pd.DataFrame(stability_ranking, columns=['Polymer', 'Stability'])
    miscibility_df = pd.DataFrame(miscibility_ranking, columns=['Polymer', 'Miscibility'])
    
    # Merge dataframes
    comparison_df = pd.merge(stability_df, miscibility_df, on='Polymer')
    
    # Sort by stability
    comparison_df = comparison_df.sort_values(by='Stability', ascending=False)
    
    # Plot stability vs. miscibility
    polymers = comparison_df['Polymer'].tolist()
    stabilities = comparison_df['Stability'].tolist()
    miscibilities = comparison_df['Miscibility'].tolist()
    
    # Plot stability bars
    ax1.barh(polymers, stabilities, color='skyblue')
    ax1.set_xlabel('Stability Score')
    ax1.set_ylabel('Polymer')
    ax1.set_title('Polymer Stability Ranking')
    ax1.set_xlim(0, 1)
    ax1.axvline(x=0.7, color='red', linestyle='--', linewidth=1, label='Good Stability Threshold')
    ax1.legend()
    
    # Plot miscibility bars
    ax2.barh(polymers, miscibilities, color='lightgreen')
    ax2.set_xlabel('Miscibility Score')
    ax2.set_ylabel('Polymer')
    ax2.set_title('Polymer Miscibility Ranking')
    ax2.set_xlim(0, 1)
    ax2.axvline(x=0.7, color='red', linestyle='--', linewidth=1, label='Good Miscibility Threshold')
    ax2.legend()
    
    plt.tight_layout()
    
    # Save figure
    fig.savefig(os.path.join(output_dir, 'polymer_comparison.png'), dpi=300)
    plt.close(fig)
    
    # Save report
    report = screener.generate_report()
    with open(os.path.join(output_dir, 'screening_report.md'), 'w') as f:
        f.write(report)


def test_multiple_apis(apis, polymers, output_dir="screening_results"):
    """
    Run polymer screening for multiple APIs and save the results.
    
    Args:
        apis (dict): Dictionary of API objects
        polymers (dict): Dictionary of Polymer objects
        output_dir (str, optional): Base directory to save results
    """
    # List of APIs to test
    test_api_names = ['ibuprofen', 'indomethacin', 'felodipine', 'carbamazepine']
    
    # Test each API
    for api_name in test_api_names:
        if api_name not in apis:
            print(f"API '{api_name}' not found. Skipping.")
            continue
        
        print(f"\n====== Testing API: {api_name} ======\n")
        
        # Create API-specific output directory
        api_output_dir = os.path.join(output_dir, api_name)
        os.makedirs(api_output_dir, exist_ok=True)
        
        try:
            # Run screening
            screener, polymer_list, stability_ranking, miscibility_ranking = run_polymer_screening(
                api_name=api_name,
                apis=apis,
                polymers=polymers
            )
            
            # Analyze results
            analyze_screening_results(screener, stability_ranking, miscibility_ranking)
            
            # Create visualizations
            create_visualization(screener, api_output_dir)
            
            print(f"\nResults saved to: {api_output_dir}")
            
        except Exception as e:
            print(f"Error testing API '{api_name}': {e}")


def main():
    """
    Main function to test the PolymerScreener functionality.
    """
    print("Loading test data...")
    test_apis, test_polymers, _, _ = load_test_data()
    
    print(f"Loaded {len(test_apis)} APIs, {len(test_polymers)} polymers")
    
    print("\nCreating objects from test data...")
    # Create objects
    apis = create_apis_from_test_data(test_apis)
    polymers = create_polymers_from_test_data(test_polymers)
    
    print(f"Created {len(apis)} API objects, {len(polymers)} Polymer objects")
    
    # Test multiple APIs
    test_multiple_apis(apis, polymers)
    
    print("\nPolymer screening tests complete!")


if __name__ == "__main__":
    main()