"""
Windows Registry Utilities
Windows 레지스트리 유틸리티

This module provides utility functions for Windows Registry operations.
Note: These functions only work on Windows systems.

Windows 레지스트리 작업을 위한 유틸리티 함수들을 제공합니다.
주의: 이 함수들은 Windows 시스템에서만 작동합니다.
"""

import sys
from typing import Optional, List, Tuple, Any

from sys_util_core.jsystems import CmdSystem, JLogger


# Check if winreg is available (Windows only)
if sys.platform == 'win32':
    import winreg
else:
    winreg = None


"""
@brief	Check if running on Windows. Windows에서 실행 중인지 확인합니다.
@return	True if Windows, False otherwise Windows이면 True, 아니면 False
"""
def is_windows() -> bool:
    return sys.platform == 'win32'


"""
@brief	Get a value from Windows Registry. Windows 레지스트리에서 값을 가져옵니다.
@param	key_path	Registry key path (e.g., 'Software\\Microsoft\\Windows') 레지스트리 키 경로 (예: 'Software\\Microsoft\\Windows')
@param	value_name	Name of the value to read 읽을 값의 이름
@param	root_key	Root registry key (default: HKEY_CURRENT_USER) 루트 레지스트리 키 (기본값: HKEY_CURRENT_USER)
@return	Registry value or None if error 레지스트리 값, 에러시 None
"""
def get_registry_value(
		key_path: str,
		value_name: str,
		root_key=None
 	) -> Optional[Any]:
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


"""
@brief	Set a value in Windows Registry. Windows 레지스트리에 값을 설정합니다.
@param	key_path	Registry key path 레지스트리 키 경로
@param	value_name	Name of the value to set 설정할 값의 이름
@param	value	    Value to set 설정할 값
@param	value_type	Registry value type (default: REG_SZ) 레지스트리 값 타입 (기본값: REG_SZ)
@param	root_key	Root registry key (default: HKEY_CURRENT_USER) 루트 레지스트리 키 (기본값: HKEY_CURRENT_USER)
@return	True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def set_registry_value(
		key_path: str,
		value_name: str,
		value: Any,
		value_type=None,
		root_key=None
 	) -> bool:
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


"""
@brief	Delete a value from Windows Registry. Windows 레지스트리에서 값을 삭제합니다.
@param	key_path	Registry key path 레지스트리 키 경로
@param	value_name	Name of the value to delete 삭제할 값의 이름
@param	root_key	Root registry key (default: HKEY_CURRENT_USER) 루트 레지스트리 키 (기본값: HKEY_CURRENT_USER)
@return	True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def delete_registry_value(
		key_path: str,
		value_name: str,
		root_key=None
 	) -> bool:
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


"""
@brief	Create a registry key. 레지스트리 키를 생성합니다.
@param	key_path	Registry key path to create 생성할 레지스트리 키 경로
@param	root_key	Root registry key (default: HKEY_CURRENT_USER) 루트 레지스트리 키 (기본값: HKEY_CURRENT_USER)
@return	True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def create_registry_key(key_path: str, root_key=None) -> bool:
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


"""
@brief	Delete a registry key. 레지스트리 키를 삭제합니다.
@param	key_path	Registry key path to delete 삭제할 레지스트리 키 경로
@param	root_key	Root registry key (default: HKEY_CURRENT_USER) 루트 레지스트리 키 (기본값: HKEY_CURRENT_USER)
@return	True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def delete_registry_key(key_path: str, root_key=None) -> bool:
    if not is_windows() or winreg is None:
        return False
    
    if root_key is None:
        root_key = winreg.HKEY_CURRENT_USER
    
    try:
        winreg.DeleteKey(root_key, key_path)
        return True
    except Exception:
        return False


"""
@brief	Check if a registry key exists. 레지스트리 키가 존재하는지 확인합니다.
@param	key_path	Registry key path 레지스트리 키 경로
@param	root_key	Root registry key (default: HKEY_CURRENT_USER) 루트 레지스트리 키 (기본값: HKEY_CURRENT_USER)
@return	True if exists, False otherwise 존재하면 True, 아니면 False
"""
def registry_key_exists(key_path: str, root_key=None) -> bool:
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


"""
@brief	List all subkeys of a registry key. 레지스트리 키의 모든 하위 키를 나열합니다.
@param	key_path	Registry key path 레지스트리 키 경로
@param	root_key	Root registry key (default: HKEY_CURRENT_USER) 루트 레지스트리 키 (기본값: HKEY_CURRENT_USER)
@return	List of subkey names 하위 키 이름 리스트
"""
def list_registry_subkeys(key_path: str, root_key=None) -> List[str]:
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


"""
@brief	List all values in a registry key. 레지스트리 키의 모든 값을 나열합니다.
@param	key_path	Registry key path 레지스트리 키 경로
@param	root_key	Root registry key (default: HKEY_CURRENT_USER) 루트 레지스트리 키 (기본값: HKEY_CURRENT_USER)
@return	List of tuples (value_name, value_data, value_type) (값 이름, 값 데이터, 값 타입) 튜플 리스트
"""
def list_registry_values(key_path: str, root_key=None) -> List[Tuple[str, Any, int]]:
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


"""
@brief	Get the name of a registry value type. 레지스트리 값 타입의 이름을 가져옵니다.
@param	type_code	Registry type code 레지스트리 타입 코드
@return	Type name as string 문자열로 된 타입 이름
"""
def get_registry_type_name(type_code: int) -> str:
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


"""
@brief	Export a registry key to a .reg file. 레지스트리 키를 .reg 파일로 내보냅니다.
@param	key_path	Registry key path to export 내보낼 레지스트리 키 경로
@param	output_file	Output file path 출력 파일 경로
@param	root_key	Root registry key (default: HKEY_CURRENT_USER) 루트 레지스트리 키 (기본값: HKEY_CURRENT_USER)
@return	True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def export_registry_key(
		key_path: str,
		output_file: str,
		root_key=None
 	) -> bool:
    if not is_windows():
        return False
    
    try:        
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
        
        cmd_ret: CmdSystem.Result = CmdSystem.run(['reg', 'export', full_path, output_file, '/y'])
        if cmd_ret.is_error():
            raise Exception(cmd_ret.stderr)
        return True
    except Exception as e:
        JLogger().log_error(f"Registry export failed: {e}")
        return False
