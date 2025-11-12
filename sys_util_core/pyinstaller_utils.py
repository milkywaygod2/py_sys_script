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

"""
@brief	Exception raised for PyInstaller operations. PyInstaller 작업 중 발생하는 예외
"""
class PyInstallerError(Exception):
    pass

"""
@brief	Install pip globally. pip를 전역에 설치합니다.
@return	True if pip is successfully installed, False otherwise pip가 성공적으로 설치되면 True, 아니면 False
"""
def install_pip() -> bool:
    try:
        if subprocess.run([sys.executable, '-m', 'ensurepip', '--upgrade'], capture_output=True, text=True).returncode == 0:
            return subprocess.run(['pip', '--version'], capture_output=True, text=True).returncode == 0
        else:
            return False
    except Exception:
        return False

"""
@brief	Install PyInstaller globally. PyInstaller를 전역에 설치합니다.
@param	version	    Specific version to install (optional) 설치할 특정 버전 (선택사항)
@param	upgrade	    Upgrade if already installed (default: False) 이미 설치된 경우 업그레이드 여부 (기본값: False)
@return	Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
@throws	PyInstallerError: If installation fails 설치 실패 시
"""
def install_pyinstaller(
        upgrade: bool = False,
        version: Optional[str] = None,
    ) -> bool:
    try:
        # check if pip is installed
        if not check_cmd_installed('pip'):
            raise PyInstallerError("pip is not installed. Please install pip first.")
        else:
            # call install by pip
            cmd = ['pip', 'install']

            # mandatory re-install with latest version flag
            if upgrade:
                cmd.append('--upgrade')

            # mandatory install specific version or latest
            if version:
                cmd.append(f'pyinstaller=={version}')
            else:
                cmd.append('pyinstaller')

            return subprocess.run(cmd, capture_output=True, text=True, check=True).returncode == 0

    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to install PyInstaller: {e.stderr}"
        raise PyInstallerError(error_msg)

    except Exception as e:
        error_msg = f"Unexpected error installing PyInstaller: {str(e)}"
        raise PyInstallerError(error_msg)

"""
@brief	Check if a command-line tool is installed, and install it if not. 명령줄 도구가 설치되어 있는지 확인하고, 없으면 설치합니다.
@return	True if the tool is installed or successfully installed, False otherwise 도구가 설치되어 있거나 성공적으로 설치되면 True, 아니면 False
"""
def check_cmd_installed(package_name: Optional[str]) -> bool:
    try:        
        cmd = [package_name, '--version']
        return subprocess.run(cmd, capture_output=True, text=True).returncode == 0  # 0 means installed (terminal code)
    
    except FileNotFoundError:  # Command not found
        if package_name == 'pip':
            return install_pip(upgrade=True)
        elif package_name == 'pyinstaller':
            return install_pyinstaller(upgrade=True)
        return False  # For other tools, automatic installation is not supported
    
    except Exception:  # Other unexpected errors
        return False
    
"""
@brief	Build an executable from a Python script using PyInstaller. PyInstaller를 사용하여 파이썬 스크립트에서 실행 파일을 빌드합니다.
@param	path_script	    Path to Python script to build 빌드할 파이썬 스크립트 경로 (str)
@param	path_icon	    Path to icon file (.ico on Windows, .icns on macOS) 아이콘 파일 경로 (.ico Windows, .icns macOS) (Optional[str])
@param	path_rsc	    List of (srcpath, dest_rel) tuples for data files; OS-specific separator is handled automatically OS별 구분자가 자동으로 처리되는 데이터 파일을 위한 (srcpath, dest_rel) 튜플 목록
@param	onefile	        Bundle everything into single file 모든 것을 단일 파일로 번들 (default: True)
@param	console	    Create windowed application (no console) 윈도우 응용프로그램 생성 (콘솔 없음) (default: False)
@param	path_py	        Path to Python executable 파이썬 실행 파일 경로 (Optional[str], None이면 현재 인터프리터 사용)
@return	None (prints output and calls subprocess directly)
@throws	subprocess.CalledProcessError: If build fails 빌드 실패 시
"""
def build_exe_with_pyinstaller(
        path_script: str,
        path_icon: Optional[str] = None,
        path_rsc: Optional[List[Tuple[str, str]]] = None,
        onefile: bool = True,
        console: bool = True,
        path_py: Optional[str] = None,
    ) -> None:
    # python -m PyInstaller --onefile (--console) (--icon /icon.ico) (--add-data /pathRsc:tempName) /pathTarget.py

    try:
        # Python executable
        c_path_py = Path(path_py) if path_py else Path(sys.executable)

        if not c_path_py.exists():
            raise FileNotFoundError(f"Python executable not found: {c_path_py}")
        
        cmd = [str(c_path_py), "-m", "PyInstaller"]

        # onefile option
        cmd.append("--onefile" if onefile else "--onedir")

        # icon option
        c_path_icon = Path(path_icon) if path_icon else None
        if c_path_icon:
            if not c_path_icon.exists():
                raise FileNotFoundError(f"Icon file not found: {c_path_icon}")
            else:
                cmd += ["--icon", str(c_path_icon)]
        
        # console option
        if not console:
            cmd.append("--noconsole")

        if path_rsc:
            seperator = os.pathsep # Use os.pathsep for  ';' separator on Windows, ':' on other OS, PyInstaller's --add-data uses
            for src, dst in path_rsc:
                cmd += ["--add-data", f"{src}{seperator}{dst}"]

        # script path
        c_path_script = Path(path_script)
        if not c_path_script.exists():
            raise FileNotFoundError(f"Script not found: {c_path_script}")
        else:
           cmd.append(str(c_path_script))

        # Run PyInstaller
        if not check_cmd_installed('pyinstaller'):
            raise PyInstallerError("PyInstaller is not installed. Please install it first.")
        else:
            print("[INFO] running:", " ".join(cmd))
            subprocess.run(cmd)
            print("[INFO] PyInstaller finished")

        ####################################################################
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
            cmd.append(path_script)
            
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
        
        exe_name = name if name else Path(path_script).stem
        if sys.platform == 'win32':
            exe_name += '.exe'
        
        if onefile:
            output_path = os.path.join(dist_dir, exe_name)
        else:
            # For onedir builds, the executable is in a subdirectory
            # Use the name parameter if provided, otherwise script stem
            dir_name = name if name else Path(path_script).stem
            output_path = os.path.join(dist_dir, dir_name, exe_name)
        
        return True, output_path, f"Executable built successfully: {result.stdout}"
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to build executable: {e.stderr}"
        raise PyInstallerError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error building executable: {str(e)}"
        raise PyInstallerError(error_msg)
    
    
    

"""
@brief	Build an executable from a Python script using PyInstaller. PyInstaller를 사용하여 파이썬 스크립트에서 실행 파일을 빌드합니다.
@param	path_script	    Path to Python script 파이썬 스크립트 경로
@param	output_dir	    Output directory for executable 실행 파일 출력 디렉토리
@param	name	        Name for the executable 실행 파일 이름
@param	onefile	        Bundle everything into single file 모든 것을 단일 파일로 번들
@param	windowed	    Create windowed application (no console) 윈도우 응용프로그램 생성 (콘솔 없음)
@param	icon	        Path to icon file (.ico on Windows, .icns on macOS) 아이콘 파일 경로
@param	console	        Show console window 콘솔 창 표시
@param	hidden_imports	List of modules to include that PyInstaller might miss PyInstaller가 놓칠 수 있는 모듈 목록
@param	additional_data	List of (source, dest) tuples for data files 데이터 파일을 위한 (소스, 대상) 튜플 목록
@param	exclude_modules	List of modules to exclude 제외할 모듈 목록
@param	venv_path	    Path to virtual environment (optional) 가상 환경 경로 (선택사항)
@param	clean	Clean   PyInstaller cache before building 빌드 전 PyInstaller 캐시 정리
@param	spec_file	    Use existing .spec file instead of generating one 새로 생성하는 대신 기존 .spec 파일 사용
@return	Tuple of (success: bool, output_path: str, message: str) (성공 여부, 출력 경로, 메시지) 튜플
@throws	PyInstallerError: If build fails 빌드 실패 시
"""
def build_exe(
		path_script: str,
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
		spec_file: Optional[str] = None
 	) -> Tuple[bool, str, str]:
    


"""
@brief	Generate a PyInstaller .spec file without building. 빌드하지 않고 PyInstaller .spec 파일을 생성합니다.
@param	path_script	    Path to Python script 파이썬 스크립트 경로
@param	output_path	    Path for the .spec file .spec 파일 경로
@param	onefile	        Bundle everything into single file 모든 것을 단일 파일로 번들
@param	windowed	    Create windowed application 윈도우 응용프로그램 생성
@param	icon	        Path to icon file 아이콘 파일 경로
@param	hidden_imports	List of hidden imports 숨겨진 임포트 목록
@param	additional_data	List of (source, dest) tuples (소스, 대상) 튜플 목록
@param	venv_path	    Path to virtual environment 가상 환경 경로
@return	Tuple of (success: bool, spec_file_path: str) (성공 여부, spec 파일 경로) 튜플
@throws	PyInstallerError: If spec file generation fails spec 파일 생성 실패 시
"""
def generate_spec_file(
		path_script: str,
		output_path: Optional[str] = None,
		onefile: bool = True,
		windowed: bool = False,
		icon: Optional[str] = None,
		hidden_imports: Optional[List[str]] = None,
		additional_data: Optional[List[Tuple[str, str]]] = None,
		venv_path: Optional[str] = None
 	) -> Tuple[bool, str]:
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
        cmd = [pyi_makespec, path_script]
        
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
        script_name = Path(path_script).stem
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


"""
@brief	Clean PyInstaller build artifacts. PyInstaller 빌드 아티팩트를 정리합니다.
@param	path_script	    Path to script (for finding .spec file) 스크립트 경로 (spec 파일 찾기용)
@param	remove_dist	    Remove dist directory dist 디렉토리 제거
@param	remove_build	Remove build directory build 디렉토리 제거
@param	remove_spec	    Remove .spec file .spec 파일 제거
@return	Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
"""
def clean_build_files(
		path_script: Optional[str] = None,
		remove_dist: bool = False,
		remove_build: bool = True,
		remove_spec: bool = False
 	) -> Tuple[bool, str]:
    try:
        removed = []
        
        if remove_build and os.path.exists('build'):
            shutil.rmtree('build')
            removed.append('build')
        
        if remove_dist and os.path.exists('dist'):
            shutil.rmtree('dist')
            removed.append('dist')
        
        if remove_spec and path_script:
            spec_file = f"{Path(path_script).stem}.spec"
            if os.path.exists(spec_file):
                os.remove(spec_file)
                removed.append(spec_file)
        
        if removed:
            return True, f"Removed: {', '.join(removed)}"
        else:
            return True, "No build files found to remove"
        
    except Exception as e:
        return False, f"Error cleaning build files: {str(e)}"


"""
@brief	Get the installed PyInstaller version. 설치된 PyInstaller 버전을 가져옵니다.
@param	venv_path	Path to virtual environment (optional) 가상 환경 경로 (선택사항)
@return	Version string or None if not installed 버전 문자열 또는 설치되지 않은 경우 None
"""
def get_pyinstaller_version(venv_path: Optional[str] = None) -> Optional[str]:
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


"""
@brief	Analyze a Python script to see what PyInstaller will include. 파이썬 스크립트를 분석하여 PyInstaller가 포함할 항목을 확인합니다.
@param	path_script	Path to Python script 파이썬 스크립트 경로
@param	venv_path	Path to virtual environment (optional) 가상 환경 경로 (선택사항)
@return	Tuple of (success: bool, analysis: str) (성공 여부, 분석 결과) 튜플
@throws	PyInstallerError: If analysis fails 분석 실패 시
"""
def analyze_script(path_script: str, 
                  venv_path: Optional[str] = None) -> Tuple[bool, str]:
    try:
        if not os.path.exists(path_script):
            raise PyInstallerError(f"Script not found: {path_script}")
        
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
        with open(path_script, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=path_script)
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        analysis = f"Detected imports in {path_script}:\n"
        analysis += "\n".join(f"  - {imp}" for imp in sorted(set(imports)))
        
        return True, analysis
        
    except Exception as e:
        error_msg = f"Failed to analyze script: {str(e)}"
        raise PyInstallerError(error_msg)


"""
@brief	Create a venv, install requirements, and build executable all in one step. 가상 환경을 생성하고 requirements를 설치한 후 실행 파일을 빌드합니다.
@param	path_script	        Path to Python script 파이썬 스크립트 경로
@param	requirements_file	Path to requirements.txt requirements.txt 경로
@param	venv_path	        Path for virtual environment 가상 환경 경로
@param	output_dir	        Output directory for executable 실행 파일 출력 디렉토리
@param	**build_options	Additional options for build_exe build_exe를 위한 추가 옵션
@return	Tuple of (success: bool, exe_path: str, message: str) (성공 여부, 실행 파일 경로, 메시지) 튜플
@throws	PyInstallerError: If any step fails 단계 실패 시
"""
def build_from_requirements(
		path_script: str,
		requirements_file: str,
		venv_path: str,
		output_dir: Optional[str] = None,
		**build_options
 	) -> Tuple[bool, str, str]:
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
            path_script,
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

