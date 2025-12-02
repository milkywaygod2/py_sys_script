"""
Batch File Processing Utilities
일괄 파일 처리 유틸리티

This module provides utility functions for batch processing files.
파일을 일괄 처리하기 위한 유틸리티 함수들을 제공합니다.
"""

import os
import shutil
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path
import fnmatch


"""
@brief	Batch rename files in a directory by replacing a pattern. 디렉토리 내 파일들의 이름을 패턴 치환으로 일괄 변경합니다.
@param	directory	    Directory containing files 파일이 있는 디렉토리
@param	pattern	        Pattern to replace in filenames 파일명에서 치환할 패턴
@param	replacement	    Replacement text 치환할 텍스트
@param	extensions	    List of file extensions to process (e.g., ['txt', 'pdf']) 처리할 파일 확장자 리스트 (예: ['txt', 'pdf'])
@return	List of renamed file paths 이름이 변경된 파일 경로 리스트
"""
def batch_rename_files(
		directory: str,
		pattern: str,
		replacement: str,
		extensions: Optional[List[str]] = None
 	) -> List[str]:
    renamed_files = []
    
    try:
        for filename in os.listdir(directory):
            if extensions:
                ext = filename.split('.')[-1] if '.' in filename else ''
                if ext not in extensions:
                    continue
            
            if pattern in filename:
                old_path = os.path.join(directory, filename)
                new_filename = filename.replace(pattern, replacement)
                new_path = os.path.join(directory, new_filename)
                
                os.rename(old_path, new_path)
                renamed_files.append(new_path)
    except Exception:
        pass
    
    return renamed_files


"""
@brief	Batch convert file extensions. 파일 확장자를 일괄 변환합니다.
@param	directory	Directory containing files 파일이 있는 디렉토리
@param	old_ext	    Old extension (without dot) 이전 확장자 (점 제외)
@param	new_ext	    New extension (without dot) 새 확장자 (점 제외)
@param	recursive	Process subdirectories 하위 디렉토리 처리
@return	List of converted file paths 변환된 파일 경로 리스트
"""
def batch_convert_extension(
		directory: str,
		old_ext: str,
		new_ext: str,
		recursive: bool = False
 	) -> List[str]:
    converted_files = []
    
    def convert_in_dir(dir_path):
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            
            if os.path.isdir(file_path) and recursive:
                convert_in_dir(file_path)
            elif filename.endswith(f'.{old_ext}'):
                new_path = file_path[:-len(old_ext)] + new_ext
                os.rename(file_path, new_path)
                converted_files.append(new_path)
    
    try:
        convert_in_dir(directory)
    except Exception:
        pass
    
    return converted_files


"""
@brief	Move files to target directory based on extensions. 확장자에 따라 파일을 대상 디렉토리로 이동합니다.
@param	source_dir	Source directory 소스 디렉토리
@param	target_dir	Target directory 대상 디렉토리
@param	extensions	List of extensions to move 이동할 확장자 리스트
@return	Dictionary with extension as key and count of moved files as value 확장자를 키로, 이동된 파일 수를 값으로 하는 딕셔너리
"""
def batch_move_by_extension(
		source_dir: str,
		target_dir: str,
		extensions: List[str]
 	) -> Dict[str, int]:
    moved_counts = {ext: 0 for ext in extensions}
    
    try:
        os.makedirs(target_dir, exist_ok=True)
        
        for filename in os.listdir(source_dir):
            ext = filename.split('.')[-1] if '.' in filename else ''
            
            if ext in extensions:
                source_path = os.path.join(source_dir, filename)
                if os.path.isfile(source_path):
                    target_path = os.path.join(target_dir, filename)
                    shutil.move(source_path, target_path)
                    moved_counts[ext] += 1
    except Exception:
        pass
    
    return moved_counts


"""
@brief	Copy files to target directory based on extensions. 확장자에 따라 파일을 대상 디렉토리로 복사합니다.
@param	source_dir	Source directory 소스 디렉토리
@param	target_dir	Target directory 대상 디렉토리
@param	extensions	List of extensions to copy 복사할 확장자 리스트
@return	Dictionary with extension as key and count of copied files as value 확장자를 키로, 복사된 파일 수를 값으로 하는 딕셔너리
"""
def batch_copy_by_extension(
		source_dir: str,
		target_dir: str,
		extensions: List[str]
 	) -> Dict[str, int]:
    copied_counts = {ext: 0 for ext in extensions}
    
    try:
        os.makedirs(target_dir, exist_ok=True)
        
        for filename in os.listdir(source_dir):
            ext = filename.split('.')[-1] if '.' in filename else ''
            
            if ext in extensions:
                source_path = os.path.join(source_dir, filename)
                if os.path.isfile(source_path):
                    target_path = os.path.join(target_dir, filename)
                    shutil.copy2(source_path, target_path)
                    copied_counts[ext] += 1
    except Exception:
        pass
    
    return copied_counts


"""
@brief	Delete files with specific extensions. 특정 확장자를 가진 파일들을 삭제합니다.
@param	directory	Directory to process 처리할 디렉토리
@param	extensions	List of extensions to delete 삭제할 확장자 리스트
@param	recursive	Process subdirectories 하위 디렉토리 처리
@return	Number of files deleted 삭제된 파일 수
"""
def batch_delete_by_extension(
		directory: str,
		extensions: List[str],
		recursive: bool = False
 	) -> int:
    deleted_count = 0
    
    def delete_in_dir(dir_path):
        nonlocal deleted_count
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            
            if os.path.isdir(file_path) and recursive:
                delete_in_dir(file_path)
            else:
                ext = filename.split('.')[-1] if '.' in filename else ''
                if ext in extensions:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except Exception:
                        pass
    
    try:
        delete_in_dir(directory)
    except Exception:
        pass
    
    return deleted_count


"""
@brief	Apply a processing function to files with specific extensions. 특정 확장자를 가진 파일들에 처리 함수를 적용합니다.
@param	directory	    Directory to process 처리할 디렉토리
@param	extensions	    List of extensions to process 처리할 확장자 리스트
@param	processor_func	Function to apply to each file path 각 파일 경로에 적용할 함수
@param	recursive	    Process subdirectories 하위 디렉토리 처리
@return	Dictionary mapping file paths to processing results 파일 경로를 처리 결과에 매핑한 딕셔너리
"""
def batch_process_files(
		directory: str,
		extensions: List[str],
		processor_func: Callable[[str], Any],
		recursive: bool = False
 	) -> Dict[str, Any]:
    results = {}
    
    def process_in_dir(dir_path):
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            
            if os.path.isdir(file_path) and recursive:
                process_in_dir(file_path)
            else:
                ext = filename.split('.')[-1] if '.' in filename else ''
                if ext in extensions:
                    try:
                        result = processor_func(file_path)
                        results[file_path] = result
                    except Exception as e:
                        results[file_path] = f"Error: {str(e)}"
    
    try:
        process_in_dir(directory)
    except Exception:
        pass
    
    return results


"""
@brief	Organize files into subdirectories based on their extensions. 확장자에 따라 파일들을 하위 디렉토리로 정리합니다.
@param	source_dir	    Directory to organize 정리할 디렉토리
@param	create_subdirs	Create subdirectories for each extension 각 확장자별로 하위 디렉토리 생성
@return	Dictionary with extension as key and count of organized files as value 확장자를 키로, 정리된 파일 수를 값으로 하는 딕셔너리
"""
def organize_files_by_extension(source_dir: str, create_subdirs: bool = True) -> Dict[str, int]:
    organized_counts = {}
    
    try:
        for filename in os.listdir(source_dir):
            file_path = os.path.join(source_dir, filename)
            
            if os.path.isfile(file_path):
                ext = filename.split('.')[-1] if '.' in filename else 'no_extension'
                
                if create_subdirs:
                    ext_dir = os.path.join(source_dir, ext)
                    os.makedirs(ext_dir, exist_ok=True)
                    
                    target_path = os.path.join(ext_dir, filename)
                    shutil.move(file_path, target_path)
                    
                    organized_counts[ext] = organized_counts.get(ext, 0) + 1
    except Exception:
        pass
    
    return organized_counts


"""
@brief	Find duplicate files based on content hash. 콘텐츠 해시를 기반으로 중복 파일을 찾습니다.
@param	directory	Directory to search 검색할 디렉토리
@param	extensions	List of extensions to check (None for all) 확인할 확장자 리스트 (None이면 모두)
@return	Dictionary mapping hash to list of duplicate file paths 해시를 중복 파일 경로 리스트에 매핑한 딕셔너리
"""
def find_duplicate_files(directory: str, extensions: Optional[List[str]] = None) -> Dict[str, List[str]]:
    import hashlib
    
    hash_map = {}
    duplicates = {}
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            if not os.path.isfile(file_path):
                continue
            
            if extensions:
                ext = filename.split('.')[-1] if '.' in filename else ''
                if ext not in extensions:
                    continue
            
            # Calculate file hash
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            
            file_hash = hasher.hexdigest()
            
            if file_hash in hash_map:
                if file_hash not in duplicates:
                    duplicates[file_hash] = [hash_map[file_hash]]
                duplicates[file_hash].append(file_path)
            else:
                hash_map[file_hash] = file_path
    except Exception:
        pass
    
    return duplicates


"""
@brief	Compress files with specific extensions into a zip file. 특정 확장자를 가진 파일들을 zip 파일로 압축합니다.
@param	directory	Directory containing files 파일이 있는 디렉토리
@param	extensions	List of extensions to compress 압축할 확장자 리스트
@param	output_zip	Output zip file path 출력 zip 파일 경로
@return	True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def batch_compress_files(
		directory: str,
		extensions: List[str],
		output_zip: str
 	) -> bool:
    import zipfile
    
    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in os.listdir(directory):
                ext = filename.split('.')[-1] if '.' in filename else ''
                
                if ext in extensions:
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        zipf.write(file_path, filename)
        
        return True
    except Exception:
        return False
