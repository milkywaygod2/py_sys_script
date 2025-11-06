"""
File System Utilities

This module provides utility functions for file system operations.
"""

import os
import shutil
import glob
import hashlib
import stat
from typing import List, Optional, Callable
from pathlib import Path
import tempfile


def create_directory(path: str, exist_ok: bool = True) -> bool:
    """
    Create a directory and all necessary parent directories.
    
    Args:
        path: Path to create
        exist_ok: Don't raise error if directory exists
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(path, exist_ok=exist_ok)
        return True
    except Exception:
        return False


def delete_directory(path: str, recursive: bool = True) -> bool:
    """
    Delete a directory.
    
    Args:
        path: Path to delete
        recursive: Delete recursively including contents
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if recursive:
            shutil.rmtree(path)
        else:
            os.rmdir(path)
        return True
    except Exception:
        return False


def copy_file(src: str, dst: str, overwrite: bool = True) -> bool:
    """
    Copy a file from source to destination.
    
    Args:
        src: Source file path
        dst: Destination file path
        overwrite: Overwrite if destination exists
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not overwrite and os.path.exists(dst):
            return False
        
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False


def copy_directory(src: str, dst: str, overwrite: bool = True) -> bool:
    """
    Copy a directory recursively.
    
    Args:
        src: Source directory path
        dst: Destination directory path
        overwrite: Overwrite if destination exists
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if os.path.exists(dst) and not overwrite:
            return False
        
        if os.path.exists(dst):
            shutil.rmtree(dst)
        
        shutil.copytree(src, dst)
        return True
    except Exception:
        return False


def move_file(src: str, dst: str) -> bool:
    """
    Move a file from source to destination.
    
    Args:
        src: Source file path
        dst: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        shutil.move(src, dst)
        return True
    except Exception:
        return False


def file_exists(path: str) -> bool:
    """
    Check if a file exists.
    
    Args:
        path: File path to check
        
    Returns:
        True if exists, False otherwise
    """
    return os.path.isfile(path)


def directory_exists(path: str) -> bool:
    """
    Check if a directory exists.
    
    Args:
        path: Directory path to check
        
    Returns:
        True if exists, False otherwise
    """
    return os.path.isdir(path)


def get_file_size(path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        path: File path
        
    Returns:
        File size in bytes, -1 if error
    """
    try:
        return os.path.getsize(path)
    except Exception:
        return -1


def get_file_hash(path: str, algorithm: str = 'md5') -> Optional[str]:
    """
    Calculate hash of a file.
    
    Args:
        path: File path
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        Hex digest of file hash or None if error
    """
    try:
        hash_obj = hashlib.new(algorithm)
        
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    except Exception:
        return None


def list_files(directory: str, pattern: str = '*', 
               recursive: bool = False) -> List[str]:
    """
    List files in a directory matching a pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern to match
        recursive: Search recursively
        
    Returns:
        List of matching file paths
    """
    if recursive:
        search_pattern = os.path.join(directory, '**', pattern)
        return glob.glob(search_pattern, recursive=True)
    else:
        search_pattern = os.path.join(directory, pattern)
        return glob.glob(search_pattern)


def find_files(directory: str, name_pattern: Optional[str] = None,
               extension: Optional[str] = None,
               recursive: bool = True) -> List[str]:
    """
    Find files in a directory by name pattern or extension.
    
    Args:
        directory: Directory to search
        name_pattern: File name pattern to match
        extension: File extension to match (without dot)
        recursive: Search recursively
        
    Returns:
        List of matching file paths
    """
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


def get_file_modified_time(path: str) -> float:
    """
    Get the last modification time of a file.
    
    Args:
        path: File path
        
    Returns:
        Modification time as timestamp, -1 if error
    """
    try:
        return os.path.getmtime(path)
    except Exception:
        return -1


def set_file_permissions(path: str, permissions: int) -> bool:
    """
    Set file permissions (Unix-like systems).
    
    Args:
        path: File path
        permissions: Octal permission value (e.g., 0o755)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.chmod(path, permissions)
        return True
    except Exception:
        return False


def make_file_readonly(path: str) -> bool:
    """
    Make a file read-only.
    
    Args:
        path: File path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.chmod(path, stat.S_IREAD)
        return True
    except Exception:
        return False


def make_file_writable(path: str) -> bool:
    """
    Make a file writable.
    
    Args:
        path: File path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        return True
    except Exception:
        return False


def get_directory_size(path: str) -> int:
    """
    Calculate total size of a directory and all its contents.
    
    Args:
        path: Directory path
        
    Returns:
        Total size in bytes, -1 if error
    """
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


def create_temp_file(suffix: str = '', prefix: str = 'tmp',
                     dir: Optional[str] = None, text: bool = True) -> str:
    """
    Create a temporary file.
    
    Args:
        suffix: File suffix
        prefix: File prefix
        dir: Directory to create file in
        text: Open in text mode
        
    Returns:
        Path to temporary file
    """
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, 
                                 dir=dir, text=text)
    os.close(fd)
    return path


def create_temp_directory(suffix: str = '', prefix: str = 'tmp',
                         dir: Optional[str] = None) -> str:
    """
    Create a temporary directory.
    
    Args:
        suffix: Directory suffix
        prefix: Directory prefix
        dir: Parent directory
        
    Returns:
        Path to temporary directory
    """
    return tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)


def walk_directory(directory: str, 
                   callback: Callable[[str], None]) -> None:
    """
    Walk a directory tree and execute callback for each file.
    
    Args:
        directory: Directory to walk
        callback: Function to call for each file path
    """
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            callback(file_path)
