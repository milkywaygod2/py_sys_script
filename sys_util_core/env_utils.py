"""
Environment Variable Utilities
환경 변수 유틸리티

This module provides utility functions for managing environment variables.
환경 변수를 관리하기 위한 유틸리티 함수들을 제공합니다.
"""
import os
import sys
import subprocess
import inspect

from typing import Optional, Dict, List, Union

from sys_util_core import cmd_utils


def generate_env_var_name_from_this_file(prefix: str = "path_", suffix: Optional[str] = None) -> str:
    # Get the caller's file path
    caller_frame = inspect.stack()[1]  # The caller's stack frame
    caller_file = caller_frame.filename  # The caller's file path

    # Extract the file name and extension
    current_file_name, file_extension = os.path.splitext(os.path.basename(caller_file))
    file_extension = file_extension.lstrip('.')  # Remove the leading dot from the extension

    # Use the provided suffix or default to the file extension
    suffix = suffix or file_extension
    return f"{prefix}{current_file_name}_{suffix}"

"""
@brief	Get system-wide environment variables (Windows only). 시스템 전체 환경 변수를 가져옵니다 (Windows 전용).
@return	Dictionary of system environment variables 시스템 환경 변수 딕셔너리
"""
def get_global_env_path_by_key(key: Optional[str] = None) -> Optional[Dict[str, str]]:
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
                        
            if key:
                env_vars = {key: env_vars.get(key, '')}
            else:
                pass # return all env vars

        except Exception:
            pass

    if key is None or not os.path.isdir(key):
        cmd_utils.print_error(f"환경변수 'path_jfw_py'에 py_sys_script 폴더 경로가 세팅되어 있지 않거나, 경로가 잘못되었습니다.")
        sys.exit(1)

    return env_vars if env_vars else None

def get_global_env_keys_by_path(path: str) -> Optional[Dict[str, str]]:    
    env_keys = {}
    
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
                    if len(parts) >= 3 and parts[2] == path:
                        env_keys[parts[0]] = parts[2]  # Add matching key-value pair to the dictionary
                    
        except Exception:
            pass

    return env_keys if env_keys else None

"""
@brief	Set an environment variable. 환경 변수를 설정합니다.
@param	var_name	Name of the environment variable 환경 변수 이름
@param	value	    Value to set 설정할 값
@param	permanent	Whether to set permanently (system-wide) 영구적으로 설정할지 여부 (시스템 전체)
@param	user_scope	Whether to set in user scope (True) or system scope (False) 유저 범위에 설정할지 (True) 시스템 범위에 설정할지 (False)
@return	True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def set_global_env_pair(
    key: str,
    value: str,
    global_scope: bool = True,
    permanent: bool = True,
    ) -> bool:
    try:        
        if permanent:
            if sys.platform == 'win32':
                scope = 'HKCU\\Environment' if not global_scope else 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'
                subprocess.run(['reg', 'add', scope, '/v', key, '/t', 'REG_SZ', '/d', value, '/f'], capture_output=True, check=True)
            else:
                # On Unix-like systems, would need to modify shell config files
                shell_config = os.path.expanduser('~/.bashrc') if not global_scope else '/etc/environment'
                with open(shell_config, 'a') as f:
                    f.write(f'\nexport {key}="{value}"\n')
        
            return True
        
    except Exception:
        return False
    
"""
@brief	Delete global system-wide environment variables by dictionary or single key. 딕셔너리나 단일 키를 받아 시스템 전체 환경 변수를 삭제합니다.
@param	env_input	Dictionary of environment variables or a single key to delete 삭제할 환경 변수 딕셔너리 또는 단일 키
@return	True if all deletions are successful, False otherwise 모두 성공하면 True, 하나라도 실패하면 False
"""
def clear_global_env_pair_by_key_or_pairs(env_input: Union[Dict[str, str], str]) -> bool:
    try:
        if sys.platform == 'win32':
            if isinstance(env_input, dict):
                keys_to_delete = env_input
            elif isinstance(env_input, str):
                keys_to_delete = [env_input]
            else:
                return False

            for key in keys_to_delete:
                subprocess.run(['reg', 'delete', 
                                'HKCU\\Environment', '/v', key, '/f'],
                                capture_output=True, check=True)
        else:
            # On Unix-like systems, modify shell config files
            shell_config = os.path.expanduser('~/.bashrc')
            with open(shell_config, 'r') as f:
                lines = f.readlines()
            with open(shell_config, 'w') as f:
                for line in lines:
                    if isinstance(env_input, dict):
                        if not any(line.strip().startswith(f'export {key}=') for key in env_input.keys()):
                            f.write(line)
                    elif isinstance(env_input, str):
                        if not line.strip().startswith(f'export {env_input}='):
                            f.write(line)
        
        return True
    
    except Exception:
        return False

def ensure_global_env_pair_to_Path(key: str, value: str, global_scope: bool = True, permanent: bool = True) -> bool:
    try:
        if sys.platform == 'win32':
            # Determine the registry scope
            scope = 'HKCU\\Environment' if not global_scope else 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'
            
            # Get the current Path value
            result = subprocess.run(
                ['reg', 'query', scope, '/v', 'Path'],
                capture_output=True,
                text=True,
                check=True
            )
            current_path = ""
            for line in result.stdout.splitlines():
                if "Path" in line:
                    current_path = line.split("    ")[-1].strip()
                    break

            # Remove hardcoded 'value' from the Path if present
            if value:
                new_path = current_path.replace(value, "").replace(";;", ";").strip(";")
            else:
                new_path = current_path

            # Append %key% to the Path if not already present
            if f"%{key}%" not in new_path:
                if not new_path:
                    new_path = f"%{key}%"
                else:
                    new_path = f"{new_path};%{key}%"

            # Auto-arrange Path entries
            path_entries = [entry.strip() for entry in new_path.split(";") if entry.strip()]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_entries = []
            for entry in path_entries:
                if entry not in seen:
                    seen.add(entry)
                    unique_entries.append(entry)
            
            def sort_key(entry):  # SystemRoot and System32 should always come first
                if entry.lower() == "%systemroot%":
                    return (0, entry)
                elif entry.lower() == "%systemroot%\\system32":
                    return (1, entry)
                elif entry.lower().startswith("%systemroot%"):
                    return (2, entry)  # Other SystemRoot-related paths
                elif entry.startswith("%"): #and entry.endswith("%"):
                    return (4, entry)  # Environment variables last
                else:
                    return (3, entry)  # Custom paths in the middle
            
            # Sort the entries based on the defined priorities
            sorted_entries = sorted(unique_entries, key=sort_key)
            
            # Join the sorted entries back into a single string
            new_path = ";".join(sorted_entries)

            # Update the Path variable
            subprocess.run(
                ['reg', 'add', scope, '/v', 'Path', '/t', 'REG_SZ', '/d', new_path, '/f'],
                capture_output=True,
                check=True
            )
        else:
            # Unix-like systems: Modify ~/.bashrc or equivalent
            shell_config = os.path.expanduser('~/.bashrc') if not global_scope else '/etc/environment'
            with open(shell_config, 'r') as f:
                lines = f.readlines()
            with open(shell_config, 'a') as f:
                if f'export PATH="$PATH:${key}"' not in lines:
                    f.write(f'\nexport PATH="$PATH:${key}"\n')

        return True
    
    except Exception as e:
        cmd_utils.print_error(f"Failed to add {key} to Path: {e}")
        return False

"""
@brief	Ensure a global system-wide environment variable is set. 시스템 전체 환경 변수가 설정되어 있는지 확인합니다.
@param	key	Name of the environment variable 환경 변수 이름
@param	value	Value to set 설정할 값
@param	permanent	Whether to set permanently (system-wide) 영구적으로 설정할지 여부 (시스템 전체)
@return	True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def ensure_global_env_pair(key: str, value: str, global_scope: bool = True, permanent: bool = True) -> bool:
    try:        
        dict_check_reg_key_value = get_global_env_keys_by_path(value) # dictionary of key-value pairs
        if dict_check_reg_key_value is None:
            varialbe_ok = set_global_env_pair(key, value, global_scope, permanent)    
        elif len(dict_check_reg_key_value) == 1 and key in dict_check_reg_key_value:
            varialbe_ok = True
            pass
        else: # multiple and different keys with same value
            varialbe_ok = clear_global_env_pair_by_key_or_pairs(dict_check_reg_key_value) and \
            set_global_env_pair(key, value, global_scope, permanent)

        to_path_ok = ensure_global_env_pair_to_Path(key, value, global_scope, permanent)
        return varialbe_ok and to_path_ok
    
    except Exception:
        return False