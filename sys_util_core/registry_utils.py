"""
Windows Registry Utilities

This module provides utility functions for Windows Registry operations.
Note: These functions only work on Windows systems.
"""

import sys
from typing import Optional, List, Tuple, Any


# Check if winreg is available (Windows only)
if sys.platform == 'win32':
    import winreg
else:
    winreg = None


def is_windows() -> bool:
    """
    Check if running on Windows.
    
    Returns:
        True if Windows, False otherwise
    """
    return sys.platform == 'win32'


def get_registry_value(key_path: str, value_name: str, 
                       root_key=None) -> Optional[Any]:
    """
    Get a value from Windows Registry.
    
    Args:
        key_path: Registry key path (e.g., 'Software\\Microsoft\\Windows')
        value_name: Name of the value to read
        root_key: Root registry key (default: HKEY_CURRENT_USER)
        
    Returns:
        Registry value or None if error
    """
    if not is_windows() or winreg is None:
        return None
    
    if root_key is None:
        root_key = winreg.HKEY_CURRENT_USER
    
    try:
        key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        return value
    except Exception:
        return None


def set_registry_value(key_path: str, value_name: str, value: Any,
                       value_type=None, root_key=None) -> bool:
    """
    Set a value in Windows Registry.
    
    Args:
        key_path: Registry key path
        value_name: Name of the value to set
        value: Value to set
        value_type: Registry value type (default: REG_SZ)
        root_key: Root registry key (default: HKEY_CURRENT_USER)
        
    Returns:
        True if successful, False otherwise
    """
    if not is_windows() or winreg is None:
        return False
    
    if root_key is None:
        root_key = winreg.HKEY_CURRENT_USER
    
    if value_type is None:
        value_type = winreg.REG_SZ
    
    try:
        key = winreg.CreateKey(root_key, key_path)
        winreg.SetValueEx(key, value_name, 0, value_type, value)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def delete_registry_value(key_path: str, value_name: str,
                          root_key=None) -> bool:
    """
    Delete a value from Windows Registry.
    
    Args:
        key_path: Registry key path
        value_name: Name of the value to delete
        root_key: Root registry key (default: HKEY_CURRENT_USER)
        
    Returns:
        True if successful, False otherwise
    """
    if not is_windows() or winreg is None:
        return False
    
    if root_key is None:
        root_key = winreg.HKEY_CURRENT_USER
    
    try:
        key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_WRITE)
        winreg.DeleteValue(key, value_name)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def create_registry_key(key_path: str, root_key=None) -> bool:
    """
    Create a registry key.
    
    Args:
        key_path: Registry key path to create
        root_key: Root registry key (default: HKEY_CURRENT_USER)
        
    Returns:
        True if successful, False otherwise
    """
    if not is_windows() or winreg is None:
        return False
    
    if root_key is None:
        root_key = winreg.HKEY_CURRENT_USER
    
    try:
        key = winreg.CreateKey(root_key, key_path)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def delete_registry_key(key_path: str, root_key=None) -> bool:
    """
    Delete a registry key.
    
    Args:
        key_path: Registry key path to delete
        root_key: Root registry key (default: HKEY_CURRENT_USER)
        
    Returns:
        True if successful, False otherwise
    """
    if not is_windows() or winreg is None:
        return False
    
    if root_key is None:
        root_key = winreg.HKEY_CURRENT_USER
    
    try:
        winreg.DeleteKey(root_key, key_path)
        return True
    except Exception:
        return False


def registry_key_exists(key_path: str, root_key=None) -> bool:
    """
    Check if a registry key exists.
    
    Args:
        key_path: Registry key path
        root_key: Root registry key (default: HKEY_CURRENT_USER)
        
    Returns:
        True if exists, False otherwise
    """
    if not is_windows() or winreg is None:
        return False
    
    if root_key is None:
        root_key = winreg.HKEY_CURRENT_USER
    
    try:
        key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def list_registry_subkeys(key_path: str, root_key=None) -> List[str]:
    """
    List all subkeys of a registry key.
    
    Args:
        key_path: Registry key path
        root_key: Root registry key (default: HKEY_CURRENT_USER)
        
    Returns:
        List of subkey names
    """
    if not is_windows() or winreg is None:
        return []
    
    if root_key is None:
        root_key = winreg.HKEY_CURRENT_USER
    
    subkeys = []
    
    try:
        key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ)
        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkeys.append(subkey_name)
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except Exception:
        pass
    
    return subkeys


def list_registry_values(key_path: str, root_key=None) -> List[Tuple[str, Any, int]]:
    """
    List all values in a registry key.
    
    Args:
        key_path: Registry key path
        root_key: Root registry key (default: HKEY_CURRENT_USER)
        
    Returns:
        List of tuples (value_name, value_data, value_type)
    """
    if not is_windows() or winreg is None:
        return []
    
    if root_key is None:
        root_key = winreg.HKEY_CURRENT_USER
    
    values = []
    
    try:
        key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ)
        i = 0
        while True:
            try:
                value_tuple = winreg.EnumValue(key, i)
                values.append(value_tuple)
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except Exception:
        pass
    
    return values


def get_registry_type_name(type_code: int) -> str:
    """
    Get the name of a registry value type.
    
    Args:
        type_code: Registry type code
        
    Returns:
        Type name as string
    """
    if not is_windows() or winreg is None:
        return "UNKNOWN"
    
    type_names = {
        winreg.REG_BINARY: "REG_BINARY",
        winreg.REG_DWORD: "REG_DWORD",
        winreg.REG_DWORD_LITTLE_ENDIAN: "REG_DWORD_LITTLE_ENDIAN",
        winreg.REG_DWORD_BIG_ENDIAN: "REG_DWORD_BIG_ENDIAN",
        winreg.REG_EXPAND_SZ: "REG_EXPAND_SZ",
        winreg.REG_LINK: "REG_LINK",
        winreg.REG_MULTI_SZ: "REG_MULTI_SZ",
        winreg.REG_NONE: "REG_NONE",
        winreg.REG_SZ: "REG_SZ",
    }
    
    return type_names.get(type_code, "UNKNOWN")


def export_registry_key(key_path: str, output_file: str,
                        root_key=None) -> bool:
    """
    Export a registry key to a .reg file.
    
    Args:
        key_path: Registry key path to export
        output_file: Output file path
        root_key: Root registry key (default: HKEY_CURRENT_USER)
        
    Returns:
        True if successful, False otherwise
    """
    if not is_windows():
        return False
    
    try:
        import subprocess
        
        root_names = {
            winreg.HKEY_CURRENT_USER: "HKCU",
            winreg.HKEY_LOCAL_MACHINE: "HKLM",
            winreg.HKEY_CLASSES_ROOT: "HKCR",
            winreg.HKEY_USERS: "HKU",
            winreg.HKEY_CURRENT_CONFIG: "HKCC",
        }
        
        if root_key is None:
            root_key = winreg.HKEY_CURRENT_USER
        
        root_name = root_names.get(root_key, "HKCU")
        full_path = f"{root_name}\\{key_path}"
        
        subprocess.run(['reg', 'export', full_path, output_file, '/y'],
                      capture_output=True, check=True)
        return True
    except Exception:
        return False
