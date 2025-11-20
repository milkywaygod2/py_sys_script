"""
File System Utilities
파일 시스템 유틸리티

This module provides utility functions for file system operations.
파일 시스템 작업을 위한 유틸리티 함수들을 제공합니다.
"""
# Standard Library Imports
import os
import sys
import json
import ctypes
import subprocess
import shutil
import glob
import hashlib
import stat
import tempfile
import urllib.request
import shlex

from pathlib import Path
from typing import Optional, List, Dict, Tuple, Callable, Union

from sys_util_core.env_utils import get_env_var, set_env_var

"""
@namespace cmd_util
@brief	Namespace for command-related utilities. 명령 관련 유틸리티를 위한 네임스페이스
"""
class ErrorCommandSystem(Exception): pass
class CommandSystem:
    def print_info(msg):
        print(f"[INFO] {msg}")

    def print_error(msg):
        print(f"[ERROR] {msg}")

    def pause_exit(msg=None):
        if msg:
            CommandSystem.print_error(msg)
        input("Press Enter to exit...")
        sys.exit(1)

    """
    @brief	Execute a command and return its exit code, stdout, and stderr. 명령어를 실행하고 종료 코드, 표준 출력, 표준 에러를 반환합니다.
    @param	cmd	Command to execute (string or list of arguments) 실행할 명령어 (문자열 또는 인자 리스트)
    @param	shell	Whether to execute through shell 셸을 통해 실행할지 여부
    @param	timeout	Command timeout in seconds 명령어 타임아웃 (초 단위)
    @param	cwd	    Working directory for command execution 명령어 실행 작업 디렉토리
    @param	env	    Environment variables for command 명령어에 사용할 환경 변수
    @return	Tuple of (return_code, stdout, stderr) (리턴 코드, 표준 출력, 표준 에러) 튜플
    """
    def run_command(
            cmd: Union[str, List[str]],
            timeout: Optional[int] = None,
            specific_working_dir: Optional[str] = None,
            cumstem_env: Optional[Dict[str, str]] = None
        ) -> Tuple[int, str, str]:
        try:
            sentense_or_list = isinstance(cmd, str)
            
            result = subprocess.run(
                cmd,
                capture_output=True, # Capture stdout and stderr
                text=True, # Decode output as string (UTF-8)
                timeout=timeout,
                shell=sentense_or_list,
                cwd=specific_working_dir, # Working directory
                env=cumstem_env # Environment variables or path
            )
            return result.returncode, result.stdout, result.stderr
        
        except subprocess.TimeoutExpired as e:
            return -1, "", f"Command timed out after {timeout} seconds"
        
        except Exception as e:
            return -1, "", str(e)


    """
    @brief	Execute a command and stream output in real-time. 명령어를 실행하고 실시간으로 출력을 스트리밍합니다.
    @param	cmd	    Command to execute 실행할 명령어
    @param	shell	Whether to execute through shell 셸을 통해 실행할지 여부
    @param	cwd	    Working directory 작업 디렉토리
    @param	env	    Environment variables 환경 변수
    @yields Line-by-line output from the command 명령어의 줄 단위 출력
    """
    def run_command_streaming(
            cmd: Union[str, List[str]],
            shell: bool = False,
            cwd: Optional[str] = None,
            env: Optional[Dict[str, str]] = None
        ):
        if isinstance(cmd, str) and not shell:
            cmd = shlex.split(cmd)
        
        process = subprocess.Popen(
            cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=cwd,
            env=env
        )
        
        for line in iter(process.stdout.readline, ''):
            if line:
                yield line.rstrip()
        
        process.wait()


    """
    @brief	Check if a command exists in the system PATH. 시스템 PATH에 명령어가 존재하는지 확인합니다.
    @param	command	Command name to check 확인할 명령어 이름
    @return	True if command exists, False otherwise 명령어가 존재하면 True, 아니면 False
    """
    def check_command_exists(command: str) -> bool:
        if sys.platform == 'win32':
            result = subprocess.run(
                ['where', command],
                capture_output=True,
                text=True
            )
        else:
            result = subprocess.run(
                ['which', command],
                capture_output=True,
                text=True
            )
        
        return result.returncode == 0


    """
    @brief	Execute a command asynchronously and return the process object. 명령어를 비동기로 실행하고 프로세스 객체를 반환합니다.
    @param	cmd	    Command to execute 실행할 명령어
    @param	shell	Whether to execute through shell 셸을 통해 실행할지 여부
    @param	cwd	    Working directory 작업 디렉토리
    @param	env	    Environment variables 환경 변수
    @return	Process object 프로세스 객체
    """
    def run_command_async(
            cmd: Union[str, List[str]],
            shell: bool = False,
            cwd: Optional[str] = None,
            env: Optional[Dict[str, str]] = None
        ) -> subprocess.Popen:
        if isinstance(cmd, str) and not shell:
            cmd = shlex.split(cmd)
        
        return subprocess.Popen(
            cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
            env=env
        )


    """
    @brief	Kill all processes with the given name. 지정한 이름의 모든 프로세스를 종료합니다.
    @param	process_name	Name of the process to kill 종료할 프로세스 이름
    @return	True if successful, False otherwise 성공하면 True, 실패하면 False
    """
    def kill_process_by_name(process_name: str) -> bool:
        try:
            if sys.platform == 'win32':
                subprocess.run(['taskkill', '/F', '/IM', process_name], 
                            capture_output=True, check=True)
            else:
                subprocess.run(['pkill', '-9', process_name], 
                            capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False


    """
    @brief	Execute a command and return only its stdout. 명령어를 실행하고 표준 출력만 반환합니다.
    @param	cmd	    Command to execute 실행할 명령어
    @param	shell	Whether to execute through shell 셸을 통해 실행할지 여부
    @return	Command stdout as string 명령어 표준 출력 문자열
    """
    def get_command_output(cmd: Union[str, List[str]], shell: bool = False) -> str:
        _, stdout, _ = run_command(cmd, shell=shell)
        return stdout


    """
    @brief	Execute a command with elevated privileges (admin/sudo). 관리자 권한(admin/sudo)으로 명령어를 실행합니다.
    @param	cmd	Command to execute 실행할 명령어
    @return	Tuple of (return_code, stdout, stderr) (리턴 코드, 표준 출력, 표준 에러) 튜플
    """
    def run_elevated_command(cmd: Union[str, List[str]]) -> Tuple[int, str, str]:
        if isinstance(cmd, str):
            cmd_str = cmd
        else:
            cmd_str = ' '.join(cmd)
        
        if sys.platform == 'win32':
            # On Windows, use runas (note: may require user interaction)
            elevated_cmd = f'runas /user:Administrator "{cmd_str}"'
            return run_command(elevated_cmd, shell=True)
        else:
            # On Unix-like systems, use sudo
            if isinstance(cmd, str):
                elevated_cmd = f'sudo {cmd_str}'
            else:
                elevated_cmd = ['sudo'] + cmd
            return run_command(elevated_cmd)


    """
    @brief	Execute a command with stdin input. 표준 입력(stdin)과 함께 명령어를 실행합니다.
    @param	cmd	        Command to execute 실행할 명령어
    @param	input_data	Data to send to stdin 표준 입력으로 보낼 데이터
    @param	shell	    Whether to execute through shell 셸을 통해 실행할지 여부
    @return	Tuple of (return_code, stdout, stderr) (리턴 코드, 표준 출력, 표준 에러) 튜플
    """
    def run_command_with_input(
            cmd: Union[str, List[str]],
            input_data: str,
            shell: bool = False
        ) -> Tuple[int, str, str]:
        if isinstance(cmd, str) and not shell:
            cmd = shlex.split(cmd)
        
        try:
            result = subprocess.run(
                cmd,
                shell=shell,
                input=input_data,
                capture_output=True,
                text=True
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)


    """
    @brief	Get list of running processes. 실행 중인 프로세스 목록을 가져옵니다.
    @return	List of dictionaries containing process information 프로세스 정보를 담은 딕셔너리 리스트
    """
    def get_process_list() -> List[Dict[str, str]]:
        processes = []
        
        try:
            if sys.platform == 'win32':
                result = subprocess.run(
                    ['tasklist', '/FO', 'CSV', '/NH'],
                    capture_output=True,
                    text=True
                )
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.replace('"', '').split(',')
                        if len(parts) >= 2:
                            processes.append({
                                'name': parts[0],
                                'pid': parts[1]
                            })
            else:
                result = subprocess.run(
                    ['ps', 'aux'],
                    capture_output=True,
                    text=True
                )
                for line in result.stdout.strip().split('\n')[1:]:
                    parts = line.split()
                    if len(parts) >= 11:
                        processes.append({
                            'user': parts[0],
                            'pid': parts[1],
                            'name': parts[10]
                        })
        except Exception:
            pass
        
        return processes


    """
    @brief	Execute multiple commands in sequence. 여러 명령어를 순차적으로 실행합니다.
    @param	commands	    List of commands to execute 실행할 명령어 리스트
    @param	stop_on_error	Whether to stop execution on first error 첫 에러 발생 시 실행을 중지할지 여부
    @param	shell	        Whether to execute through shell 셸을 통해 실행할지 여부
    @return	List of tuples (return_code, stdout, stderr) for each command 각 명령어의 (리턴 코드, 표준 출력, 표준 에러) 튜플 리스트
    """
    def run_batch_commands(
            commands: List[Union[str, List[str]]],
            stop_on_error: bool = False,
            shell: bool = False
        ) -> List[Tuple[int, str, str]]:
        results = []
        
        for cmd in commands:
            result = run_command(cmd, shell=shell)
            results.append(result)
            
            if stop_on_error and result[0] != 0:
                break
        
        return results


"""
@namespace file_util
@brief	Namespace for file-related utilities. 파일 관련 유틸리티를 위한 네임스페이스
"""
class ErrorFileSystem(Exception): pass
class FileSystem:
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
            print(f"[ERROR] 관리자 권한으로 실행하는 데 실패했습니다: {e}")
            sys.exit(1)

    """
    @brief  Get the filename of the currently executing script. 현재 실행 중인 스크립트의 파일명을 반환합니다.
    @return Filename as a string 파일명을 문자열로 반환
    """
    def get_current_script_name() -> str:
        return os.path.basename(sys.argv[0])

    """
    @brief  Extract the string inside square brackets from the currently executing script's name. 현재 실행 중인 스크립트 이름에서 대괄호([]) 안의 문자열을 추출합니다.
    @return Extracted string inside square brackets, or an empty string if not found 대괄호 안의 추출된 문자열, 없으면 빈 문자열 반환
    """
    def get_string_in_brackets_from_string(input_str: str) -> str:
        start = input_str.find('[')
        end = input_str.find(']')
        if start != -1 and end != -1 and start < end:
            return input_str[start + 1:end]
        return ""
    
    """
    @brief	Check if a command-line tool is installed, and install it if not. 명령줄 도구가 설치되어 있는지 확인하고, 없으면 설치합니다.
    @return	True if the tool is installed or successfully installed, False otherwise 도구가 설치되어 있거나 성공적으로 설치되면 True, 아니면 False
    """
    def check_cmd_installed(package_name: Optional[str], global_check: bool = False) -> bool:
        try:
            # Determine the Python executable based on global_check flag

            if package_name == 'python':
                cmd = ['python', '--version']
            else:
                python_executable = "python" if global_check else sys.executable
                cmd = [python_executable, '-m', package_name, '--version']
        
            return subprocess.run(cmd, capture_output=True, text=True, check=True).returncode == 0  # 0 means installed (terminal code)
            
        except FileNotFoundError:  # Command not found
            if package_name == 'python':
                print("[INFO] Python is not installed or not found in PATH.")
                return InstallSystem.PythonRelated.install_python_global()
            elif package_name == 'pip':
                print("[INFO] pip is not installed or not found in PATH.")
                return InstallSystem.PythonRelated.install_pip_global(global_excute=global_check, upgrade=True)
            elif package_name == 'pyinstaller':
                print("[INFO] PyInstaller is not installed or not found in PATH.")
                return InstallSystem.PythonRelated.install_pyinstaller_global(global_excute=global_check, upgrade=True)
            else:
                print(f"[INFO] {package_name} is not installed or not found in PATH.")
                return False  # For other tools, automatic installation is not supported
            
        except Exception as e:  # Other unexpected errors
            print(f"[ERROR] Unexpected error checking {package_name}: {str(e)}")
            return False

    """
    @brief	Create a directory and all necessary parent directories. 디렉토리와 필요한 모든 상위 디렉토리를 생성합니다.
    @param	path	    Path to create 생성할 경로
    @param	exist_ok	Don't raise error if directory exists 디렉토리가 이미 존재해도 에러를 발생시키지 않음
    @return	True if successful, False otherwise 성공하면 True, 실패하면 False
    """
    def create_directory(path: str, exist_ok: bool = True) -> bool:
        try:
            os.makedirs(path, exist_ok=exist_ok)
            return True
        except Exception:
            return False


    """
    @brief	Delete a directory. 디렉토리를 삭제합니다.
    @param	path	    Path to delete 삭제할 경로
    @param	recursive	Delete recursively including contents 내용물을 포함하여 재귀적으로 삭제
    @return	True if successful, False otherwise 성공하면 True, 실패하면 False
    """
    def delete_directory(path: str, recursive: bool = True) -> bool:
        try:
            if recursive:
                shutil.rmtree(path)
            else:
                os.rmdir(path)
            return True
        except Exception:
            return False


    """
    @brief	Copy a file from source to destination. 소스에서 목적지로 파일을 복사합니다.
    @param	src	        Source file path 소스 파일 경로
    @param	dst	        Destination file path 목적지 파일 경로
    @param	overwrite	Overwrite if destination exists 목적지가 존재할 경우 덮어쓰기
    @return	True if successful, False otherwise 성공하면 True, 실패하면 False
    """
    def copy_file(
            src: str,
            dst: str,
            overwrite: bool = True
        ) -> bool:
        try:
            if not overwrite and os.path.exists(dst):
                return False
            
            shutil.copy2(src, dst)
            return True
        except Exception:
            return False


    """
    @brief	Copy a directory recursively. 디렉토리를 재귀적으로 복사합니다.
    @param	src	        Source directory path 소스 디렉토리 경로
    @param	dst	        Destination directory path 목적지 디렉토리 경로
    @param	overwrite	Overwrite if destination exists 목적지가 존재할 경우 덮어쓰기
    @return	True if successful, False otherwise 성공하면 True, 실패하면 False
    """
    def copy_directory(
            src: str,
            dst: str,
            overwrite: bool = True
        ) -> bool:
        try:
            if os.path.exists(dst) and not overwrite:
                return False
            
            if os.path.exists(dst):
                shutil.rmtree(dst)
            
            shutil.copytree(src, dst)
            return True
        except Exception:
            return False


    """
    @brief	Move a file from source to destination. 소스에서 목적지로 파일을 이동합니다.
    @param	src	Source file path 소스 파일 경로
    @param	dst	Destination file path 목적지 파일 경로
    @return	True if successful, False otherwise 성공하면 True, 실패하면 False
    """
    def move_file(src: str, dst: str) -> bool:
        try:
            shutil.move(src, dst)
            return True
        except Exception:
            return False


    """
    @brief	Check if a file exists. 파일이 존재하는지 확인합니다.
    @param	path	File path to check 확인할 파일 경로
    @return	True if exists, False otherwise 존재하면 True, 아니면 False
    """
    def file_exists(path: str) -> bool:
        return os.path.isfile(path)


    """
    @brief	Check if a directory exists. 디렉토리가 존재하는지 확인합니다.
    @param	path	Directory path to check 확인할 디렉토리 경로
    @return	True if exists, False otherwise 존재하면 True, 아니면 False
    """
    def directory_exists(path: str) -> bool:
        return os.path.isdir(path)


    """
    @brief	Get the size of a file in bytes. 파일 크기를 바이트 단위로 가져옵니다.
    @param	path	File path 파일 경로
    @return	File size in bytes, -1 if error 파일 크기(바이트), 에러시 -1
    """
    def get_file_size(path: str) -> int:
        try:
            return os.path.getsize(path)
        except Exception:
            return -1


    """
    @brief	Check if an executable file exists and print its details. 실행 파일이 존재하는지 확인하고 세부 정보를 출력합니다.
    @param	path_file	Path to the executable file 실행 파일 경로 (str)
    @return	bool (True if the file exists, False otherwise)
    """
    def check_file(path_file: str) -> bool:
        c_path_file = Path(path_file)
        if c_path_file.exists():
            print(f"File exists: {c_path_file}")
            size_bytes = c_path_file.stat().st_size
            if size_bytes >= 1024 * 1024:  # 1 MB 이상
                size_mb = size_bytes / (1024 * 1024)  # 파일 크기를 MB로 변환
                print(f"Size: {size_mb:.2f} MB")
            elif size_bytes >= 1024:  # 1 KB 이상
                size_kb = size_bytes / 1024  # 파일 크기를 KB로 변환
                print(f"Size: {size_kb:.2f} KB")
            else:  # 1 KB 미만
                print("Size: 1 KB")
            return True
        else:
            print(f"File does not exist: {c_path_file}")
            return False


    """
    @brief	Calculate hash of a file. 파일의 해시를 계산합니다.
    @param	path	    File path 파일 경로
    @param	algorithm	Hash algorithm (md5, sha1, sha256) 해시 알고리즘 (md5, sha1, sha256)
    @return	Hex digest of file hash or None if error 파일 해시의 16진수 다이제스트, 에러시 None
    """
    def get_file_hash(path: str, algorithm: str = 'md5') -> Optional[str]:
        try:
            hash_obj = hashlib.new(algorithm)
            
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
        except Exception:
            return None


    """
    @brief	List files in a directory matching a pattern. 패턴과 일치하는 디렉토리 내 파일 목록을 가져옵니다.
    @param	directory	Directory to search 검색할 디렉토리
    @param	pattern	    Glob pattern to match 일치시킬 Glob 패턴
    @param	recursive	Search recursively 재귀적으로 검색
    @return	List of matching file paths 일치하는 파일 경로 리스트
    """
    def list_files(
            directory: str,
            pattern: str = '*',
            recursive: bool = False
        ) -> List[str]:
        if recursive:
            search_pattern = os.path.join(directory, '**', pattern)
            return glob.glob(search_pattern, recursive=True)
        else:
            search_pattern = os.path.join(directory, pattern)
            return glob.glob(search_pattern)


    def find_git_root(start_dir):
        cur = os.path.abspath(start_dir)
        root = os.path.abspath(os.sep)
        while True:
            git_path = os.path.join(cur, '.git')
            if os.path.isdir(git_path):
                return cur
            if cur == root:
                return None
            cur = os.path.dirname(cur)

    def find_vcpkg(vcpkg_dir_names=['vcpkg']):
        for d in vcpkg_dir_names:
            if os.path.isdir(d) and (os.path.isfile(os.path.join(d, 'vcpkg.exe')) or os.path.isfile(os.path.join(d, 'bootstrap-vcpkg.bat'))):
                return os.path.abspath(d)
        return None

    """
    @brief	Find files in a directory by name pattern or extension. 이름 패턴이나 확장자로 디렉토리 내 파일을 찾습니다.
    @param	directory	    Directory to search 검색할 디렉토리
    @param	name_pattern	File name pattern to match 일치시킬 파일 이름 패턴
    @param	extension	    File extension to match (without dot) 일치시킬 파일 확장자 (점 제외)
    @param	recursive	    Search recursively 재귀적으로 검색
    @return	List of matching file paths 일치하는 파일 경로 리스트
    """
    def find_files(
            directory: str,
            name_pattern: Optional[str] = None,
            extension: Optional[str] = None,
            recursive: bool = True
        ) -> List[str]:
        results = []
        
        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    match = True
                    
                    if name_pattern and name_pattern not in file:
                        match = False
                    
                    if extension and not file.endswith(f'.{extension}'):
                        match = False
                    
                    if match:
                        results.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if not os.path.isfile(file_path):
                    continue
                
                match = True
                
                if name_pattern and name_pattern not in file:
                    match = False
                
                if extension and not file.endswith(f'.{extension}'):
                    match = False
                
                if match:
                    results.append(file_path)
        
        return results


    """
    @brief	Get the last modification time of a file. 파일의 마지막 수정 시간을 가져옵니다.
    @param	path	File path 파일 경로
    @return	Modification time as timestamp, -1 if error 타임스탬프로 표현된 수정 시간, 에러시 -1
    """
    def get_file_modified_time(path: str) -> float:
        try:
            return os.path.getmtime(path)
        except Exception:
            return -1


    """
    @brief	Set file permissions (Unix-like systems). 파일 권한을 설정합니다 (Unix 계열 시스템).
    @param	path	    File path 파일 경로
    @param	permissions	Octal permission value (e.g., 0o755) 8진수 권한 값 (예: 0o755)
    @return	True if successful, False otherwise 성공하면 True, 실패하면 False
    """
    def set_file_permissions(path: str, permissions: int) -> bool:
        try:
            os.chmod(path, permissions)
            return True
        except Exception:
            return False


    """
    @brief	Make a file read-only. 파일을 읽기 전용으로 만듭니다.
    @param	path	File path 파일 경로
    @return	True if successful, False otherwise 성공하면 True, 실패하면 False
    """
    def make_file_readonly(path: str) -> bool:
        try:
            os.chmod(path, stat.S_IREAD)
            return True
        except Exception:
            return False


    """
    @brief	Make a file writable. 파일을 쓰기 가능하게 만듭니다.
    @param	path	File path 파일 경로
    @return	True if successful, False otherwise 성공하면 True, 실패하면 False
    """
    def make_file_writable(path: str) -> bool:
        try:
            os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
            return True
        except Exception:
            return False


    """
    @brief	Calculate total size of a directory and all its contents. 디렉토리와 모든 내용물의 전체 크기를 계산합니다.
    @param	path	Directory path 디렉토리 경로
    @return	Total size in bytes, -1 if error 전체 크기(바이트), 에러시 -1
    """
    def get_directory_size(path: str) -> int:
        try:
            total_size = 0
            for dirpath, _, filenames in os.walk(path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
            return total_size
        except Exception:
            return -1


    """
    @brief	Create a temporary file. 임시 파일을 생성합니다.
    @param	suffix	File suffix 파일 접미사
    @param	prefix	File prefix 파일 접두사
    @param	dir	    Directory to create file in 파일을 생성할 디렉토리
    @param	text	Open in text mode 텍스트 모드로 열기
    @return	Path to temporary file 임시 파일 경로
    """
    def create_temp_file(
            suffix: str = '',
            prefix: str = 'tmp',
            dir: Optional[str] = None,
            text: bool = True
        ) -> str:
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, 
                                    dir=dir, text=text)
        os.close(fd)
        return path


    """
    @brief	Create a temporary directory. 임시 디렉토리를 생성합니다.
    @param	suffix	Directory suffix 디렉토리 접미사
    @param	prefix	Directory prefix 디렉토리 접두사
    @param	dir	    Parent directory 상위 디렉토리
    @return	Path to temporary directory 임시 디렉토리 경로
    """
    def create_temp_directory(
            suffix: str = '',
            prefix: str = 'tmp',
            dir: Optional[str] = None
        ) -> str:
        return tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)


    """
    @brief	Walk a directory tree and execute callback for each file. 디렉토리 트리를 탐색하고 각 파일에 대해 콜백을 실행합니다.
    @param	directory	Directory to walk 탐색할 디렉토리
    @param	callback	Function to call for each file path 각 파일 경로에 대해 호출할 함수
    """
    def walk_directory(directory: str, 
                    callback: Callable[[str], None]) -> None:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                callback(file_path)

    """
    @brief	Download a file from a given URL. 주어진 URL에서 파일을 다운로드합니다.
    @param	url	        URL of the file 파일의 URL
    @param	save_path	Path to save the downloaded file 다운로드한 파일을 저장할 경로
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
    @brief	Download a file using curl from a given URL. 주어진 URL에서 curl을 사용하여 파일을 다운로드합니다.
    @param	url	        URL of the file 파일의 URL
    @param	save_path	Path to save the downloaded file 다운로드한 파일을 저장할 경로
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

###################################################################################################################
###################################################################################################################
###################################################################################################################

"""
@namespace install
@brief	Namespace for installation-related utilities. 설치 관련 유틸리티를 위한 네임스페이스
"""
class ErrorInstall(Exception): pass
class InstallSystem:
    """
    @namespace PythonRelated
    @brief	Namespace for py-related. PythonRelated 관련을 위한 네임스페이스
    """
    class ErrorPythonRelated(ErrorInstall): pass
    class PythonRelated:
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
                    raise InstallSystem.ErrorPythonRelated(f"Failed to fetch data from API (HTTP {response.status})")
            raise InstallSystem.ErrorPythonRelated("Failed to fetch the latest Python installer URL")

        """
        @brief	Download and run the Python installer to install Python. Python 설치 프로그램을 다운로드하고 실행하여 Python을 설치합니다.
        @return	bool
        """
        def install_python_global() -> bool:
            try:
                python_url, python_filename = InstallSystem.PythonRelated.get_latest_python_url_with_filename()
                path_where_python_download = Path.home() / "Downloads" / python_filename

                # curl -o path_where_python_download python_url
                FileSystem.download_url(python_url, str(path_where_python_download))
            
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
                FileSystem.check_cmd_installed('python') if global_excute else None

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
        @throws	InstallPyError: If installation fails 설치 실패 시
        """
        def install_pyinstaller_global(
            global_excute: bool = True,
            upgrade: bool = False,
            version: Optional[str] = None,
            ) -> bool:
            try:
                # Check if pip is installed
                FileSystem.check_cmd_installed('pip')

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
                raise InstallSystem.ErrorPythonRelated(error_msg)

            except Exception as e:
                error_msg = f"Unexpected error installing PyInstaller: {str(e)}"
                raise InstallSystem.ErrorPythonRelated(error_msg)

        
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
                FileSystem.check_cmd_installed('pyinstaller', global_check=related_install_global)
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
                if subprocess.run(cmd, capture_output=True, text=True, check=True).returncode == 0:  # 0 means installed (terminal code)
                    return FileSystem.check_file(f"dist/{c_path_script.stem}.exe")

            except subprocess.CalledProcessError as e:
                error_msg = f"Failed to build executable: {e.stderr}"
                raise InstallSystem.ErrorPythonRelated(error_msg)
            
            except Exception as e:
                error_msg = f"Unexpected error building executable: {str(e)}"
                raise InstallSystem.ErrorPythonRelated(error_msg)

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
        @throws	InstallPyError: If spec file generation fails spec 파일 생성 실패 시
        """
        def UNCENCORED_generate_spec_file_for_engeering_build_option_without_hardcoding(
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
                FileSystem.check_cmd_installed('pyinstaller', global_check=global_install)
                
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
                raise InstallSystem.ErrorPythonRelated(error_msg)
            
            except Exception as e:
                error_msg = f"Unexpected error generating spec file: {str(e)}"
                raise InstallSystem.ErrorPythonRelated(error_msg)

        """
        @brief	Clean PyInstaller build artifacts. PyInstaller 빌드 아티팩트를 정리합니다.
        @param	path_script	    Path to script (for finding .spec file) 스크립트 경로 (spec 파일 찾기용)
        @param	remove_dist	    Remove dist directory dist 디렉토리 제거
        @param	remove_build	Remove build directory build 디렉토리 제거
        @param	remove_spec	    Remove .spec file .spec 파일 제거
        @return	Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
        """
        def UNCENCORED_clean_build_files(
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
        def UNCENCORED_get_pyinstaller_version(global_check: bool = False) -> Optional[str]:
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
        @throws	InstallPyError: If analysis fails 분석 실패 시
        """
        def UNCENCORED_analyze_script(path_script: str) -> Tuple[bool, str]:
            try:
                if not os.path.exists(path_script):
                    raise InstallSystem.ErrorPythonRelated(f"Script not found: {path_script}")

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
                raise InstallSystem.ErrorPythonRelated(error_msg)


        """
        @brief	Install requirements and build executable in one step. requirements를 설치하고 실행 파일을 빌드합니다.
        @param	path_script	        Path to Python script 파이썬 스크립트 경로
        @param	requirements_file	Path to requirements.txt requirements.txt 경로
        @param	output_dir	        Output directory for executable 실행 파일 출력 디렉토리
        @param	**build_options	    Additional options for build_exe_with_pyinstaller build_exe_with_pyinstaller를 위한 추가 옵션
        @return	Tuple of (success: bool, exe_path: str, message: str) (성공 여부, 실행 파일 경로, 메시지) 튜플
        @throws	InstallPyError: If any step fails 단계 실패 시
        """
        def UNCENCORED_build_from_requirements(
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
                    raise InstallSystem.ErrorPythonRelated(f"Failed to install requirements: {result.stderr}")
                messages.append("[INFO] Requirements installed successfully.")

                # Install PyInstaller
                success = InstallSystem.PythonRelated.install_pyinstaller_global(global_excute=False)
                if not success:
                    raise InstallSystem.ErrorPythonRelated("Failed to install PyInstaller.")
                messages.append("[INFO] PyInstaller installed successfully.")

                # Build executable
                success = InstallSystem.PythonRelated.build_exe_with_pyinstaller(
                    path_script=path_script,
                    related_install_global=False,
                    **build_options
                )
                if not success:
                    raise InstallSystem.ErrorPythonRelated("Failed to build executable.")
                messages.append("[INFO] Executable built successfully.")

                exe_path = os.path.join(output_dir or "dist", f"{Path(path_script).stem}.exe")
                return True, exe_path, "\n".join(messages)

            except Exception as e:
                error_msg = f"Failed in build_from_requirements: {str(e)}"
                raise InstallSystem.ErrorPythonRelated(error_msg)

    """
    @namespace VcpkgRelated
    @brief	Namespace for vcpkg-related utilities. vcpkg 관련 유틸리티를 위한 네임스페이스
    """
    class ErrorVcpkgRelated(ErrorInstall): pass
    class VcpkgRelated:
        def install_vcpkg_global():
            script_dir = os.path.dirname(os.path.abspath(__file__))
            vcpkg_json = os.path.join(script_dir, 'vcpkg.json')
            if not FileSystem.file_exists(vcpkg_json):
                pause_exit("vcpkg.json 파일이 없습니다. 설치를 중지합니다.")

            # 1. vcpkg 폴더 & 실행파일 확인/설치
            vcpkg_dir = os.path.join(script_dir, 'vcpkg')
            vcpkg_exe = os.path.join(vcpkg_dir, 'vcpkg.exe')

            if not (FileSystem.directory_exists(vcpkg_dir) and FileSystem.file_exists(vcpkg_exe)):
                print_info("vcpkg 설치가 필요합니다.")
                git_root = FileSystem.find_git_root(script_dir)
                if not git_root:
                    pause_exit(".git 폴더 경로를 찾을 수 없습니다.")
                
                # .git의 상위 폴더(vcpkg 설치할 위치)
                vcpkg_dir = os.path.join(os.path.dirname(git_root), 'vcpkg')
                
                if not FileSystem.directory_exists(vcpkg_dir):
                    print_info(f"git clone https://github.com/microsoft/vcpkg.git \"{vcpkg_dir}\"")
                    if not run_cmd(f"git clone https://github.com/microsoft/vcpkg.git \"{vcpkg_dir}\""):
                        pause_exit("vcpkg 클론 실패")
                
                vcpkg_exe = os.path.join(vcpkg_dir, 'vcpkg.exe')
                
                # bootstrap 실행
                if not FileSystem.file_exists(vcpkg_exe):
                    bootstrap_bat = os.path.join(vcpkg_dir, 'bootstrap-vcpkg.bat')
                    if not run_cmd(f"\"{bootstrap_bat}\"", cwd=vcpkg_dir):
                        pause_exit("bootstrap-vcpkg.bat 실패")
                
                set_env_var('path_vcpkg', vcpkg_dir)
            else:
                set_env_var('path_vcpkg', vcpkg_dir)

            # 2. Path 환경변수에 path_vcpkg 경로 추가
            cur_path = get_env_var('Path', '')
            cur_path_list = [p.strip().lower() for p in cur_path.split(';') if p.strip()]
            if vcpkg_dir.lower() not in cur_path_list:
                new_path = f"{cur_path};{vcpkg_dir}" if cur_path else vcpkg_dir
                set_env_var('Path', new_path)

            # 3. vcpkg install
            cmd = f"\"{vcpkg_exe}\" install --triplet x64-windows"
            if not run_cmd(cmd, cwd=script_dir):
                pause_exit("vcpkg install 실패")
            else:
                print_info("vcpkg 패키지 설치 및 환경설정이 완료되었습니다!")

    """
    @namespace UNCENCORED
    @brief	Namespace for uncencored utilities. UNCENCORED 관련 유틸리티를 위한 네임스페이스
    """
    