"""
Logging Utilities
로그 기록 유틸리티

This module provides utility functions for logging and log management.
로그 기록 및 로그 관리를 위한 유틸리티 함수들을 제공합니다.
"""

import logging
import os
from datetime import datetime
from typing import Optional


# -------------------------------------------------------------------
# Set up and configure a logger.
# 로거를 설정하고 구성합니다.
# Args:
# name: Logger name
# 로거 이름
# log_file: Path to log file (None for console only)
# 로그 파일 경로 (None이면 콘솔만)
# level: Logging level
# 로깅 레벨
# format_string: Custom format string
# 사용자 정의 포맷 문자열
# Returns:
# Configured logger
# 구성된 로거
# -------------------------------------------------------------------
def setup_logger(name: str, log_file: Optional[str] = None,
                 level: int = logging.INFO,
                 format_string: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Default format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# -------------------------------------------------------------------
# Write a log message to file.
# 로그 메시지를 파일에 씁니다.
# Args:
# log_file: Path to log file
# 로그 파일 경로
# message: Log message
# 로그 메시지
# level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# 로그 레벨
# Returns:
# True if successful, False otherwise
# 성공하면 True, 실패하면 False
# -------------------------------------------------------------------
def log_to_file(log_file: str, message: str, level: str = 'INFO') -> bool:
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return True
    except Exception:
        return False


# -------------------------------------------------------------------
# Read log file content.
# 로그 파일 내용을 읽습니다.
# Args:
# log_file: Path to log file
# 로그 파일 경로
# last_n_lines: Number of last lines to read (None for all)
# 읽을 마지막 줄 수 (None이면 전체)
# Returns:
# Log content or None if error
# 로그 내용, 에러시 None
# -------------------------------------------------------------------
def read_log_file(log_file: str, last_n_lines: Optional[int] = None) -> Optional[str]:
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            if last_n_lines is None:
                return f.read()
            else:
                lines = f.readlines()
                return ''.join(lines[-last_n_lines:])
    except Exception:
        return None


# -------------------------------------------------------------------
# Clear log file content.
# 로그 파일 내용을 지웁니다.
# Args:
# log_file: Path to log file
# 로그 파일 경로
# Returns:
# True if successful, False otherwise
# 성공하면 True, 실패하면 False
# -------------------------------------------------------------------
def clear_log_file(log_file: str) -> bool:
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('')
        return True
    except Exception:
        return False


# -------------------------------------------------------------------
# Rotate log file if it exceeds max size.
# 로그 파일이 최대 크기를 초과하면 로테이션합니다.
# Args:
# log_file: Path to log file
# 로그 파일 경로
# max_size_mb: Maximum file size in MB
# 최대 파일 크기 (MB)
# Returns:
# True if rotated, False otherwise
# 로테이션되면 True, 아니면 False
# -------------------------------------------------------------------
def rotate_log_file(log_file: str, max_size_mb: float = 10) -> bool:
    try:
        if not os.path.exists(log_file):
            return False
        
        file_size_mb = os.path.getsize(log_file) / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{log_file}.{timestamp}"
            os.rename(log_file, backup_file)
            return True
        
        return False
    except Exception:
        return False


# -------------------------------------------------------------------
# Filter log entries by level.
# 레벨별로 로그 항목을 필터링합니다.
# Args:
# log_file: Path to log file
# 로그 파일 경로
# level: Log level to filter
# 필터링할 로그 레벨
# Returns:
# List of matching log entries or None if error
# 일치하는 로그 항목 리스트, 에러시 None
# -------------------------------------------------------------------
def filter_logs_by_level(log_file: str, level: str) -> Optional[list]:
    try:
        filtered_logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if f'[{level}]' in line:
                    filtered_logs.append(line.strip())
        return filtered_logs
    except Exception:
        return None


# -------------------------------------------------------------------
# Get statistics about log file.
# 로그 파일에 대한 통계를 가져옵니다.
# Args:
# log_file: Path to log file
# 로그 파일 경로
# Returns:
# Dictionary with log statistics or None if error
# 로그 통계 딕셔너리, 에러시 None
# -------------------------------------------------------------------
def get_log_statistics(log_file: str) -> Optional[dict]:
    try:
        stats = {
            'total_lines': 0,
            'DEBUG': 0,
            'INFO': 0,
            'WARNING': 0,
            'ERROR': 0,
            'CRITICAL': 0,
            'file_size_kb': 0
        }
        
        if os.path.exists(log_file):
            stats['file_size_kb'] = os.path.getsize(log_file) / 1024
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    stats['total_lines'] += 1
                    for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                        if f'[{level}]' in line:
                            stats[level] += 1
                            break
        
        return stats
    except Exception:
        return None


# -------------------------------------------------------------------
# Archive log files older than specified days.
# 지정된 일수보다 오래된 로그 파일을 아카이브합니다.
# Args:
# log_dir: Directory containing log files
# 로그 파일이 있는 디렉토리
# days_old: Age threshold in days
# 일 단위 나이 임계값
# Returns:
# Number of files archived
# 아카이브된 파일 수
# -------------------------------------------------------------------
def archive_old_logs(log_dir: str, days_old: int = 7) -> int:
    import time
    import zipfile
    
    archived_count = 0
    current_time = time.time()
    threshold = days_old * 24 * 60 * 60
    
    try:
        archive_name = os.path.join(log_dir, f'logs_archive_{datetime.now().strftime("%Y%m%d")}.zip')
        
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in os.listdir(log_dir):
                if not filename.endswith('.log'):
                    continue
                
                file_path = os.path.join(log_dir, filename)
                file_age = current_time - os.path.getmtime(file_path)
                
                if file_age > threshold:
                    zipf.write(file_path, filename)
                    os.remove(file_path)
                    archived_count += 1
        
        # Remove empty archive
        if archived_count == 0 and os.path.exists(archive_name):
            os.remove(archive_name)
        
        return archived_count
    except Exception:
        return 0


# -------------------------------------------------------------------
# Create a rotating file handler for logger.
# 로거용 로테이팅 파일 핸들러를 생성합니다.
# Args:
# log_file: Path to log file
# 로그 파일 경로
# max_bytes: Maximum file size in bytes
# 최대 파일 크기 (바이트)
# backup_count: Number of backup files to keep
# 유지할 백업 파일 수
# Returns:
# Configured rotating file handler
# 구성된 로테이팅 파일 핸들러
# -------------------------------------------------------------------
def create_rotating_file_handler(log_file: str, max_bytes: int = 10485760,
                                  backup_count: int = 5) -> logging.Handler:
    from logging.handlers import RotatingFileHandler
    
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    return handler
