"""
File System Utilities
파일 시스템 유틸리티

This module provides utility functions for file system operations.
파일 시스템 작업을 위한 유틸리티 함수들을 제공합니다.
"""
# Standard Library Imports
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
import threading
from enum import IntEnum

from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Callable, Union, Set
from dataclasses import dataclass

from sys_util_core.jutils import TextUtils

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
    stt_time_f: float = 0.0
    cur_time_f: float = 0.0
    end_time_f: float = 0.0

    @staticmethod
    def start_logger(level: int = None, log_file_fullpath: Optional[str] = None):
        _t =LogSystem.get_stt_time_str_ymdhms(True, True)
        LogSystem.setup_logger(level, log_file_fullpath)
        LogSystem.log_info(f"process started at {_t}")

    @staticmethod
    def end_logger(is_proper: bool = True):
        elapsed_time_f = LogSystem.elapsed_time_f(end = True if LogSystem.end_time_f == 0.0 else False)
        LogSystem.log_info(f"process completed properly in {elapsed_time_f:.2f} seconds" if is_proper else f"process exited with errors in {elapsed_time_f:.2f} seconds")
        logging.shutdown()

    @staticmethod
    def format_ymd_hms(dt: datetime, ymd: bool = True, hms: bool = True) -> str:
        format_str = ""
        if ymd:
            format_str += "%Y-%m-%d"
        if hms:
            if ymd:
                format_str += " "
            format_str += "%H:%M:%S"
        return dt.strftime(format_str)    
    
    @staticmethod
    def get_stt_time_f() -> float:
        if LogSystem.stt_time_f == 0.0:
            LogSystem.stt_time_f = time.time()
        return LogSystem.stt_time_f
    @staticmethod
    def get_stt_time() -> datetime:
        return datetime.fromtimestamp(LogSystem.get_stt_time_f())
    @staticmethod
    def get_stt_time_str_ymdhms(ymd: bool = True, hms: bool = True) -> str:
        return LogSystem.format_ymd_hms(LogSystem.get_stt_time(), ymd, hms)
    
    @staticmethod
    def get_cur_time_f() -> float:
        LogSystem.cur_time_f = time.time()
        return LogSystem.cur_time_f
    @staticmethod
    def get_cur_time() -> datetime:
        return datetime.fromtimestamp(LogSystem.get_cur_time_f())    
    @staticmethod
    def get_cur_time_str_ymdhms(ymd: bool = True, hms: bool = True) -> str:
        return LogSystem.format_ymd_hms(LogSystem.get_cur_time(), ymd, hms)
    
    
    @staticmethod
    def elapsed_time_f(end: bool = False) -> float:
        return (LogSystem.end_time_f if end else LogSystem.cur_time_f) - LogSystem.stt_time_f
    @staticmethod
    def elapsed_time() -> datetime:
        return datetime.fromtimestamp(LogSystem.elapsed_time_f())
    @staticmethod
    def elapsed_time_str_ymdhms(ymd: bool = False, hms: bool = True) -> str:
        return LogSystem.format_ymd_hms(LogSystem.elapsed_time(), ymd, hms)
    
    @staticmethod
    def get_end_time_f() -> float:
        if LogSystem.end_time_f == 0.0:
            LogSystem.end_time_f = LogSystem.get_cur_time_f()
        return LogSystem.end_time_f
    @staticmethod
    def get_end_time() -> datetime:
        return datetime.fromtimestamp(LogSystem.get_end_time_f())
    @staticmethod
    def get_end_time_str_ymdhms(ymd: bool = True, hms: bool = True) -> str:
        return LogSystem.format_ymd_hms(LogSystem.get_end_time(), ymd, hms)

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
    def log_debug(msg: str, print_input_args: bool = True, f_back: int = 0):
        logging.debug(msg.strip(), stacklevel=f_back)
        if print_input_args:
            input_args = LogSystem.log_input_args()
            logging.debug(input_args.strip(), stacklevel=f_back+3)
    @staticmethod
    def log_info(msg: str, f_back: int = 0):
        logging.info(msg.strip(), stacklevel=f_back+3)

    @staticmethod
    def log_warning(msg: str, f_back: int = 0):
        logging.warning(msg.strip(), stacklevel=f_back+3)
    @staticmethod
    def log_error(msg: str, f_back: int = 0):
        logging.error(msg.strip(), stacklevel=f_back+3)

    @staticmethod
    def log_critical(msg: str, f_back: int = 0):
        logging.critical(msg.strip(), stacklevel=f_back+3)
"""
@namespace cmd_util
@brief	Namespace for command-related utilities. 명령 관련 유틸리티를 위한 네임스페이스
"""

class ErrorCmdSystem(Exception): pass
class CmdSystem:
    class ReturnCode(IntEnum): # .name shall get string name
        SUCCESS = 0
        ERROR_GENERAL = 1
        ERROR_FILE_NOT_FOUND = 2
        ERROR_PATH_NOT_FOUND = 3
        ERROR_ACCESS_DENIED = 5
        ERROR_COMMAND_NOT_FOUND = 9009
        ERROR_OTHER_EXCEPTION = -1

    
    @dataclass
    class Result:
        returncode: 'CmdSystem.ReturnCode'
        stdout: str = ""
        stderr: str = ""
        def is_success(self) -> bool:
            return self.returncode == CmdSystem.ReturnCode.SUCCESS
        def is_error(self) -> bool:
            return self.returncode != CmdSystem.ReturnCode.SUCCESS

    def run(
            cmd: Union[str, List[str]],
            f_back: int = 1,
            stdin: Optional[str] = None,
            timeout: Optional[int] = None,
            specific_working_dir: Optional[str] = None,
            cumstem_env: Optional[Dict[str, str]] = None 
        ) -> Result:
        try:
            LogSystem.log_info(f"| cmd.exe | {' '.join(cmd) if isinstance(cmd, list) else cmd}", f_back)
            sentense_or_list = isinstance(cmd, str)
            cmd_ret: CmdSystem.Result = subprocess.run(
                cmd,
                input=stdin,
                timeout=timeout,
                shell=sentense_or_list,
                cwd=specific_working_dir, # Working directory
                env=cumstem_env, # Environment variables or path
                capture_output=True, # Capture stdout and stderr
                text=True, # Decode output as string (UTF-8)
                check=True, # Raise exception on non-zero exit
            )
            ret_code = cmd_ret.returncode
            ret_out = cmd_ret.stdout.strip() if cmd_ret.stdout else ""
            ret_err = cmd_ret.stderr.strip() if cmd_ret.stderr else ""
        except subprocess.CalledProcessError as e:
            ret_code = e.returncode
            ret_out = e.stdout.strip() if e.stdout else ""
            ret_err = e.stderr.strip() if e.stderr else ""
        except subprocess.TimeoutExpired as e:
            ret_code = CmdSystem.ReturnCode.ERROR_OTHER_EXCEPTION
            ret_out = ""
            ret_err = f"Command timed out after {timeout} seconds"
        except Exception as e:
            ret_code = CmdSystem.ReturnCode.ERROR_OTHER_EXCEPTION
            ret_out = ""
            ret_err = str(e).strip()
        finally:
            rc = CmdSystem.ReturnCode(ret_code)
            LogSystem.log_info(f"| cmd.ret | {rc.name} ({rc})", f_back)
            if ret_out:
                LogSystem.log_info(f"| cmd.out | {ret_out}", f_back)
            if ret_err:
                LogSystem.log_error(f"| cmd.err | {ret_err}", f_back)
            return CmdSystem.Result(ret_code, ret_out, ret_err)



    """
    @brief	Execute a command and stream output in real-time. 명령어를 실행하고 실시간으로 출력을 스트리밍합니다.
    @param	cmd	    Command to execute 실행할 명령어
    @param	shell	Whether to execute through shell 셸을 통해 실행할지 여부
    @param	cwd	    Working directory 작업 디렉토리
    @param	env	    Environment variables 환경 변수
    @yields Line-by-line output from the command 명령어의 줄 단위 출력
    """
    def run_streaming(
            cmd: Union[str, List[str]],
            shell: bool = False,
            specific_working_dir: Optional[str] = None,
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
            cwd=specific_working_dir,
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
    def get_where(program_name: str) -> Optional[str]:
        try:
            if sys.platform == 'win32':
                cmd_ret: CmdSystem.Result = CmdSystem.run(['where', program_name])
                if cmd_ret.is_success() and cmd_ret.stdout:
                    for line in cmd_ret.stdout.strip().splitlines():
                        if os.path.exists(line):
                            return line  # 실제 존재하는 첫 번째 경로 반환
                return None
            else:
                cmd_ret: CmdSystem.Result = CmdSystem.run(['which', program_name])
                if cmd_ret.is_error(): return None
                return cmd_ret.stdout.strip() if cmd_ret.stdout else None
        except ErrorCmdSystem as e:
            LogSystem.log_error(f"where '{program_name}' not found: {e}")
            return None

    def get_version(package_name: Optional[str], global_check: bool = False) -> Optional[str]:
        try:
            if package_name in ['git', 'python']:
                cmd = [package_name, '--version']
            elif package_name in ['pip', 'PyInstaller']:
                python_executable = "python" if global_check else sys.executable
                cmd = [python_executable, '-m', package_name, '--version']
            else:
                raise ValueError(f"version check of this package is unsupported.")
            cmd_ret: CmdSystem.Result = CmdSystem.run(cmd)
            _ret = TextUtils.extract_version(cmd_ret.stdout) if cmd_ret.is_success() else None
            return _ret
        except Exception as e:  # Other unexpected errors
            LogSystem.log_error(f"{package_name}: {str(e)}")
            return None
    """
    @brief	Execute a command asynchronously and return the process object. 명령어를 비동기로 실행하고 프로세스 객체를 반환합니다.
    @param	cmd	    Command to execute 실행할 명령어
    @param	shell	Whether to execute through shell 셸을 통해 실행할지 여부
    @param	cwd	    Working directory 작업 디렉토리
    @param	env	    Environment variables 환경 변수
    @return	Process object 프로세스 객체
    """
    def run_async(
            cmd: Union[str, List[str]],
            shell: bool = False,
            specific_working_dir: Optional[str] = None,
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
            cwd=specific_working_dir,
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
                cmd = ['taskkill', '/F', '/IM', process_name]
            else:
                cmd = ['pkill', '-9', process_name]

            cmd_ret: CmdSystem.Result = CmdSystem.run(cmd)
            if cmd_ret.is_error(): return False
            
            # Verify the process is actually killed by checking if it's still running
            if sys.platform == 'win32':
                cmd = ['tasklist', '/FI', f'IMAGENAME eq {process_name}']
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd)
                if cmd_ret.is_error(): return False
                return "No tasks are running" in cmd_ret.stdout or process_name not in cmd_ret.stdout
            else:
                cmd = ['pgrep', '-x', process_name]
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd)
                if cmd_ret.is_error(): return False
                return cmd_ret.returncode != CmdSystem.ReturnCode.SUCCESS
                
        except Exception as e:
            LogSystem.log_error(f"Failed to kill process '{process_name}': {e}")
            return False

    """
    @brief	Get list of running processes. 실행 중인 프로세스 목록을 가져옵니다.
    @return	List of dictionaries containing process information 프로세스 정보를 담은 딕셔너리 리스트
    """
    def get_process_list() -> Optional[List[Dict[str, str]]]:    
        try:
            processes = []
            if sys.platform == 'win32':
                cmd_ret: CmdSystem.Result = CmdSystem.run(['tasklist', '/FO', 'CSV', '/NH'])
                if cmd_ret.is_error(): return None
                for line in cmd_ret.stdout.strip().split('\n'):
                    if line:
                        parts = line.replace('"', '').split(',')
                        if len(parts) >= 2:
                            processes.append({
                                'name': parts[0],
                                'pid': parts[1]
                            })
            else:
                cmd_ret: CmdSystem.Result = CmdSystem.run(['ps', 'aux'])
                if cmd_ret.is_error(): return None                
                for line in cmd_ret.stdout.strip().split('\n')[1:]:
                    parts = line.split()
                    if len(parts) >= 11:
                        processes.append({
                            'user': parts[0],
                            'pid': parts[1],
                            'name': parts[10]
                        })
            return processes
        except Exception as e:
            LogSystem.log_error(f"Failed to get process list: {e}")
            return None
        


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
            cmd_ret: CmdSystem.Result = CmdSystem.run(cmd)
            results.append(cmd_ret)
            
            if stop_on_error and cmd_ret.is_error():
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
            sys.exit(0)  # 관리자 권한으로 재실행 후 현재 프로세스 종료, exit_proper

        except Exception as e:
            sys.exit(f"관리자 권한으로 실행하는 데 실패했습니다: {e}") # exit_proper


    #def get_cpp_sln_beside

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
            raise ErrorFileSystem(f"Current script path not found: {current_file_path}") # exit_proper

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
    def ensure_installed(package_name: Optional[str], global_check: bool = False) -> bool:
        try:
            if CmdSystem.get_version(package_name, global_check):
                _success = True
            else:
                # possiblity_1, not installed, try to install
                c_path = InstallSystem.install_global(package_name, global_check)
                # possiblity_2, PATH issue, try to set PATH and check again
                if c_path:
                    envvar_name = f"path_{package_name.lower()}"
                    is_pathed = EnvvarSystem.ensure_global_envvar(envvar_name, str(c_path),  global_scope=True, permanent=True)

                _success = is_pathed and bool(CmdSystem.get_version(package_name, global_check))
            return _success
        except Exception as e:  # Other unexpected errors
            LogSystem.log_error(f"Unexpected error checking {package_name}: {str(e)}")
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
        except Exception as e:
            LogSystem.log_error(f"Failed to create directory: {path}, Error: {str(e)}")
            return False


    """
    @brief	Delete a directory. 디렉토리를 삭제합니다.
    @param	path	    Path to delete 삭제할 경로
    @param	recursive	Delete recursively including contents 내용물을 포함하여 재귀적으로 삭제
    @return	True if successful, False otherwise 성공하면 True, 실패하면 False
    """
    def delete_directory(path: str, recursive: bool = True) -> bool:
        try:
            if FileSystem.directory_exists(path) == False:
                LogSystem.log_warning(f"Directory does not exist: {path}")
                return False
            if recursive:
                shutil.rmtree(path)
            else:
                os.rmdir(path)
            return True
        except Exception as e:
            raise ErrorFileSystem(f"Failed to delete directory: {str(e)}") # exit_proper


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
        try:
            return os.path.isfile(path)
        except Exception as e:
            LogSystem.log_error(f"Error checking file existence: {path}, Error: {str(e)}")
            return False


    """
    @brief	Check if a directory exists. 디렉토리가 존재하는지 확인합니다.
    @param	path	Directory path to check 확인할 디렉토리 경로
    @return	True if exists, False otherwise 존재하면 True, 아니면 False
    """
    def directory_exists(path: str) -> bool:
        try:
            return os.path.isdir(path)
        except Exception as e:
            LogSystem.log_error(f"Error checking directory existence: {path}, Error: {str(e)}")
            return False


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
    def check_file(path_file: str, f_back: int = 0) -> bool:
        c_path_file = Path(path_file)
        if c_path_file.exists():
            size_bytes = c_path_file.stat().st_size
            size_info = FileSystem.format_size(size_bytes)
            LogSystem.log_info(f"File exists: {c_path_file}, Size: {size_info}", f_back)
            return True
        else:
            LogSystem.log_info(f"File does not exist: {c_path_file}", f_back)
            return False

    def get_tree_size(path):
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += FileSystem.get_tree_size(entry.path)
        except Exception: pass
        return total

    def format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    def monitor_vcpkg_size(stop_event: threading.Event, vcpkg_dir: Optional[str] = None):
        download_dir = os.path.join(vcpkg_dir, 'downloads')
        build_dir = os.path.join(vcpkg_dir, 'buildtrees')
        installed_dir = os.path.join(vcpkg_dir, 'installed')
        
        print(f"Monitoring vcpkg directories:\n - Downloads: {download_dir}\n - Build: {build_dir}")

        while not stop_event.is_set():
            d_size = FileSystem.get_tree_size(download_dir) if os.path.exists(download_dir) else 0
            b_size = FileSystem.get_tree_size(build_dir) if os.path.exists(build_dir) else 0
            i_size = FileSystem.get_tree_size(installed_dir) if os.path.exists(installed_dir) else 0
            
            # vcpkg는 '전체 용량'을 미리 알려주지 않으므로, 현재 용량 증가를 보여줍니다.
            msg = f"[Status] Downloads: {FileSystem.format_size(d_size)} | BuildTemp: {FileSystem.format_size(b_size)} | Installed: {FileSystem.format_size(i_size)}"
            print(msg)
            time.sleep(5)

    # ---------------------------------------
    # LogSystem.log_info(f"Running vcpkg install... Output will be streamed.")
    
    # stop_monitor = threading.Event()
    # t = threading.Thread(target=monitor_vcpkg_size, args=(stop_monitor,))
    # t.daemon = True
    # t.start()

    # try:
    #     # Stream output line by line
    #     process = subprocess.Popen(
    #         cmd_install_vcpkg,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.STDOUT,
    #         text=True,
    #         cwd=main_file_path,
    #         encoding='utf-8', 
    #         errors='replace'
    #     )
        
    #     for line in iter(process.stdout.readline, ''):
    #         if line:
    #             print(line.rstrip())
        
    #     process.wait()
    #     stop_monitor.set()
    #     t.join(timeout=1)
        
    #     if process.returncode == 0:
    #         return Path(core_install_root)
    #     else:
    #         LogSystem.log_error(f"vcpkg install failed with return code {process.returncode}")
    #         return None
    # except Exception as e:
    #     stop_monitor.set()
    #     LogSystem.log_error(f"vcpkg install error: {e}")
    #     return None

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


    def find_git_root(start_dir: str) -> Optional[str]:
        cur = os.path.abspath(start_dir)
        root = os.path.abspath(os.sep)
        while True:
            git_path = os.path.join(cur, '.git')
            if os.path.isdir(git_path):
                return Path(cur)
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
    @param	timeout	    Timeout in seconds (default: 600) 타임아웃 (초)
    @return	None
    """
    def download_url(url: str, save_path: str, timeout: int = 600) -> None:
        # If save_path is a string and looks like a path (contains / or \), convert to Path
        if isinstance(save_path, str) and not ("/" in save_path or "\\" in save_path):
            save_path = Path.home() / "Downloads" / save_path
        if not FileSystem.file_exists(save_path):
            LogSystem.log_info(f"Downloading from: {url}...")
            try:
                #urllib.request.urlretrieve(url, save_path)
                with urllib.request.urlopen(url, timeout=timeout) as response, open(save_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                LogSystem.log_info(f"Saved to: {save_path}")
            except Exception as e:
                LogSystem.log_error(f"Download failed: {e}")
                raise e
        else:
            LogSystem.log_info(f"File already exists: {save_path}")

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
            LogSystem.log_info(f"Downloading from: {url}...")
            CmdSystem.run(cmd_download_python)
            LogSystem.log_info(f"Saved to: {save_path}")
        else:
            LogSystem.log_info(f"File already exists: {save_path}")

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
    
    def install_global(package_name: Optional[str], global_execute = False) -> Optional[Path]:
        LogSystem.log_info(f"Module '{package_name}' is not installed or not found in PATH.")
        if package_name == 'git':
            c_path = InstallSystem.WingetRelated.install_git_global(global_execute)
        elif package_name == 'python':
            c_path = InstallSystem.PythonRelated.install_python_global()
        elif package_name == 'pip':
            c_path = InstallSystem.PythonRelated.install_pip_global(global_execute, upgrade=True)
        elif package_name == 'pyinstaller':
            c_path = InstallSystem.PythonRelated.install_pyinstaller_global(global_execute, upgrade=True)
        elif package_name == 'vcpkg':
            c_path = InstallSystem.VcpkgRelated.install_vcpkg_global(global_execute)
        else:
            LogSystem.log_error(f"Automatic installation for '{package_name}' is not supported.")
            raise ErrorInstallSystem(f"Package install unsupported: '{package_name}'.")
        
        LogSystem.log_info(f"Module '{package_name}' installed successfully." if c_path else f"Failed to install module '{package_name}'.")
        return c_path

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

        def install_python_global() -> Optional[Path]:
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
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_install_python)
                return CmdSystem.get_where('python') if cmd_ret.is_success() else None
            except InstallSystem.ErrorPythonRelated as e:
                LogSystem.log_error(f"{str(e)}")
                return None
            except Exception as e:
                LogSystem.log_error(f"Failed to install Python: {str(e)}")
                return None

        """
        @brief	Install pip globally or temporarily. pip를 전역 또는 임시로 설치합니다.
        @param	global_execute	Whether to install pip globally (True) or temporarily (False) pip를 전역에 설치할지 여부 (True: 전역, False: 임시)
        @return	True if pip is successfully installed, False otherwise pip가 성공적으로 설치되면 True, 아니면 False
        """
        def install_pip_global(global_execute: bool = True, upgrade: bool = False) -> Optional[Path]:
            try:
                # undercover
                FileSystem.ensure_installed('python') if global_execute else None

                # execute
                cmd_install_pip = [
                    'python' if global_execute else sys.executable,
                    '-m',
                    'ensurepip',
                    '--upgrade' if upgrade else ''
                ]
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_install_pip)
                return CmdSystem.get_where('pip') if cmd_ret.is_success() else None                
            except Exception as e:
                LogSystem.log_error(f"Failed to install pip: {e}")
                return None

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
            ) -> Optional[Path]:
            try:
                # undercover
                FileSystem.ensure_installed('pip')

                # execute
                cmd_install_pyinstaller = [
                    'python' if global_execute else sys.executable,
                    '-m',
                    'pip',
                    'install',
                    'pyinstaller' + (f'=={version}' if version else ''),
                    '--upgrade' if upgrade else ''
                ]                
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_install_pyinstaller)
                return CmdSystem.get_where('PyInstaller') if cmd_ret.is_success() else None
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
                global_execute: bool = False,
                onefile: bool = True,
                console: bool = True,
            ) -> bool:
            if FileSystem.check_file(path_script):
                # python -m PyInstaller --clean --onefile  (--console) (--icon /icon.ico) (--add-data /pathRsc:tempName) /pathTarget.py
                try:
                    if not FileSystem.ensure_installed('PyInstaller', global_check=global_execute):
                        raise InstallSystem.ErrorPythonRelated("PyInstaller is not installed or not found in PATH.")
                    
                    # Determine the Python executable based on global_execute flag
                    python_executable = "python" if global_execute else sys.executable                    
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
                    if CmdSystem.run(cmd).is_success():  # 0 means no stderr
                        return FileSystem.check_file(f"dist/{c_path_script.stem}.exe")
                
                except Exception as e:
                    error_msg = f"Unexpected error building executable: {str(e)}"
                    raise InstallSystem.ErrorPythonRelated(error_msg)
            else:
                raise InstallSystem.ErrorPythonRelated(f"Target script for exe build not found: {path_script}") #exit_proper


        """
        @brief	Clean PyInstaller build artifacts. PyInstaller 빌드 아티팩트를 정리합니다.
        @param	path_script	    Path to script (for finding .spec file) 스크립트 경로 (spec 파일 찾기용)
        @param	remove_dist	    Remove dist directory dist 디렉토리 제거
        @param	remove_build	Remove build directory build 디렉토리 제거
        @param	remove_spec	    Remove .spec file .spec 파일 제거
        @return	Tuple of (success: bool, message: str) (성공 여부, 메시지) 튜플
        """
        def clean_build_files_with_pyinstaller(
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
            
            
    class ErrorWingetRelated(ErrorInstallSystem): pass
    class WingetRelated:
        def install_git_global(global_execute: bool = True) -> Optional[Path]:
            try:
                if sys.platform == 'win32':
                    cmd_install_git = [
                        "winget",
                        "install",
                        "--id",
                        "Git.Git",
                        "--silent",
                        "--accept-package-agreements",
                        "--accept-source-agreements"
                    ]
                    cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_install_git)
                    return CmdSystem.get_where('git') if cmd_ret.is_success() else None
                else:
                    raise NotImplementedError("Git installation is only implemented for Windows.")
            except InstallSystem.ErrorWingetRelated as e:
                LogSystem.log_error(f"Failed to install Git: {str(e)}")
                return None


    class ErrorVcpkgRelated(ErrorInstallSystem): pass
    class VcpkgRelated:
        def install_vcpkg_global(global_execute: bool = True) -> Optional[Path]:
            # 1. git 설치 확인/설치
            _success = FileSystem.ensure_installed('git', global_check=global_execute)
            if not _success:
                raise InstallSystem.ErrorVcpkgRelated("Git 설치 실패")
            
            # 2. vcpkg.json 확인
            main_file_path, main_file_name, file_extension = FileSystem.get_main_script_path_name_extension()
            vcpkg_json = os.path.join(main_file_path, 'vcpkg.json')
            if not FileSystem.file_exists(vcpkg_json):
                raise InstallSystem.ErrorVcpkgRelated("vcpkg.json 파일이 없습니다. 설치를 중지합니다.") #exit_proper

            # 3. vcpkg 설치할 위치 확인 및 설치 - .git의 상위 폴더
            # > git clone https://github.com/microsoft/vcpkg.git "%path_vcpkg%"
            git_root = FileSystem.find_git_root(main_file_path)
            if not git_root:
                raise InstallSystem.ErrorVcpkgRelated(".git 폴더 경로를 찾을 수 없습니다.") #exit_proper            
            vcpkg_dir = os.path.join(os.path.dirname(git_root), 'vcpkg')
            if not FileSystem.directory_exists(vcpkg_dir):
                LogSystem.log_info("vcpkg 설치가 필요합니다.")
                cmd_ret: CmdSystem.Result = CmdSystem.run(f"git clone https://github.com/microsoft/vcpkg.git \"{vcpkg_dir}\"")
                if cmd_ret.is_error() or not FileSystem.directory_exists(vcpkg_dir):
                    raise InstallSystem.ErrorVcpkgRelated("vcpkg 클론 실패") #exit_proper                
            
            # 4. 설치후 빌드 - bootstrap 실행
            # > %path_vcpkg%\bootstrap-vcpkg.bat
            vcpkg_exe = os.path.join(vcpkg_dir, 'vcpkg.exe')
            if not FileSystem.file_exists(vcpkg_exe):
                bootstrap_bat = os.path.join(vcpkg_dir, 'bootstrap-vcpkg.bat')
                cmd_ret: CmdSystem.Result = CmdSystem.run(f"\"{bootstrap_bat}\"", specific_working_dir=vcpkg_dir)
                if cmd_ret.is_error() or not FileSystem.file_exists(vcpkg_exe):
                    raise InstallSystem.ErrorVcpkgRelated("bootstrap-vcpkg.bat 실패") #exit_proper
                        
            # 5. 환경변수에 %path_vcpkg% 추가
            _success = EnvvarSystem.ensure_global_envvar('path_vcpkg', vcpkg_dir,  global_scope=True, permanent=True)
            if not _success:
                raise InstallSystem.ErrorVcpkgRelated("환경변수 path_vcpkg 등록 실패") #exit_proper

            # 6. vcpkg.exe install 실행
            # > cd %path_vcpkg%
            # > %path_vcpkg%\vcpkg install --triplet x64-windows
            # > %path_vcpkg%\vcpkg export zlib tesseract --raw --output C:\path\to\myproject\vcpkg_installed
            core_install_root = os.path.join(vcpkg_dir, 'installed')
            cmd_install_vcpkg = [
                vcpkg_exe,
                'install',
                '--triplet',
                'x64-windows',
                '--x-install-root',
                core_install_root
            ]
            cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_install_vcpkg, specific_working_dir=main_file_path)
            return Path(core_install_root) if cmd_ret.is_success() else None
        
        def integrate_vcpkg_to_visualstudio() -> bool:
            # > %path_vcpkg%\vcpkg integrate install
            env_path = EnvvarSystem.get_global_env_path('path_vcpkg')
            cmd_integrate_install = [os.path.join(env_path, 'vcpkg.exe'), 'integrate', 'install']
            cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_integrate_install)
            return cmd_ret.is_success()
        
        def integrate_vcpkg_to_vcxproj(vcxproj_files: Optional[Union[str, List[str]]] = None) -> bool:
            try:
                if vcxproj_files is None: # find all vcxproj in main dir
                    main_dir = FileSystem.get_main_script_path_name_extension()[0]
                    vcxproj_files = FileSystem.list_files(main_dir, '*.vcxproj', recursive=True)
                elif isinstance(vcxproj_files, str):
                    vcxproj_files = [vcxproj_files]
                elif not isinstance(vcxproj_files, list):
                    raise InstallSystem.ErrorVcpkgRelated("vcxproj_files 인자는 문자열 또는 문자열 리스트여야 합니다.") #exit_proper
                
                env_path = EnvvarSystem.get_global_env_path('path_vcpkg') # check path_vcpkg if raised error
                vcpkg_targets_path = os.path.join('$(path_vcpkg)', 'scripts', 'buildsystems', 'msbuild', 'vcpkg.targets')
                
                _success = True
                for vcxproj_path in vcxproj_files:
                    try:
                        with open(vcxproj_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if 'vcpkg.targets' in content:
                            LogSystem.log_info(f"vcpkg.targets already imported in {vcxproj_path}")
                        else:
                            target_line = '<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.targets" />'
                            import_line = f'<Import Project="{vcpkg_targets_path}" Condition="exists(\'{vcpkg_targets_path}\')" />'
                            
                            if target_line in content:
                                target_index = content.find(target_line)
                                line_start_index = content.rfind('\n', 0, target_index) + 1
                                indentation = content[line_start_index:target_index]
                                
                                replacement = f'{target_line}\n{indentation}{import_line}'
                                new_content = content.replace(target_line, replacement)
                                with open(vcxproj_path, 'w', encoding='utf-8') as f:
                                    f.write(new_content)
                                LogSystem.log_info(f"Successfully integrated vcpkg to {vcxproj_path}")
                            else:
                                raise InstallSystem.ErrorVcpkgRelated(f"Target import line not found in {vcxproj_path}")
                    except Exception as e:
                        LogSystem.log_error(f"Error processing {vcxproj_path}: {str(e)}")
                        _success = False
                return _success
            except Exception as e:
                LogSystem.log_error(f"Failed to integrate vcpkg to vcxproj: {str(e)}")
                return False

        def setup_vcpkg_extra() -> bool:
            try:
                main_file_path, main_file_name, file_extension = FileSystem.get_main_script_path_name_extension()
                vcpkg_json = os.path.join(main_file_path, 'vcpkg.json')
                if not FileSystem.file_exists(vcpkg_json):
                    raise InstallSystem.ErrorVcpkgRelated("vcpkg.json 파일이 없습니다. 설치를 중지합니다.") #exit_proper
                
                with open(vcpkg_json, 'r', encoding='utf-8') as f:
                    vcpkg_data = json.load(f)

                if 'dependencies' not in vcpkg_data:
                    raise InstallSystem.ErrorVcpkgRelated("vcpkg.json에 'dependencies' 항목이 없습니다.")  # exit_proper

                dependencies = vcpkg_data['dependencies']
                if not isinstance(dependencies, list):
                    raise InstallSystem.ErrorVcpkgRelated("'dependencies' 항목이 리스트 형식이 아닙니다.")  # exit_proper

                for dependency in dependencies:
                    if not isinstance(dependency, str):
                        LogSystem.log_warning(f"'{dependency}'는 지원되지 않는 형식입니다. 문자열이어야 합니다.")
                        continue
                    if dependency.lower() == 'openssl':
                        # 예: 환경 변수 설정, 추가 파일 복사 등
                        LogSystem.log_info("OpenSSL extra configuration completed.")
                    elif dependency.lower() == 'boost':
                        # 예: 환경 변수 설정, 추가 파일 복사 등
                        LogSystem.log_info("Boost extra configuration completed.")
                    elif dependency.lower() == 'tesseract':
                        # 언어팩 환경변수 설정 및 설치
                        env_path = EnvvarSystem.get_global_env_path('path_vcpkg')
                        tessdata_parent = f"{env_path}\\installed\\x64-windows\\share"
                        tessdata_dir = f"{tessdata_parent}\\tessdata"
                        EnvvarSystem.ensure_global_envvar(
                            'TESSDATA_PREFIX',
                            #tessdata_parent,
                            tessdata_dir,
                            global_scope=True, permanent=True, with_path=False
                        )
                        
                        langs = ['eng', 'kor', 'chi_tra']#, 'jpn', 'chi_sim']  # 필요한 언어팩 리스트
                        base_url = 'https://github.com/tesseract-ocr/tessdata/raw/main'
                        #base_url = 'https://raw.githubusercontent.com/tesseract-ocr/tessdata/main'
                        for lang in langs:
                            tesseract_data_url = f'{base_url}/{lang}.traineddata'
                            save_path = f'{tessdata_dir}\\{lang}.traineddata'
                            FileSystem.download_url(tesseract_data_url, save_path)
                        
                        LogSystem.log_info("Tesseract extra configuration completed.")
                    elif dependency.lower() == 'opencv':
                        # 예: 환경 변수 설정, 추가 파일 복사 등
                        LogSystem.log_info("OpenCV extra configuration completed.")
                    else:
                        LogSystem.log_warning(f"Do not support extra-setup for '{dependency}', It may require manual configuration.")
                return True
            except InstallSystem.ErrorVcpkgRelated as e:
                LogSystem.log_error(f"Failed to setup vcpkg extra: {str(e)}")
                return False

        def clear_vcpkg_global() -> Optional[str]:
            try:
                # Core\vcpkg\buildtrees, downloads, packages 폴더 삭제
                main_file_path, main_file_name, file_extension = FileSystem.get_main_script_path_name_extension()
                git_root = FileSystem.find_git_root(main_file_path)
                if not git_root:
                    raise InstallSystem.ErrorVcpkgRelated(".git 폴더 경로를 찾을 수 없습니다.") #exit_proper
                
                c_cpp_vcpkg = Path(git_root).parent / 'vcpkg'
                buildtrees_dir = str(c_cpp_vcpkg / 'buildtrees')
                downloads_dir = str(c_cpp_vcpkg / 'downloads')
                packages_dir = str(c_cpp_vcpkg / 'packages')
                rm_core1 = FileSystem.delete_directory(buildtrees_dir)
                rm_core2 = FileSystem.delete_directory(downloads_dir)
                rm_core3 = FileSystem.delete_directory(packages_dir)

                # Project\vcpkg_installed 폴더 삭제
                proj_installed_dir = str(Path(main_file_path) / 'vcpkg_installed')
                rm_proj = FileSystem.delete_directory(proj_installed_dir)
                core_installed_dir = str(c_cpp_vcpkg / 'installed')
                rm_core = FileSystem.delete_directory(core_installed_dir)

                missing, deleted, msgs = [], [], []
                deleted.append(buildtrees_dir) if rm_core1 else missing.append(buildtrees_dir)
                deleted.append(downloads_dir) if rm_core2 else missing.append(downloads_dir)
                deleted.append(packages_dir) if rm_core3 else missing.append(packages_dir)
                deleted.append(proj_installed_dir) if rm_proj else missing.append(proj_installed_dir)
                if deleted: msgs.append(f"\n__Success to delete__\n" + "\n".join(deleted) + "\n")
                if missing: msgs.append(f"\n__Passing no directory__\n" + "\n".join(missing) + "\n")
                return ", ".join(msgs)
            except Exception as e:
                LogSystem.log_error(f"Unexpected error clearing vcpkg: {str(e)}")
                return None
            
        def delete_vcpkg_global() -> bool:
            try:
                # git clone한 vcpkg 폴더 자체를 전체 삭제
                git_root = FileSystem.find_git_root(os.getcwd())
                if not git_root:
                    raise InstallSystem.ErrorVcpkgRelated(".git 폴더 경로를 찾을 수 없습니다.") #exit_proper
                rm_vcpkg = FileSystem.delete_directory(str(Path(git_root).parent / 'vcpkg'))

                # Project\vcpkg_installed 폴더 삭제
                main_file_path, main_file_name, file_extension = FileSystem.get_main_script_path_name_extension()
                rm_proj = FileSystem.delete_directory(str(Path(main_file_path) / 'vcpkg_installed'))
                return rm_vcpkg and rm_proj
            except InstallSystem.ErrorVcpkgRelated as e:
                LogSystem.log_error(f"Failed to delete vcpkg: {str(e)}")
            except Exception as e:
                LogSystem.log_error(f"Unexpected error deleting vcpkg: {str(e)}")
                return False        
            
"""
@namespace environment variables
@brief	Namespace for environment variable-related utilities. 환경 변수 관련 유틸리티를 위한 네임스페이스
"""
class ErrorEnvvarSystem(Exception):
    def __init__(self, message):
        LogSystem.log_error(str(message), 1)
        super().__init__(message)
class EnvvarSystem:
    USER_SCOPE = 'HKCU\\Environment'
    GLOBAL_SCOPE = 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'

    def generate_env_name_from_main_script(prefix: Optional[str] = None, suffix: Optional[str] = None) -> str:
        main_file_path, main_file_name, file_extension = FileSystem.get_main_script_path_name_extension()
        return f"{f'{prefix}_' if prefix else ''}{main_file_name}{f'_{suffix}' if suffix else ''}"

    def generate_env_name_from_current_script(prefix: Optional[str] = None, suffix: Optional[str] = None) -> str:
        current_file_path, current_file_name, file_extension = FileSystem.get_current_script_path_name_extension(2)
        return f"{f'{prefix}_' if prefix else ''}{current_file_name}{f'_{suffix}' if suffix else ''}"

    def get_global_env_path(key: str) -> Optional[str]:
        try:
            dict_env = EnvvarSystem.get_global_env_keydict_by_key(key)
            if not dict_env:
                raise ErrorEnvvarSystem(f"환경변수 {key} 가 존재하지 않습니다.") #exit_proper
            else:
                return dict_env[key]

        except ErrorEnvvarSystem as e:
            LogSystem.log_error(f"Error querying system environment variable '{key}': {e}")
            return None

    def get_global_env_keydict_by_key(key: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        @brief	Get system-wide environment variables (Windows only). 시스템 전체 환경 변수를 가져옵니다 (Windows 전용).
        @return	Dictionary of system environment variables 시스템 환경 변수 딕셔너리
        """
        dict_envvars = {}
        if sys.platform == 'win32':
            cmd_query_global_envvar = [
                'reg',
                'query',
                EnvvarSystem.GLOBAL_SCOPE
            ]
            cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_query_global_envvar)
            if cmd_ret.is_error():
                dict_envvars = None
            else:
                for line in cmd_ret.stdout.splitlines():
                    line = line.strip()
                    if 'REG_' in line: # REG_SZ, REG_EXPAND_SZ
                        parts = line.split(None, 2) # Format: <key> <type> <value>
                        if len(parts) == 3:
                            var, typ, val = parts
                            dict_envvars[var.strip()] = val.strip()
                        elif len(parts) == 2:
                            var, typ = parts
                            dict_envvars[var.strip()] = ''
                if key:
                    keypath_pair = {key: dict_envvars.get(key, None)}
                    dict_envvars = keypath_pair if keypath_pair[key] is not None else None
            return dict_envvars
        else:
            raise ErrorEnvvarSystem("get_global_env_keydict_by_key is only implemented for Windows.")

    def get_global_env_keydict_by_path(path: str) -> Optional[Dict[str, None]]:    
        dict_env_keys = {}
        if sys.platform == 'win32':
            cmd_query_global_envvar = [
                'reg',
                'query',
                EnvvarSystem.GLOBAL_SCOPE
            ]
            cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_query_global_envvar)
            if cmd_ret.is_success():
                for line in cmd_ret.stdout.splitlines():
                    line = line.strip()
                    if 'REG_' in line: # REG_SZ, REG_EXPAND_SZ
                        parts = line.split(None, 2) # Format: <key> <type> <value>
                        if len(parts) == 3 and parts[2].strip() == path:
                            dict_env_keys[parts[0].strip()] = None
                return dict_env_keys if dict_env_keys else None
            else:
                raise ErrorEnvvarSystem("Failed to query global environment variables.")
        else:
            raise ErrorEnvvarSystem("get_global_env_keydict_by_path is only implemented for Windows.")
        
    def extract_registry_value(query_output: str) -> Optional[str]:
        for line in query_output.splitlines():
            if 'REG_' in line:
                parts = line.split(None, 2)
                if len(parts) >= 3:
                    return parts[2]
        return None

    def ensure_envvar_set(scope, key, value = None) -> bool:
        try:
            if sys.platform == 'win32':
                cmd_query_global_envvar = [
                    'reg', 'query', scope,
                    '/v', # value
                    key # key name
                ]
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_query_global_envvar)
                if cmd_ret.is_success():
                    query_value = EnvvarSystem.extract_registry_value(cmd_ret.stdout)
                    if value == None and query_value != None:
                        os.environ[key] = query_value
                        return True
                    if value != None and query_value == value:
                        os.environ[key] = value
                        return True
                    LogSystem.log_info(f"re-setting 'path_jfw_py' env var first, before build exe.")
                    return False
                else:
                    raise ErrorEnvvarSystem(f"Env var '{key}' not found in scope '{scope}'")
            else:
                raise ErrorEnvvarSystem("ensure_envvar_set is only implemented for Windows.")
        except ErrorEnvvarSystem as e:
            LogSystem.log_error(f"Error querying system environment variables: {e}")
            return False

    def set_global_envvar(
        key: str,
        value: str,
        global_scope: bool = True,
        permanent: bool = True,
        ) -> bool:
        try:        
            if permanent:
                if sys.platform == 'win32':
                    scope = EnvvarSystem.USER_SCOPE if not global_scope else EnvvarSystem.GLOBAL_SCOPE
                    cmd_set_global_envvar = [
                        'reg', 'add', scope,
                        '/v', # value name
                        key, # key
                        '/t', # type
                        'REG_SZ', # type string
                        '/d', # data
                        value, # value data
                        '/f' # force
                    ]                    
                    cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_set_global_envvar)
                    return EnvvarSystem.ensure_envvar_set(scope, key, value) if cmd_ret.is_success() else False
                else:
                    # On Unix-like systems, would need to modify shell config files
                    shell_config = os.path.expanduser('~/.bashrc') if not global_scope else '/etc/environment'
                    with open(shell_config, 'a') as f:
                        f.write(f'\nexport {key}="{value}"\n')
                    return True
            else:
                raise ErrorEnvvarSystem("Non-permanent env var setting not implemented")
        except ErrorEnvvarSystem as e:
            LogSystem.log_error(f"Failed to set env var: {e}")
            return False
        
    def clear_global_envvar_by_key_or_keylist(keys: Union[List[str], str], global_scope: bool = True, permanent: bool = True) -> bool:
        try:
            if sys.platform != 'win32':
                raise ErrorEnvvarSystem("clear_global_envvar_by_key_or_keylist is only implemented for Windows.")

            if not permanent:
                raise ErrorEnvvarSystem("Non-permanent env var deletion not implemented")

            if isinstance(keys, list):
                keys_to_delete = keys
            elif isinstance(keys, str):
                keys_to_delete = [keys]
            else:
                raise ErrorEnvvarSystem("Invalid type for keys parameter")

            scope = EnvvarSystem.USER_SCOPE if not global_scope else EnvvarSystem.GLOBAL_SCOPE
            is_cmd_all = True
            for key in keys_to_delete:
                cmd_ret: CmdSystem.Result = CmdSystem.run(['reg', 'delete', scope, '/v', key, '/f'])
                is_cmd_all = False if cmd_ret.is_error() else is_cmd_all
            
            if not is_cmd_all:
                raise ErrorEnvvarSystem("Failed to delete one or more env vars via reg delete command.")
            
            is_deleted_all = True
            for key in keys_to_delete:
                cmd_query_global_envvar = [ 'reg', 'query', scope, '/v', key ]
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_query_global_envvar)
                if cmd_ret.is_success():
                    query_value = EnvvarSystem.extract_registry_value(cmd_ret.stdout)
                    is_deleted_all = False if query_value else is_deleted_all
            
            if not is_deleted_all:
                raise ErrorEnvvarSystem("One or more env vars still exist after deletion attempt.")
            
            return True
        except ErrorEnvvarSystem:
            raise
        except Exception as e:
            raise ErrorEnvvarSystem(f"Failed to clear env vars: {e}")

    def ensure_global_envvar_to_Path(key: str, value: str, global_scope: bool = True, permanent: bool = True) -> bool:
        try:
            if sys.platform == 'win32':
                
                # Get the current Path value
                scope = EnvvarSystem.USER_SCOPE if not global_scope else EnvvarSystem.GLOBAL_SCOPE
                cmd_ret: CmdSystem.Result = CmdSystem.run(
                    ['reg', 'query', scope, '/v', 'Path']
                )
                if cmd_ret.is_success():                
                    current_path = ""
                    for line in cmd_ret.stdout.splitlines():
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
                            match = re.search(r'%([^%]+)%', entry) # Extract variable name from patterns like %VAR% or %VAR%/bin or %VAR%\something
                            if match:
                                var_name = match.group(1)
                                var_value = os.environ.get(var_name, value)
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
                    
                    def order_seq_envvar(entry): # Sort the entries based on the defined priorities
                        if entry.lower() == "%systemroot%": # SystemRoot and System32 should always come first
                            return (0, entry)
                        elif entry.lower() == "%systemroot%\\system32":
                            return (1, entry)
                        elif entry.lower().startswith("%systemroot%"):
                            return (2, entry)  # Other SystemRoot-related paths
                        elif entry.startswith("%"): #and entry.endswith("%"):
                            return (4, entry)  # Environment variables last
                        else:
                            return (3, entry)  # Custom paths in the middle
                    sorted_entries = sorted(unique_entries, key=order_seq_envvar)
                    new_path = ";".join(sorted_entries)

                    # Update the Path variable (NEEDS ADMIN PRIVILEGES FOR GLOBAL SCOPE)
                    cmd_ret: CmdSystem.Result = CmdSystem.run(
                        ['reg', 'add', scope, '/v', 'Path', '/t', 'REG_SZ', '/d', new_path, '/f']
                    )
                    return True if cmd_ret.is_success() else False
                else:
                    return False
            else:
                raise ErrorEnvvarSystem("ensure_global_envvar_to_Path is only implemented for Windows.")
        except ErrorEnvvarSystem as e:
            LogSystem.log_error(f"Failed to add {key} to Path: {e}")
            return False

    def ensure_clear_global_envvar(key: str, path: str, global_scope: bool = True, permanent: bool = True) -> bool:
        """
        @brief	Ensure a global system-wide environment variable is cleared. 시스템 전체 환경 변수가 정리되어 있는지 확인합니다.
        @param	key	Name of the environment variable 환경 변수 이름
        @param	path	path to clear 정리할 값
        @param	permanent	Whether to clear permanently (system-wide) 영구적으로 정리할지 여부 (시스템 전체)
        @return	True if successful, False otherwise 성공하면 True, 실패하면 False
        """
        try:
            key_dict = EnvvarSystem.get_global_env_keydict_by_path(path) # dictionary of key-path pairs
            path = EnvvarSystem.get_global_env_path(key) # dictionary of key-path pairs
            if key_dict is not None and path is not None: 
                key_dict[key] = path
            elif key_dict is None and path:
                key_dict = {key: path} # key 존재
            elif key_dict and path is None: 
                pass # key_dict 유지
            else:
                return True # 이미 정리된 상태
            return EnvvarSystem.clear_global_envvar_by_key_or_keylist(list(key_dict.keys()), global_scope, permanent)
        except ErrorEnvvarSystem:
            raise
        except Exception as e:
            raise Exception(f"환경변수 '{key}' 정리 실패: {e}")
        

    def ensure_global_envvar(key: str, path: str, global_scope: bool = True, permanent: bool = True, with_path: bool = True) -> bool:
        """
        @brief	Ensure a global system-wide environment variable is set. 시스템 전체 환경 변수가 설정되어 있는지 확인합니다.
        @param	key	Name of the environment variable 환경 변수 이름
        @param	path	path to set 설정할 값
        @param	permanent	Whether to set permanently (system-wide) 영구적으로 설정할지 여부 (시스템 전체)
        @return	True if successful, False otherwise 성공하면 True, 실패하면 False
        """
        # 벨류가 비존재 + 키는 존재 -> 삭제 : 키 비존재
        # 벨류가 비존재 + 키도 비존재 -> 추가 : 키 존재
        # 벨류가 존재 + 키가 여러개 -> 삭제 : 키 비존재
        # 벨류가 존재 + 키가 하나면, 키도 같은지 확인 -> 다르면 삭제 : 키 비존재
        # 벨류가 존재 + 키가 하나면, 키도 같은지 확인 -> 같으면 패스 : 키 존재
        # 키가 존재 + 값이 같은지 확인 -> 다르면 삭제 : 키 비존재
        # 키가 존재 + 값이 같은지 확인 -> 같으면 패스 : 키 존재
        # 키가 비존재 -> 추가 : 키 존재
        #____> 그냥 싹 지우기 보장후 추가
        try:
            is_clear = EnvvarSystem.ensure_clear_global_envvar(key, path, global_scope, permanent)
            is_set = EnvvarSystem.set_global_envvar(key, path, global_scope, permanent)
            if with_path:
                is_pathed = EnvvarSystem.ensure_global_envvar_to_Path(key, path, global_scope, permanent)
            success_ = is_clear and is_set and (is_pathed if with_path else True)
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
        # if dll_subpath and os.name == "nt":
        #     dll_dir = GuiManager().root.joinpath(dll_subpath).resolve()
        #     if dll_dir.exists():
        #         try:
        #             os.add_dll_directory(str(dll_dir))
        #         except Exception:
        #             # os.add_dll_directory may not be available on very old Python versions
        #             pass





