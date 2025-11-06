"""
Command Execution Utilities

This module provides utility functions for executing and managing system commands.
"""

import subprocess
import shlex
import os
import sys
from typing import Optional, Dict, List, Tuple, Union


def run_command(cmd: Union[str, List[str]], shell: bool = False, 
                timeout: Optional[int] = None, cwd: Optional[str] = None,
                env: Optional[Dict[str, str]] = None) -> Tuple[int, str, str]:
    """
    Execute a command and return its exit code, stdout, and stderr.
    
    Args:
        cmd: Command to execute (string or list of arguments)
        shell: Whether to execute through shell
        timeout: Command timeout in seconds
        cwd: Working directory for command execution
        env: Environment variables for command
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
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


def run_command_streaming(cmd: Union[str, List[str]], shell: bool = False,
                         cwd: Optional[str] = None,
                         env: Optional[Dict[str, str]] = None):
    """
    Execute a command and stream output in real-time.
    
    Args:
        cmd: Command to execute
        shell: Whether to execute through shell
        cwd: Working directory
        env: Environment variables
        
    Yields:
        Lines of output as they are produced
    """
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


def check_command_exists(command: str) -> bool:
    """
    Check if a command exists in the system PATH.
    
    Args:
        command: Command name to check
        
    Returns:
        True if command exists, False otherwise
    """
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


def run_command_async(cmd: Union[str, List[str]], shell: bool = False,
                     cwd: Optional[str] = None,
                     env: Optional[Dict[str, str]] = None) -> subprocess.Popen:
    """
    Execute a command asynchronously and return the process object.
    
    Args:
        cmd: Command to execute
        shell: Whether to execute through shell
        cwd: Working directory
        env: Environment variables
        
    Returns:
        Process object
    """
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


def kill_process_by_name(process_name: str) -> bool:
    """
    Kill all processes with the given name.
    
    Args:
        process_name: Name of the process to kill
        
    Returns:
        True if successful, False otherwise
    """
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


def get_command_output(cmd: Union[str, List[str]], shell: bool = False) -> str:
    """
    Execute a command and return only its stdout.
    
    Args:
        cmd: Command to execute
        shell: Whether to execute through shell
        
    Returns:
        Command stdout as string
    """
    _, stdout, _ = run_command(cmd, shell=shell)
    return stdout


def run_elevated_command(cmd: Union[str, List[str]]) -> Tuple[int, str, str]:
    """
    Execute a command with elevated privileges (admin/sudo).
    
    Args:
        cmd: Command to execute
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
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


def run_command_with_input(cmd: Union[str, List[str]], 
                           input_data: str,
                           shell: bool = False) -> Tuple[int, str, str]:
    """
    Execute a command with stdin input.
    
    Args:
        cmd: Command to execute
        input_data: Data to send to stdin
        shell: Whether to execute through shell
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
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


def get_process_list() -> List[Dict[str, str]]:
    """
    Get list of running processes.
    
    Returns:
        List of dictionaries containing process information
    """
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


def run_batch_commands(commands: List[Union[str, List[str]]], 
                       stop_on_error: bool = False,
                       shell: bool = False) -> List[Tuple[int, str, str]]:
    """
    Execute multiple commands in sequence.
    
    Args:
        commands: List of commands to execute
        stop_on_error: Whether to stop execution on first error
        shell: Whether to execute through shell
        
    Returns:
        List of tuples (return_code, stdout, stderr) for each command
    """
    results = []
    
    for cmd in commands:
        result = run_command(cmd, shell=shell)
        results.append(result)
        
        if stop_on_error and result[0] != 0:
            break
    
    return results
