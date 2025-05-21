"""
File I/O utilities for the ASDii library.

This module provides utility functions for file input/output operations.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import os
import json
import pickle
import logging
import csv
import yaml
import tempfile

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logging.warning("Pandas not available. Some file I/O functionality will be limited.")


def save_json(data: Dict[str, Any], file_path: str, indent: int = 2) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data (dict): Data to save
        file_path (str): Path to save the file
        indent (int, optional): Indentation level for the JSON file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Save data
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
        
        return True
    except Exception as e:
        logging.error(f"Failed to save JSON file: {e}")
        return False


def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load data from a JSON file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        dict or None: Loaded data, None if failed
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        logging.error(f"Failed to load JSON file: {e}")
        return None


def save_pickle(data: Any, file_path: str) -> bool:
    """
    Save data to a pickle file.
    
    Args:
        data: Data to save
        file_path (str): Path to save the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Save data
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
        
        return True
    except Exception as e:
        logging.error(f"Failed to save pickle file: {e}")
        return False


def load_pickle(file_path: str) -> Optional[Any]:
    """
    Load data from a pickle file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        Data from the pickle file, None if failed
    """
    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        return data
    except Exception as e:
        logging.error(f"Failed to load pickle file: {e}")
        return None


def save_csv(data: List[Dict[str, Any]], file_path: str, dialect: str = 'excel') -> bool:
    """
    Save data to a CSV file.
    
    Args:
        data (list): List of dictionaries to save
        file_path (str): Path to save the file
        dialect (str, optional): CSV dialect to use
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Check if data is empty
        if not data:
            logging.warning("No data to save.")
            return False
        
        # Get field names from the first dict
        fieldnames = list(data[0].keys())
        
        # Save data
        with open(file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, dialect=dialect)
            writer.writeheader()
            writer.writerows(data)
        
        return True
    except Exception as e:
        logging.error(f"Failed to save CSV file: {e}")
        return False


def load_csv(file_path: str, dialect: str = 'excel') -> Optional[List[Dict[str, str]]]:
    """
    Load data from a CSV file.
    
    Args:
        file_path (str): Path to the file
        dialect (str, optional): CSV dialect to use
        
    Returns:
        list or None: List of dictionaries with the CSV data, None if failed
    """
    try:
        with open(file_path, 'r', newline='') as f:
            reader = csv.DictReader(f, dialect=dialect)
            data = list(reader)
        
        return data
    except Exception as e:
        logging.error(f"Failed to load CSV file: {e}")
        return None


def load_csv_to_dataframe(file_path: str) -> Optional[Any]:
    """
    Load data from a CSV file into a pandas DataFrame.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        pandas.DataFrame or None: DataFrame with the CSV data, None if failed
    """
    if not PANDAS_AVAILABLE:
        logging.error("Pandas is required to load CSV to DataFrame.")
        return None
    
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        logging.error(f"Failed to load CSV to DataFrame: {e}")
        return None


def save_yaml(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save data to a YAML file.
    
    Args:
        data (dict): Data to save
        file_path (str): Path to save the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Save data
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        
        return True
    except Exception as e:
        logging.error(f"Failed to save YAML file: {e}")
        return False


def load_yaml(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load data from a YAML file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        dict or None: Loaded data, None if failed
    """
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return data
    except Exception as e:
        logging.error(f"Failed to load YAML file: {e}")
        return None


def create_temp_file(suffix: str = '.tmp', prefix: str = 'asdii_', content: Optional[str] = None) -> Optional[str]:
    """
    Create a temporary file.
    
    Args:
        suffix (str, optional): Suffix for the temporary file
        prefix (str, optional): Prefix for the temporary file
        content (str, optional): Content to write to the file
        
    Returns:
        str or None: Path to the temporary file, None if failed
    """
    try:
        # Create a temporary file
        fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        
        # Write content if provided
        if content is not None:
            with os.fdopen(fd, 'w') as f:
                f.write(content)
        else:
            os.close(fd)
        
        return temp_path
    except Exception as e:
        logging.error(f"Failed to create temporary file: {e}")
        return None


def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from a file path.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File extension (without the dot)
    """
    return os.path.splitext(file_path)[1][1:]


def is_file_type(file_path: str, extension: str) -> bool:
    """
    Check if a file has the specified extension.
    
    Args:
        file_path (str): Path to the file
        extension (str): Extension to check (without the dot)
        
    Returns:
        bool: True if the file has the specified extension, False otherwise
    """
    return get_file_extension(file_path).lower() == extension.lower()