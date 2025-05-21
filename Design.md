# ASDii: High-Level Design Document

## 1. Project Overview

ASDii (Amorphous Solid Dispersion Intelligent Insights) is a Python library designed to help pharmaceutical scientists predict and optimize amorphous solid dispersion (ASD) formulations. The library aims to reduce the experimental burden by providing computational tools for screening APIs, polymers, and process parameters to identify promising formulation candidates.

## 2. Core Modules and Data Flow

### 2.1 Core Components

```
[User Input] → [Data Structures] → [Property Calculators] → [Predictive Models] → [Reports/Visualizations]
```

The library consists of the following key components:

1. **Core Data Structures**
   - API: Representation of active pharmaceutical ingredients
   - Polymer: Representation of carrier polymers
   - ASDFormulation: Representation of an API-polymer formulation
   - ProcessParameters: Representation of manufacturing parameters

2. **Property Calculators**
   - MolecularDescriptors: Calculate molecular properties of APIs and polymers
   - SolubilityParameters: Calculate Hildebrand and Hansen solubility parameters
   - ThermalProperties: Calculate glass transition temperatures and related properties
   - MiscibilityCalculator: Assess API-polymer miscibility
   - MolecularMobilityCalculator: Estimate molecular mobility parameters

3. **Predictive Models**
   - FormationPredictor: Predict ASD formation feasibility
   - StabilityPredictor: Predict long-term stability of ASDs
   - LoadingOptimizer: Optimize drug loading capacity
   - ProcessOptimizer: Recommend process parameters

4. **Reporting and Visualization**
   - FormulationReport: Generate detailed reports on formulation properties
   - StabilityVisualizer: Visualize stability predictions
   - PhaseVisualizer: Generate phase diagrams
   - PropertyVisualizer: Visualize molecular and formulation properties

5. **Database and Data Management**
   - MaterialsDatabase: Store and retrieve API and polymer data
   - LiteratureDatabase: Store and retrieve literature data on ASDs

6. **Utilities**
   - SMILESParser: Parse SMILES strings to create molecular representations
   - FileIO: Handle file input/output operations
   - UnitConverter: Convert between different units

### 2.2 Data Flow

1. User provides API and polymer information (structure, name, properties)
2. System calculates molecular descriptors and key properties
3. Predictive models use calculated properties to assess formation, stability, etc.
4. Results are formatted into reports and visualizations
5. Recommendations for optimization are provided

## 3. Key Algorithms and Models

### 3.1 Property Calculation Methods

1. **Solubility Parameters**
   - Group contribution methods (GCM) for Hansen solubility parameters
   - Molecular dynamics-based approaches for refined estimates

2. **Glass Transition Temperature**
   - Gordon-Taylor equation for mixture Tg prediction
   - Fox equation as an alternative approach
   - Group contribution methods for pure component Tg estimation

3. **Miscibility Assessment**
   - Flory-Huggins interaction parameter calculation
   - Hansen space distance calculation
   - Bagley plot generation

4. **Molecular Mobility**
   - Williams-Landel-Ferry (WLF) equation implementation
   - Adam-Gibbs approach for molecular mobility

### 3.2 Predictive Models

1. **ASD Formation Prediction**
   - Rule-based screening (initial implementation)
   - Machine learning models (future enhancement)
     - Random Forest classifier
     - Support Vector Machine classifier
     - Gradient Boosting classifier

2. **Stability Prediction**
   - Thermodynamic stability assessment
   - Kinetic stability assessment
   - Combined stability score calculation

3. **Drug Loading Optimization**
   - Binary search algorithm for maximum stable loading
   - Constraints-based optimization

4. **Process Parameter Optimization**
   - Decision tree-based recommendation system
   - Process-specific models for HME, spray drying, etc.

## 4. User Interaction

### 4.1 Library Usage Workflows

1. **Single Formulation Assessment**
   ```python
   # Create API and polymer instances
   api = API.from_smiles(smiles_string)
   polymer = Polymer.from_name(polymer_name)
   
   # Create formulation and assess properties
   formulation = ASDFormulation(api, polymer, drug_loading=0.3)
   stability = formulation.predict_stability()
   
   # Generate report
   report = FormulationReport(formulation)
   report.save("formulation_report.pdf")
   ```

2. **Polymer Screening for an API**
   ```python
   # Create API instance
   api = API.from_smiles(smiles_string)
   
   # Screen against multiple polymers
   polymers = Polymer.load_common_polymers()
   screener = PolymerScreener(api, polymers)
   results = screener.rank_by_stability()
   
   # Visualize results
   screener.plot_ranking()
   ```

3. **Drug Loading Optimization**
   ```python
   # Create API and polymer instances
   api = API.from_smiles(smiles_string)
   polymer = Polymer.from_name(polymer_name)
   
   # Optimize loading
   optimizer = LoadingOptimizer(api, polymer)
   optimal_loading = optimizer.find_optimal_loading()
   
   # Create optimized formulation
   formulation = ASDFormulation(api, polymer, drug_loading=optimal_loading)
   ```

4. **Process Parameter Optimization**
   ```python
   # Create formulation
   formulation = ASDFormulation(api, polymer, drug_loading=0.3)
   
   # Optimize process parameters
   process_optimizer = ProcessOptimizer(formulation, method="hot_melt_extrusion")
   optimal_parameters = process_optimizer.optimize()
   ```

### 4.2 Input Sources

1. **Direct Input**
   - SMILES strings for APIs
   - Names or identifiers for common polymers
   - Manual property input for custom materials

2. **Database Retrieval**
   - Internal database of common APIs and polymers
   - Integration with external databases (e.g., PubChem)

3. **File Import**
   - SDF, MOL, XYZ file import for structures
   - CSV import for property data
   - JSON import for complete formulation specifications

### 4.3 Output Formats

1. **Reports**
   - PDF reports with formulation properties and predictions
   - Markdown reports for integration with notebooks
   - JSON data for programmatic access

2. **Visualizations**
   - Static plots (PNG, PDF)
   - Interactive plots for notebooks (HTML)
   - 3D visualizations of molecular structures

## 5. Implementation Plan

### 5.1 Initial Version (v0.1)

**Core Functionality:**
- Basic API and Polymer classes with essential properties
- Simple property calculators using established equations
- Rule-based formation and stability predictors
- Basic reporting functionality
- Database of common polymers with key properties
- Command-line interface for basic operations

**Limitations:**
- Limited to small molecule APIs
- Simplified prediction models
- Limited validation against experimental data
- Basic visualization capabilities

### 5.2 Future Enhancements

**Medium-term (v0.2-0.5):**
- Enhanced molecular descriptors
- Machine learning models for prediction
- Integration with molecular dynamics tools
- Advanced visualization capabilities
- Expanded database of APIs and polymers
- Web API for remote access

**Long-term (v1.0+):**
- Comprehensive validation against experimental data
- Advanced optimization algorithms
- Integration with laboratory automation systems
- Real-time stability monitoring tools
- Customizable prediction models
- GUI for non-programmatic access

## 6. Dependencies

### 6.1 Core Dependencies

- **NumPy & SciPy**: Numerical operations and scientific computing
- **Pandas**: Data manipulation and analysis
- **RDKit**: Cheminformatics and molecular property calculation
- **Scikit-learn**: Machine learning models
- **Matplotlib & Seaborn**: Visualization
- **Mordred**: Molecular descriptor calculation

### 6.2 Optional Dependencies

- **PyTorch/TensorFlow**: Advanced ML models
- **MDTraj**: Molecular dynamics trajectory analysis
- **Panel/Plotly**: Interactive visualizations
- **Streamlit**: Simple web interfaces
- **ReportLab/PDFKit**: PDF report generation

## 7. Testing Strategy

1. **Unit Tests**
   - Test each calculator and predictor individually
   - Verify against known values from literature
   - Test edge cases and error handling

2. **Integration Tests**
   - Test complete workflows
   - Verify consistency across different pathways

3. **Validation Tests**
   - Compare predictions with experimental data
   - Benchmark against existing tools and methods

## 8. Appendix: Terminology and Definitions

- **ASD**: Amorphous Solid Dispersion
- **API**: Active Pharmaceutical Ingredient
- **Tg**: Glass Transition Temperature
- **HSP**: Hansen Solubility Parameters
- **HME**: Hot Melt Extrusion
- **FH**: Flory-Huggins (interaction parameter)
- **GCM**: Group Contribution Method
- **QSPR**: Quantitative Structure-Property Relationship