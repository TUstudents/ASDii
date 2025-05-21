Quick Start
===========

This guide will help you get started with ASDii by walking through some common use cases.

Basic Usage
----------

1. Import the necessary classes from ASDii:

   .. code-block:: python

      from asdii import API, Polymer, ASDFormulation

2. Create an API (Active Pharmaceutical Ingredient) object:

   .. code-block:: python

      # Create from SMILES
      ibuprofen = API.from_smiles("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", name="Ibuprofen")
      
      # Or look up from the database
      # ibuprofen = API.from_name("Ibuprofen")
      
      # Calculate properties
      ibuprofen.calculate_properties()
      ibuprofen.calculate_solubility_parameters()
      
      print(f"Ibuprofen properties:")
      print(f"  Molecular Weight: {ibuprofen.molecular_weight:.2f} g/mol")
      print(f"  LogP: {ibuprofen.log_p:.2f}")
      print(f"  Melting Point: {ibuprofen.melting_point:.1f}°C")
      print(f"  Glass Transition Temperature: {ibuprofen.glass_transition_temp:.1f}°C")

3. Create a Polymer object:

   .. code-block:: python

      # Look up from the database
      pvp = Polymer.from_name("PVP K30")
      
      print(f"PVP K30 properties:")
      print(f"  Glass Transition Temperature: {pvp.glass_transition_temp:.1f}°C")
      print(f"  Hygroscopicity: {pvp.hygroscopicity:.2f}")

4. Create an ASD formulation:

   .. code-block:: python

      # Create formulation with 30% drug loading
      formulation = ASDFormulation(
          api=ibuprofen,
          polymer=pvp,
          drug_loading=0.3,
          process_method="hot_melt_extrusion"
      )

5. Predict formulation properties:

   .. code-block:: python

      # Predict glass transition temperature
      tg = formulation.predict_glass_transition_temp()
      print(f"Predicted Glass Transition Temperature: {tg:.1f}°C")
      
      # Predict miscibility
      miscibility = formulation.predict_miscibility()
      print(f"Predicted Miscibility: {miscibility:.2f}")
      
      # Predict stability
      stability = formulation.predict_stability()
      print(f"Predicted Stability Score: {stability['score']:.2f}")
      print(f"Estimated Shelf Life: {stability['shelf_life_estimate']} months")

6. Generate a formulation report:

   .. code-block:: python

      # Generate a report
      report = formulation.generate_report()
      
      # Save report to a file
      with open("formulation_report.md", "w") as f:
          f.write(report)

Screening Multiple Polymers
--------------------------

1. Create an API object:

   .. code-block:: python

      ibuprofen = API.from_smiles("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", name="Ibuprofen")

2. Load common polymers:

   .. code-block:: python

      from asdii import PolymerScreener
      
      # Create polymer screener
      screener = PolymerScreener(
          api=ibuprofen, 
          drug_loading=0.3
      )

3. Screen polymers:

   .. code-block:: python

      # Screen polymers
      results = screener.screen_all()
      
      # Rank polymers by stability
      stability_ranking = screener.rank_by_stability()
      
      print("Polymers ranked by stability:")
      for i, (polymer_name, stability) in enumerate(stability_ranking):
          print(f"{i+1}. {polymer_name}: {stability:.2f}")

4. Visualize results:

   .. code-block:: python

      import matplotlib.pyplot as plt
      
      # Plot ranking
      fig = screener.plot_ranking(criterion='stability')
      
      # Save plot
      plt.savefig("polymer_ranking.png")
      plt.close(fig)

5. Generate a screening report:

   .. code-block:: python

      # Generate a report
      report = screener.generate_report()
      
      # Save report to a file
      with open("screening_report.md", "w") as f:
          f.write(report)

Optimizing Drug Loading
----------------------

1. Create API and polymer objects:

   .. code-block:: python

      ibuprofen = API.from_smiles("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", name="Ibuprofen")
      pvp = Polymer.from_name("PVP K30")

2. Create a loading optimizer:

   .. code-block:: python

      from asdii import LoadingOptimizer
      
      # Create loading optimizer
      optimizer = LoadingOptimizer(
          api=ibuprofen,
          polymer=pvp,
          process_method="hot_melt_extrusion",
          min_loading=0.1,
          max_loading=0.5,
          min_stability=0.7
      )

3. Find optimal loading:

   .. code-block:: python

      # Find optimal loading
      optimal_loading = optimizer.find_optimal_loading()
      
      print(f"Optimal Drug Loading: {optimal_loading:.1%}")
      
      # Get result for optimal loading
      optimal_result = optimizer.results[optimal_loading]
      print(f"Stability Score: {optimal_result['stability']:.2f}")
      print(f"Glass Transition Temperature: {optimal_result['glass_transition_temp']:.1f}°C")
      print(f"Estimated Shelf Life: {optimal_result['shelf_life_estimate']} months")

4. Visualize loading optimization:

   .. code-block:: python

      import matplotlib.pyplot as plt
      
      # Plot stability vs. loading
      fig = optimizer.plot_stability_vs_loading()
      
      # Save plot
      plt.savefig("loading_optimization.png")
      plt.close(fig)

Next Steps
---------

Now that you're familiar with the basic functionality of ASDii, you can explore more advanced features:

- Customize stability prediction models
- Optimize process parameters
- Create custom visualization plots
- Integrate with your own experimental data

Check out the :doc:`tutorials/index` for more detailed examples.