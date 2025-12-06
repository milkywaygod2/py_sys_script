"""
File System Utilities
파일 시스템 유틸리티

This module provides utility functions for file system operations.
파일 시스템 작업을 위한 유틸리티 함수들을 제공합니다.
"""
# Standard Library Imports
from hmac import new
import os, sys, subprocess
import json
import ctypes
import shutil
import glob
import hashlib
import stat
import tempfile
import urllib.request
import shlex
import re, inspect
import logging, time

from datetime import datetime
from pathlib import Path
from typing import Generic, Optional, List, Dict, Tuple, Callable, TypeVar, Union

import tkinter
from tkinter import filedialog
from tkinter.ttk import Progressbar
from tkinter.ttk import Treeview
from enum import Enum

from sys_util_core import common, cmd_utils


"""
@namespace log_util
@brief	Namespace for logger utilities. 로거 관련 유틸리티를 위한 네임스페이스
"""
class ErrorLogSystem(Exception): pass
class LogSystem:
    LOG_LEVEL_DEBUG = logging.DEBUG
    LOG_LEVEL_INFO = logging.INFO
    LOG_LEVEL_WARNING = logging.WARNING
    LOG_LEVEL_ERROR = logging.ERROR
    LOG_LEVEL_CRITICAL = logging.CRITICAL
    start_time: float = 0.0

    @staticmethod
    def start_logger(level: int = None, log_file_fullpath: Optional[str] = None):
        LogSystem.start_time = time.time()
        LogSystem.setup_logger(level, log_file_fullpath)

    @staticmethod
    def end_logger(is_exit: bool = False):
        elapsed_time = time.time() - LogSystem.start_time
        LogSystem.log_info(f"process exited in {elapsed_time:.2f} seconds" if is_exit else f"process completed in {elapsed_time:.2f} seconds")
        logging.shutdown()

    @staticmethod
    def setup_logger(level: int = None, log_file_fullpath: Optional[str] = None):
        if level is None:
            if FileSystem.is_exe():
                level = LogSystem.LOG_LEVEL_INFO
            else:
                level = LogSystem.LOG_LEVEL_DEBUG

        if log_file_fullpath is None:
            file_path, file_name = FileSystem.get_main_script_path_name_extension()[:2]
            log_folder_name = "logs"
            
            current_time = datetime.now().strftime("%y%m%d-%H%M%S-%f")[:-3]
            file_name = f"{current_time} " + file_name

            c_log_dir_path = Path(file_path) / log_folder_name    
            log_file_fullpath = str(c_log_dir_path / Path(file_name + ".log"))
        else:
            c_log_dir_path = Path(log_file_fullpath).parent

        # Create log directory if it doesn't exist
        c_log_dir_path.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)-7s] %(filename)-20s:%(lineno)5d %(funcName)-30s %(message)s",
            handlers=[
            logging.StreamHandler(),  # Console output
            logging.FileHandler(log_file_fullpath, encoding="utf-8")  # File output
            ]
        )
        LogSystem.log_info(f"Logging initialized.")

    @staticmethod
    def log_to_str(value):
        if isinstance(value, (int, float, bool, type(None))):  # Handle basic types
            return str(value)
        elif isinstance(value, str):
            return value
        elif isinstance(value, (list, tuple, set)):  # Handle collections
            return f"{type(value).__name__}({len(value)})"
        elif isinstance(value, dict):  # Handle dictionaries
            return f"dict({len(value)})"
        else:  # Handle objects
            return f"{type(value).__name__}"

    @staticmethod
    def format_args_with(args_name, args_value, seperate_mark: str = ", ", max_length=0):
        args_value_list = []
        for arg_name in args_name:
            value_str = LogSystem.log_to_str(args_value[arg_name]) # to_string
            if max_length > 0:
                if len(value_str) > max_length: value_str = f"{value_str[:max_length]}" # cutting
                value_str = f"{value_str:<{max_length}}" # add after aligning left with space
            args_value_list.append(value_str)
        return seperate_mark.join(args_value_list)

    @staticmethod
    def log_input_args():
        interest_frame = inspect.currentframe().f_back.f_back  # 두 단계 위의 프레임
        args_name, var_args_name, var_keyword_args_name, args_value = inspect.getargvalues(interest_frame)  # 인자값 추출
        arg_str = LogSystem.format_args_with(args_name, args_value)
        return f"InputArgs: ({arg_str})"
    
    @staticmethod
    def log_debug(msg: str, print_input_args: bool = True, stacklevel: int = 2):
        logging.debug(msg, stacklevel=stacklevel)
        if print_input_args:
            input_args = LogSystem.log_input_args()
            logging.debug(input_args, stacklevel=stacklevel)

    @staticmethod
    def log_info(msg: str, stacklevel: int = 2):
        logging.info(msg, stacklevel=stacklevel)

    @staticmethod
    def log_warning(msg: str, stacklevel: int = 2):
        logging.warning(msg, stacklevel=stacklevel)
    @staticmethod
    def log_error(msg: str, stacklevel: int = 2):
        logging.error(msg, stacklevel=stacklevel)

    @staticmethod
    def log_critical(msg: str, stacklevel: int = 2):
        logging.critical(msg, stacklevel=stacklevel)

"""
@namespace cmd_util
@brief	Namespace for command-related utilities. 명령 관련 유틸리티를 위한 네임스페이스
"""
class ErrorCommandSystem(Exception): pass
class CommandSystem:
    @staticmethod
    def launch_proper(level: int = None, log_file_fullpath: Optional[str] = None):
        LogSystem.start_logger(level, log_file_fullpath)
        CommandSystem.ensure_admin_running()
        

    @staticmethod
    def exit_proper(msg=None, is_proper=False):
        if msg == None:
            msg = "process completed properly" if is_proper else "process finished with errors"
        if is_proper:
            LogSystem.log_info(msg)
            LogSystem.end_logger()
            GuiManager.show_msg_box(msg, 'Info')
            sys.exit(0)
        else:
            LogSystem.log_error(msg)
            LogSystem.end_logger(True)
            GuiManager.show_msg_box(msg, 'Error')
            sys.exit(1)

    @staticmethod
    def ensure_admin_running() -> bool: # 운영체제에 따라 관리자 권한 확인
        if os.name == 'posix':  # Unix 계열 (Linux, macOS)
            is_window = False
            is_admin = os.getuid() == 0
        elif os.name == 'nt':  # Windows
            is_window = True
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            is_window = False
            is_admin = False

        if is_window:
            if not is_admin:
                LogSystem.log_error("이 스크립트는 관리자 권한으로 실행되어야 합니다. 관리자 권한으로 다시 실행하세요.")
                raise PermissionError("이 스크립트는 관리자 권한으로 실행되어야 합니다. 관리자 권한으로 다시 실행하세요.")
            else:
                LogSystem.log_info("관리자 권한으로 실행 중입니다.")
                return True
        else:
            LogSystem.log_error("지원되지 않는 운영체제입니다.")
            raise OSError("지원되지 않는 운영체제입니다.")

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
        _, stdout, _ = cmd_utils.run_command(cmd, shell=shell)
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
            return cmd_utils.run_command(elevated_cmd, shell=True)
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
            result = cmd_utils.run_command(cmd, shell=shell)
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
    def is_exe() -> bool: # exe로 패키징 되었는지 확인
        return bool(getattr(sys, "frozen", False))

    """
    @brief  Re-run the script with administrator privileges. 관리자 권한으로 스크립트를 다시 실행합니다.
    """
    def restart_as_admin():
        if ctypes.windll.shell32.IsUserAnAdmin():
            return  # 이미 관리자 권한으로 실행 중이면 아무 작업도 하지 않음

        # 관리자 권한으로 실행하기 위한 명령어 생성
        params = ' '.join([f'"{arg}"' for arg in sys.argv])
        executable = sys.executable
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", executable, params, None, 1
            )
            CommandSystem.exit_proper("관리자 권한으로 재실행 중입니다...")

        except Exception as e:
            CommandSystem.exit_proper(f"관리자 권한으로 실행하는 데 실패했습니다: {e}")

    """
    @brief  Get the filename of the first executing script. 현재 실행 중인 스크립트의 파일명을 반환합니다.
    @return Filename as a string 파일명을 문자열로 반환
    """
    def get_main_script_fullpath(stack_depth: int = 0) -> str:
        main_file_fullpath = sys.executable if FileSystem.is_exe() else sys.argv[0]
        return os.path.abspath(main_file_fullpath)
        
    def get_main_script_path_name_extension() -> Tuple[str, str, str]:
        main_file_fullpath = sys.executable if FileSystem.is_exe() else sys.argv[0]
        main_dir = os.path.dirname(os.path.abspath(main_file_fullpath))
        main_file_name, file_extension = os.path.splitext(os.path.basename(main_file_fullpath))
        return main_dir, main_file_name, file_extension.lstrip('.')

    def get_current_script_fullpath(stack_depth: int = 0) -> str:
        # Get the caller's file path
        caller_frame = inspect.stack()[1 + stack_depth]  # The caller's stack frame
        current_file_path = os.path.abspath(caller_frame.filename)  # The caller's file path
        if FileSystem.check_file(current_file_path):
            return current_file_path
        else:
            CommandSystem.exit_proper(f"src not found: {current_file_path}")

    def get_current_script_path_name_extension(stack_depth: int = 1) -> Tuple[str, str, str]:
        current_file_path = FileSystem.get_current_script_fullpath(stack_depth)
        current_dir = os.path.abspath(os.path.dirname(current_file_path))
        current_file_name, file_extension = os.path.splitext(os.path.basename(current_file_path))
        return current_dir, current_file_name, file_extension.lstrip('.')

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
    def ensure_cmd_installed(package_name: Optional[str], global_check: bool = False) -> bool:
        try:
            def _install_missing(package_name: Optional[str]) -> bool:
                LogSystem.log_info(f"Module '{package_name}' is not installed or not found in PATH.")
                if package_name == 'python':
                    _success = InstallSystem.PythonRelated.install_python_global()
                elif package_name == 'pip':
                    _success = InstallSystem.PythonRelated.install_pip_global(global_execute=global_check, upgrade=True)
                elif package_name == 'pyinstaller':
                    _success = InstallSystem.PythonRelated.install_pyinstaller_global(global_execute=global_check, upgrade=True)
                else:
                    LogSystem.log_error(f"Automatic installation for '{package_name}' is not supported.")
                    _success = False                
                if _success:
                    LogSystem.log_info(f"Module '{package_name}' installed successfully.")
                return _success
            
            # Determine the Python executable based on global_check flag
            if package_name == 'python':
                cmd = ['python', '--version']
            else:
                python_executable = "python" if global_check else sys.executable
                cmd = [python_executable, '-m', package_name, '--version']

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if result.returncode == 0:
                msg = result.stdout.strip()
                if msg != "":
                    LogSystem.log_info(f"{msg}")  # Log stdout as info
                
                msg_err = result.stderr.strip()
                if msg_err != "":
                    LogSystem.log_error(f"{msg_err}")  # Log stderr as error

                    if "No module named" in msg_err:
                        _install_complete = _install_missing(package_name)
                    else:
                        LogSystem.log_error(f"Can't handle error of {package_name} which is not 'No module named'.")
                        _install_complete = False
                else:
                    LogSystem.log_info(f"Module '{package_name}' is already installed.")
                    _install_complete = True
            else:
                _install_complete = _install_missing(package_name)
            return _install_complete
            
            
        except FileNotFoundError:  # Command not found
            return _install_missing(package_name)
            
        except Exception as e:  # Other unexpected errors
            LogSystem.log_error(f"[ERROR] Unexpected error checking {package_name}: {str(e)}")
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
    def check_file(path_file: str, stacklevel: int = 2) -> bool:
        c_path_file = Path(path_file)
        if c_path_file.exists():
            size_bytes = c_path_file.stat().st_size
            if size_bytes >= 1024 * 1024:  # 1 MB 이상
                size_mb = size_bytes / (1024 * 1024)  # 파일 크기를 MB로 변환
                size_info = f"{size_mb:.2f} MB"
            elif size_bytes >= 1024:  # 1 KB 이상
                size_kb = size_bytes / 1024  # 파일 크기를 KB로 변환
                size_info = f"{size_kb:.2f} KB"
            else:  # 1 KB 미만
                size_info = "1 KB"
            LogSystem.log_info(f"File exists: {c_path_file}, Size: {size_info}", stacklevel=stacklevel)
            return True
        else:
            LogSystem.log_info(f"File does not exist: {c_path_file}", stacklevel=stacklevel)
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


"""
@namespace install
@brief	Namespace for installation-related utilities. 설치 관련 유틸리티를 위한 네임스페이스
"""
class ErrorInstallSystem(Exception): pass
class InstallSystem:
    def fetch_url_to_json(api_url: str) -> Union[list, dict]:
        try:
            with urllib.request.urlopen(api_url) as response:
                if response.status == 200:
                    return json.loads(response.read())
                else:
                    raise InstallSystem.ErrorPythonRelated(f"Failed to fetch data from API (HTTP {response.status})")
        except InstallSystem.ErrorPythonRelated as e:
            raise InstallSystem.ErrorPythonRelated(f"Error fetching data from URL: {str(e)}")

    class ErrorPackageManager(ErrorInstallSystem): pass
    class PackageManager:
        class ErrorWingetRelated(ErrorInstallSystem): pass
        class WingetRelated:
            pass
        class ErrorChocoRelated(ErrorInstallSystem): pass
        class ChocoRelated:
            pass
    
    class ErrorPythonRelated(ErrorInstallSystem): pass
    class PythonRelated:
        def get_url_latest_python_with_filename() -> Tuple[str, str]:
            api_url = "https://www.python.org/api/v2/downloads/release/"
            list_releases = InstallSystem.fetch_url_to_json(api_url)
            for dict_release in list_releases:
                if dict_release["is_published"]:
                    for file in dict_release["files"]:
                        if "amd64.exe" in file["url"]:
                            file_name = file["url"].split("/")[-1]
                            return file["url"], file_name
            raise InstallSystem.ErrorPythonRelated("Failed to fetch the latest Python URL")

        """
        @brief	Download and run the Python installer to install Python. Python 설치 프로그램을 다운로드하고 실행하여 Python을 설치합니다.
        @return	bool
        """
        def install_python_global() -> bool:
            try:
                python_url, python_filename = InstallSystem.PythonRelated.get_url_latest_python_with_filename()
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
            except InstallSystem.ErrorPythonRelated as e:
                LogSystem.log_error(f"[ERROR] {str(e)}")
                return False
            except Exception as e:
                LogSystem.log_error(f"[ERROR] Failed to install Python: {str(e)}")
                return False

        """
        @brief	Install pip globally or temporarily. pip를 전역 또는 임시로 설치합니다.
        @param	global_execute	Whether to install pip globally (True) or temporarily (False) pip를 전역에 설치할지 여부 (True: 전역, False: 임시)
        @return	True if pip is successfully installed, False otherwise pip가 성공적으로 설치되면 True, 아니면 False
        """
        def install_pip_global(global_execute: bool = True) -> bool:
            try:
                # Check if python is installed if global_execute is True
                FileSystem.ensure_cmd_installed('python') if global_execute else None

                # Determine the Python executable based on global_execute flag
                python_executable = "python" if global_execute else sys.executable

                if subprocess.run([python_executable, '-m', 'ensurepip', '--upgrade'], capture_output=True, text=True, check=True).returncode == 0:
                    return subprocess.run([python_executable, '-m', 'pip', '--version'], capture_output=True, text=True, check=True).returncode == 0
                else:
                    return False
                
            except Exception as e:
                LogSystem.log_error(f"Failed to install pip: {e}")
                return False

        """
        @brief	Install PyInstaller globally. PyInstaller를 전역에 설치합니다.
        @param	version	    Specific version to install (optional) 설치할 특정 버전 (선택사항)
        @param	upgrade	    Upgrade if already installed (default: False) 이미 설치된 경우 업그레이드 여부 (기본값: False)
        @return	Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
        @throws	InstallPyError: If installation fails 설치 실패 시
        """
        def install_pyinstaller_global(
            global_execute: bool = True,
            upgrade: bool = False,
            version: Optional[str] = None,
            ) -> bool:
            try:
                # Check if pip is installed
                FileSystem.ensure_cmd_installed('pip')

                # Determine the Python executable based on global_execute flag
                python_executable = "python" if global_execute else sys.executable

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
            if FileSystem.check_file(path_script):
                # python -m PyInstaller --clean --onefile  (--console) (--icon /icon.ico) (--add-data /pathRsc:tempName) /pathTarget.py
                try:
                    # Determine the Python executable based on related_install_global flag
                    installed_pyinstaller = FileSystem.ensure_cmd_installed('pyinstaller', global_check=related_install_global)
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
            else:
                CommandSystem.exit_proper(f"Target script for exe build not found: {path_script}")


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
                from threading import Lock
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
                success = InstallSystem.PythonRelated.install_pyinstaller_global(global_execute=False)
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

    class ErrorGitRelated(ErrorInstallSystem): pass
    class GitRelated:
        def install_choco_global_via_winget(global_execute: bool = True) -> bool:
            if sys.platform == 'win32':
                cmd_install_choco = [
                    'winget',
                    'install',
                    '--id', 
                    'Chocolatey.Chocolatey',
                    '-e',
                    '--silent'
                ]
                if subprocess.run(cmd_install_choco, check=True).returncode == 0:
                    return InstallSystem.GitRelated.install_git_global_choco_via_choco()
                else:
                    return False

        def install_git_global_via_choco(global_execute: bool = True) -> bool:
            try:
                # ensure chocolatey via winget            

                # ensure git via chocolatey
                if sys.platform == 'win32':                            
                    # ensure git via chocolatey
                    cmd_install_git = [
                        'choco',
                        'install',
                        'git',
                        '-y'
                    ]
                    if subprocess.run(cmd_install_git, check=True).returncode == 0:
                        return subprocess.run(['git', '--version'], check=True).returncode == 0
                    else:
                        return False
                else:
                    LogSystem.log_error("Git installation via Chocolatey is only implemented for Windows.")
                    return False
            except InstallSystem.ErrorInstallSystem as e:
                LogSystem.log_error(f"Failed to install Git: {str(e)}")
                return False

        def install_git_global(global_execute: bool = True) -> bool:
            try:
                if sys.platform == 'win32':                            
                    # Download Git for Windows installer
                    git_url = "https://github.com/git-for-windows/git/releases/latest/download/Git-2.42.0-64-bit.exe"
                    git_installer_path = Path.home() / "Downloads" / "Git-Installer.exe"
                    FileSystem.download_url(git_url, str(git_installer_path))

                    # Run the installer silently
                    cmd_install_git = [
                        str(git_installer_path),
                        "/VERYSILENT",
                        "/NORESTART"
                    ]
                    subprocess.run(cmd_install_git, check=True)
                    # Determine the Python executable based on global_execute flag
                    python_executable = "python" if global_execute else sys.executable

                    if subprocess.run([python_executable, '-m', 'ensurepip', '--upgrade'], capture_output=True, text=True, check=True).returncode == 0:
                        return subprocess.run([python_executable, '-m', 'pip', '--version'], capture_output=True, text=True, check=True).returncode == 0
                    else:
                        return False
                else:
                    LogSystem.log_error("Git installation is only implemented for Windows.")
                    return False
        
            except InstallSystem.ErrorInstallSystem as e:
                LogSystem.log_error(f"Failed to install Git: {str(e)}")
                return False


    class ErrorVcpkgRelated(ErrorInstallSystem): pass
    class VcpkgRelated:
        def install_vcpkg_global(global_execute: bool = True) -> bool:            
            main_file_fullpath = FileSystem.get_main_script_fullpath()
            script_dir = os.path.dirname(os.path.abspath(main_file_fullpath))
            vcpkg_json = os.path.join(script_dir, 'vcpkg.json')
            if not FileSystem.file_exists(vcpkg_json):
                CommandSystem.exit_proper("vcpkg.json 파일이 없습니다. 설치를 중지합니다.")

            # 1. vcpkg 폴더 & 실행파일 확인/설치
            vcpkg_dir = os.path.join(script_dir, 'vcpkg')
            vcpkg_exe = os.path.join(vcpkg_dir, 'vcpkg.exe')

            if not (FileSystem.directory_exists(vcpkg_dir) and FileSystem.file_exists(vcpkg_exe)):
                LogSystem.log_info("vcpkg 설치가 필요합니다.")
                git_root = FileSystem.find_git_root(script_dir)
                if not git_root:
                    CommandSystem.exit_proper(".git 폴더 경로를 찾을 수 없습니다.")
                
                # .git의 상위 폴더(vcpkg 설치할 위치)
                vcpkg_dir = os.path.join(os.path.dirname(git_root), 'vcpkg')
                
                if not FileSystem.directory_exists(vcpkg_dir):
                    LogSystem.log_info(f"git clone https://github.com/microsoft/vcpkg.git \"{vcpkg_dir}\"")
                    if not cmd_utils.run_command(f"git clone https://github.com/microsoft/vcpkg.git \"{vcpkg_dir}\""):
                        CommandSystem.exit_proper("vcpkg 클론 실패")
                
                vcpkg_exe = os.path.join(vcpkg_dir, 'vcpkg.exe')
                
                # bootstrap 실행
                if not FileSystem.file_exists(vcpkg_exe):
                    bootstrap_bat = os.path.join(vcpkg_dir, 'bootstrap-vcpkg.bat')
                    if not cmd_utils.run_command(f"\"{bootstrap_bat}\"", cwd=vcpkg_dir):
                        CommandSystem.exit_proper("bootstrap-vcpkg.bat 실패")
                        

            # 2. 환경변수에 path_vcpkg 추가
            _success = EnvvarSystem.ensure_global_env_pair('path_vcpkg', vcpkg_dir,  global_scope=True, permanent=True)

            # 3. vcpkg install
            cmd = f"\"{vcpkg_exe}\" install --triplet x64-windows"
            returncode, stdout, stderr = cmd_utils.run_command(cmd, cwd=script_dir)



"""
@namespace environment variables
@brief	Namespace for environment variable-related utilities. 환경 변수 관련 유틸리티를 위한 네임스페이스
"""
class ErrorEnvvarSystem(Exception): pass
class EnvvarSystem:
    USER_SCOPE = 'HKCU\\Environment'
    GLOBAL_SCOPE = 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'

    def generate_env_name_from_main_script(prefix: Optional[str] = None, suffix: Optional[str] = None) -> str:
        main_file_path, main_file_name, file_extension = FileSystem.get_main_script_path_name_extension()
        return f"{f'{prefix}_' if prefix else ''}{main_file_name}{f'_{suffix}' if suffix else ''}"

    def generate_env_name_from_current_script(prefix: Optional[str] = None, suffix: Optional[str] = None) -> str:
        current_file_path, current_file_name, file_extension = FileSystem.get_current_script_path_name_extension(2)
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

            except ErrorEnvvarSystem:
                pass

        if key is None or not os.path.isdir(os.environ.get(key)):
            CommandSystem.exit_proper(f"환경변수 'path_jfw_py'에 py_sys_script 폴더 경로가 세팅되어 있지 않거나, 경로가 잘못되었습니다.")

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
                        
            except ErrorEnvvarSystem:
                pass

        return env_keys if env_keys else None
    
    def extract_registry_value(query_output: str) -> Optional[str]:
        for line in query_output.splitlines():
            if 'REG_' in line:
                parts = line.split(None, 2)
                if len(parts) >= 3:
                    return parts[2]
        return None

    def ensure_env_var_set(scope, key, value = None) -> bool:
        query = EnvvarSystem.extract_registry_value(subprocess.run(['reg', 'query', scope, '/v', key], capture_output=True, text=True).stdout)
        if value == None:
            if query != None:
                os.environ[key] = query
                return True
            else:
                LogSystem.log_info(f"re-setting 'path_jfw_py' env var first, before build exe.")
                return False
        else:
            if query == value:
                os.environ[key] = value
                return True
            else:
                LogSystem.log_info(f"re-setting 'path_jfw_py' env var first, before build exe.")
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
                    scope = EnvvarSystem.USER_SCOPE if not global_scope else EnvvarSystem.GLOBAL_SCOPE
                    subprocess.run(['reg', 'add', scope, '/v', key, '/t', 'REG_SZ', '/d', value, '/f'], capture_output=True, check=True)
                    EnvvarSystem.ensure_env_var_set(scope, key, value)
                else:
                    # On Unix-like systems, would need to modify shell config files
                    shell_config = os.path.expanduser('~/.bashrc') if not global_scope else '/etc/environment'
                    with open(shell_config, 'a') as f:
                        f.write(f'\nexport {key}="{value}"\n')
            
                return True
            
        except ErrorEnvvarSystem:
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
                        scope = EnvvarSystem.USER_SCOPE if not global_scope else EnvvarSystem.GLOBAL_SCOPE
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
        
        except ErrorEnvvarSystem as e:
            LogSystem.log_error(f"Failed to clear env vars: {e}")
            return False

    def ensure_global_env_pair_to_Path(key: str, value: str, global_scope: bool = True, permanent: bool = True) -> bool:
        try:
            if sys.platform == 'win32':
                # Determine the registry scope
                scope = EnvvarSystem.USER_SCOPE if not global_scope else EnvvarSystem.GLOBAL_SCOPE
                
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
                                LogSystem.log_error(f"Environment variable '{var_name}' not found for entry '{entry}'")
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
        
        except ErrorEnvvarSystem as e:
            LogSystem.log_error(f"Failed to add {key} to Path: {e}")
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
            dict_check_reg_value_key = EnvvarSystem.get_global_env_keys_by_path(value) # dictionary of key-value pairs
            if dict_check_reg_value_key is None:
                varialbe_ok = EnvvarSystem.set_global_env_pair(key, value, global_scope, permanent)    
            elif len(dict_check_reg_value_key) == 1 and key in dict_check_reg_value_key:
                varialbe_ok = True
                pass
            else: # multiple and different keys with same value
                varialbe_ok = EnvvarSystem.clear_global_env_pair_by_key_or_pairs(dict_check_reg_value_key) and \
                EnvvarSystem.set_global_env_pair(key, value, global_scope, permanent)

            to_path_ok = EnvvarSystem.ensure_global_env_pair_to_Path(key, value, global_scope, permanent)

            success_ = varialbe_ok and to_path_ok
            LogSystem.log_info(f"환경변수 '{key}' 설정 {'성공' if success_ else '실패'}")    
            return success_
        
        except ErrorEnvvarSystem as e:
            LogSystem.log_error(f"환경변수 '{key}' 설정 실패: {e}")
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
            dll_dir = GuiManager.root.joinpath(dll_subpath).resolve()
            if dll_dir.exists():
                try:
                    os.add_dll_directory(str(dll_dir))
                except Exception:
                    # os.add_dll_directory may not be available on very old Python versions
                    pass


"""
@namespace gui system
@brief	Namespace for GUI-related utilities. GUI 관련 유틸리티를 위한 네임스페이스
"""
_gui_system_root_instance = None
_gui_system_mainloop_running = False
class ErrorGuiManager(Exception): pass
class GuiManager(common.SingletonBase):
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        if not hasattr(instance, "_initialized"):
            # init flag
            instance._initialized = True

            # root
            instance.root = tkinter.Tk()
            instance.GuiManager.root.withdraw()

            # mainloop
            instance.mainloop_running = False
        return instance


    # Singleton instance for the Tk root window
    def get_root():
        return GuiManager().root

    def run_mainloop():
        GuiManager.mainloop_running = True
        GuiManager().GuiManager.root.mainloop()
        
    class GuiType(Enum):
        MSG_BOX = "message_box" # 모달
        FILE_DLG = "file_dialog" # 모달
        INPUT_DLG = "input_dialog" # 모달
        CONFIRM_DLG = "confirm_dialog" # 모달
        COLOR_DLG = "color_dialog" # 모달
        SAVE_FILE_DLG = "save_file_dialog" # 모달
        POPUP_CTT_MENU = "popup_context_menu" # 논모달
        SCROLL_TEXT_WND = "scroll_text_window" # 논모달
        PROGRESS_BAR_WND = "progress_bar_window" # 논모달
        TREE_VIEW_WND = "tree_view_window" # 논모달
        CANVAS_WND = "canvas_window" # 논모달
        TOPLEVEL_SUB_WND = "toplevel_sub_window" # 논모달
        MAIN_WND = "main_window" # 논모달


    def show_msg_box(message, title="Info"):
        try:        
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            title = f"{title} ({current_time})"    
            
            GuiManager.root.attributes('-topmost', True)  # 메시지 박스를 최상위로 설정
            tkinter.messagebox.showinfo(title, message)
            GuiManager.root.attributes('-topmost', False)  # 최상위 설정 해제
            
        except Exception as e:
            LogSystem.log_error(f"show_msg_box error: {e}")

    def show_file_dialog(title="Select a file") -> str:
        try:
            file_path = filedialog.askopenfilename(title=title)
            return file_path
        except Exception as e:
            LogSystem.log_error(f"show_file_dialog error: {e}")
            return ""

    def show_input_dialog(prompt="Please enter something:", title="Input") -> str:
        try:
            user_input = tkinter.simpledialog.askstring(title, prompt)
            return user_input
        except Exception as e:
            LogSystem.log_error(f"show_input_dialog error: {e}")
            return None

    def show_confirm_dialog(message="Do you want to proceed?", title="Confirm") -> bool:
        try:
            result = tkinter.messagebox.askyesno(title, message)
            return result
        except Exception as e:
            LogSystem.log_error(f"show_confirm_dialog error: {e}")
            return False

    def show_color_dialog(title="Choose a color") -> str:
        try:
            color_code = tkinter.colorchooser.askcolor(title=title)[1]
            return color_code
        except Exception as e:
            LogSystem.log_error(f"show_color_dialog error: {e}")
            return ""

    def show_save_file_dialog(title="Save file as") -> str:
        try:
            file_path = filedialog.asksaveasfilename(title=title)
            return file_path
        except Exception as e:
            LogSystem.log_error(f"show_save_file_dialog error: {e}")
            return ""

    def show_popup_context_menu(root, options=None):
        try:
            if options is None:
                options = [("Option 1", None), ("Option 2", None), ("Exit", GuiManager.root.quit)]

            def popup(event):
                popup_menu.post(event.x_root, event.y_root)

            popup_menu = tkinter.Menu(root, tearoff=0)
            for label, command in options:
                if label == "separator":
                    popup_menu.add_separator()
                else:
                    popup_menu.add_command(label=label, command=command)

            GuiManager.root.bind("<Button-3>", popup)
            GuiManager.root.deiconify()
            GuiManager.run_mainloop()

        except Exception as e:
            LogSystem.log_error(f"show_popup_context_menu error: {e}")

    def show_scroll_text_window(title="Scroll Text Window"):
        try:
            top = tkinter.Toplevel(GuiManager.root)
            top.title(title)
            text_area = tkinter.Text(top, wrap="word")
            scroll_bar = tkinter.Scrollbar(top, command=text_area.yview)
            text_area.configure(yscrollcommand=scroll_bar.set)
            text_area.pack(side="left", fill="both", expand=True)
            scroll_bar.pack(side="right", fill="y")

        except Exception as e:
            LogSystem.log_error(f"show_scroll_text_window error: {e}")

    def show_progress_bar_window(progress_value=50, title="Progress Bar Window"):
        try:
            top = tkinter.Toplevel(GuiManager.root)
            top.title(title)
            progress = Progressbar(top, orient="horizontal", length=200, mode="determinate")
            progress.pack(pady=20)
            progress["value"] = progress_value

        except Exception as e:
            LogSystem.log_error(f"show_progress_bar_window error: {e}")

    def show_tree_view_window(columns=("one", "two"), items=None, title="Tree View Window"):
        try:
            if items is None:
                items = [("", "end", "Item 1", ("Value 1", "Value 2"))]
            top = tkinter.Toplevel(GuiManager.root)
            top.title(title)
            tree = Treeview(top)
            tree["columns"] = columns
            tree.heading("#0", text="Item")
            for col in columns:
                tree.heading(col, text=f"Column {col}")
            for parent, index, text, values in items:
                tree.insert(parent, index, text=text, values=values)
            tree.pack(fill="both", expand=True)

        except Exception as e:
            LogSystem.log_error(f"show_tree_view_window error: {e}")

    def show_canvas_window(width=200, height=100, shapes=None, title="Canvas Window"):
        try:
            if shapes is None:
                shapes = [("rectangle", (50, 25, 150, 75), {"fill": "blue"})]

            GuiManager.root.title(title)
            canvas = tkinter.Canvas(GuiManager.root, width=width, height=height)
            canvas.pack()
            for shape, coords, options in shapes:
                getattr(canvas, f"create_{shape}")(*coords, **options)
            GuiManager.root.deiconify()
            GuiManager.run_mainloop()

        except Exception as e:
            LogSystem.log_error(f"show_canvas_window error: {e}")

    def show_toplevel_window(message="This is a Toplevel window", title="TopLevel Window"):
        try:
            top = tkinter.Toplevel(GuiManager.root)
            top.title(title)
            tkinter.Label(top, text=message).pack()

        except Exception as e:
            LogSystem.log_error(f"show_toplevel_window error: {e}")

    def show_main_window(message="This is the main window", title="Main Window"):
        try:
            GuiManager.root.deiconify()
            GuiManager.root.title(title)
            tkinter.Label(GuiManager.root, text=message).pack()
            GuiManager.run_mainloop()
            
        except Exception as e:
            LogSystem.log_error(f"show_main_window error: {e}")


    

