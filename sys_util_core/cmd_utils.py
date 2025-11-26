"""
Command Execution Utilities
명령어 실행 유틸리티

This module provides utility functions for executing and managing system commands.
시스템 명령어를 실행하고 관리하기 위한 유틸리티 함수들을 제공합니다.
"""

import subprocess
import shlex
import os
import sys
from typing import Optional, Dict, List, Tuple, Union

from sys_util_core import file_utils

def pause_exit(msg=None):
    if msg:
        file_utils.LogSystem.print_error(msg)
    input("Press Enter to exit...")
    sys.exit(1)

def run_cmd(
		cmd,
		cwd=None,
		shell=True
	):
    file_utils.LogSystem.print_info(f"실행: {cmd}")
    result = subprocess.run(cmd, cwd=cwd, shell=shell)
    return result.returncode == 0

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
		shell: bool = False,
		timeout: Optional[int] = None,
		cwd: Optional[str] = None,
		env: Optional[Dict[str, str]] = None
 	) -> Tuple[int, str, str]:
    try:
        if isinstance(cmd, str) and not shell:
            cmd = shlex.split(cmd)
        
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=env
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
