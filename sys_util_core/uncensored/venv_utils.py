"""
Virtual Environment Utilities
가상 환경 유틸리티

This module provides utility functions for managing Python virtual environments (.venv).
파이썬 가상 환경(.venv)을 관리하기 위한 유틸리티 함수들을 제공합니다.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict, Tuple

from sys_util_core.jsystems import CmdSystem, LogSystem

"""
@brief	Exception raised for virtual environment operations. 가상 환경 작업 중 발생하는 예외
"""
class VenvError(Exception): pass



"""
@brief  Create a Python virtual environment. 파이썬 가상 환경을 생성합니다.
@param  venv_path               Path where virtual environment will be created 가상 환경을 생성할 경로
@param  python_executable       Specific Python executable to use (optional) 사용할 특정 파이썬 실행 파일 (선택사항)
@param  system_site_packages    Give venv access to system site-packages 시스템 site-packages 접근 허용 여부
@param  clear                   Delete existing venv if it exists 기존 가상 환경이 있으면 삭제
@param  with_pip                Install pip in the virtual environment 가상 환경에 pip 설치 여부
@return Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
@throws VenvError: If virtual environment creation fails 가상 환경 생성 실패 시
"""
def create_venv(
        venv_path: str, 
        python_executable: Optional[str] = None, 
        system_site_packages: bool = False, 
        clear: bool = False,
        with_pip: bool = True
    ) -> Tuple[bool, str]:
    try:
        venv_path = os.path.abspath(venv_path)
        
        # Check if venv already exists
        if os.path.exists(venv_path) and not clear:
            return False, f"Virtual environment already exists at {venv_path}. Use clear=True to recreate."
        
        # Remove existing venv if clear is True
        if os.path.exists(venv_path) and clear:
            import shutil
            shutil.rmtree(venv_path)
        
        # Build command
        if python_executable:
            cmd = [python_executable, '-m', 'venv']
        else:
            cmd = [sys.executable, '-m', 'venv']
        
        if system_site_packages:
            cmd.append('--system-site-packages')
        
        if not with_pip:
            cmd.append('--without-pip')
        
        cmd.append(venv_path)
        
        # Create virtual environment
        cmd_ret: CmdSystem.Result = CmdSystem.run(cmd)
        if cmd_ret.is_error():
            raise Exception(cmd_ret.stderr)
        
        return True, f"Virtual environment created successfully at {venv_path}"
        
    except Exception as e:
        LogSystem.log_error(f"Unexpected error creating virtual environment: {str(e)}")
        return False, f"Failed to create virtual environment: {str(e)}"


"""
@brief Delete a virtual environment. 가상 환경을 삭제합니다.
@param venv_path    Path to virtual environment 가상 환경 경로
@return Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
@throws VenvError: If deletion fails 삭제 실패 시
"""
def delete_venv(venv_path: str) -> Tuple[bool, str]:
    try:
        venv_path = os.path.abspath(venv_path)
        
        if not os.path.exists(venv_path):
            return False, f"Virtual environment not found at {venv_path}"
        
        # Verify it's a virtual environment
        if not is_venv(venv_path):
            return False, f"Path {venv_path} does not appear to be a virtual environment"
        
        import shutil
        shutil.rmtree(venv_path)
        
        return True, f"Virtual environment deleted successfully from {venv_path}"
        
    except Exception as e:
        error_msg = f"Failed to delete virtual environment: {str(e)}"
        raise VenvError(error_msg)


"""
@brief Check if a directory is a virtual environment. 디렉토리가 가상 환경인지 확인합니다.
@param path     Path to check 확인할 경로
@return True if path is a virtual environment, False otherwise 가상 환경이면 True, 아니면 False
"""
def is_venv(path: str) -> bool:
    try:
        path = os.path.abspath(path)
        
        if not os.path.exists(path):
            return False
        
        # Check for common venv markers
        if sys.platform == 'win32':
            python_exe = os.path.join(path, 'Scripts', 'python.exe')
            activate_script = os.path.join(path, 'Scripts', 'activate.bat')
        else:
            python_exe = os.path.join(path, 'bin', 'python')
            activate_script = os.path.join(path, 'bin', 'activate')
        
        pyvenv_cfg = os.path.join(path, 'pyvenv.cfg')
        
        return (os.path.exists(python_exe) or os.path.exists(activate_script) 
                or os.path.exists(pyvenv_cfg))
        
    except Exception:
        return False


"""
@brief Get the Python executable path for a virtual environment. 가상 환경의 파이썬 실행 파일 경로를 가져옵니다.
@param venv_path    Path to virtual environment 가상 환경 경로
@return Path to Python executable or None if not found 파이썬 실행 파일 경로 또는 None
"""
def get_venv_python(venv_path: str) -> Optional[str]:
    try:
        venv_path = os.path.abspath(venv_path)
        
        if sys.platform == 'win32':
            python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
        else:
            python_exe = os.path.join(venv_path, 'bin', 'python')
        
        if os.path.exists(python_exe):
            return python_exe
        
        return None
        
    except Exception:
        return None


"""
@brief Get the pip executable path for a virtual environment. 가상 환경의 pip 실행 파일 경로를 가져옵니다.
@param venv_path    Path to virtual environment 가상 환경 경로
@return Path to pip executable or None if not found pip 실행 파일 경로 또는 None
"""
def get_venv_pip(venv_path: str) -> Optional[str]:
    try:
        venv_path = os.path.abspath(venv_path)
        
        if sys.platform == 'win32':
            pip_exe = os.path.join(venv_path, 'Scripts', 'pip.exe')
        else:
            pip_exe = os.path.join(venv_path, 'bin', 'pip')
        
        if os.path.exists(pip_exe):
            return pip_exe
        
        return None
        
    except Exception:
        return None


"""
@brief Install a package in a virtual environment. 가상 환경에 패키지를 설치합니다.
@param venv_path            Path to virtual environment 가상 환경 경로
@param package_name         Name of package to install 설치할 패키지 이름
@param version              Specific version to install (e.g., "1.2.3") 설치할 특정 버전
@param upgrade              Upgrade package if already installed 이미 설치된 경우 업그레이드 여부
@param requirements_file    Install from requirements.txt file requirements.txt 파일에서 설치
@return Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
@throws VenvError: If package installation fails 패키지 설치 실패 시
"""
def install_package(venv_path: str, package_name: str, 
                   version: Optional[str] = None,
                   upgrade: bool = False,
                   requirements_file: Optional[str] = None) -> Tuple[bool, str]:
    try:
        pip_exe = get_venv_pip(venv_path)
        
        if not pip_exe:
            raise VenvError(f"pip not found in virtual environment at {venv_path}")
        
        if requirements_file:
            if not os.path.exists(requirements_file):
                raise VenvError(f"Requirements file not found: {requirements_file}")
            cmd = [pip_exe, 'install', '-r', requirements_file]
        else:
            if version:
                package_spec = f"{package_name}=={version}"
            else:
                package_spec = package_name
            
            cmd = [pip_exe, 'install']
            
            if upgrade:
                cmd.append('--upgrade')
            
            cmd.append(package_spec)
        
        cmd_ret: CmdSystem.Result = CmdSystem.run(cmd)        
        if cmd_ret.is_error():
            raise Exception(cmd_ret.stderr)        
        return True, f"Package installed successfully: {cmd_ret.stdout}"
    except Exception as e:
        LogSystem.log_error(f"Unexpected error installing package: {str(e)}")
        return False, f"Unexpected error installing package: {str(e)}"


"""
@brief Uninstall a package from a virtual environment. 가상 환경에서 패키지를 제거합니다.
@param venv_path    Path to virtual environment 가상 환경 경로
@param package_name Name of package to uninstall 제거할 패키지 이름
@param yes          Automatically confirm uninstallation 자동으로 제거 확인
@return Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
@throws VenvError: If package uninstallation fails 패키지 제거 실패 시
"""
def uninstall_package(venv_path: str, package_name: str, 
                     yes: bool = True) -> Tuple[bool, str]:
    try:
        pip_exe = get_venv_pip(venv_path)
        
        if not pip_exe:
            raise VenvError(f"pip not found in virtual environment at {venv_path}")
        
        cmd = [pip_exe, 'uninstall']
        
        if yes:
            cmd.append('-y')
        
        cmd.append(package_name)
        
        cmd_ret: CmdSystem.Result = CmdSystem.run(cmd)
        if cmd_ret.is_error():
            raise Exception(cmd_ret.stderr)        
        return True, f"Package uninstalled successfully: {cmd_ret.stdout}"
    except Exception as e:
        LogSystem.log_error(f"Unexpected error uninstalling package: {str(e)}")
        return False, f"Unexpected error uninstalling package: {str(e)}"


"""
@brief List all installed packages in a virtual environment. 가상 환경에 설치된 모든 패키지를 나열합니다.
@param venv_path    Path to virtual environment 가상 환경 경로
@param format       Output format ('columns', 'freeze', 'json') 출력 형식
@return Tuple of (success: bool, output: str, packages: List[Dict]) (성공 여부, 출력, 패키지 목록) 튜플
@throws VenvError: If listing packages fails 패키지 목록 조회 실패 시
"""
def list_packages(venv_path: str, format: str = 'columns') -> Tuple[bool, str, List[Dict[str, str]]]:
    try:
        pip_exe = get_venv_pip(venv_path)
        
        if not pip_exe:
            raise VenvError(f"pip not found in virtual environment at {venv_path}")
        
        cmd = [pip_exe, 'list']
        
        if format == 'freeze':
            cmd = [pip_exe, 'freeze']
        elif format == 'json':
            cmd.append('--format=json')
        
        cmd_ret: CmdSystem.Result = CmdSystem.run(cmd)
        if cmd_ret.is_error():
            raise Exception(cmd_ret.stderr)
        if format == 'json':
            packages = json.loads(cmd_ret.stdout)        
        return True, cmd_ret.stdout, packages
    except Exception as e:
        LogSystem.log_error(f"Unexpected error listing packages: {str(e)}")
        return False, f"Unexpected error listing packages: {str(e)}", []


"""
@brief Upgrade pip in a virtual environment. 가상 환경의 pip를 업그레이드합니다.
@param venv_path    Path to virtual environment 가상 환경 경로
@return Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
@throws VenvError: If pip upgrade fails pip 업그레이드 실패 시
"""
def upgrade_pip(venv_path: str) -> Tuple[bool, str]:
    try:
        pip_exe = get_venv_pip(venv_path)
        
        if not pip_exe:
            raise VenvError(f"pip not found in virtual environment at {venv_path}")
        
        cmd = [pip_exe, 'install', '--upgrade', 'pip']
        
        cmd_ret: CmdSystem.Result = CmdSystem.run(cmd)        
        if cmd_ret.is_error():
            raise Exception(cmd_ret.stderr)
        
        return True, f"pip upgraded successfully: {cmd_ret.stdout}"
    except Exception as e:
        LogSystem.log_error(f"Unexpected error upgrading pip: {str(e)}")
        return False, f"Unexpected error upgrading pip: {str(e)}"


"""
@brief Get detailed information about an installed package. 설치된 패키지에 대한 상세 정보를 가져옵니다.
@param venv_path        Path to virtual environment 가상 환경 경로
@param package_name     Name of package 패키지 이름
@return Tuple of (success: bool, info: Dict) (성공 여부, 정보) 튜플
@throws VenvError: If getting package info fails 패키지 정보 조회 실패 시
"""
def get_package_info(venv_path: str, package_name: str) -> Tuple[bool, Dict[str, str]]:
    try:
        pip_exe = get_venv_pip(venv_path)
        
        if not pip_exe:
            raise VenvError(f"pip not found in virtual environment at {venv_path}")
        
        cmd = [pip_exe, 'show', package_name]
        
        cmd_ret: CmdSystem.Result = CmdSystem.run(cmd)
        if cmd_ret.is_error():
            raise Exception(cmd_ret.stderr)
        
        # Parse output into dictionary
        info = {}
        for line in cmd_ret.stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':')
                info[key.strip()] = value.strip()        
        return True, info
    except Exception as e:
        LogSystem.log_error(f"Unexpected error getting package info: {str(e)}")
        return False, {}


"""
@brief Export installed packages to a requirements.txt file. 설치된 패키지를 requirements.txt 파일로 내보냅니다.
@param venv_path    Path to virtual environment 가상 환경 경로
@param output_file  Path to output requirements.txt file 출력할 requirements.txt 파일 경로
@return Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
@throws VenvError: If freezing requirements fails requirements 내보내기 실패 시
"""
def freeze_requirements(venv_path: str, output_file: str) -> Tuple[bool, str]:
    try:
        pip_exe = get_venv_pip(venv_path)
        
        if not pip_exe:
            raise VenvError(f"pip not found in virtual environment at {venv_path}")
        
        cmd = [pip_exe, 'freeze']
        
        cmd_ret: CmdSystem.Result = CmdSystem.run(cmd, check=True)
        if cmd_ret.is_error():
            raise Exception(cmd_ret.stderr)
        with open(output_file, 'w') as f:
            f.write(cmd_ret.stdout)        
        return True, f"Requirements frozen to {output_file}"
    except Exception as e:
        LogSystem.log_error(f"Unexpected error freezing requirements: {str(e)}")
        return False, f"Unexpected error freezing requirements: {str(e)}"


"""
@brief Run a command inside a virtual environment. 가상 환경 내에서 명령을 실행합니다.
@param venv_path    Path to virtual environment 가상 환경 경로
@param command      Command to run (as list) 실행할 명령 (리스트)
@param cwd          Working directory for command 명령 실행 디렉토리
@return Tuple of (returncode, stdout, stderr) (반환 코드, 표준 출력, 표준 에러) 튜플
@throws VenvError: If command execution fails 명령 실행 실패 시
"""
def run_in_venv(
        venv_path: str, 
        command: List[str], 
        cwd: Optional[str] = None
    ) -> Tuple[int, str]:
    try:
        python_exe = get_venv_python(venv_path)
        
        if not python_exe:
            raise VenvError(f"Python not found in virtual environment at {venv_path}")
        
        # If command starts with 'python', replace with venv python
        # Create a copy to avoid modifying the caller's list
        cmd = command.copy()
        if cmd[0] in ['python', 'python3']:
            cmd[0] = python_exe
        
        cmd_ret: CmdSystem.Result = CmdSystem.run(cmd, cwd=cwd)
        if cmd_ret.is_error():
            raise Exception(cmd_ret.stderr)        
        return cmd_ret        
    except Exception as e:
        LogSystem.log_error(f"Failed to run command in venv: {str(e)}")
        return -1, f"Error: {str(e)}"


"""
@brief Get information about a virtual environment. 가상 환경에 대한 정보를 가져옵니다.
@param venv_path    Path to virtual environment 가상 환경 경로
@return Dictionary with venv information 가상 환경 정보를 담은 딕셔너리
"""
def get_venv_info(venv_path: str) -> Dict[str, str]:
    try:
        venv_path = os.path.abspath(venv_path)
        
        info = {
            'path': venv_path,
            'exists': os.path.exists(venv_path),
            'is_venv': is_venv(venv_path),
            'python': get_venv_python(venv_path),
            'pip': get_venv_pip(venv_path),
        }
        
        # Read pyvenv.cfg if available
        pyvenv_cfg = os.path.join(venv_path, 'pyvenv.cfg')
        if os.path.exists(pyvenv_cfg):
            with open(pyvenv_cfg, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=')
                        info[key.strip()] = value.strip()
        
        return info
        
    except Exception as e:
        return {
            'path': venv_path,
            'error': str(e)
        }


"""
@brief Get both Python and pip executable paths for a virtual environment. 가상 환경의 Python과 pip 실행 파일 경로를 함께 가져옵니다.
@param venv_path    Path to virtual environment 가상 환경 경로
@return Tuple of (python_exe: Optional[str], pip_exe: Optional[str]) paths, or (None, None) if not found (Python 실행 파일 경로, pip 실행 파일 경로) 튜플 또는 (None, None)
"""
def venv_paths(venv_path: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        return get_venv_python(venv_path), get_venv_pip(venv_path)
    except Exception:
        return None, None


"""
@brief Install requirements from a requirements.txt file. requirements.txt 파일에서 의존성을 설치합니다.
@param venv_path        Path to virtual environment 가상 환경 경로
@param requirements_file    Path to requirements.txt file requirements.txt 파일 경로
@return Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
@throws VenvError: If requirements installation fails requirements 설치 실패 시
"""
def install_requirements(venv_path: str, requirements_file: str) -> Tuple[bool, str]:
    try:
        if not os.path.exists(requirements_file):
            return False, f"Requirements file not found: {requirements_file}"
        
        pip_exe = get_venv_pip(venv_path)
        
        if not pip_exe:
            raise VenvError(f"pip not found in virtual environment at {venv_path}")
        
        cmd = [pip_exe, 'install', '-r', requirements_file]
        
        cmd_ret: CmdSystem.Result = CmdSystem.run(cmd)
        if cmd_ret.is_error():
            raise Exception(cmd_ret.stderr)        
        return True, f"Requirements installed successfully: {cmd_ret.stdout}"
    except Exception as e:
        LogSystem.log_error(f"Unexpected error installing requirements: {str(e)}")
        return False, f"Unexpected error installing requirements: {str(e)}"

"""
@brief Ensure PyInstaller is installed in the virtual environment. 가상 환경에 PyInstaller가 설치되어 있는지 확인하고 설치합니다.
@param venv_path    Path to virtual environment 가상 환경 경로
@param version      Specific version to install (optional) 설치할 특정 버전 (선택사항)
@return Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
@throws VenvError: If PyInstaller installation fails PyInstaller 설치 실패 시
"""
def ensure_pyinstaller(venv_path: str, version: Optional[str] = None) -> Tuple[bool, str]:
    try:
        pip_exe = get_venv_pip(venv_path)
        
        if not pip_exe:
            raise VenvError(f"pip not found in virtual environment at {venv_path}")
        
        cmd = [pip_exe, 'install', '--upgrade']
        
        if version:
            cmd.append(f'pyinstaller=={version}')
        else:
            cmd.append('pyinstaller')
        
        cmd_ret: CmdSystem.Result = CmdSystem.run(cmd)
        if cmd_ret.is_error():
            raise Exception(cmd_ret.stderr)
        return True, f"PyInstaller ensured in virtual environment: {cmd_ret.stdout}"
    except Exception as e:
        LogSystem.log_error(f"Unexpected error ensuring PyInstaller: {str(e)}")
        return False, f"Unexpected error ensuring PyInstaller: {str(e)}"


"""
@brief Clean PyInstaller build directories. PyInstaller 빌드 디렉토리를 정리합니다.
@param build_dir        Build directory to remove (default: 'build') 제거할 빌드 디렉토리 (기본값: 'build')
@param pycache_dir      Python cache directory to remove (default: '__pycache__') 제거할 Python 캐시 디렉토리 (기본값: '__pycache__')
@param dist_dir         Dist directory (default: 'dist') dist 디렉토리 (기본값: 'dist')
@param preserve_dist    Whether to preserve the dist directory dist 디렉토리 보존 여부 (기본값: True)
@return Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
"""
def clean_build_dirs(build_dir: str = 'build', 
                    pycache_dir: str = '__pycache__',
                    dist_dir: str = 'dist',
                    preserve_dist: bool = True
    ) -> Tuple[bool, str]:
    try:
        import shutil
        removed = []
        
        # Remove build directory
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
            removed.append(build_dir)
        
        # Remove __pycache__ directory
        if os.path.exists(pycache_dir):
            shutil.rmtree(pycache_dir)
            removed.append(pycache_dir)
        
        # Optionally remove dist directory
        if not preserve_dist and os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
            removed.append(dist_dir)
        
        if removed:
            return True, f"Removed directories: {', '.join(removed)}"
        else:
            return True, "No build directories found to remove"
        
    except Exception as e:
        error_msg = f"Failed to clean build directories: {str(e)}"
        return False, error_msg
