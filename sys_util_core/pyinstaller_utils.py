"""
PyInstaller Utilities
PyInstaller 유틸리티

This module provides utility functions for converting Python scripts to executables using PyInstaller.
PyInstaller를 사용하여 파이썬 스크립트를 실행 파일로 변환하기 위한 유틸리티 함수들을 제공합니다.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple


class PyInstallerError(Exception):
    """
    Exception raised for PyInstaller operations.
    PyInstaller 작업 중 발생하는 예외
    """
    pass


def install_pyinstaller(venv_path: Optional[str] = None, 
                       version: Optional[str] = None,
                       upgrade: bool = False) -> Tuple[bool, str]:
    """
    Install PyInstaller in a virtual environment or globally.
    가상 환경 또는 전역에 PyInstaller를 설치합니다.
    
    Args:
        venv_path: Path to virtual environment (optional, uses global if None)
                   가상 환경 경로 (선택사항, None이면 전역)
        version: Specific version to install
                설치할 특정 버전
        upgrade: Upgrade if already installed
                이미 설치된 경우 업그레이드 여부
        
    Returns:
        Tuple of (success: bool, message: str)
        (성공 여부, 메시지) 튜플
        
    Raises:
        PyInstallerError: If installation fails
                         설치 실패 시
    """
    try:
        # Determine pip executable
        if venv_path:
            from . import venv_utils
            pip_exe = venv_utils.get_venv_pip(venv_path)
            if not pip_exe:
                raise PyInstallerError(f"pip not found in virtual environment at {venv_path}")
        else:
            pip_exe = 'pip'
        
        # Build command
        cmd = [pip_exe, 'install']
        
        if upgrade:
            cmd.append('--upgrade')
        
        if version:
            cmd.append(f'pyinstaller=={version}')
        else:
            cmd.append('pyinstaller')
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        return True, f"PyInstaller installed successfully: {result.stdout}"
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to install PyInstaller: {e.stderr}"
        raise PyInstallerError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error installing PyInstaller: {str(e)}"
        raise PyInstallerError(error_msg)


def check_pyinstaller_installed(venv_path: Optional[str] = None) -> bool:
    """
    Check if PyInstaller is installed.
    PyInstaller가 설치되어 있는지 확인합니다.
    
    Args:
        venv_path: Path to virtual environment (optional)
                   가상 환경 경로 (선택사항)
        
    Returns:
        True if PyInstaller is installed, False otherwise
        PyInstaller가 설치되어 있으면 True, 아니면 False
    """
    try:
        if venv_path:
            from . import venv_utils
            pip_exe = venv_utils.get_venv_pip(venv_path)
            if not pip_exe:
                return False
        else:
            pip_exe = 'pip'
        
        cmd = [pip_exe, 'show', 'pyinstaller']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return result.returncode == 0
        
    except Exception:
        return False


def build_exe(script_path: str,
             output_dir: Optional[str] = None,
             name: Optional[str] = None,
             onefile: bool = True,
             windowed: bool = False,
             icon: Optional[str] = None,
             console: bool = True,
             hidden_imports: Optional[List[str]] = None,
             additional_data: Optional[List[Tuple[str, str]]] = None,
             exclude_modules: Optional[List[str]] = None,
             venv_path: Optional[str] = None,
             clean: bool = False,
             spec_file: Optional[str] = None) -> Tuple[bool, str, str]:
    """
    Build an executable from a Python script using PyInstaller.
    PyInstaller를 사용하여 파이썬 스크립트에서 실행 파일을 빌드합니다.
    
    Args:
        script_path: Path to Python script
                    파이썬 스크립트 경로
        output_dir: Output directory for executable
                   실행 파일 출력 디렉토리
        name: Name for the executable
             실행 파일 이름
        onefile: Bundle everything into single file
                모든 것을 단일 파일로 번들
        windowed: Create windowed application (no console)
                 윈도우 응용프로그램 생성 (콘솔 없음)
        icon: Path to icon file (.ico on Windows, .icns on macOS)
             아이콘 파일 경로
        console: Show console window
                콘솔 창 표시
        hidden_imports: List of modules to include that PyInstaller might miss
                       PyInstaller가 놓칠 수 있는 모듈 목록
        additional_data: List of (source, dest) tuples for data files
                        데이터 파일을 위한 (소스, 대상) 튜플 목록
        exclude_modules: List of modules to exclude
                        제외할 모듈 목록
        venv_path: Path to virtual environment (optional)
                  가상 환경 경로 (선택사항)
        clean: Clean PyInstaller cache before building
              빌드 전 PyInstaller 캐시 정리
        spec_file: Use existing .spec file instead of generating one
                  새로 생성하는 대신 기존 .spec 파일 사용
        
    Returns:
        Tuple of (success: bool, output_path: str, message: str)
        (성공 여부, 출력 경로, 메시지) 튜플
        
    Raises:
        PyInstallerError: If build fails
                         빌드 실패 시
    """
    try:
        # Check if script exists
        if not os.path.exists(script_path):
            raise PyInstallerError(f"Script not found: {script_path}")
        
        # Check if PyInstaller is installed
        if not check_pyinstaller_installed(venv_path):
            raise PyInstallerError("PyInstaller is not installed. Please install it first.")
        
        # Determine PyInstaller executable
        if venv_path:
            from . import venv_utils
            if sys.platform == 'win32':
                pyinstaller_exe = os.path.join(venv_path, 'Scripts', 'pyinstaller.exe')
            else:
                pyinstaller_exe = os.path.join(venv_path, 'bin', 'pyinstaller')
            
            if not os.path.exists(pyinstaller_exe):
                raise PyInstallerError(f"PyInstaller executable not found at {pyinstaller_exe}")
        else:
            pyinstaller_exe = 'pyinstaller'
        
        # Build command
        if spec_file:
            if not os.path.exists(spec_file):
                raise PyInstallerError(f"Spec file not found: {spec_file}")
            cmd = [pyinstaller_exe, spec_file]
        else:
            cmd = [pyinstaller_exe]
            
            # Add script path
            cmd.append(script_path)
            
            # Add options
            if onefile:
                cmd.append('--onefile')
            
            if windowed or not console:
                cmd.append('--windowed')
            
            if name:
                cmd.extend(['--name', name])
            
            if icon and os.path.exists(icon):
                cmd.extend(['--icon', icon])
            
            if output_dir:
                cmd.extend(['--distpath', output_dir])
            
            if hidden_imports:
                for module in hidden_imports:
                    cmd.extend(['--hidden-import', module])
            
            if additional_data:
                for src, dst in additional_data:
                    cmd.extend(['--add-data', f'{src}{os.pathsep}{dst}'])
            
            if exclude_modules:
                for module in exclude_modules:
                    cmd.extend(['--exclude-module', module])
            
            if clean:
                cmd.append('--clean')
        
        # Run PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Determine output path
        if output_dir:
            dist_dir = output_dir
        else:
            dist_dir = 'dist'
        
        exe_name = name if name else Path(script_path).stem
        if sys.platform == 'win32':
            exe_name += '.exe'
        
        if onefile:
            output_path = os.path.join(dist_dir, exe_name)
        else:
            output_path = os.path.join(dist_dir, exe_name)
        
        return True, output_path, f"Executable built successfully: {result.stdout}"
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to build executable: {e.stderr}"
        raise PyInstallerError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error building executable: {str(e)}"
        raise PyInstallerError(error_msg)


def generate_spec_file(script_path: str,
                      output_path: Optional[str] = None,
                      onefile: bool = True,
                      windowed: bool = False,
                      icon: Optional[str] = None,
                      hidden_imports: Optional[List[str]] = None,
                      additional_data: Optional[List[Tuple[str, str]]] = None,
                      venv_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Generate a PyInstaller .spec file without building.
    빌드하지 않고 PyInstaller .spec 파일을 생성합니다.
    
    Args:
        script_path: Path to Python script
                    파이썬 스크립트 경로
        output_path: Path for the .spec file
                    .spec 파일 경로
        onefile: Bundle everything into single file
                모든 것을 단일 파일로 번들
        windowed: Create windowed application
                 윈도우 응용프로그램 생성
        icon: Path to icon file
             아이콘 파일 경로
        hidden_imports: List of hidden imports
                       숨겨진 임포트 목록
        additional_data: List of (source, dest) tuples
                        (소스, 대상) 튜플 목록
        venv_path: Path to virtual environment
                  가상 환경 경로
        
    Returns:
        Tuple of (success: bool, spec_file_path: str)
        (성공 여부, spec 파일 경로) 튜플
        
    Raises:
        PyInstallerError: If spec file generation fails
                         spec 파일 생성 실패 시
    """
    try:
        # Check if PyInstaller is installed
        if not check_pyinstaller_installed(venv_path):
            raise PyInstallerError("PyInstaller is not installed.")
        
        # Determine PyInstaller executable
        if venv_path:
            if sys.platform == 'win32':
                pyi_makespec = os.path.join(venv_path, 'Scripts', 'pyi-makespec.exe')
            else:
                pyi_makespec = os.path.join(venv_path, 'bin', 'pyi-makespec')
        else:
            pyi_makespec = 'pyi-makespec'
        
        # Build command
        cmd = [pyi_makespec, script_path]
        
        if onefile:
            cmd.append('--onefile')
        
        if windowed:
            cmd.append('--windowed')
        
        if icon:
            cmd.extend(['--icon', icon])
        
        if hidden_imports:
            for module in hidden_imports:
                cmd.extend(['--hidden-import', module])
        
        if additional_data:
            for src, dst in additional_data:
                cmd.extend(['--add-data', f'{src}{os.pathsep}{dst}'])
        
        # Run pyi-makespec
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Determine spec file path
        script_name = Path(script_path).stem
        spec_file = f"{script_name}.spec"
        
        if output_path:
            shutil.move(spec_file, output_path)
            spec_file = output_path
        
        return True, spec_file
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to generate spec file: {e.stderr}"
        raise PyInstallerError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error generating spec file: {str(e)}"
        raise PyInstallerError(error_msg)


def clean_build_files(script_path: Optional[str] = None,
                     remove_dist: bool = False,
                     remove_build: bool = True,
                     remove_spec: bool = False) -> Tuple[bool, str]:
    """
    Clean PyInstaller build artifacts.
    PyInstaller 빌드 아티팩트를 정리합니다.
    
    Args:
        script_path: Path to script (for finding .spec file)
                    스크립트 경로 (spec 파일 찾기용)
        remove_dist: Remove dist directory
                    dist 디렉토리 제거
        remove_build: Remove build directory
                     build 디렉토리 제거
        remove_spec: Remove .spec file
                    .spec 파일 제거
        
    Returns:
        Tuple of (success: bool, message: str)
        (성공 여부, 메시지) 튜플
    """
    try:
        removed = []
        
        if remove_build and os.path.exists('build'):
            shutil.rmtree('build')
            removed.append('build')
        
        if remove_dist and os.path.exists('dist'):
            shutil.rmtree('dist')
            removed.append('dist')
        
        if remove_spec and script_path:
            spec_file = f"{Path(script_path).stem}.spec"
            if os.path.exists(spec_file):
                os.remove(spec_file)
                removed.append(spec_file)
        
        if removed:
            return True, f"Removed: {', '.join(removed)}"
        else:
            return True, "No build files found to remove"
        
    except Exception as e:
        return False, f"Error cleaning build files: {str(e)}"


def get_pyinstaller_version(venv_path: Optional[str] = None) -> Optional[str]:
    """
    Get the installed PyInstaller version.
    설치된 PyInstaller 버전을 가져옵니다.
    
    Args:
        venv_path: Path to virtual environment (optional)
                   가상 환경 경로 (선택사항)
        
    Returns:
        Version string or None if not installed
        버전 문자열 또는 설치되지 않은 경우 None
    """
    try:
        if venv_path:
            from . import venv_utils
            pip_exe = venv_utils.get_venv_pip(venv_path)
            if not pip_exe:
                return None
        else:
            pip_exe = 'pip'
        
        cmd = [pip_exe, 'show', 'pyinstaller']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
        
        return None
        
    except Exception:
        return None


def analyze_script(script_path: str, 
                  venv_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Analyze a Python script to see what PyInstaller will include.
    파이썬 스크립트를 분석하여 PyInstaller가 포함할 항목을 확인합니다.
    
    Args:
        script_path: Path to Python script
                    파이썬 스크립트 경로
        venv_path: Path to virtual environment (optional)
                  가상 환경 경로 (선택사항)
        
    Returns:
        Tuple of (success: bool, analysis: str)
        (성공 여부, 분석 결과) 튜플
        
    Raises:
        PyInstallerError: If analysis fails
                         분석 실패 시
    """
    try:
        if not os.path.exists(script_path):
            raise PyInstallerError(f"Script not found: {script_path}")
        
        # Determine PyInstaller executable
        if venv_path:
            if sys.platform == 'win32':
                pyi_archive = os.path.join(venv_path, 'Scripts', 'pyi-archive_viewer.exe')
            else:
                pyi_archive = os.path.join(venv_path, 'bin', 'pyi-archive_viewer')
        else:
            pyi_archive = 'pyi-archive_viewer'
        
        # For now, just return imports analysis
        import ast
        with open(script_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=script_path)
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        analysis = f"Detected imports in {script_path}:\n"
        analysis += "\n".join(f"  - {imp}" for imp in sorted(set(imports)))
        
        return True, analysis
        
    except Exception as e:
        error_msg = f"Failed to analyze script: {str(e)}"
        raise PyInstallerError(error_msg)


def build_from_requirements(script_path: str,
                           requirements_file: str,
                           venv_path: str,
                           output_dir: Optional[str] = None,
                           **build_options) -> Tuple[bool, str, str]:
    """
    Create a venv, install requirements, and build executable all in one step.
    가상 환경을 생성하고 requirements를 설치한 후 실행 파일을 빌드합니다.
    
    Args:
        script_path: Path to Python script
                    파이썬 스크립트 경로
        requirements_file: Path to requirements.txt
                          requirements.txt 경로
        venv_path: Path for virtual environment
                  가상 환경 경로
        output_dir: Output directory for executable
                   실행 파일 출력 디렉토리
        **build_options: Additional options for build_exe
                        build_exe를 위한 추가 옵션
        
    Returns:
        Tuple of (success: bool, exe_path: str, message: str)
        (성공 여부, 실행 파일 경로, 메시지) 튜플
        
    Raises:
        PyInstallerError: If any step fails
                         단계 실패 시
    """
    try:
        from . import venv_utils
        
        messages = []
        
        # Create virtual environment
        success, msg = venv_utils.create_venv(venv_path)
        if not success:
            raise PyInstallerError(f"Failed to create venv: {msg}")
        messages.append(msg)
        
        # Install requirements
        success, msg = venv_utils.install_package(
            venv_path, 
            package_name='',  # Not used when requirements_file is provided
            requirements_file=requirements_file
        )
        if not success:
            raise PyInstallerError(f"Failed to install requirements: {msg}")
        messages.append(msg)
        
        # Install PyInstaller
        success, msg = install_pyinstaller(venv_path)
        if not success:
            raise PyInstallerError(f"Failed to install PyInstaller: {msg}")
        messages.append(msg)
        
        # Build executable
        success, exe_path, msg = build_exe(
            script_path,
            output_dir=output_dir,
            venv_path=venv_path,
            **build_options
        )
        if not success:
            raise PyInstallerError(f"Failed to build executable: {msg}")
        messages.append(msg)
        
        full_message = "\n".join(messages)
        return True, exe_path, full_message
        
    except Exception as e:
        error_msg = f"Failed in build_from_requirements: {str(e)}"
        raise PyInstallerError(error_msg)
