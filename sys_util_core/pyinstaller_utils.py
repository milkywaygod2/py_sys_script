"""
PyInstaller Utilities
PyInstaller 유틸리티

This module provides utility functions for converting Python scripts to executables using PyInstaller.
PyInstaller를 사용하여 파이썬 스크립트를 실행 파일로 변환하기 위한 유틸리티 함수들을 제공합니다.
"""

import json
import os
import sys
import ctypes
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple

import urllib.request

"""
@brief	Exception raised for PyInstaller operations. PyInstaller 작업 중 발생하는 예외
"""
class PyInstallerError(Exception):
    pass

"""
@brief  Re-run the script with administrator privileges. 관리자 권한으로 스크립트를 다시 실행합니다.
"""
def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return  # 이미 관리자 권한으로 실행 중이면 아무 작업도 하지 않음

    # 관리자 권한으로 실행하기 위한 명령어 생성
    params = ' '.join([f'"{arg}"' for arg in sys.argv])
    executable = sys.executable
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", executable, params, None, 1
        )
        sys.exit(0)  # 관리자 권한으로 실행되면 현재 프로세스 종료

    except Exception as e:
        raise PyInstallerError(f"Failed to elevate to administrator privileges: {str(e)}")

def get_latest_python_url_with_filename() -> Tuple[str, str]:
    api_url = "https://www.python.org/api/v2/downloads/release/"
    with urllib.request.urlopen(api_url) as response:
        if response.status == 200:
            releases = json.loads(response.read())
            for release in releases:
                if release["is_published"]:
                    for file in release["files"]:
                        if "amd64.exe" in file["url"]:
                            file_name = file["url"].split("/")[-1]
                            return file["url"], file_name
        else:
            raise Exception(f"Failed to fetch data from API (HTTP {response.status})")
    raise Exception("Failed to fetch the latest Python installer URL")

"""
@brief	Download Python installer from a given URL. 주어진 URL에서 Python 설치 프로그램을 다운로드합니다.
@param	url	        URL of the Python installer Python 설치 프로그램의 URL
@param	save_path	Path to save the downloaded installer 다운로드한 설치 프로그램을 저장할 경로
@return	None
"""
def download_url(url: str, save_path: str) -> None:
    if not save_path.exists():
        print(f"[INFO] Downloading from: {url}...")
        urllib.request.urlretrieve(url, save_path)
        print(f"[INFO] Saved to: {save_path}")
    else:
        print(f"[INFO] File already exists: {save_path}")
    

"""
@brief	Download Python installer from a given URL. 주어진 URL에서 Python 설치 프로그램을 다운로드합니다.
@param	url	        URL of the Python installer Python 설치 프로그램의 URL
@param	save_path	Path to save the downloaded installer 다운로드한 설치 프로그램을 저장할 경로
@return	None
"""
def download_url_curl(url: str, save_path: str) -> None:
    cmd_download_python = [
            'curl',
            "-o", 
            str(save_path),
            url
        ]
    if not save_path.exists():
        print(f"[INFO] Downloading from: {url}...")
        subprocess.run(cmd_download_python, capture_output=True, text=True, check=True)
        print(f"[INFO] Saved to: {save_path}")
    else:
        print(f"[INFO] File already exists: {save_path}")
"""
@brief	Download and run the Python installer to install Python. Python 설치 프로그램을 다운로드하고 실행하여 Python을 설치합니다.
@return	bool
"""
def install_python_global() -> bool:
    try:
        python_url, python_filename = get_latest_python_url_with_filename()
        path_where_python_download = Path.home() / "Downloads" / python_filename

        # curl -o path_where_python_download python_url
        download_url(python_url, str(path_where_python_download))
    
        # path_where_python_download /quiet InstallAllUsers=1 PrependPath=1
        cmd_install_python = [
            str(path_where_python_download),
            "/quiet",  # 조용히 설치
            "InstallAllUsers=1",  # 시스템 전체 설치
            "PrependPath=1",  # PATH 환경 변수에 추가
        ]
        if subprocess.run(cmd_install_python, capture_output=True, text=True, check=True).returncode == 0:
            return subprocess.run(['python', '--version'], check=True).returncode == 0

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install Python: {e.stderr}")
        return False

"""
@brief	Install pip globally or temporarily. pip를 전역 또는 임시로 설치합니다.
@param	global_excute	Whether to install pip globally (True) or temporarily (False) pip를 전역에 설치할지 여부 (True: 전역, False: 임시)
@return	True if pip is successfully installed, False otherwise pip가 성공적으로 설치되면 True, 아니면 False
"""
def install_pip_global(global_excute: bool = True) -> bool:
    try:
        # Check if python is installed if global_excute is True
        check_cmd_installed('python') if global_excute else None

        # Determine the Python executable based on global_excute flag
        python_executable = "python" if global_excute else sys.executable

        if subprocess.run([python_executable, '-m', 'ensurepip', '--upgrade'], capture_output=True, text=True, check=True).returncode == 0:
            return subprocess.run([python_executable, '-m', 'pip', '--version'], capture_output=True, text=True, check=True).returncode == 0
        else:
            return False
        
    except Exception as e:
        print(f"[ERROR] Failed to install pip: {e}")
        return False


"""
@brief	Install PyInstaller globally. PyInstaller를 전역에 설치합니다.
@param	version	    Specific version to install (optional) 설치할 특정 버전 (선택사항)
@param	upgrade	    Upgrade if already installed (default: False) 이미 설치된 경우 업그레이드 여부 (기본값: False)
@return	Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
@throws	PyInstallerError: If installation fails 설치 실패 시
"""
def install_pyinstaller_global(
    global_excute: bool = True,
    upgrade: bool = False,
    version: Optional[str] = None,
    ) -> bool:
    try:
        # Check if pip is installed
        check_cmd_installed('pip')

        # Determine the Python executable based on global_excute flag
        python_executable = "python" if global_excute else sys.executable

        # Call install by pip
        cmd = [python_executable, '-m', 'pip', 'install']

        # Mandatory re-install with latest version flag
        if upgrade:
            cmd.append('--upgrade')

        # Mandatory install specific version or latest
        if version:
            cmd.append(f'pyinstaller=={version}')
        else:
            cmd.append('pyinstaller')

        if subprocess.run(cmd, capture_output=True, text=True, check=True).returncode == 0:
            return subprocess.run([python_executable, '-m', 'pyinstaller', '--version'], capture_output=True, text=True, check=True).returncode == 0

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
def check_cmd_installed(package_name: Optional[str], global_check: bool = False) -> bool:
    try:
        # Determine the Python executable based on global_check flag

        if package_name is 'python':
            cmd = ['python', '--version']
        else:
            python_executable = "python" if global_check else sys.executable
            cmd = [python_executable, '-m', package_name, '--version']
    
        return subprocess.run(cmd, capture_output=True, text=True, check=True).returncode == 0  # 0 means installed (terminal code)
        
    except FileNotFoundError:  # Command not found
        if package_name == 'python':
            print("[INFO] Python is not installed or not found in PATH.")
            return install_python_global()
        elif package_name == 'pip':
            print("[INFO] pip is not installed or not found in PATH.")
            return install_pip_global(global_excute=global_check, upgrade=True)
        elif package_name == 'pyinstaller':
            print("[INFO] PyInstaller is not installed or not found in PATH.")
            return install_pyinstaller_global(global_excute=global_check, upgrade=True)
        else:
            print(f"[INFO] {package_name} is not installed or not found in PATH.")
            return False  # For other tools, automatic installation is not supported
        
    except Exception as e:  # Other unexpected errors
        print(f"[ERROR] Unexpected error checking {package_name}: {str(e)}")
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
        related_install_global: bool = False,
        onefile: bool = True,
        console: bool = True,
    ) -> bool:
    # python -m PyInstaller --clean --onefile  (--console) (--icon /icon.ico) (--add-data /pathRsc:tempName) /pathTarget.py

    try:
        # Determine the Python executable based on related_install_global flag
        check_cmd_installed('pyinstaller', global_check=related_install_global)
        python_executable = "python" if related_install_global else sys.executable
        
        cmd = [python_executable, "-m", "PyInstaller", "--clean"]

        # onefile option
        cmd.append("--onefile" if onefile else "--onedir")

        # console option
        if not console:
            cmd.append("--noconsole")

        # icon option
        if path_icon:
            c_path_icon = Path(path_icon)
            if c_path_icon.exists():
                cmd += ["--icon", str(c_path_icon)]
            else:
                raise FileNotFoundError(f"Icon file not found: {c_path_icon}")
        
        # rsc add-data option
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

        # Run 
        return subprocess.run(cmd, capture_output=True, text=True, check=True).returncode == 0  # 0 means installed (terminal code)
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to build executable: {e.stderr}"
        raise PyInstallerError(error_msg)
    
    except Exception as e:
        error_msg = f"Unexpected error building executable: {str(e)}"
        raise PyInstallerError(error_msg)

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
def generate_spec_file_for_engeering_build_option_without_hardcoding(
		path_script: str,
		global_install: bool = False,
		output_path: Optional[str] = None,
		onefile: bool = True,
		windowed: bool = False,
		icon: Optional[str] = None,
		hidden_imports: Optional[List[str]] = None,
		additional_data: Optional[List[Tuple[str, str]]] = None,
 	) -> Tuple[bool, str]:
    try:
        # Check PyInstaller installed
        check_cmd_installed('pyinstaller', global_check=global_install)
        
        # Build command
        cmd = ['pyi-makespec', path_script]
        
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
@return	Version string or None if not installed 버전 문자열 또는 설치되지 않은 경우 None
"""
def get_pyinstaller_version(global_check: bool = False) -> Optional[str]:
    try:
        # Determine the Python executable based on global_check flag
        python_executable = "python" if global_check else sys.executable

        cmd = [python_executable, '-m', 'pip', 'show', 'pyinstaller']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

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
@return	Tuple of (success: bool, analysis: str) (성공 여부, 분석 결과) 튜플
@throws	PyInstallerError: If analysis fails 분석 실패 시
"""
def analyze_script(path_script: str) -> Tuple[bool, str]:
    try:
        if not os.path.exists(path_script):
            raise PyInstallerError(f"Script not found: {path_script}")

        # Analyze imports using AST
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
@brief	Install requirements and build executable in one step. requirements를 설치하고 실행 파일을 빌드합니다.
@param	path_script	        Path to Python script 파이썬 스크립트 경로
@param	requirements_file	Path to requirements.txt requirements.txt 경로
@param	output_dir	        Output directory for executable 실행 파일 출력 디렉토리
@param	**build_options	    Additional options for build_exe_with_pyinstaller build_exe_with_pyinstaller를 위한 추가 옵션
@return	Tuple of (success: bool, exe_path: str, message: str) (성공 여부, 실행 파일 경로, 메시지) 튜플
@throws	PyInstallerError: If any step fails 단계 실패 시
"""
def build_from_requirements(
        path_script: str,
        requirements_file: str,
        output_dir: Optional[str] = None,
        **build_options
    ) -> Tuple[bool, str, str]:
    try:
        messages = []

        # Install requirements
        cmd = [sys.executable, '-m', 'pip', 'install', '-r', requirements_file]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.returncode != 0:
            raise PyInstallerError(f"Failed to install requirements: {result.stderr}")
        messages.append("[INFO] Requirements installed successfully.")

        # Install PyInstaller
        success = install_pyinstaller_global(global_excute=False)
        if not success:
            raise PyInstallerError("Failed to install PyInstaller.")
        messages.append("[INFO] PyInstaller installed successfully.")

        # Build executable
        success = build_exe_with_pyinstaller(
            path_script=path_script,
            related_install_global=False,
            **build_options
        )
        if not success:
            raise PyInstallerError("Failed to build executable.")
        messages.append("[INFO] Executable built successfully.")

        exe_path = os.path.join(output_dir or "dist", f"{Path(path_script).stem}.exe")
        return True, exe_path, "\n".join(messages)

    except Exception as e:
        error_msg = f"Failed in build_from_requirements: {str(e)}"
        raise PyInstallerError(error_msg)
