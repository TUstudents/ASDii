"""
Basic usage example for the ASDii library.

This script demonstrates the basic functionality of the ASDii library by
creating an API and polymer, forming an ASD formulation, and analyzing its
properties.
"""

import os
import time
import matplotlib.pyplot as plt

from asdii import API, Polymer, ASDFormulation
from asdii import MaterialsDatabase
from asdii import PolymerScreener
from asdii import StabilityPredictor
from asdii import LoadingOptimizer


def main():
    """
    Demonstrate basic usage of the ASDii library.
    """
    print("ASDii: Amorphous Solid Dispersion Intelligent Insights")
    print("Basic Usage Example\n")
    
    # Step 1: Create an API from a SMILES string
    print("Step 1: Creating API...")
    ibuprofen = API.from_smiles("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", name="Ibuprofen")
    print(f"Created API: {ibuprofen}")
    
    # Calculate properties
    ibuprofen.calculate_properties()
    ibuprofen.calculate_solubility_parameters()
    print(f"  Molecular Weight: {ibuprofen.molecular_weight:.2f} g/mol")
    print(f"  LogP: {ibuprofen.log_p:.2f}")
    print(f"  H-Bond Donors: {ibuprofen.h_bond_donors}")
    print(f"  H-Bond Acceptors: {ibuprofen.h_bond_acceptors}")
    print(f"  Solubility Parameters: δd={ibuprofen.solubility_parameters['dispersive']:.2f}, " +
          f"δp={ibuprofen.solubility_parameters['polar']:.2f}, " +
          f"δh={ibuprofen.solubility_parameters['hydrogen']:.2f}")
    
    # Step 2: Create a polymer from the database
    print("\nStep 2: Creating polymer...")
    try:
        pvp = Polymer.from_name("PVP K30")
        print(f"Created polymer: {pvp}")
        print(f"  Type: {pvp.type}")
        print(f"  Glass Transition Temperature: {pvp.glass_transition_temp:.1f}°C")
        print(f"  Solubility Parameters: δd={pvp.solubility_parameters['dispersive']:.2f}, " +
              f"δp={pvp.solubility_parameters['polar']:.2f}, " +
              f"δh={pvp.solubility_parameters['hydrogen']:.2f}")
        print(f"  Hydrophilicity: {pvp.hydrophilicity:.2f}")
        print(f"  Hygroscopicity: {pvp.hygroscopicity:.2f}")
    except Exception as e:
        print(f"Error creating polymer from database: {e}")
        print("Creating a generic polymer instead...")
        pvp = Polymer("PVP K30", type="vinyl", 
                      molecular_weight=50000, 
                      glass_transition_temp=149.0,
                      solubility_parameters={
                          'dispersive': 17.0,
                          'polar': 8.0,
                          'hydrogen': 12.0,
                          'total': 22.2
                      },
                      hydrophilicity=0.85,
                      hygroscopicity=0.80)
    
    # Step 3: Create an ASD formulation
    print("\nStep 3: Creating ASD formulation...")
    formulation = ASDFormulation(
        api=ibuprofen,
        polymer=pvp,
        drug_loading=0.3,
        process_method="hot_melt_extrusion"
    )
    print(f"Created formulation: {formulation}")
    
    # Step 4: Predict formulation properties
    print("\nStep 4: Predicting formulation properties...")
    # Predict glass transition temperature
    tg = formulation.predict_glass_transition_temp()
    print(f"  Predicted Glass Transition Temperature: {tg:.1f}°C")
    
    # Predict miscibility
    miscibility = formulation.predict_miscibility()
    print(f"  Predicted Miscibility: {miscibility:.2f}")
    
    # Predict stability
    stability = formulation.predict_stability()
    print(f"  Predicted Stability Score: {stability['score']:.2f}")
    print(f"  Thermodynamic Stability: {stability['thermodynamic']:.2f}")
    print(f"  Kinetic Stability: {stability['kinetic']:.2f}")
    print(f"  Estimated Shelf Life: {stability['shelf_life_estimate']} months")
    print("  Major Factors Affecting Stability:")
    for factor, score in stability['major_factors']:
        print(f"    - {factor}: {score:.2f}")
    
    # Step 5: Generate a formulation report
    print("\nStep 5: Generating formulation report...")
    report = formulation.generate_report()
    print("Report generated. First 200 characters:")
    print(report[:200] + "...")
    
    # Step 6: Screen multiple polymers
    print("\nStep 6: Screening multiple polymers...")
    # Load common polymers
    try:
        common_polymers = Polymer.load_common_polymers()
        print(f"Loaded {len(common_polymers)} common polymers")
    except Exception as e:
        print(f"Error loading common polymers: {e}")
        print("Creating a list of generic polymers instead...")
        common_polymers = [
            pvp,
            Polymer("HPMC", type="cellulosic", 
                    molecular_weight=22000, 
                    glass_transition_temp=175.0,
                    solubility_parameters={
                        'dispersive': 18.0,
                        'polar': 8.6,
                        'hydrogen': 11.9,
                        'total': 23.3
                    },
                    hydrophilicity=0.70,
                    hygroscopicity=0.65),
            Polymer("Soluplus", type="graft copolymer", 
                    molecular_weight=90000, 
                    glass_transition_temp=70.0,
                    solubility_parameters={
                        'dispersive': 17.5,
                        'polar': 7.0,
                        'hydrogen': 9.0,
                        'total': 20.9
                    },
                    hydrophilicity=0.55,
                    hygroscopicity=0.45)
        ]
    
    # Create polymer screener
    screener = PolymerScreener(ibuprofen, common_polymers, drug_loading=0.3)
    
    # Screen polymers
    print("Screening polymers...")
    start_time = time.time()
    results = screener.screen_all()
    end_time = time.time()
    print(f"Screening completed in {end_time - start_time:.2f} seconds")
    
    # Rank polymers by stability
    stability_ranking = screener.rank_by_stability()
    print("\nPolymers ranked by stability:")
    for i, (polymer_name, stability) in enumerate(stability_ranking):
        print(f"  {i+1}. {polymer_name}: {stability:.2f}")
    
    # Step 7: Optimize drug loading
    print("\nStep 7: Optimizing drug loading...")
    # Create loading optimizer for the best polymer
    best_polymer_name, _ = stability_ranking[0]
    best_polymer = None
    for polymer in common_polymers:
        if polymer.name == best_polymer_name:
            best_polymer = polymer
            break
    
    if best_polymer:
        optimizer = LoadingOptimizer(
            api=ibuprofen,
            polymer=best_polymer,
            process_method="hot_melt_extrusion",
            min_loading=0.1,
            max_loading=0.5,
            min_stability=0.7
        )
        
        # Find optimal loading
        print(f"Finding optimal drug loading for {best_polymer.name}...")
        optimal_loading = optimizer.find_optimal_loading()
        print(f"  Optimal Drug Loading: {optimal_loading:.1%}")
        
        # Get result for optimal loading
        optimal_result = optimizer.results[optimal_loading]
        print(f"  Stability Score: {optimal_result['stability']:.2f}")
        print(f"  Glass Transition Temperature: {optimal_result['glass_transition_temp']:.1f}°C")
        print(f"  Estimated Shelf Life: {optimal_result['shelf_life_estimate']} months")
    
    # Step 8: Generate visualizations
    print("\nStep 8: Generating visualizations...")
    
    # Create output directory for visualizations
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot polymer ranking
    try:
        fig = screener.plot_ranking(criterion='stability')
        plt.savefig(os.path.join(output_dir, "polymer_ranking.png"))
        plt.close(fig)
        print(f"  Saved polymer ranking plot to {os.path.join(output_dir, 'polymer_ranking.png')}")
    except Exception as e:
        print(f"  Error generating polymer ranking plot: {e}")
    
    # Plot stability visualization
    try:
        fig = formulation.visualize_stability()
        plt.savefig(os.path.join(output_dir, "stability_visualization.png"))
        plt.close(fig)
        print(f"  Saved stability visualization to {os.path.join(output_dir, 'stability_visualization.png')}")
    except Exception as e:
        print(f"  Error generating stability visualization: {e}")
    
    # Plot phase diagram
    try:
        fig = formulation.visualize_phase_diagram()
        plt.savefig(os.path.join(output_dir, "phase_diagram.png"))
        plt.close(fig)
        print(f"  Saved phase diagram to {os.path.join(output_dir, 'phase_diagram.png')}")
    except Exception as e:
        print(f"  Error generating phase diagram: {e}")
    
    # Plot loading optimization
    if best_polymer:
        try:
            fig = optimizer.plot_stability_vs_loading()
            plt.savefig(os.path.join(output_dir, "loading_optimization.png"))
            plt.close(fig)
            print(f"  Saved loading optimization plot to {os.path.join(output_dir, 'loading_optimization.png')}")
        except Exception as e:
            print(f"  Error generating loading optimization plot: {e}")
    
    print("\nBasic usage example completed.")


if __name__ == "__main__":
    main()