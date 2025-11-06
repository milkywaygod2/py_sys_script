"""
CSV and Excel File Utilities
CSV 및 Excel 파일 유틸리티

This module provides utility functions for working with CSV and Excel files.
CSV 및 Excel 파일을 다루기 위한 유틸리티 함수들을 제공합니다.

Note: Excel functions require openpyxl package for .xlsx files
참고: Excel 함수는 .xlsx 파일을 위해 openpyxl 패키지가 필요합니다
"""

import csv
import os
from typing import List, Dict, Any, Optional, Union


def read_csv(file_path: str, encoding: str = 'utf-8', 
             delimiter: str = ',') -> List[List[str]]:
    """
    Read CSV file and return data as list of lists.
    CSV 파일을 읽고 리스트의 리스트로 데이터를 반환합니다.
    
    Args:
        file_path: Path to CSV file
                   CSV 파일 경로
        encoding: File encoding
                  파일 인코딩
        delimiter: CSV delimiter character
                   CSV 구분 문자
        
    Returns:
        List of rows, each row is a list of values
        행의 리스트, 각 행은 값의 리스트
    """
    data = []
    try:
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            reader = csv.reader(f, delimiter=delimiter)
            data = list(reader)
    except Exception:
        pass
    
    return data


def read_csv_as_dict(file_path: str, encoding: str = 'utf-8',
                     delimiter: str = ',') -> List[Dict[str, str]]:
    """
    Read CSV file with headers and return data as list of dictionaries.
    헤더가 있는 CSV 파일을 읽고 딕셔너리 리스트로 데이터를 반환합니다.
    
    Args:
        file_path: Path to CSV file
                   CSV 파일 경로
        encoding: File encoding
                  파일 인코딩
        delimiter: CSV delimiter character
                   CSV 구분 문자
        
    Returns:
        List of dictionaries, each representing a row
        각 행을 나타내는 딕셔너리 리스트
    """
    data = []
    try:
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            data = list(reader)
    except Exception:
        pass
    
    return data


def write_csv(file_path: str, data: List[List[Any]], 
              encoding: str = 'utf-8', delimiter: str = ',') -> bool:
    """
    Write data to CSV file.
    CSV 파일에 데이터를 씁니다.
    
    Args:
        file_path: Path to CSV file
                   CSV 파일 경로
        data: Data to write (list of lists)
              쓸 데이터 (리스트의 리스트)
        encoding: File encoding
                  파일 인코딩
        delimiter: CSV delimiter character
                   CSV 구분 문자
        
    Returns:
        True if successful, False otherwise
        성공하면 True, 실패하면 False
    """
    try:
        with open(file_path, 'w', encoding=encoding, newline='') as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerows(data)
        return True
    except Exception:
        return False


def write_csv_from_dict(file_path: str, data: List[Dict[str, Any]],
                        fieldnames: Optional[List[str]] = None,
                        encoding: str = 'utf-8', delimiter: str = ',') -> bool:
    """
    Write dictionary data to CSV file with headers.
    헤더와 함께 딕셔너리 데이터를 CSV 파일에 씁니다.
    
    Args:
        file_path: Path to CSV file
                   CSV 파일 경로
        data: Data to write (list of dictionaries)
              쓸 데이터 (딕셔너리 리스트)
        fieldnames: Column names (auto-detected if None)
                    컬럼 이름 (None이면 자동 감지)
        encoding: File encoding
                  파일 인코딩
        delimiter: CSV delimiter character
                   CSV 구분 문자
        
    Returns:
        True if successful, False otherwise
        성공하면 True, 실패하면 False
    """
    try:
        if not data:
            return False
        
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        
        with open(file_path, 'w', encoding=encoding, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception:
        return False


def append_to_csv(file_path: str, rows: List[List[Any]], 
                  encoding: str = 'utf-8', delimiter: str = ',') -> bool:
    """
    Append rows to existing CSV file.
    기존 CSV 파일에 행을 추가합니다.
    
    Args:
        file_path: Path to CSV file
                   CSV 파일 경로
        rows: Rows to append
              추가할 행들
        encoding: File encoding
                  파일 인코딩
        delimiter: CSV delimiter character
                   CSV 구분 문자
        
    Returns:
        True if successful, False otherwise
        성공하면 True, 실패하면 False
    """
    try:
        with open(file_path, 'a', encoding=encoding, newline='') as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerows(rows)
        return True
    except Exception:
        return False


def filter_csv_rows(file_path: str, condition_func, 
                    output_path: Optional[str] = None,
                    encoding: str = 'utf-8') -> List[Dict[str, str]]:
    """
    Filter CSV rows based on a condition function.
    조건 함수에 따라 CSV 행을 필터링합니다.
    
    Args:
        file_path: Path to CSV file
                   CSV 파일 경로
        condition_func: Function that takes a row dict and returns bool
                        행 딕셔너리를 받아 bool을 반환하는 함수
        output_path: Optional path to save filtered data
                     필터링된 데이터를 저장할 선택적 경로
        encoding: File encoding
                  파일 인코딩
        
    Returns:
        List of filtered rows
        필터링된 행 리스트
    """
    data = read_csv_as_dict(file_path, encoding=encoding)
    filtered = [row for row in data if condition_func(row)]
    
    if output_path and filtered:
        write_csv_from_dict(output_path, filtered, encoding=encoding)
    
    return filtered


def merge_csv_files(input_files: List[str], output_file: str,
                    encoding: str = 'utf-8', include_headers: bool = True) -> bool:
    """
    Merge multiple CSV files into one.
    여러 CSV 파일을 하나로 병합합니다.
    
    Args:
        input_files: List of CSV file paths to merge
                     병합할 CSV 파일 경로 리스트
        output_file: Output file path
                     출력 파일 경로
        encoding: File encoding
                  파일 인코딩
        include_headers: Include headers from first file only
                         첫 번째 파일의 헤더만 포함
        
    Returns:
        True if successful, False otherwise
        성공하면 True, 실패하면 False
    """
    try:
        all_data = []
        first_file = True
        
        for file_path in input_files:
            data = read_csv(file_path, encoding=encoding)
            
            if not data:
                continue
            
            if first_file or not include_headers:
                all_data.extend(data)
                first_file = False
            else:
                # Skip header row for subsequent files
                all_data.extend(data[1:])
        
        return write_csv(output_file, all_data, encoding=encoding)
    except Exception:
        return False


def get_csv_column(file_path: str, column_name: str, 
                   encoding: str = 'utf-8') -> List[str]:
    """
    Extract a specific column from CSV file.
    CSV 파일에서 특정 컬럼을 추출합니다.
    
    Args:
        file_path: Path to CSV file
                   CSV 파일 경로
        column_name: Name of column to extract
                     추출할 컬럼 이름
        encoding: File encoding
                  파일 인코딩
        
    Returns:
        List of values from the column
        컬럼의 값 리스트
    """
    data = read_csv_as_dict(file_path, encoding=encoding)
    return [row.get(column_name, '') for row in data]


def convert_csv_to_json(csv_path: str, json_path: Optional[str] = None,
                        encoding: str = 'utf-8') -> Optional[List[Dict[str, str]]]:
    """
    Convert CSV file to JSON format.
    CSV 파일을 JSON 형식으로 변환합니다.
    
    Args:
        csv_path: Path to CSV file
                  CSV 파일 경로
        json_path: Optional path to save JSON file
                   JSON 파일을 저장할 선택적 경로
        encoding: File encoding
                  파일 인코딩
        
    Returns:
        Data as list of dictionaries, or None if error
        딕셔너리 리스트로 된 데이터, 에러시 None
    """
    import json
    
    try:
        data = read_csv_as_dict(csv_path, encoding=encoding)
        
        if json_path:
            with open(json_path, 'w', encoding=encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        return data
    except Exception:
        return None


def get_csv_statistics(file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
    """
    Get basic statistics about a CSV file.
    CSV 파일에 대한 기본 통계를 가져옵니다.
    
    Args:
        file_path: Path to CSV file
                   CSV 파일 경로
        encoding: File encoding
                  파일 인코딩
        
    Returns:
        Dictionary with file statistics
        파일 통계를 담은 딕셔너리
    """
    data = read_csv(file_path, encoding=encoding)
    
    if not data:
        return {
            'row_count': 0,
            'column_count': 0,
            'has_header': False,
            'file_size': 0
        }
    
    return {
        'row_count': len(data),
        'column_count': len(data[0]) if data else 0,
        'has_header': True,  # Assumed
        'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
    }
