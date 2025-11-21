"""
Environment Variable Utilities
환경 변수 유틸리티

This module provides utility functions for managing environment variables.
환경 변수를 관리하기 위한 유틸리티 함수들을 제공합니다.
"""

import os
import sys
import subprocess
from typing import Optional, Dict, List, Union

from sys_util_core import cmd_utils


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
@return	True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def set_global_env_pair(
        key: str,
        value: str,
        permanent: bool = True
    ) -> bool:
    try:        
        if permanent:
            if sys.platform == 'win32':
                subprocess.run(['setx', key, value], capture_output=True, check=True)
            else:
                # On Unix-like systems, would need to modify shell config files
                shell_config = os.path.expanduser('~/.bashrc')
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
def delete_global_env_pair_by_key_or_pairs(env_input: Union[Dict[str, str], str]) -> bool:
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


"""
@brief	Ensure a global system-wide environment variable is set. 시스템 전체 환경 변수가 설정되어 있는지 확인합니다.
@param	key	Name of the environment variable 환경 변수 이름
@param	value	Value to set 설정할 값
@param	permanent	Whether to set permanently (system-wide) 영구적으로 설정할지 여부 (시스템 전체)
@return	True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def ensure_global_env_pair(key: str, value: str = os.path.dirname(os.path.abspath(__file__)), permanent: bool = True) -> bool:
    try:        
        dict_check_reg_key_value = get_global_env_keys_by_path(value) # dictionary of key-value pairs
        if dict_check_reg_key_value is None:
            set_global_env_pair(key, value, permanent=permanent)    
        elif len(dict_check_reg_key_value) == 1 and key in dict_check_reg_key_value:
            pass
        else: # multiple and different keys with same value
            delete_global_env_pair_by_key_or_pairs(dict_check_reg_key_value)
            set_global_env_pair(key, value, permanent=permanent)        
        return True
    
    except Exception:
        return False