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
import re
from pathlib import Path
from typing import Optional, Dict, List, Union

from sys_util_core import file_utils


def generate_env_name_from_main_script(prefix: Optional[str] = None, suffix: Optional[str] = None) -> str:
    main_file_path, main_file_name, file_extension = file_utils.FileSystem.get_main_script_path_name_extension()
    return f"{f'{prefix}_' if prefix else ''}{main_file_name}{f'_{suffix}' if suffix else ''}"

def generate_env_name_from_current_script(prefix: Optional[str] = None, suffix: Optional[str] = None) -> str:
    current_file_path, current_file_name, file_extension = file_utils.FileSystem.get_current_script_path_name_extension(2)
    return f"{f'{prefix}_' if prefix else ''}{current_file_name}{f'_{suffix}' if suffix else ''}"

def get_global_env_path_by_key(key: Optional[str] = None) -> Optional[Dict[str, str]]:
    """
    @brief	Get system-wide environment variables (Windows only). 시스템 전체 환경 변수를 가져옵니다 (Windows 전용).
    @return	Dictionary of system environment variables 시스템 환경 변수 딕셔너리
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
                        
            if key:
                env_vars = {key: env_vars.get(key, '')}
            else:
                pass # return all env vars

        except Exception:
            pass

    if key is None or not os.path.isdir(os.environ.get(key)):
        file_utils.LogSystem.log_error(f"환경변수 'path_jfw_py'에 py_sys_script 폴더 경로가 세팅되어 있지 않거나, 경로가 잘못되었습니다.")
        sys.exit(1)

    return env_vars if env_vars else None

def get_global_env_keys_by_path(path: str) -> Optional[List[str]]:    
    env_keys = []
    
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
                    if len(parts) >= 3 and parts[2] == path: # parts[2] is value
                        env_keys.append(parts[0])  # parts[0] is key, parts[1] is type
                    
        except Exception:
            pass

    return env_keys if env_keys else None

def extract_registry_value(query_output: str) -> Optional[str]:
    for line in query_output.splitlines():
        if 'REG_' in line:
            parts = line.split(None, 2)
            if len(parts) >= 3:
                return parts[2]
    return None

def is_env_var_set(scope, key, value = None) -> bool:
    query = extract_registry_value(subprocess.run(['reg', 'query', scope, '/v', key], capture_output=True, text=True).stdout)
    if value == None:
        if query != None:
            os.environ[key] = query
            return True
        else:
            return False
    else:
        if query == value:
            os.environ[key] = value
            return True
        else:
            return False
    
def set_global_env_pair(
    key: str,
    value: str,
    global_scope: bool = True,
    permanent: bool = True,
    ) -> bool:
    """
    @brief	Set an environment variable. 환경 변수를 설정합니다.
    @param	var_name	Name of the environment variable 환경 변수 이름
    @param	value	    Value to set 설정할 값
    @param	permanent	Whether to set permanently (system-wide) 영구적으로 설정할지 여부 (시스템 전체)
    @param	user_scope	Whether to set in user scope (True) or system scope (False) 유저 범위에 설정할지 (True) 시스템 범위에 설정할지 (False)
    @return	True if successful, False otherwise 성공하면 True, 실패하면 False
    """
    try:        
        if permanent:
            if sys.platform == 'win32':
                scope = 'HKCU\\Environment' if not global_scope else 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'
                subprocess.run(['reg', 'add', scope, '/v', key, '/t', 'REG_SZ', '/d', value, '/f'], capture_output=True, check=True)
                is_env_var_set(scope, key, value)
            else:
                # On Unix-like systems, would need to modify shell config files
                shell_config = os.path.expanduser('~/.bashrc') if not global_scope else '/etc/environment'
                with open(shell_config, 'a') as f:
                    f.write(f'\nexport {key}="{value}"\n')
        
            return True
        
    except Exception:
        return False
    
def clear_global_env_pair_by_key_or_pairs(keys: Union[List[str], str], global_scope: bool = True, permanent: bool = True) -> bool:
    """
    @brief	Delete global system-wide environment variables by dictionary or single key. 딕셔너리나 단일 키를 받아 시스템 전체 환경 변수를 삭제합니다.
    @param	keys	Dictionary of environment variables or a single key to delete 삭제할 환경 변수 딕셔너리 또는 단일 키
    @return	True if all deletions are successful, False otherwise 모두 성공하면 True, 하나라도 실패하면 False
    """
    try:
        if permanent:
            if sys.platform == 'win32':
                if isinstance(keys, list):
                    keys_to_delete = keys
                elif isinstance(keys, str):
                    keys_to_delete = [keys]
                else:
                    return False

                for key in keys_to_delete:
                    scope = 'HKCU\\Environment' if not global_scope else 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'
                    subprocess.run(['reg', 'delete', scope, '/v', key, '/f'], capture_output=True, check=True)
            else:
                # On Unix-like systems, modify shell config files
                shell_config = os.path.expanduser('~/.bashrc')
                with open(shell_config, 'r') as f:
                    lines = f.readlines()
                with open(shell_config, 'w') as f:
                    for line in lines:
                        if isinstance(keys, dict):
                            if not any(line.strip().startswith(f'export {key}=') for key in keys.keys()):
                                f.write(line)
                        elif isinstance(keys, str):
                            if not line.strip().startswith(f'export {keys}='):
                                f.write(line)
            return True
        else:
            return False # TODO: implement for non-permanent env var deletion
    
    except Exception as e:
        file_utils.LogSystem.log_error(f"Failed to clear env vars: {e}")
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
            
            # 환경변수와 하드코드 경로가 논리적으로 같으면 하드코드 경로는 제거
            seen = set()
            entry_var_map = {}
            unique_entries = []
            for entry in path_entries:
                if '%' in entry:
                    # Extract variable name from patterns like %VAR% or %VAR%/bin or %VAR%\something
                    match = re.search(r'%([^%]+)%', entry)
                    if match:
                        var_name = match.group(1)
                        var_value = os.environ.get(var_name, None)
                        if var_value:
                            resolved_path = entry.replace(f'%{var_name}%', var_value)
                            if resolved_path.lower() not in seen:
                                entry_var_map[entry] = resolved_path
                                seen.add(resolved_path.lower())
                                unique_entries.append(entry)
                        else:
                            file_utils.LogSystem.log_error(f"Environment variable '{var_name}' not found for entry '{entry}'")
            for entry in path_entries:
                if '%' not in entry and entry.lower() not in seen:
                    seen.add(entry.lower())
                    unique_entries.append(entry)
            
            # Sort the entries based on the defined priorities
            def sort_env_key(entry):  # SystemRoot and System32 should always come first
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
            sorted_entries = sorted(unique_entries, key=sort_env_key)
            
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
        file_utils.LogSystem.log_error(f"Failed to add {key} to Path: {e}")
        return False

def ensure_global_env_pair(key: str, value: str, global_scope: bool = True, permanent: bool = True) -> bool:
    """
    @brief	Ensure a global system-wide environment variable is set. 시스템 전체 환경 변수가 설정되어 있는지 확인합니다.
    @param	key	Name of the environment variable 환경 변수 이름
    @param	value	Value to set 설정할 값
    @param	permanent	Whether to set permanently (system-wide) 영구적으로 설정할지 여부 (시스템 전체)
    @return	True if successful, False otherwise 성공하면 True, 실패하면 False
    """
    try:        
        dict_check_reg_value_key = get_global_env_keys_by_path(value) # dictionary of key-value pairs
        if dict_check_reg_value_key is None:
            varialbe_ok = set_global_env_pair(key, value, global_scope, permanent)    
        elif len(dict_check_reg_value_key) == 1 and key in dict_check_reg_value_key:
            varialbe_ok = True
            pass
        else: # multiple and different keys with same value
            varialbe_ok = clear_global_env_pair_by_key_or_pairs(dict_check_reg_value_key) and \
            set_global_env_pair(key, value, global_scope, permanent)

        to_path_ok = ensure_global_env_pair_to_Path(key, value, global_scope, permanent)

        success_ = varialbe_ok and to_path_ok
        file_utils.LogSystem.log_info(f"환경변수 '{key}' 설정 {'성공' if success_ else '실패'}")    
        return success_
    
    except Exception as e:
        file_utils.LogSystem.log_error(f"환경변수 '{key}' 설정 실패: {e}")
        return False
    
def set_python_env_path(global_env_path: Optional[str] = None,
                      package_name: str = "sys_util_core",
                      max_up_levels: int = 8,
                      dll_subpath: Optional[str] = None) -> bool:
    # If already importable, nothing to do
    if package_name in sys.modules:
        return True

    candidate_root = None

    # 1) explicit global_env_path
    if global_env_path:
        p = Path(global_env_path).expanduser().resolve()
        if (p / package_name).exists():
            candidate_root = p
        else:
            # allow global_env_path to point directly to package folder
            if Path(global_env_path).name == package_name and Path(global_env_path).exists():
                candidate_root = Path(global_env_path).resolve().parent

    # 2) env var
    if candidate_root is None:
        env = os.environ.get("SYS_UTIL_CORE_PATH") or os.environ.get("PY_SYS_UTIL_CORE")
        if env:
            p = Path(env).expanduser().resolve()
            if (p / package_name).exists() or p.name == package_name:
                candidate_root = p if (p / package_name).exists() else p.parent

    # 3) search upwards from cwd and this file's dir
    if candidate_root is None:
        starts = [Path.cwd(), Path(__file__).resolve().parent]
        for start in starts:
            cur = start.resolve()
            for _ in range(max_up_levels):
                if (cur / package_name).exists():
                    candidate_root = cur
                    break
                if cur.parent == cur:
                    break
                cur = cur.parent
            if candidate_root:
                break

    if candidate_root is None:
        # not found; don't modify sys.path silently — raise helpful ImportError
        raise ImportError(
            f"Could not find '{package_name}' folder. "
            "Set SYS_UTIL_CORE_PATH env var, pass global_env_path, or place this script near your project."
        )

    root_str = str(candidate_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    # Optional: add DLL lookup directory on Windows (Python 3.8+)
    if dll_subpath and os.name == "nt":
        dll_dir = candidate_root.joinpath(dll_subpath).resolve()
        if dll_dir.exists():
            try:
                os.add_dll_directory(str(dll_dir))
            except Exception:
                # os.add_dll_directory may not be available on very old Python versions
                pass


