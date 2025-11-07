"""
File System Utilities
파일 시스템 유틸리티

This module provides utility functions for file system operations.
파일 시스템 작업을 위한 유틸리티 함수들을 제공합니다.
"""

import os
import shutil
import glob
import hashlib
import stat
from typing import List, Optional, Callable
from pathlib import Path
import tempfile


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
@param	dir	Parent directory 상위 디렉토리
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
