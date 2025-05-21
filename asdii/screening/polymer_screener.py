"""
Implementation of the PolymerScreener class.

This module provides the PolymerScreener class which screens polymers for
compatibility with a given API in ASD formulations.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import logging
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

from asdii.core.api import API
from asdii.core.polymer import Polymer
from asdii.core.formulation import ASDFormulation
from asdii.database.materials_db import MaterialsDatabase


class PolymerScreener:
    """
    Screens polymers for compatibility with a given API.
    
    Attributes:
        api (API): API object
        polymers (list): List of Polymer objects
        formulations (list): List of ASDFormulation objects
        results (dict): Dictionary of screening results
    """
    
    def __init__(
        self, 
        api: API, 
        polymers: Optional[List[Polymer]] = None, 
        drug_loading: float = 0.3
    ) -> None:
        """
        Initialize a PolymerScreener object.
        
        Args:
            api (API): API object
            polymers (list, optional): List of Polymer objects. If not provided,
                common polymers will be loaded from the database.
            drug_loading (float, optional): Drug loading for screening formulations
        
        Raises:
            ValueError: If drug_loading is not between 0 and 1
        """
        if not 0 <= drug_loading <= 1:
            raise ValueError("Drug loading must be between 0 and 1.")
        
        self.api = api
        self.drug_loading = drug_loading
        
        # Load polymers if not provided
        if polymers is None:
            self.polymers = self._load_common_polymers()
        else:
            self.polymers = polymers
        
        self.formulations = []
        self.results = {}
        
        # Create formulations
        self._create_formulations()
    
    def _load_common_polymers(self) -> List[Polymer]:
        """
        Load common polymers from the database.
        
        Returns:
            list: List of Polymer objects
        """
        return Polymer.load_common_polymers()
    
    def _create_formulations(self) -> None:
        """
        Create formulations for all polymers.
        """
        self.formulations = []
        
        for polymer in self.polymers:
            formulation = ASDFormulation(
                api=self.api,
                polymer=polymer,
                drug_loading=self.drug_loading
            )
            self.formulations.append(formulation)
    
    def screen_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Screen all polymers for compatibility with the API.
        
        Returns:
            dict: Dictionary of screening results
        """
        results = {}
        
        for formulation in self.formulations:
            polymer_name = formulation.polymer.name
            
            # Calculate properties
            try:
                # Get miscibility
                miscibility = formulation.predict_miscibility()
                
                # Get glass transition temperature
                tg = formulation.predict_glass_transition_temp()
                
                # Get stability prediction
                stability = formulation.predict_stability()
                
                results[polymer_name] = {
                    'miscibility': miscibility,
                    'glass_transition_temp': tg,
                    'stability': stability['score'],
                    'thermodynamic_stability': stability['thermodynamic'],
                    'kinetic_stability': stability['kinetic'],
                    'shelf_life_estimate': stability['shelf_life_estimate'],
                    'formulation': formulation
                }
            except Exception as e:
                logging.warning(f"Failed to screen polymer {polymer_name}: {e}")
                results[polymer_name] = {
                    'error': str(e),
                    'formulation': formulation
                }
        
        self.results = results
        
        return results
    
    def screen_parallel(self, max_workers: int = 4) -> Dict[str, Dict[str, Any]]:
        """
        Screen all polymers in parallel for compatibility with the API.
        
        Args:
            max_workers (int, optional): Maximum number of worker threads
            
        Returns:
            dict: Dictionary of screening results
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks
            future_to_polymer = {
                executor.submit(self._screen_polymer, formulation): formulation.polymer.name
                for formulation in self.formulations
            }
            
            # Process results as they complete
            for future in as_completed(future_to_polymer):
                polymer_name = future_to_polymer[future]
                try:
                    result = future.result()
                    results[polymer_name] = result
                except Exception as e:
                    logging.warning(f"Failed to screen polymer {polymer_name}: {e}")
                    results[polymer_name] = {
                        'error': str(e),
                        'formulation': self._get_formulation_by_polymer_name(polymer_name)
                    }
        
        self.results = results
        
        return results
    
    def _screen_polymer(self, formulation: ASDFormulation) -> Dict[str, Any]:
        """
        Screen a single polymer for compatibility with the API.
        
        Args:
            formulation (ASDFormulation): Formulation to screen
            
        Returns:
            dict: Screening results
        """
        # Calculate properties
        try:
            # Get miscibility
            miscibility = formulation.predict_miscibility()
            
            # Get glass transition temperature
            tg = formulation.predict_glass_transition_temp()
            
            # Get stability prediction
            stability = formulation.predict_stability()
            
            return {
                'miscibility': miscibility,
                'glass_transition_temp': tg,
                'stability': stability['score'],
                'thermodynamic_stability': stability['thermodynamic'],
                'kinetic_stability': stability['kinetic'],
                'shelf_life_estimate': stability['shelf_life_estimate'],
                'formulation': formulation
            }
        except Exception as e:
            raise Exception(f"Failed to screen polymer {formulation.polymer.name}: {e}")
    
    def _get_formulation_by_polymer_name(self, polymer_name: str) -> Optional[ASDFormulation]:
        """
        Get a formulation by polymer name.
        
        Args:
            polymer_name (str): Polymer name
            
        Returns:
            ASDFormulation or None: Formulation object if found, None otherwise
        """
        for formulation in self.formulations:
            if formulation.polymer.name == polymer_name:
                return formulation
        
        return None
    
    def rank_by_miscibility(self) -> List[Tuple[str, float]]:
        """
        Rank polymers by miscibility with the API.
        
        Returns:
            list: List of (polymer_name, score) tuples sorted by miscibility
        """
        # Ensure screening has been performed
        if not self.results:
            self.screen_all()
        
        # Create ranking
        ranking = []
        
        for polymer_name, result in self.results.items():
            if 'miscibility' in result:
                ranking.append((polymer_name, result['miscibility']))
        
        # Sort by miscibility (descending)
        ranking.sort(key=lambda x: x[1], reverse=True)
        
        return ranking
    
    def rank_by_stability(self) -> List[Tuple[str, float]]:
        """
        Rank polymers by predicted formulation stability.
        
        Returns:
            list: List of (polymer_name, score) tuples sorted by stability
        """
        # Ensure screening has been performed
        if not self.results:
            self.screen_all()
        
        # Create ranking
        ranking = []
        
        for polymer_name, result in self.results.items():
            if 'stability' in result:
                ranking.append((polymer_name, result['stability']))
        
        # Sort by stability (descending)
        ranking.sort(key=lambda x: x[1], reverse=True)
        
        return ranking
    
    def get_top_polymers(self, n: int = 3, criterion: str = 'stability') -> List[Polymer]:
        """
        Get the top n polymers based on a specified criterion.
        
        Args:
            n (int, optional): Number of top polymers to return
            criterion (str, optional): Ranking criterion ('stability', 'miscibility',
                'shelf_life', 'thermodynamic_stability', 'kinetic_stability')
            
        Returns:
            list: List of top n Polymer objects
            
        Raises:
            ValueError: If criterion is not valid
        """
        # Validate criterion
        valid_criteria = [
            'stability', 'miscibility', 'shelf_life', 'thermodynamic_stability', 'kinetic_stability'
        ]
        if criterion not in valid_criteria:
            raise ValueError(
                f"Invalid criterion: {criterion}. "
                f"Valid criteria are: {', '.join(valid_criteria)}"
            )
        
        # Ensure screening has been performed
        if not self.results:
            self.screen_all()
        
        # Create ranking
        ranking = []
        
        for polymer_name, result in self.results.items():
            if criterion == 'shelf_life' and 'shelf_life_estimate' in result:
                ranking.append((polymer_name, result['shelf_life_estimate']))
            elif criterion in result:
                ranking.append((polymer_name, result[criterion]))
        
        # Sort by criterion (descending)
        ranking.sort(key=lambda x: x[1], reverse=True)
        
        # Get top n polymers
        top_polymers = []
        
        for i, (polymer_name, _) in enumerate(ranking):
            if i >= n:
                break
                
            # Find polymer object
            for polymer in self.polymers:
                if polymer.name == polymer_name:
                    top_polymers.append(polymer)
                    break
        
        return top_polymers
    
    def plot_ranking(self, criterion: str = 'stability') -> Any:
        """
        Plot the ranking of polymers based on a specified criterion.
        
        Args:
            criterion (str, optional): Ranking criterion ('stability', 'miscibility',
                'shelf_life', 'thermodynamic_stability', 'kinetic_stability')
            
        Returns:
            matplotlib.figure.Figure: Figure object with the ranking plot
            
        Raises:
            ImportError: If matplotlib is not available
            ValueError: If criterion is not valid
        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.figure import Figure
        except ImportError:
            raise ImportError("Matplotlib is required for visualization.")
        
        # Validate criterion
        valid_criteria = [
            'stability', 'miscibility', 'shelf_life', 'thermodynamic_stability', 'kinetic_stability'
        ]
        if criterion not in valid_criteria:
            raise ValueError(
                f"Invalid criterion: {criterion}. "
                f"Valid criteria are: {', '.join(valid_criteria)}"
            )
        
        # Get ranking
        if criterion == 'stability':
            ranking = self.rank_by_stability()
        elif criterion == 'miscibility':
            ranking = self.rank_by_miscibility()
        else:
            # Create custom ranking
            ranking = []
            
            for polymer_name, result in self.results.items():
                if criterion == 'shelf_life' and 'shelf_life_estimate' in result:
                    ranking.append((polymer_name, result['shelf_life_estimate']))
                elif criterion in result:
                    ranking.append((polymer_name, result[criterion]))
                    
            # Sort by criterion (descending)
            ranking.sort(key=lambda x: x[1], reverse=True)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Extract data
        polymer_names = [item[0] for item in ranking]
        scores = [item[1] for item in ranking]
        
        # Create horizontal bar chart
        bars = ax.barh(polymer_names, scores, color='skyblue')
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(
                width + 0.01,
                bar.get_y() + bar.get_height() / 2,
                f'{width:.2f}',
                va='center'
            )
        
        # Set title and labels
        criterion_label = criterion.replace('_', ' ').title()
        ax.set_title(f'Polymer Ranking by {criterion_label}')
        ax.set_xlabel(f'{criterion_label} Score')
        ax.set_ylabel('Polymer')
        
        # Set x-axis limits
        if criterion != 'shelf_life':
            ax.set_xlim(0, max(scores) * 1.1)
            # Add threshold line for criteria with 0-1 scale
            if criterion in ['stability', 'miscibility', 'thermodynamic_stability', 'kinetic_stability']:
                ax.axvline(x=0.7, color='red', linestyle='--', linewidth=1)
                ax.text(0.71, ax.get_ylim()[0], '0.7 (Good)', color='red', va='bottom')
        else:
            ax.set_xlim(0, max(scores) * 1.2)
        
        # Add grid
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Tight layout
        plt.tight_layout()
        
        return fig
    
    def generate_report(self, format: str = 'markdown') -> Union[str, Dict[str, Any]]:
        """
        Generate a comprehensive report of the screening results.
        
        Args:
            format (str, optional): Report format ('markdown', 'json')
            
        Returns:
            str or dict: Report content
            
        Raises:
            ValueError: If format is not valid
        """
        # Validate format
        valid_formats = ['markdown', 'json']
        if format not in valid_formats:
            raise ValueError(f"Invalid format: {format}. Valid formats are: {', '.join(valid_formats)}")
        
        # Ensure screening has been performed
        if not self.results:
            self.screen_all()
        
        # Generate JSON report
        if format == 'json':
            report = {
                'api': {
                    'name': self.api.name,
                    'molecular_weight': self.api.molecular_weight,
                    'melting_point': self.api.melting_point,
                    'glass_transition_temp': self.api.glass_transition_temp,
                    'log_p': self.api.log_p
                },
                'drug_loading': self.drug_loading,
                'results': {}
            }
            
            for polymer_name, result in self.results.items():
                polymer_result = {}
                
                # Copy result without formulation object
                for key, value in result.items():
                    if key != 'formulation':
                        polymer_result[key] = value
                
                report['results'][polymer_name] = polymer_result
            
            return report
        
        # Generate Markdown report
        elif format == 'markdown':
            # Get rankings
            stability_ranking = self.rank_by_stability()
            miscibility_ranking = self.rank_by_miscibility()
            
            # Begin report
            report = f"# Polymer Screening Report for {self.api.name}\n\n"
            
            # API information
            report += "## API Information\n\n"
            report += f"- **Name**: {self.api.name}\n"
            report += f"- **Molecular Weight**: {self.api.molecular_weight:.2f} g/mol\n" if self.api.molecular_weight else ""
            report += f"- **Melting Point**: {self.api.melting_point:.1f}°C\n" if self.api.melting_point else ""
            report += f"- **Glass Transition Temperature**: {self.api.glass_transition_temp:.1f}°C\n" if self.api.glass_transition_temp else ""
            report += f"- **LogP**: {self.api.log_p:.2f}\n" if self.api.log_p else ""
            report += f"- **Drug Loading**: {self.drug_loading:.1%}\n\n"
            
            # Top polymers
            report += "## Top Polymers by Stability\n\n"
            report += "| Rank | Polymer | Stability Score | Miscibility Score | Tg (°C) | Shelf Life (months) |\n"
            report += "|------|---------|----------------|-------------------|---------|--------------------|\n"
            
            for i, (polymer_name, stability) in enumerate(stability_ranking[:5]):
                result = self.results[polymer_name]
                miscibility = result.get('miscibility', 'N/A')
                tg = result.get('glass_transition_temp', 'N/A')
                shelf_life = result.get('shelf_life_estimate', 'N/A')
                
                report += f"| {i+1} | {polymer_name} | {stability:.2f} | {miscibility:.2f} | {tg:.1f} | {shelf_life} |\n"
            
            report += "\n"
            
            # Detailed results
            report += "## Detailed Results\n\n"
            
            for polymer_name, result in self.results.items():
                if 'error' in result:
                    report += f"### {polymer_name}\n\n"
                    report += f"Error: {result['error']}\n\n"
                    continue
                
                report += f"### {polymer_name}\n\n"
                report += f"- **Stability Score**: {result.get('stability', 'N/A'):.2f}\n"
                report += f"- **Thermodynamic Stability**: {result.get('thermodynamic_stability', 'N/A'):.2f}\n"
                report += f"- **Kinetic Stability**: {result.get('kinetic_stability', 'N/A'):.2f}\n"
                report += f"- **Miscibility Score**: {result.get('miscibility', 'N/A'):.2f}\n"
                report += f"- **Glass Transition Temperature**: {result.get('glass_transition_temp', 'N/A'):.1f}°C\n"
                report += f"- **Estimated Shelf Life**: {result.get('shelf_life_estimate', 'N/A')} months\n\n"
            
            # Recommendations
            report += "## Recommendations\n\n"
            
            if stability_ranking:
                top_polymer_name, top_stability = stability_ranking[0]
                
                report += f"Based on the screening results, **{top_polymer_name}** is the most promising polymer "
                report += f"for forming a stable ASD with {self.api.name} at {self.drug_loading:.1%} drug loading.\n\n"
                
                # Add recommendations based on stability
                if top_stability < 0.5:
                    report += "**Warning**: Even the top polymer has a relatively low stability score. "
                    report += "Consider reducing the drug loading or exploring alternative formulation approaches.\n\n"
                elif top_stability < 0.7:
                    report += "The top polymer shows moderate stability. "
                    report += "Consider optimizing the formulation further, such as adjusting the drug loading "
                    report += "or adding stabilizing excipients.\n\n"
                else:
                    report += "The top polymer shows good stability potential. "
                    report += "Proceed with experimental verification and optimization.\n\n"
                
                # Polymer comparison
                if len(stability_ranking) >= 2:
                    second_polymer_name, second_stability = stability_ranking[1]
                    
                    if abs(top_stability - second_stability) < 0.1:
                        report += f"Note that **{second_polymer_name}** shows similar stability potential "
                        report += f"({second_stability:.2f} vs {top_stability:.2f}). "
                        report += "Consider evaluating both polymers experimentally.\n\n"
            
            # Additional considerations
            report += "### Additional Considerations\n\n"
            report += "- **Experimental Verification**: Computational predictions should be verified experimentally.\n"
            report += "- **Process Optimization**: Manufacturing process parameters can significantly affect ASD stability.\n"
            report += "- **Drug Loading Optimization**: Consider optimizing the drug loading for the selected polymer.\n"
            report += "- **Stability Testing**: Conduct stability studies under various conditions to validate predictions.\n"
            
            return report
        
        else:
            # This should not happen due to the validation at the beginning
            raise ValueError(f"Invalid format: {format}")
    
    def __str__(self) -> str:
        """Return a string representation of the PolymerScreener object."""
        return f"PolymerScreener(API: {self.api.name}, Polymers: {len(self.polymers)}, Drug Loading: {self.drug_loading:.1%})"