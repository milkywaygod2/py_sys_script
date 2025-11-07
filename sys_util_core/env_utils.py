"""
Environment Variable Utilities
환경 변수 유틸리티

This module provides utility functions for managing environment variables.
환경 변수를 관리하기 위한 유틸리티 함수들을 제공합니다.
"""

import os
import sys
import subprocess
from typing import Optional, Dict, List


"""
@brief  Get the value of an environment variable. 환경 변수의 값을 가져옵니다.
@param  var_name Name of the environment variable 환경 변수 이름
@param  default Default value if variable doesn't exist 변수가 존재하지 않을 때 기본값
@return  Value of the environment variable or default 환경 변수 값 또는 기본값
"""
def get_env_var(var_name: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(var_name, default)


"""
@brief  Set an environment variable. 환경 변수를 설정합니다.
@param  var_name Name of the environment variable 환경 변수 이름
@param  value Value to set 설정할 값
@param  permanent Whether to set permanently (system-wide) 영구적으로 설정할지 여부 (시스템 전체)
@return  True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def set_env_var(var_name: str, value: str, permanent: bool = False) -> bool:
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


"""
@brief  Delete an environment variable. 환경 변수를 삭제합니다.
@param  var_name Name of the environment variable 환경 변수 이름
@param  permanent Whether to delete permanently 영구적으로 삭제할지 여부
@return  True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def delete_env_var(var_name: str, permanent: bool = False) -> bool:
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


"""
@brief  Get all environment variables as a dictionary. 모든 환경 변수를 딕셔너리로 가져옵니다.
@return  Dictionary of all environment variables 모든 환경 변수 딕셔너리
"""
def get_all_env_vars() -> Dict[str, str]:
    return dict(os.environ)


"""
@brief  Check if an environment variable exists. 환경 변수가 존재하는지 확인합니다.
@param  var_name Name of the environment variable 환경 변수 이름
@return  True if exists, False otherwise 존재하면 True, 아니면 False
"""
def env_var_exists(var_name: str) -> bool:
    return var_name in os.environ


"""
@brief  Get the PATH environment variable as a list of directories. PATH 환경 변수를 디렉토리 리스트로 가져옵니다.
@return  List of directories in PATH PATH에 있는 디렉토리 리스트
"""
def get_path_variable() -> List[str]:
    path = os.environ.get('PATH', '')
    separator = ';' if sys.platform == 'win32' else ':'
    return [p for p in path.split(separator) if p]

def add_env_var(name, value, user=True):
    # 등록만 (새로운 프로세스에는 바로 반영 안됨)
    import winreg
    reg_path = r"Environment" if user else r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER if user else winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
        key.Close()
    except Exception as e:
        print_error(f"{name} 환경변수 등록 실패: {e}")

def ensure_path_env(vcpkg_path):
    env = os.environ.get("Path", "")
    if vcpkg_path.lower() in [p.strip().lower() for p in env.split(";")]:
        return
    new_env = f"{env};{vcpkg_path}"
    add_env_var("Path", new_env)

"""
@brief  Add a directory to the PATH environment variable. PATH 환경 변수에 디렉토리를 추가합니다.
@param  directory Directory to add 추가할 디렉토리
@param  permanent Whether to add permanently 영구적으로 추가할지 여부
@param  position 'start' or 'end' of PATH PATH의 '시작' 또는 '끝' 위치
@return  True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def add_to_path(directory: str, permanent: bool = False, 
                position: str = 'end') -> bool:
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


"""
@brief  Remove a directory from the PATH environment variable. PATH 환경 변수에서 디렉토리를 제거합니다.
@param  directory Directory to remove 제거할 디렉토리
@param  permanent Whether to remove permanently 영구적으로 제거할지 여부
@return  True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def remove_from_path(directory: str, permanent: bool = False) -> bool:
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


"""
@brief  Expand environment variables in a string. 문자열 내의 환경 변수를 확장합니다.
@param  text Text containing environment variable references 환경 변수 참조를 포함한 텍스트
@return  Text with expanded variables 환경 변수가 확장된 텍스트
"""
def expand_env_vars(text: str) -> str:
    return os.path.expandvars(text)


"""
@brief  Get system-wide environment variables (Windows only). 시스템 전체 환경 변수를 가져옵니다 (Windows 전용).
@return  Dictionary of system environment variables 시스템 환경 변수 딕셔너리
"""
def get_system_env_vars() -> Dict[str, str]:
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
