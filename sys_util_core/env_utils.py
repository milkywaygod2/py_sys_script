"""
Environment Variable Utilities

This module provides utility functions for managing environment variables.
"""

import os
import sys
import subprocess
from typing import Optional, Dict, List


def get_env_var(var_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get the value of an environment variable.
    
    Args:
        var_name: Name of the environment variable
        default: Default value if variable doesn't exist
        
    Returns:
        Value of the environment variable or default
    """
    return os.environ.get(var_name, default)


def set_env_var(var_name: str, value: str, permanent: bool = False) -> bool:
    """
    Set an environment variable.
    
    Args:
        var_name: Name of the environment variable
        value: Value to set
        permanent: Whether to set permanently (system-wide)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.environ[var_name] = value
        
        if permanent:
            if sys.platform == 'win32':
                # Set permanently on Windows using setx
                subprocess.run(['setx', var_name, value], 
                             capture_output=True, check=True)
            else:
                # On Unix-like systems, would need to modify shell config files
                # This is a simplified version
                shell_config = os.path.expanduser('~/.bashrc')
                with open(shell_config, 'a') as f:
                    f.write(f'\nexport {var_name}="{value}"\n')
        
        return True
    except Exception:
        return False


def delete_env_var(var_name: str, permanent: bool = False) -> bool:
    """
    Delete an environment variable.
    
    Args:
        var_name: Name of the environment variable
        permanent: Whether to delete permanently
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if var_name in os.environ:
            del os.environ[var_name]
        
        if permanent and sys.platform == 'win32':
            # Delete from Windows registry
            subprocess.run(['reg', 'delete', 
                          'HKCU\\Environment', '/v', var_name, '/f'],
                         capture_output=True)
        
        return True
    except Exception:
        return False


def get_all_env_vars() -> Dict[str, str]:
    """
    Get all environment variables as a dictionary.
    
    Returns:
        Dictionary of all environment variables
    """
    return dict(os.environ)


def env_var_exists(var_name: str) -> bool:
    """
    Check if an environment variable exists.
    
    Args:
        var_name: Name of the environment variable
        
    Returns:
        True if exists, False otherwise
    """
    return var_name in os.environ


def get_path_variable() -> List[str]:
    """
    Get the PATH environment variable as a list of directories.
    
    Returns:
        List of directories in PATH
    """
    path = os.environ.get('PATH', '')
    separator = ';' if sys.platform == 'win32' else ':'
    return [p for p in path.split(separator) if p]


def add_to_path(directory: str, permanent: bool = False, 
                position: str = 'end') -> bool:
    """
    Add a directory to the PATH environment variable.
    
    Args:
        directory: Directory to add
        permanent: Whether to add permanently
        position: 'start' or 'end' of PATH
        
    Returns:
        True if successful, False otherwise
    """
    try:
        directory = os.path.abspath(directory)
        path_list = get_path_variable()
        
        if directory in path_list:
            return True
        
        separator = ';' if sys.platform == 'win32' else ':'
        
        if position == 'start':
            path_list.insert(0, directory)
        else:
            path_list.append(directory)
        
        new_path = separator.join(path_list)
        os.environ['PATH'] = new_path
        
        if permanent:
            if sys.platform == 'win32':
                subprocess.run(['setx', 'PATH', new_path],
                             capture_output=True, check=True)
            else:
                shell_config = os.path.expanduser('~/.bashrc')
                with open(shell_config, 'a') as f:
                    f.write(f'\nexport PATH="{directory}:$PATH"\n')
        
        return True
    except Exception:
        return False


def remove_from_path(directory: str, permanent: bool = False) -> bool:
    """
    Remove a directory from the PATH environment variable.
    
    Args:
        directory: Directory to remove
        permanent: Whether to remove permanently
        
    Returns:
        True if successful, False otherwise
    """
    try:
        directory = os.path.abspath(directory)
        path_list = get_path_variable()
        
        if directory not in path_list:
            return True
        
        path_list.remove(directory)
        separator = ';' if sys.platform == 'win32' else ':'
        new_path = separator.join(path_list)
        os.environ['PATH'] = new_path
        
        if permanent and sys.platform == 'win32':
            subprocess.run(['setx', 'PATH', new_path],
                         capture_output=True, check=True)
        
        return True
    except Exception:
        return False


def expand_env_vars(text: str) -> str:
    """
    Expand environment variables in a string.
    
    Args:
        text: Text containing environment variable references
        
    Returns:
        Text with expanded variables
    """
    return os.path.expandvars(text)


def get_system_env_vars() -> Dict[str, str]:
    """
    Get system-wide environment variables (Windows only).
    
    Returns:
        Dictionary of system environment variables
    """
    env_vars = {}
    
    if sys.platform == 'win32':
        try:
            result = subprocess.run(
                ['reg', 'query', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if 'REG_' in line:
                    parts = line.split(None, 2)
                    if len(parts) >= 3:
                        env_vars[parts[0]] = parts[2]
        except Exception:
            pass
    
    return env_vars
