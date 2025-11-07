"""
Archive and Compression Utilities
압축 파일 관리 유틸리티

This module provides utility functions for working with archive files (ZIP, TAR, etc.).
압축 파일(ZIP, TAR 등)을 다루기 위한 유틸리티 함수들을 제공합니다.
"""

import zipfile
import tarfile
import os
import shutil
from typing import List, Optional


# -------------------------------------------------------------------
# Create a ZIP archive from a file or directory.
# 파일이나 디렉토리에서 ZIP 아카이브를 생성합니다.
# Args:
# source_path: Path to file or directory to compress
# 압축할 파일이나 디렉토리 경로
# output_zip: Output ZIP file path
# 출력 ZIP 파일 경로
# include_base_folder: Include base folder in archive
# 아카이브에 기본 폴더 포함
# Returns:
# True if successful, False otherwise
# 성공하면 True, 실패하면 False
# -------------------------------------------------------------------
def create_zip(source_path: str, output_zip: str, 
               include_base_folder: bool = True) -> bool:
    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isfile(source_path):
                zipf.write(source_path, os.path.basename(source_path))
            else:
                for root, _, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        if include_base_folder:
                            arcname = os.path.relpath(file_path, 
                                                     os.path.dirname(source_path))
                        else:
                            arcname = os.path.relpath(file_path, source_path)
                        
                        zipf.write(file_path, arcname)
        
        return True
    except Exception:
        return False


# -------------------------------------------------------------------
# Extract a ZIP archive.
# ZIP 아카이브를 압축 해제합니다.
# Args:
# zip_file: Path to ZIP file
# ZIP 파일 경로
# extract_to: Directory to extract to
# 압축 해제할 디렉토리
# Returns:
# True if successful, False otherwise
# 성공하면 True, 실패하면 False
# -------------------------------------------------------------------
def extract_zip(zip_file: str, extract_to: str) -> bool:
    try:
        with zipfile.ZipFile(zip_file, 'r') as zipf:
            zipf.extractall(extract_to)
        return True
    except Exception:
        return False


# -------------------------------------------------------------------
# List contents of a ZIP archive.
# ZIP 아카이브의 내용을 나열합니다.
# Args:
# zip_file: Path to ZIP file
# ZIP 파일 경로
# Returns:
# List of file names in archive or None if error
# 아카이브의 파일 이름 리스트, 에러시 None
# -------------------------------------------------------------------
def list_zip_contents(zip_file: str) -> Optional[List[str]]:
    try:
        with zipfile.ZipFile(zip_file, 'r') as zipf:
            return zipf.namelist()
    except Exception:
        return None


# -------------------------------------------------------------------
# Create a TAR archive from a file or directory.
# 파일이나 디렉토리에서 TAR 아카이브를 생성합니다.
# Args:
# source_path: Path to file or directory to compress
# 압축할 파일이나 디렉토리 경로
# output_tar: Output TAR file path
# 출력 TAR 파일 경로
# compression: Compression type ('gz', 'bz2', 'xz', or '' for none)
# 압축 타입 ('gz', 'bz2', 'xz', 또는 압축 없음은 '')
# Returns:
# True if successful, False otherwise
# 성공하면 True, 실패하면 False
# -------------------------------------------------------------------
def create_tar(source_path: str, output_tar: str, 
               compression: str = 'gz') -> bool:
    try:
        mode = f'w:{compression}' if compression else 'w'
        
        with tarfile.open(output_tar, mode) as tar:
            tar.add(source_path, arcname=os.path.basename(source_path))
        
        return True
    except Exception:
        return False


# -------------------------------------------------------------------
# Extract a TAR archive.
# TAR 아카이브를 압축 해제합니다.
# Args:
# tar_file: Path to TAR file
# TAR 파일 경로
# extract_to: Directory to extract to
# 압축 해제할 디렉토리
# Returns:
# True if successful, False otherwise
# 성공하면 True, 실패하면 False
# -------------------------------------------------------------------
def extract_tar(tar_file: str, extract_to: str) -> bool:
    try:
        with tarfile.open(tar_file, 'r:*') as tar:
            tar.extractall(extract_to)
        return True
    except Exception:
        return False


# -------------------------------------------------------------------
# List contents of a TAR archive.
# TAR 아카이브의 내용을 나열합니다.
# Args:
# tar_file: Path to TAR file
# TAR 파일 경로
# Returns:
# List of file names in archive or None if error
# 아카이브의 파일 이름 리스트, 에러시 None
# -------------------------------------------------------------------
def list_tar_contents(tar_file: str) -> Optional[List[str]]:
    try:
        with tarfile.open(tar_file, 'r:*') as tar:
            return tar.getnames()
    except Exception:
        return None


# -------------------------------------------------------------------
# Get information about an archive file.
# 아카이브 파일에 대한 정보를 가져옵니다.
# Args:
# archive_file: Path to archive file
# 아카이브 파일 경로
# Returns:
# Dictionary with archive information or None if error
# 아카이브 정보 딕셔너리, 에러시 None
# -------------------------------------------------------------------
def get_archive_info(archive_file: str) -> Optional[dict]:
    try:
        info = {
            'type': None,
            'size_bytes': os.path.getsize(archive_file),
            'file_count': 0
        }
        
        if archive_file.endswith('.zip'):
            info['type'] = 'ZIP'
            with zipfile.ZipFile(archive_file, 'r') as zipf:
                info['file_count'] = len(zipf.namelist())
        elif archive_file.endswith(('.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tar.xz')):
            info['type'] = 'TAR'
            with tarfile.open(archive_file, 'r:*') as tar:
                info['file_count'] = len(tar.getnames())
        
        return info
    except Exception:
        return None


# -------------------------------------------------------------------
# Compress directory to ZIP with exclusion patterns.
# 제외 패턴을 사용하여 디렉토리를 ZIP으로 압축합니다.
# Args:
# directory: Directory to compress
# 압축할 디렉토리
# output_zip: Output ZIP file path
# 출력 ZIP 파일 경로
# exclude_patterns: List of patterns to exclude (e.g., ['*.log', '__pycache__'])
# 제외할 패턴 리스트 (예: ['*.log', '__pycache__'])
# Returns:
# True if successful, False otherwise
# 성공하면 True, 실패하면 False
# -------------------------------------------------------------------
def compress_directory_to_zip(directory: str, output_zip: str,
                               exclude_patterns: Optional[List[str]] = None) -> bool:
    import fnmatch
    
    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check exclusion patterns
                    should_exclude = False
                    if exclude_patterns:
                        for pattern in exclude_patterns:
                            if fnmatch.fnmatch(file, pattern) or pattern in file_path:
                                should_exclude = True
                                break
                    
                    if not should_exclude:
                        arcname = os.path.relpath(file_path, directory)
                        zipf.write(file_path, arcname)
        
        return True
    except Exception:
        return False


# -------------------------------------------------------------------
# Extract a single file from ZIP archive.
# ZIP 아카이브에서 단일 파일을 추출합니다.
# Args:
# zip_file: Path to ZIP file
# ZIP 파일 경로
# file_name: Name of file to extract
# 추출할 파일 이름
# extract_to: Directory to extract to
# 추출할 디렉토리
# Returns:
# True if successful, False otherwise
# 성공하면 True, 실패하면 False
# -------------------------------------------------------------------
def extract_single_file_from_zip(zip_file: str, file_name: str, 
                                  extract_to: str) -> bool:
    try:
        with zipfile.ZipFile(zip_file, 'r') as zipf:
            zipf.extract(file_name, extract_to)
        return True
    except Exception:
        return False


# -------------------------------------------------------------------
# Create an archive using shutil (supports zip, tar, gztar, bztar, xztar).
# shutil을 사용하여 아카이브를 생성합니다 (zip, tar, gztar, bztar, xztar 지원).
# Args:
# source_dir: Source directory
# 소스 디렉토리
# output_name: Output archive name (without extension)
# 출력 아카이브 이름 (확장자 제외)
# format: Archive format
# 아카이브 형식
# Returns:
# Path to created archive or None if error
# 생성된 아카이브 경로, 에러시 None
# -------------------------------------------------------------------
def make_archive(source_dir: str, output_name: str, 
                 format: str = 'zip') -> Optional[str]:
    try:
        return shutil.make_archive(output_name, format, source_dir)
    except Exception:
        return None
