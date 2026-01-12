"""
File System Utilities
파일 시스템 유틸리티

This module provides utility functions for file system operations.
파일 시스템 작업을 위한 유틸리티 함수들을 제공합니다.
"""
# Standard Library Imports
import os, sys, subprocess
import json
import queue
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
import atexit
import threading
from concurrent.futures import Future
from enum import IntEnum

from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Callable, Union, Set
from dataclasses import dataclass

from sys_util_core.jcommon import SingletonBase
from sys_util_core.jutils import TextUtils


class JErrorSystem(Exception):
        """Base exception class for JErrorSystem."""
        def __init__(self, message):
            JLogger().log_error(str(message), 2) # where raise child errored
            super().__init__(message)


"""
@namespace log_util
@brief	Namespace for logger utilities. 로거 관련 유틸리티를 위한 네임스페이스
"""
class ErrorJLogger(JErrorSystem): pass
class JLogger(SingletonBase):
    LOG_LEVEL_DEBUG = logging.DEBUG
    LOG_LEVEL_INFO = logging.INFO
    LOG_LEVEL_WARNING = logging.WARNING
    LOG_LEVEL_ERROR = logging.ERROR
    LOG_LEVEL_CRITICAL = logging.CRITICAL

    def __init__(self):
        if not hasattr(self, "initialized"):
            self._lock = threading.RLock()
            self.stt_time_f: float = 0.0
            self.cur_time_f: float = 0.0
            self.end_time_f: float = 0.0
            self.initialized = True

    def start_most_early(self, level: int = None, log_file_fullpath: Optional[str] = None):
        with self._lock:
            _t = self.get_stt_time_str_ymdhms(True, True)
            self.setup_logger(level, log_file_fullpath)
            self.log_info(f"process started at {_t}")

    def end_most_early(self, is_proper: bool = True):
        with self._lock:
            elapsed_time_f = self.elapsed_time_f(end = True if self.end_time_f == 0.0 else False)
            self.log_info(f"process completed properly in {elapsed_time_f:.2f} seconds" if is_proper else f"process exited with errors in {elapsed_time_f:.2f} seconds")
            logging.shutdown()

    def format_ymd_hms(self, dt: datetime, ymd: bool = True, hms: bool = True) -> str:
        format_str = ""
        if ymd:
            format_str += "%Y-%m-%d"
        if hms:
            if ymd:
                format_str += " "
            format_str += "%H:%M:%S"
        return dt.strftime(format_str)    
    
    def get_stt_time_f(self) -> float:
        with self._lock:
            if self.stt_time_f == 0.0:
                self.stt_time_f = time.time()
            return self.stt_time_f
    def get_stt_time(self) -> datetime:
        return datetime.fromtimestamp(self.get_stt_time_f())
    def get_stt_time_str_ymdhms(self, ymd: bool = True, hms: bool = True) -> str:
        return self.format_ymd_hms(self.get_stt_time(), ymd, hms)
    
    def get_cur_time_f(self) -> float:
        with self._lock:
            self.cur_time_f = time.time()
            return self.cur_time_f
    def get_cur_time(self) -> datetime:
        return datetime.fromtimestamp(self.get_cur_time_f())    
    def get_cur_time_str_ymdhms(self, ymd: bool = True, hms: bool = True) -> str:
        return self.format_ymd_hms(self.get_cur_time(), ymd, hms)
    
    
    def elapsed_time_f(self, end: bool = False) -> float:
        with self._lock:
            return (self.end_time_f if end else self.cur_time_f) - self.stt_time_f
    def elapsed_time(self) -> datetime:
        return datetime.fromtimestamp(self.elapsed_time_f())
    def elapsed_time_str_ymdhms(self, ymd: bool = False, hms: bool = True) -> str:
        return self.format_ymd_hms(self.elapsed_time(), ymd, hms)
    
    def get_end_time_f(self) -> float:
        with self._lock:
            if self.end_time_f == 0.0:
                self.end_time_f = self.get_cur_time_f()
            return self.end_time_f
    def get_end_time(self) -> datetime:
        return datetime.fromtimestamp(self.get_end_time_f())
    def get_end_time_str_ymdhms(self, ymd: bool = True, hms: bool = True) -> str:
        return self.format_ymd_hms(self.get_end_time(), ymd, hms)

    def setup_logger(self, level: int = None, log_file_fullpath: Optional[str] = None):
        with self._lock:
            if level is None:
                if FileSystem.is_exe():
                    level = self.LOG_LEVEL_INFO
                else:
                    level = self.LOG_LEVEL_DEBUG

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
                ],
                force=True # Force reconfiguration of logging
            )
            self.log_info(f"Logging initialized.")

    def log_to_str(self, value):
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

    def format_args_with(self, args_name, args_value, seperate_mark: str = ", ", max_length=0):
        args_value_list = []
        for arg_name in args_name:
            value_str = self.log_to_str(args_value[arg_name]) # to_string
            if max_length > 0:
                if len(value_str) > max_length: value_str = f"{value_str[:max_length]}" # cutting
                value_str = f"{value_str:<{max_length}}" # add after aligning left with space
            args_value_list.append(value_str)
        return seperate_mark.join(args_value_list)

    def log_input_args(self):
        interest_frame = inspect.currentframe().f_back.f_back  # 두 단계 위의 프레임
        args_name, var_args_name, var_keyword_args_name, args_value = inspect.getargvalues(interest_frame)  # 인자값 추출
        arg_str = self.format_args_with(args_name, args_value)
        return f"InputArgs: ({arg_str})"
    
    def log_debug(self, msg: str, print_input_args: bool = True, f_back: int = 0):
        logging.debug(msg.strip(), stacklevel=f_back)
        if print_input_args:
            input_args = self.log_input_args()
            logging.debug(input_args.strip(), stacklevel=f_back+3)
    def log_info(self, msg: str, f_back: int = 0):
        logging.info(msg.strip(), stacklevel=f_back+3)

    def log_warning(self, msg: str, f_back: int = 0):
        logging.warning(msg.strip(), stacklevel=f_back+3)
    def log_error(self, msg: str, f_back: int = 0):
        logging.error(msg.strip(), stacklevel=f_back+3)

    def log_critical(self, msg: str, f_back: int = 0):
        logging.critical(msg.strip(), stacklevel=f_back+3)

"""
@namespace trace_util
@brief	Namespace for execution tracing utilities. 실행 추적 유틸리티를 위한 네임스페이스
"""
class ErrorJTracer(JErrorSystem): pass
class JTracer(SingletonBase):
    def __init__(self):
        if not hasattr(self, "initialized"):
            self._lock = threading.RLock() # threading.RLock(): 재귀적으로 락을 획득할 수 있는 락
            self.tracing = False # 추적 여부
            self.include_paths = [] # 추적할 파일 경로
            self.last_msg = "" # 마지막 메시지
            self.ignore_functions = {
                "log_debug", "log_info", "log_warning", "log_error", "log_critical", 
                "_safe_update_message", "update_message", "_safe_update", "update", 
                "_do_close", "close", "increment", "_inc", "<lambda>", 
                "_check_loop", "_worker"
            }
            self.initialized = True

    def _trace_callback(self, frame, event, arg):
        # event: 'call', 'line', 'return', 'exception'
        # call: 함수 호출
        # line: 함수 실행
        # return: 함수 반환
        # exception: 예외 발생
        if event == 'call':
            code = frame.f_code # 코드 객체
            
            # [Fix] Ignore non-file code objects (e.g. <frozen ...>, <string>) BEFORE abspath conversion
            # pseudo-filenames cause os.path.abspath to prepend CWD, making them look like user files.
            if code.co_filename.startswith('<'):
                return self._trace_callback

            filename = os.path.abspath(code.co_filename) # 파일 경로
            
            # Check if file is in user paths
            is_target = False
            for p in self.include_paths:
                # Use commonpath to ensure it's truly a subpath (handles case sensitivity on Windows somewhat better)
                # But startswith is faster. Let's make sure paths are normalized.
                if filename.startswith(p):
                    is_target = True
                    break
            
            if not is_target:
                return self._trace_callback

            func_name = code.co_name # 함수 이름

            # [Trace Filter] Ignore internal/special functions (starting with _)
            if func_name.startswith('_') or func_name.startswith('<'):
                return self._trace_callback
            
            if func_name in self.ignore_functions:
                return self._trace_callback

            line_no = frame.f_lineno # 라인 번호
            # Show function name and file name (shortened)
            short_filename = os.path.basename(filename)
            
            # [Feature] Show command line for CmdSystem.run
            # If function is 'run' and class is 'CmdSystem' (heuristically checks 'cmd' arg)
            if func_name == "run":
                # Get argument 'cmd'
                f_locals = frame.f_locals
                cmd_arg = f_locals.get('cmd')
                if cmd_arg:
                    # Format command string
                    if isinstance(cmd_arg, list):
                        cmd_str = ' '.join(str(x) for x in cmd_arg)
                    else:
                        cmd_str = str(cmd_arg)
                    
                    # Truncate if too long for UI
                    if len(cmd_str) >= 80:
                        spaces = [i for i, c in enumerate(cmd_str) if c == ' ']
                        if spaces:
                            idx = min(spaces, key=lambda x: abs(x - 80))
                            cmd_str = cmd_str[:idx] + "\n" + cmd_str[idx + 1:]
                        
                    msg = f"{cmd_str}\n({short_filename}:{line_no})"
                else:
                    msg = f"{func_name}\n({short_filename}:{line_no})"
            else:
                msg = f"{func_name}\n({short_filename}:{line_no})"
            
            # Avoid flickering if same
            if msg != self.last_msg:
                # Pad with spaces to clear previous long messages
                # TODO: display in GUI log window
                sys.stdout.write(f"\r{msg:<120}") 
                sys.stdout.flush()
                self.last_msg = msg

                # Notify optional GUI or other listener
                if hasattr(self, '_callback_trace') and callable(self._callback_trace):
                    try:
                        self._callback_trace(msg)
                    except Exception:
                        # callback must be robust; ignore errors
                        pass
        
        # Return self to continue tracing in this scope
        return self._trace_callback

    def start(self, root_dirs: Optional[List[str]] = None):
        """
        Start tracing function calls in the specified directories.
        지정된 디렉토리 내의 함수 호출 추적을 시작합니다.

        callback_trace: optional callable(msg: str) to receive trace messages (used to update GUI)
        """
        if root_dirs is None:
            root_dirs = [FileSystem.get_main_script_path_name_extension()[0]]
            path_jfw_py = EnvvarSystem.get_global_env_path('path_jfw_py')
            if FileSystem.directory_exists(path_jfw_py):
                root_dirs.append(path_jfw_py)
        
        with self._lock:
            self.include_paths = [os.path.abspath(p) for p in root_dirs]
            self.tracing = True
            sys.settrace(self._trace_callback) # 파이썬 인터프리터에 추적 콜백 함수를 등록, 한 줄 실행될 때마다 호출, callback(self, frame, event, arg)
            JLogger().log_info(f"JTracer started. Monitoring: {self.include_paths}")

    def stop(self):
        """
        Stop tracing.
        추적을 중지합니다.
        """
        with self._lock:
            if not self.tracing:
                return

            self.tracing = False
            
            # [Safe Guard] Ensure we don't detach an external debugger
            current_trace = sys.gettrace()
            # Only unregister if it's OUR callback (or None)
            if current_trace == self._trace_callback or current_trace is None:
                sys.settrace(None)
                sys.stdout.write("\n")
                JLogger().log_info("JTracer stopped.")
            else:
                JLogger().log_warning("JTracer stopped (External debugger detected, hook reserved).")

    def set_trace_callback(self, callback: Optional[Callable[[str], None]]):
        with self._lock:
            self._callback_trace = callback

class ErrorThreadPoolSystem(JErrorSystem): pass
class ThreadPoolSystem:
    def __init__(self, size: int = None):
        """
        Initialize the thread pool.
        쓰레드 풀을 초기화합니다.
        
        [Note on Performance]
        This implementation uses 'threading', which is subject to GIL (Global Interpreter Lock).
        - Recommended for: I/O-bound tasks (file I/O, network, subprocess).
        - Not recommended for: CPU-bound tasks (heavy calculation). Use 'multiprocessing' instead.
        """
        self._n_size = size if size is not None else (os.cpu_count() or 4)
        self._is_stop = False
        self._threads: List[threading.Thread] = []
        
        # Job queue (Thread-safe)
        self._job_queue = queue.Queue()
        
        # Active worker tracker
        self._active_worker_count = 0
        self._active_len_lock = threading.Lock()
        
        # [Safety] Register destroy to be called at exit
        atexit.register(self.destroy)
        
        self.init()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()

    def init(self):
        self._is_stop = False
        self._threads.clear()
        for i in range(self._n_size):
            t = threading.Thread(target=self._worker, args=(i,), daemon=True)
            t.start()
            self._threads.append(t)

    def _worker(self, index: int):
        # Apply tracer if active (since this is a new thread)
        if JTracer().tracing:
            sys.settrace(JTracer()._trace_callback)
            
        while True:
            try:
                # [Optimization] Use blocking get with Sentinel (None) instead of timeout polling.
                # This eliminates CPU waste from active waiting.
                item = self._job_queue.get()
                
                # Check for Sentinel (Stop Signal)
                if item is None:
                    # Propagate signal to other workers if needed, or rely on stop_thread putting N sentinels.
                    # Here we just acknowledge and exit.
                    self._job_queue.task_done()
                    break

                func, args, kwargs, future = item

                with self._active_len_lock:
                    self._active_worker_count += 1
                
                try:
                    if not future.set_running_or_notify_cancel():
                        continue

                    result = func(*args, **kwargs)
                    future.set_result(result)
                except Exception as e:
                    future.set_exception(e)
                finally:
                    with self._active_len_lock:
                        self._active_worker_count -= 1
                    self._job_queue.task_done()
                    
            except Exception:
                pass

    def add_job(self, func: Callable, *args, **kwargs) -> Future:
        """
        Add a job to the pool and return a Future object.
        작업을 풀에 추가하고 Future 객체를 반환합니다.
        """
        if self._is_stop:
            raise RuntimeError("Cannot add job to a stopped ThreadPoolSystem.")

        future = Future()
        # Ensure we don't add jobs if stopped? 
        # C++ implementation doesn't strictly block addition after stop, 
        # but workers won't process them if they are dead.
        self._job_queue.put((func, args, kwargs, future))
        return future

    def get_current_queue_size(self) -> int:
        return self._job_queue.qsize()

    def get_total_worker_count(self) -> int:
        return len(self._threads)

    def get_activated_worker_count(self) -> int:
        with self._active_len_lock:
            return self._active_worker_count
    
    def stop_thread(self):
        """
        Stop the thread pool gracefully.
        쓰레드 풀을 중지합니다. 큐에 남은 작업을 모두 처리하고 종료합니다.
        """
        if not self._is_stop:
            self._is_stop = True
            # Inject Sentinels to wake up and stop workers gracefully
            for _ in range(len(self._threads)):
                self._job_queue.put(None)
        
    def start_thread(self):
        # [Design Note] C++ implementation does not use a lock here.
        # Python GIL provides basic thread safety for boolean flags, but for more complex state sync,
        # a lock might be needed. Here we follow C++ design (keep it simple).
        if self._is_stop:
            self._is_stop = False
            # Re-initialize if threads are dead
            if len(self._threads) == 0 or not any(t.is_alive() for t in self._threads):
                self.init()
    
    def destroy(self):
        """
        Stop threads and wait for them to finish.
        쓰레드를 중지하고 대기합니다.
        """
        self.stop_thread()
        for t in self._threads:
            if t.is_alive():
                t.join()
        self._threads.clear()


"""
@namespace cmd_util
@brief	Namespace for command-related utilities. 명령 관련 유틸리티를 위한 네임스페이스
"""
class ErrorCmdSystem(JErrorSystem): pass
class CmdSystem:
    class ReturnCode(IntEnum): # .name shall get string name
        SUCCESS = 0
        ERROR_GENERAL = 1
        ERROR_FILE_NOT_FOUND = 2
        ERROR_PATH_NOT_FOUND = 3
        ERROR_ACCESS_DENIED = 5
        ERROR_COMMAND_NOT_FOUND = 9009
        ERROR_UNKNOWN = -1

    
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
            raise_err: bool = True,
            f_back: int = 1,
            stdin: Optional[str] = None,
            timeout: Optional[int] = None,
            specific_working_dir: Optional[str] = None,
            cumstem_env: Optional[Dict[str, str]] = None,
            encoding: Optional[str] = None
        ) -> Result:
        try:
            JLogger().log_info(f"| cmd.exe | {' '.join(cmd) if isinstance(cmd, list) else cmd}", f_back)
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
                check=False, # fail safe
                errors='replace', # Prevent UnicodeDecodeError
                encoding=encoding # Custom encoding
            )
            ret_code = cmd_ret.returncode
            ret_out = cmd_ret.stdout.strip() if cmd_ret.stdout else ""
            ret_err = cmd_ret.stderr.strip() if cmd_ret.stderr else ""
        except subprocess.CalledProcessError as e:
            ret_code = e.returncode
            ret_out = e.stdout.strip() if e.stdout else ""
            ret_err = e.stderr.strip() if e.stderr else ""
        except subprocess.TimeoutExpired as e:
            ret_code = CmdSystem.ReturnCode.ERROR_UNKNOWN
            ret_out = ""
            ret_err = f"Command timed out after {timeout} seconds"
        except Exception as e:
            ret_code = CmdSystem.ReturnCode.ERROR_UNKNOWN
            ret_out = ""
            ret_err = str(e).strip()
        finally:
            try:
                rc = CmdSystem.ReturnCode(ret_code)
                rc_msg = f"{rc.name} ({rc.value})"
            except ValueError:
                rc = CmdSystem.ReturnCode.ERROR_UNKNOWN
                rc_msg = f"UNKNOWN_ERROR_CODE ({ret_code})"

            JLogger().log_info(f"| cmd.ret | {rc_msg}", f_back)
            if ret_out:
                JLogger().log_info(f"| cmd.out | {ret_out}", f_back)
            if ret_err:
                JLogger().log_error(f"| cmd.err | {ret_err}", f_back)
            
            # [Fix] Raise exception on error only if requested
            if raise_err and ret_code != CmdSystem.ReturnCode.SUCCESS:
                raise ErrorCmdSystem(f"Command failed with return code {rc.name} ({rc}): {ret_err}")

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
                cmd_ret: CmdSystem.Result = CmdSystem.run(['where', program_name], raise_err=False)

                if not (cmd_ret.is_success() and cmd_ret.stdout):
                    EnvvarSystem.update_every_environ()
                    cmd_ret = CmdSystem.run(['where', program_name], raise_err=False)

                if cmd_ret.is_success() and cmd_ret.stdout:
                    for line in cmd_ret.stdout.strip().splitlines():
                        if os.path.exists(line):
                            return line  # 실제 존재하는 첫 번째 경로 반환
                return None
            else:
                cmd_ret: CmdSystem.Result = CmdSystem.run(['which', program_name], raise_err=False)
                if cmd_ret.is_error(): return None
                return cmd_ret.stdout.strip() if cmd_ret.stdout else None
        except ErrorCmdSystem as e:
            JLogger().log_error(f"where '{program_name}' not found: {e}")
            return None

    def get_version(package_name: Optional[str], global_execute: bool = False) -> Optional[str]:
        try:
            if package_name in ['git', 'python']:
                cmd = [package_name, '--version']
            elif package_name in ['pip', 'PyInstaller']:
                python_executable = "python" if global_execute else sys.executable
                cmd = [python_executable, '-m', package_name, '--version']
            elif package_name == 'pillow':
                python_executable = "python" if global_execute else sys.executable
                cmd = [python_executable, '-m', 'pip', 'show', 'pillow']
            elif package_name == 'google-gemini':
                python_executable = "python" if global_execute else sys.executable
                cmd = [python_executable, '-m', 'pip', 'show', 'google-genai']
            elif package_name == 'ollama-lib':
                python_executable = "python" if global_execute else sys.executable
                cmd = [python_executable, '-m', 'pip', 'show', 'ollama']
            elif package_name == 'vcpkg':
                cmd = ['vcpkg', '--version']
            elif package_name == 'nodejs':
                cmd = ['node', '--version']
            elif package_name == 'ollama':
                cmd = ['ollama', '--version']
            else:
                raise ValueError(f"version check of this package is unsupported.")
            cmd_ret: CmdSystem.Result = CmdSystem.run(cmd, raise_err=False)
            _ret = TextUtils.extract_version(cmd_ret.stdout) if cmd_ret.is_success() else None
            return _ret
        except Exception as e:  # Other unexpected errors
            JLogger().log_error(f"{package_name}: {str(e)}")
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
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd, raise_err=False)
                if cmd_ret.is_error(): return False
            
                # Verify the process is actually killed by checking if it's still running
                cmd = ['tasklist', '/FI', f'IMAGENAME eq {process_name}']
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd, raise_err=False)
                if cmd_ret.is_error(): return False
                return "No tasks are running" in cmd_ret.stdout or process_name not in cmd_ret.stdout
            else:
                cmd = ['pkill', '-9', process_name]
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd, raise_err=False)
                if cmd_ret.is_error(): return False
                return cmd_ret.returncode != CmdSystem.ReturnCode.SUCCESS
                
        except Exception as e:
            JLogger().log_error(f"Failed to kill process '{process_name}': {e}")
            return False

    """
    @brief	Get list of running processes. 실행 중인 프로세스 목록을 가져옵니다.
    @return	List of dictionaries containing process information 프로세스 정보를 담은 딕셔너리 리스트
    """
    def get_process_list() -> Optional[List[Dict[str, str]]]:    
        try:
            processes = []
            if sys.platform == 'win32':
                cmd_ret: CmdSystem.Result = CmdSystem.run(['tasklist', '/FO', 'CSV', '/NH'], raise_err=False)
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
                cmd_ret: CmdSystem.Result = CmdSystem.run(['ps', 'aux'], raise_err=False)
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
            JLogger().log_error(f"Failed to get process list: {e}")
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
            cmd_ret: CmdSystem.Result = CmdSystem.run(cmd, raise_err=False)
            results.append(cmd_ret)
            
            if stop_on_error and cmd_ret.is_error():
                break
        
        return results


"""
@namespace file_util
@brief	Namespace for file-related utilities. 파일 관련 유틸리티를 위한 네임스페이스
"""
class ErrorFileSystem(JErrorSystem): pass
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
    
    
    def get_path_appdata_roaming() -> Path:
        """
        Get the Roaming AppData directory path.
        사용자의 Roaming AppData 디렉토리 경로를 반환합니다. (e.g., C:\\Users\\USERNAME\\AppData\\Roaming)
        On non-Windows systems, returns ~/.config.
        """
        if sys.platform == 'win32':
            # Use APPDATA environment variable which points to Roaming
            return Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming')).resolve()
        else:
            # Fallback for likely Linux/macOS
            return Path.home() / '.config'

    def get_path_appdata_local_programs() -> Path:
        """
        Get the Local AppData Programs directory path.
        사용자의 Local AppData Programs 디렉토리 경로를 반환합니다. (e.g., C:\\Users\\USERNAME\\AppData\\Local\\Programs)
        This is a common install location for user-scope apps like Python, VS Code, Ollama, etc.
        On non-Windows systems, returns ~/.local/programs.
        """
        if sys.platform == 'win32':
            local_appdata = os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local')
            return (Path(local_appdata) / 'Programs').resolve()
        else:
            return (Path.home() / '.local' / 'programs').resolve()
            
    def get_path_download() -> Path:
        """
        Get the user's Downloads directory path.
        사용자의 다운로드 디렉토리 경로를 반환합니다. (e.g., C:\\Users\\USERNAME\\Downloads)
        """
        return Path.home() / 'Downloads'


    @staticmethod
    def get_path_windowsapps() -> Path:
        """
        Get the WindowsApps directory path.
        WindowsApps 디렉토리 경로를 반환합니다. (e.g., C:\\Users\\user\\AppData\\Local\\Microsoft\\WindowsApps)
        """
        if sys.platform == 'win32':
            # Use LOCALAPPDATA environment variable which points to Local
            base = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
            return (base / 'Microsoft' / 'WindowsApps').resolve()
        else:
            return Path.home() / '.local/bin' # Fallback for non-Windows (or just raise error)

    """
    @brief	Check if a command-line tool is installed, and install it if not. 명령줄 도구가 설치되어 있는지 확인하고, 없으면 설치합니다.
    @return	True if the tool is installed or successfully installed, False otherwise 도구가 설치되어 있거나 성공적으로 설치되면 True, 아니면 False
    """
    def ensure_installed(package_name: Optional[str], global_execute: bool = False) -> bool:
        try:
            if CmdSystem.get_version(package_name, global_execute):
                _success = True
            else:
                # possiblity_1, not installed, try to install
                JLogger().log_info(f"Module '{package_name}' is not installed or not found in PATH.")
                if package_name == 'git':
                    c_path = InstallSystem.WingetRelated.install_git_global(global_execute)
                    need_envvar = True
                elif package_name == 'python':
                    c_path = InstallSystem.PythonRelated.install_python_global()
                    need_envvar = True
                elif package_name == 'pip':
                    c_path = InstallSystem.PythonRelated.install_pip_global(global_execute, upgrade=True)
                    need_envvar = False
                elif package_name == 'pyinstaller':
                    c_path = InstallSystem.PythonRelated.install_pyinstaller_global(global_execute, upgrade=True)
                    need_envvar = False
                elif package_name == 'pillow':
                    c_path = InstallSystem.PythonRelated.install_pillow_lib_global(global_execute)
                    need_envvar = False
                elif package_name == 'google-gemini':
                    c_path = InstallSystem.PythonRelated.install_genai_lib_global(global_execute)
                    need_envvar = False
                elif package_name == 'ollama-lib':
                    c_path = InstallSystem.PythonRelated.install_ollama_lib_global(global_execute)
                    need_envvar = False
                elif package_name == 'vcpkg':
                    c_path = InstallSystem.VcpkgRelated.install_vcpkg_global()
                    need_envvar = True
                elif package_name == 'nodejs':
                    c_path = InstallSystem.WingetRelated.install_nodejs_global()
                    need_envvar = True
                elif package_name == 'ollama':
                    c_path = InstallSystem.WingetRelated.install_ollama_app_global()
                    global_execute = False
                    need_envvar = True
                else:
                    JLogger().log_error(f"Automatic installation for '{package_name}' is not supported.")
                    raise ErrorInstallSystem(f"Package install unsupported: '{package_name}'.")
                
                JLogger().log_info(f"Module '{package_name}' installed successfully." if c_path else f"Failed to install module '{package_name}'.")
                
                # possiblity_2, PATH issue, try to set PATH and check again
                is_pathed = False
                if c_path and need_envvar:
                    envvar_name = f"path_{package_name.lower()}"
                    is_pathed = EnvvarSystem.ensure_global_envvar(envvar_name, str(c_path),  global_scope=global_execute, permanent=True)
                    _success = is_pathed and bool(CmdSystem.get_version(package_name, global_execute))
                else:
                    _success = bool(CmdSystem.get_version(package_name, global_execute))
            return _success
        except Exception as e:  # Other unexpected errors
            JLogger().log_error(f"Unexpected error checking {package_name}: {str(e)}")
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
            JLogger().log_error(f"Failed to create directory: {path}, Error: {str(e)}")
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
                JLogger().log_warning(f"Directory does not exist: {path}")
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
            rewrite: bool = True
        ) -> bool:
        try:
            if os.path.exists(dst):
                if not rewrite:
                    return False
                else:
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
    def file_exists(path: str, raise_on: bool = False) -> bool:
        try:
            _success = os.path.isfile(path)
            if raise_on and not _success:
                raise ErrorFileSystem(f"File does not exist: {path}")
            else:
                return _success
        except Exception as e:
            raise ErrorFileSystem(f"Error checking file existence: {path}, Error: {str(e)}")


    """
    @brief	Check if a directory exists. 디렉토리가 존재하는지 확인합니다.
    @param	path	Directory path to check 확인할 디렉토리 경로
    @return	True if exists, False otherwise 존재하면 True, 아니면 False
    """
    def directory_exists(path: str, raise_on: bool = False) -> bool:
        try:
            _success = os.path.isdir(path)
            if raise_on and not _success:
                raise ErrorFileSystem(f"Directory does not exist: {path}")
            else:
                return _success
        except Exception as e:
            raise ErrorFileSystem(f"Error checking directory existence: {path}, Error: {str(e)}")


    """
    @brief	Get the size of a file in bytes. 파일 크기를 바이트 단위로 가져옵니다.
    @param	path	File path 파일 경로
    @return	File size in bytes, -1 if error 파일 크기(바이트), 에러시 -1
    """
    def get_file_size(path: str) -> int:
        try:
            return os.path.getsize(path)
        except Exception as e:
            raise ErrorFileSystem(f"Error getting file size: {path}, Error: {str(e)}")


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
            JLogger().log_info(f"File exists: {c_path_file}, Size: {size_info}", f_back)
            return True
        else:
            JLogger().log_info(f"File does not exist: {c_path_file}", f_back)
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
    # JLogger().log_info(f"Running vcpkg install... Output will be streamed.")
    
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
    #         JLogger().log_error(f"vcpkg install failed with return code {process.returncode}")
    #         return None
    # except Exception as e:
    #     stop_monitor.set()
    #     JLogger().log_error(f"vcpkg install error: {e}")
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
    def get_list(
            directory: str,
            pattern: str = '*',
            recursive: bool = False,
            target: str = 'all' # 'all', 'file', 'dir' or 'folder'
        ) -> List[str]:
        if recursive:
            search_pattern = os.path.join(directory, '**', pattern)
            items = glob.glob(search_pattern, recursive=True)
        else:
            search_pattern = os.path.join(directory, pattern)
            items = glob.glob(search_pattern)
        
        if target == 'file':
            return [f for f in items if os.path.isfile(f)]
        elif target == 'dir':
            return [f for f in items if os.path.isdir(f)]
        else:
            return items


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
            JLogger().log_info(f"Downloading from: {url}...")
            try:
                #urllib.request.urlretrieve(url, save_path)
                with urllib.request.urlopen(url, timeout=timeout) as response, open(save_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                JLogger().log_info(f"Saved to: {save_path}")
            except Exception as e:
                JLogger().log_error(f"Download failed: {e}")
                raise e
        else:
            JLogger().log_info(f"File already exists: {save_path}")

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
            JLogger().log_info(f"Downloading from: {url}...")
            CmdSystem.run(cmd_download_python, raise_err=True)
            JLogger().log_info(f"Saved to: {save_path}")
        else:
            JLogger().log_info(f"File already exists: {save_path}")

"""
@namespace install
@brief	Namespace for installation-related utilities. 설치 관련 유틸리티를 위한 네임스페이스
"""
class ErrorInstallSystem(JErrorSystem): pass
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
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_install_python, raise_err=True)
                return CmdSystem.get_where('python') if cmd_ret.is_success() else None
            except InstallSystem.ErrorPythonRelated as e:
                JLogger().log_error(f"{str(e)}")
                return None
            except Exception as e:
                JLogger().log_error(f"Failed to install Python: {str(e)}")
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
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_install_pip, raise_err=True)
                return CmdSystem.get_where('pip') if cmd_ret.is_success() else None                
            except Exception as e:
                JLogger().log_error(f"Failed to install pip: {e}")
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
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_install_pyinstaller, raise_err=True)
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
                    if not FileSystem.ensure_installed('PyInstaller', global_execute=global_execute):
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
                    if CmdSystem.run(cmd, raise_err=True).is_success():  # 0 means no stderr
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
        
        def install_pillow_lib_global(global_execute: bool = False) -> bool:
            try:
                python_executable = "python" if global_execute else sys.executable    
                cmd = [python_executable, "-m", "pip", "install", "pillow"]
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd, raise_err=True)
                if cmd_ret.is_success():
                    JLogger().log_info("Installed pillow successfully.")
                    return True
                else:
                    raise InstallSystem.ErrorPythonRelated(f"Failed to install pillow: {cmd_ret.stderr}")
            except Exception as e:
                raise InstallSystem.ErrorPythonRelated(f"Failed to install pillow: {str(e)}")
        
        def install_genai_lib_global(global_execute: bool = False) -> bool:
            try:
                # undercover
                FileSystem.ensure_installed('pillow', global_execute)

                python_executable = "python" if global_execute else sys.executable    
                cmd = [python_executable, "-m", "pip", "install", "google-genai"]
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd, raise_err=True)
                if cmd_ret.is_success():
                    JLogger().log_info("Installed google-genai successfully.")
                    return True
                else:
                    raise InstallSystem.ErrorPythonRelated(f"Failed to install google-genai: {cmd_ret.stderr}")
            except Exception as e:
                raise InstallSystem.ErrorPythonRelated(f"Failed to install google-genai: {str(e)}")

        def install_ollama_lib_global(global_execute: bool = False) -> bool:
            try:
                python_executable = "python" if global_execute else sys.executable    
                cmd = [python_executable, "-m", "pip", "install", "ollama"]
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd, raise_err=True)
                if cmd_ret.is_success():
                    JLogger().log_info("Installed ollama successfully.")
                    return True
                else:
                    raise InstallSystem.ErrorPythonRelated(f"Failed to install ollama: {cmd_ret.stderr}")
            except Exception as e:
                raise InstallSystem.ErrorPythonRelated(f"Failed to install ollama: {str(e)}")

    class ErrorWingetRelated(ErrorInstallSystem): pass
    class WingetRelated:
        def install_git_global(global_execute: bool = True) -> Optional[Path]:
            try:
                if sys.platform == 'win32':
                    winapps_folder = FileSystem.get_path_windowsapps()
                    _success_winapps = EnvvarSystem.ensure_global_envvar("path_winapps", str(winapps_folder),  global_scope=False, permanent=True)
                    if not _success_winapps:
                        raise ErrorWingetRelated("Failed to install Git: Failed to set path_winapps environment variable")
                    cmd_install_git = [
                        "winget",
                        "install",
                        "--id",
                        "Git.Git",
                        "--silent",
                        "--accept-package-agreements",
                        "--accept-source-agreements"
                    ]
                    cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_install_git, raise_err=True)
                    return CmdSystem.get_where('git') if cmd_ret.is_success() else None
                else:
                    raise NotImplementedError("Git installation is only implemented for Windows.")
            except Exception as e:
                JLogger().log_error(f"Failed to install Git: {e}")
                raise e
        
        def install_nodejs_global(version: Optional[str] = None) -> Optional[Path]:
            try:
                winapps_folder = FileSystem.get_path_windowsapps()
                _success_winapps = EnvvarSystem.ensure_global_envvar("path_winapps", str(winapps_folder),  global_scope=False, permanent=True)
                if not _success_winapps:
                    raise ErrorWingetRelated("Failed to install Node.js: Failed to set path_winapps environment variable")

                node_path = CmdSystem.get_where('node')
                if node_path:
                    JLogger().log_info(f"Node.js is already installed at: {node_path}")
                    return Path(node_path).parent
                if sys.platform != 'win32':
                    raise NotImplementedError("Node.js installation via winget is only implemented for Windows.")
                cmd = [
                    'winget', 'install',
                    '-e',                          # --exact: 정확히 일치하는 ID 검색 (유사 검색 방지)
                    '--id', 'OpenJS.NodeJS.LTS',   # 설치할 패키지 고유 ID (Node.js LTS 버전)
                    '--scope', 'machine',          # 설치 범위: 시스템 전체 (모든 사용자용), 관리자 권한 필요
                    '--accept-package-agreements', # 패키지 라이선스 동의 (사용자 입력 없이 진행)
                    '--accept-source-agreements'   # 소스(저장소) 약관 동의 (사용자 입력 없이 진행)
                ]
                if version:
                    cmd.extend(['--version', version])
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd, raise_err=True, encoding='utf-8')                    
                return Path(CmdSystem.get_where('node')).parent if cmd_ret.is_success() else None
            except Exception as e:
                raise InstallSystem.ErrorWingetRelated(e)

        def install_ollama_app_global() -> Optional[Path]:
            try:
                winapps_folder = FileSystem.get_path_windowsapps()
                _success_winapps = EnvvarSystem.ensure_global_envvar("path_winapps", str(winapps_folder),  global_scope=False, permanent=True)
                if not _success_winapps:
                    raise ErrorWingetRelated("Failed to install Node.js: Failed to set path_winapps environment variable")

                ollama_path = CmdSystem.get_where('ollama')
                if ollama_path:
                    JLogger().log_info(f"Ollama app is already installed at: {ollama_path}")
                    return Path(ollama_path).parent
                if sys.platform != 'win32':
                    raise NotImplementedError("Ollama app installation via winget is only implemented for Windows.")
 
                cmd_install = [
                    "winget", "install",
                    "--id", "Ollama.Ollama",
                    "--silent", "--accept-package-agreements", "--accept-source-agreements"
                ]                
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_install, raise_err=True)                
                if cmd_ret.is_success():
                    JLogger().log_info("Ollama installed successfully via Winget.")
                    return FileSystem.get_path_appdata_local_programs() / "Ollama" # C:\Users\USER\AppData\Local\Programs\Ollama
                else:
                    raise InstallSystem.ErrorWingetRelated(f"Winget installation failed: {cmd_ret.stderr}")

            except Exception as e:
                raise InstallSystem.ErrorWingetRelated(f"Failed to install Ollama App: {e}")

    class ErrorVcpkgRelated(ErrorInstallSystem): pass
    class VcpkgRelated:
        def install_vcpkg_global() -> Optional[Path]:
            # 1. git 설치 확인/설치
            _success = FileSystem.ensure_installed('git', global_execute=True)
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
                JLogger().log_info("vcpkg 설치가 필요합니다.")
                cmd_ret: CmdSystem.Result = CmdSystem.run(f"git clone https://github.com/microsoft/vcpkg.git \"{vcpkg_dir}\"", raise_err=True)
                if cmd_ret.is_error() or not FileSystem.directory_exists(vcpkg_dir):
                    raise InstallSystem.ErrorVcpkgRelated("vcpkg 클론 실패") #exit_proper                
            
            # 4. 설치후 빌드 - bootstrap 실행
            # > %path_vcpkg%\bootstrap-vcpkg.bat
            vcpkg_exe = os.path.join(vcpkg_dir, 'vcpkg.exe')
            if not FileSystem.file_exists(vcpkg_exe):
                bootstrap_bat = os.path.join(vcpkg_dir, 'bootstrap-vcpkg.bat')
                cmd_ret: CmdSystem.Result = CmdSystem.run(f"\"{bootstrap_bat}\"", raise_err=True, specific_working_dir=vcpkg_dir)
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
            cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_install_vcpkg, raise_err=True, specific_working_dir=main_file_path)
            return Path(core_install_root) if cmd_ret.is_success() else None
        
        def integrate_vcpkg_to_visualstudio() -> bool:
            # > %path_vcpkg%\vcpkg integrate install
            env_path = EnvvarSystem.get_global_env_path('path_vcpkg')
            cmd_integrate_install = [os.path.join(env_path, 'vcpkg.exe'), 'integrate', 'install']
            cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_integrate_install, raise_err=True)
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
                            JLogger().log_info(f"vcpkg.targets already imported in {vcxproj_path}")
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
                                JLogger().log_info(f"Successfully integrated vcpkg to {vcxproj_path}")
                            else:
                                raise InstallSystem.ErrorVcpkgRelated(f"Target import line not found in {vcxproj_path}")
                    except Exception as e:
                        JLogger().log_error(f"Error processing {vcxproj_path}: {str(e)}")
                        _success = False
                return _success
            except Exception as e:
                JLogger().log_error(f"Failed to integrate vcpkg to vcxproj: {str(e)}")
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
                    if isinstance(dependency, dict):
                        dependency = dependency.get('name')

                    if not isinstance(dependency, str):
                        JLogger().log_warning(f"'{dependency}'는 지원되지 않는 형식입니다. 문자열이어야 합니다.")
                        continue
                    if dependency.lower() == 'openssl':
                        # 예: 환경 변수 설정, 추가 파일 복사 등
                        JLogger().log_info("OpenSSL extra configuration completed.")
                    elif dependency.lower() == 'boost':
                        # 예: 환경 변수 설정, 추가 파일 복사 등
                        JLogger().log_info("Boost extra configuration completed.")
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
                        
                        JLogger().log_info("Tesseract extra configuration completed.")
                    elif dependency.lower() == 'opencv':
                        # vcpkg-opencv는 헤더를 include/opencv4/opencv2에 설치하므로,
                        # #include <opencv2/...> 작동호환성을 위해 include/opencv2로 헤더를 복사해줍니다.
                        env_path = EnvvarSystem.get_global_env_path('path_vcpkg')
                        if env_path:
                            include_dir = os.path.join(env_path, 'installed', 'x64-windows', 'include')
                            src_dir = os.path.join(include_dir, 'opencv4', 'opencv2')
                            dst_dir = os.path.join(include_dir, 'opencv2')
                            FileSystem.copy_directory(src_dir, dst_dir, rewrite=True)
                            JLogger().log_info("Synchronized opencv2 headers to standard include path.")
                        JLogger().log_info("OpenCV extra configuration completed.")
                    else:
                        JLogger().log_warning(f"Do not support extra-setup for '{dependency}', It may require manual configuration.")
                return True
            except InstallSystem.ErrorVcpkgRelated as e:
                JLogger().log_error(f"Failed to setup vcpkg extra: {str(e)}")
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
                JLogger().log_error(f"Unexpected error clearing vcpkg: {str(e)}")
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
                JLogger().log_error(f"Failed to delete vcpkg: {str(e)}")
            except Exception as e:
                JLogger().log_error(f"Unexpected error deleting vcpkg: {str(e)}")
                return False        
            
"""
@namespace environment variables
@brief	Namespace for environment variable-related utilities. 환경 변수 관련 유틸리티를 위한 네임스페이스
"""
class ErrorEnvvarSystem(JErrorSystem): pass
    # def __init__(self, message):
    #     JLogger().log_error(str(message), 1)
    #     super().__init__(message)
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
            JLogger().log_error(f"Error querying system environment variable '{key}': {e}")
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
            cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_query_global_envvar, raise_err=False)
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
            cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_query_global_envvar, raise_err=False)
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
    
    def update_every_environ(scope: Optional[str] = None, key: str = 'Path', value: Optional[str] = None) -> bool:
        """
        Refresh the current process's PATH environment variable from the Windows Registry.
        Also resolves unexpanded %VARIABLES% in PATH by loading them from registry if missing.
        """
        if sys.platform != 'win32':
            return False

        try:
            def _query_reg(target_scope, target_key) -> Optional[str]:
                cmd = ['reg', 'query', target_scope, '/v', target_key]
                res = CmdSystem.run(cmd, raise_err=False)
                if res.is_success():
                    return EnvvarSystem.extract_registry_value(res.stdout)
                return None

            # 1. Collect Path components (System then User)
            paths = []
            
            # System Path
            if scope is None or scope == EnvvarSystem.GLOBAL_SCOPE:
                if query_value := _query_reg(EnvvarSystem.GLOBAL_SCOPE, key):
                    paths.append(query_value.strip(';')) # Remove trailing semi-colon to avoid double ;;

            # User Path
            if scope is None or scope == EnvvarSystem.USER_SCOPE:
                if query_value := _query_reg(EnvvarSystem.USER_SCOPE, key):
                    paths.append(query_value.strip(';'))

            if not paths:
                return False

            # Combine (System;User)
            new_path = ";".join(paths)
            
            # 2. Smart Variable Expansion (%VAR%)
            if '%' in new_path:
                # Find all unique %VAR% tokens
                vars_in_path = set(re.findall(r'%([^%]+)%', new_path))
                
                for var_name in vars_in_path:
                    # Skip if already in environ
                    if os.environ.get(var_name) is None:
                        var_val = None                        
                        # Priority: User > System
                        if scope is None or scope == EnvvarSystem.USER_SCOPE:
                            var_val = _query_reg(EnvvarSystem.USER_SCOPE, var_name)                        
                        if (scope is None or scope == EnvvarSystem.GLOBAL_SCOPE) and var_val is None:
                            var_val = _query_reg(EnvvarSystem.GLOBAL_SCOPE, var_name)                        
                        if var_val is not None:
                            os.environ[var_name] = var_val

            # 3. Apply to Process
            os.environ['PATH'] = os.path.expandvars(new_path)
            JLogger().log_info("Refreshed process PATH from registry.")
            return True
                
        except Exception as e:
            JLogger().log_warning(f"Failed to refresh PATH from registry: {e}")
            return False

    #TODO: update_every_environ 통합
    def update_environ(scope, key, value = None) -> bool:
        try:
            if sys.platform == 'win32':
                cmd_query_global_envvar = [
                    'reg', 'query', scope,
                    '/v', # value
                    key # key name
                ]
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_query_global_envvar, raise_err=False)
                if cmd_ret.is_success():
                    query_value = EnvvarSystem.extract_registry_value(cmd_ret.stdout)
                    if value == None and query_value != None:
                        os.environ[key] = query_value
                        return True
                    if value != None and query_value == value:
                        os.environ[key] = value
                        return True
                    JLogger().log_info(f"re-setting 'path_jfw_py' env var first, before build exe.")
                    return False
                else:
                    # If reg query fails, it means the key doesn't exist, which is a valid scenario for update_environ
                    return False
            else:
                raise ErrorEnvvarSystem("update_environ is only implemented for Windows.")
        except ErrorEnvvarSystem as e:
            JLogger().log_error(f"Error querying system environment variables: {e}")
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
                    cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_set_global_envvar, raise_err=True)
                    return EnvvarSystem.update_environ(scope, key, value) if cmd_ret.is_success() else False
                else:
                    # On Unix-like systems, would need to modify shell config files
                    shell_config = os.path.expanduser('~/.bashrc') if not global_scope else '/etc/environment'
                    with open(shell_config, 'a') as f:
                        f.write(f'\nexport {key}="{value}"\n')
                    return True
            else:
                raise ErrorEnvvarSystem("Non-permanent env var setting not implemented")
        except ErrorEnvvarSystem as e:
            JLogger().log_error(f"Failed to set env var: {e}")
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
                cmd_ret: CmdSystem.Result = CmdSystem.run(['reg', 'delete', scope, '/v', key, '/f'], raise_err=False) # Allow failure if key doesn't exist
                is_cmd_all = False if cmd_ret.is_error() else is_cmd_all
            
            # Check if deletion was successful (i.e., keys no longer exist)
            is_deleted_all = True
            for key in keys_to_delete:
                cmd_query_global_envvar = [ 'reg', 'query', scope, '/v', key ]
                cmd_ret: CmdSystem.Result = CmdSystem.run(cmd_query_global_envvar, raise_err=False) # Query should fail if key is deleted
                if cmd_ret.is_success(): # If query succeeds, key still exists
                    is_deleted_all = False
            
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
                    ['reg', 'query', scope, '/v', 'Path'], raise_err=False
                )
                current_path = ""
                if cmd_ret.is_success():                
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

                # Path경로 list 얻기
                path_entries = TextUtils.split_with_list(new_path, ";")
                
                # 환경변수 목록 얻기 (치환용, 역정렬)
                path_to_envvar_map: dict[str, str] = {} # { "c:\\program files\\java\\jdk": "%JAVA_HOME%" }
                for entry in path_entries:
                    if match := re.search(r'%([^%]+)%', entry):
                        var_name = match.group(1)
                        if var_val := os.environ.get(var_name):
                            path_to_envvar_map[var_val.lower()] = f"%{var_name}%"
                path_to_envvar_map_sorted = sorted(path_to_envvar_map.keys(), reverse=True)

                # 최종 Path경로 목록 구하기 (최대한 상대경로로 치환)
                list_relative_for_use: list[str] = []
                set_absolute_for_check: set[str] = set()
                for entry in path_entries:
                    entry_clean = entry.strip()
                    if not entry_clean: continue
                    
                    relative_path = entry_clean.rstrip('\\/')
                    entry_lower = entry_clean.lower()

                    # 1. 실제 사용할 상대경로 만들기 - %문자가 없는 하드코딩 경로만 대상 (이미 변수면 패스)
                    if '%' not in entry_clean:
                        for root in path_to_envvar_map_sorted: # 가장 긴 매칭부터 검토
                            if entry_lower.startswith(root):
                                remainder = entry_clean[len(root):]
                                # 경계 검사: 정확히 일치하거나, 경로 구분자로 이어지는 경우
                                if not remainder or remainder.startswith('\\') or remainder.startswith('/'):
                                    env_var = path_to_envvar_map[root]
                                    relative_path = f"{env_var}{remainder}".rstrip('\\/')
                                    break
                    
                    # 2. 중복 검사용 절대경로 만들기 (소문자)
                    absolute_path = relative_path
                    if '%' in relative_path:
                        if match := re.search(r'%([^%]+)%', relative_path):
                            var_name = match.group(1)
                            if var_val := os.environ.get(var_name):
                                absolute_path = relative_path.replace(f'%{var_name}%', var_val)
                    absolute_path = absolute_path.lower()
                    
                    # 3. 중복 검사후 상대경로 최종저장 (소문자 절대경로 기준)
                    if absolute_path not in set_absolute_for_check:
                        set_absolute_for_check.add(absolute_path)
                        list_relative_for_use.append(relative_path)
                                
                # 최종 Path경로 목록의 정렬
                new_path = EnvvarSystem._sortting_policy_envpath(list_relative_for_use)

                # Path변수 업데이트 (NEEDS ADMIN PRIVILEGES FOR GLOBAL SCOPE)
                cmd_ret: CmdSystem.Result = CmdSystem.run(
                    ['reg', 'add', scope, '/v', 'Path', '/t', 'REG_EXPAND_SZ', '/d', new_path, '/f'], raise_err=True
                )
                return True if cmd_ret.is_success() else False
            else:
                raise ErrorEnvvarSystem("ensure_global_envvar_to_Path is only implemented for Windows.")
        except ErrorEnvvarSystem as e:
            raise ErrorEnvvarSystem(f"Failed to add {key} to Path: {e}")

    @staticmethod
    def _sortting_policy_envpath(unique_entries: List[str]) -> str:
        # 1. 정렬시 대소문자구분x
        # 2. C윈도우(0)-C프로그램파일(1)-C프로그램파일86(2)-C프로그램기타(3)-D프로그램(4)-%환경변수(5)-기타(6)
        # 3. 알파벳역순 정렬
        def get_group_to_sort(entry):
            entry_lower = entry.lower()
            if "%systemroot%" in entry_lower:
                return (0, 'c', entry_lower)
            elif entry_lower[0:1] == '%':
                return (5, "", entry_lower)
            elif entry_lower[1:2] == ':': # 드라이브 문자 확인 (예: C:)
                drive = entry_lower[0:1]
                if drive == 'c':
                    # Strict prefix check to avoid false positives (e.g., "Program Files\Windows Kits" matching "windows")
                    if entry_lower.startswith("c:\\windows") or entry_lower.startswith("c:/windows"):
                        return (0, drive, entry_lower)
                    elif entry_lower.startswith("c:\\program files") or entry_lower.startswith("c:/program files"):
                        if "(x86)" in entry_lower:
                            return (2, drive, entry_lower) # Program Files (x86) -> Group 2
                        return (1, drive, entry_lower)     # Program Files       -> Group 1
                    else: # C:\Others
                        return (3, drive, entry_lower)
                else:
                    return (4, drive, entry_lower) # D:, E:, ... Z:
            else:
                # UNC 경로(\\Server\Share)나 잘못된 경로 처리
                # 실제 드라이브(z)와 섞이지 않게 아스키 코드가 더 큰 '{' 사용
                return (6, '{', entry_lower)
        
        # 1단계: 그룹핑 적용
        groups: dict[tuple[int, str], list[str]] = {} # dictionary
        for entry in unique_entries:
            key = get_group_to_sort(entry) # (priority, drive, name)
            group_id: tuple[int, str] = (key[0], key[1]) # (0,'c'), ..., (3,'d'), (3, 'e'), ... (5, '{')...
            if group_id not in groups:
                groups[group_id] = []
            groups[group_id].append(entry)
        
        # 2단계: 그룹간 정렬
        sorted_group_keys: list[tuple[int, str]] = sorted(groups.keys())
        
        # 3단계: 각 그룹 내부 "알파벳 역순" 정렬
        final_list: list[str] = []
        for g_key in sorted_group_keys:
            entries: list[str] = groups[g_key]
            entries.sort(key=lambda x: x.lower(), reverse=True)
            final_list.extend(entries)

        return ";".join(final_list)


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
            JLogger().log_info(f"환경변수 '{key}' 설정 {'성공' if success_ else '실패'}")    
            #EnvvarSystem.update_every_environ()
            return success_
        except ErrorEnvvarSystem as e:
            JLogger().log_error(f"환경변수 '{key}' 설정 실패: {e}")
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





