"""
Configuration File Management Utilities
설정 파일 관리 유틸리티

This module provides utility functions for managing configuration files (JSON, INI, etc.).
설정 파일(JSON, INI 등)을 관리하기 위한 유틸리티 함수들을 제공합니다.
"""

import json
import configparser
import os
from typing import Any, Dict, Optional, List


def read_json_config(file_path: str, encoding: str = 'utf-8') -> Optional[Dict[str, Any]]:
    '''
    Read configuration from JSON file. JSON 파일에서 설정을 읽습니다.
    Args:
    file_path: Path to JSON file JSON 파일 경로
    encoding: File encoding 파일 인코딩
    Returns:
    Configuration dictionary or None if error 설정 딕셔너리, 에러시 None
    '''
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except Exception:
        return None


def write_json_config(file_path: str, config: Dict[str, Any], 
                      encoding: str = 'utf-8', indent: int = 2) -> bool:
    '''
    Write configuration to JSON file. 설정을 JSON 파일에 씁니다.
    Args:
    file_path: Path to JSON file JSON 파일 경로
    config: Configuration dictionary 설정 딕셔너리
    encoding: File encoding 파일 인코딩
    indent: JSON indentation level JSON 들여쓰기 레벨
    Returns:
    True if successful, False otherwise 성공하면 True, 실패하면 False
    '''
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            json.dump(config, f, ensure_ascii=False, indent=indent)
        return True
    except Exception:
        return False


def read_ini_config(file_path: str, encoding: str = 'utf-8') -> Optional[configparser.ConfigParser]:
    '''
    Read configuration from INI file. INI 파일에서 설정을 읽습니다.
    Args:
    file_path: Path to INI file INI 파일 경로
    encoding: File encoding 파일 인코딩
    Returns:
    ConfigParser object or None if error ConfigParser 객체, 에러시 None
    '''
    try:
        config = configparser.ConfigParser()
        config.read(file_path, encoding=encoding)
        return config
    except Exception:
        return None


def write_ini_config(file_path: str, config: configparser.ConfigParser,
                     encoding: str = 'utf-8') -> bool:
    '''
    Write configuration to INI file. 설정을 INI 파일에 씁니다.
    Args:
    file_path: Path to INI file INI 파일 경로
    config: ConfigParser object ConfigParser 객체
    encoding: File encoding 파일 인코딩
    Returns:
    True if successful, False otherwise 성공하면 True, 실패하면 False
    '''
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            config.write(f)
        return True
    except Exception:
        return False


def get_config_value(config: Dict[str, Any], key_path: str, 
                     default: Any = None) -> Any:
    '''
    Get nested configuration value using dot notation. 점 표기법을 사용하여 중첩된 설정 값을 가져옵니다.
    Args:
    config: Configuration dictionary 설정 딕셔너리
    key_path: Dot-separated key path (e.g., 'database.host') 점으로 구분된 키 경로 (예: 'database.host')
    default: Default value if key not found 키를 찾을 수 없을 때 기본값
    Returns:
    Configuration value or default 설정 값 또는 기본값
    '''
    keys = key_path.split('.')
    value = config
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def set_config_value(config: Dict[str, Any], key_path: str, value: Any) -> bool:
    '''
    Set nested configuration value using dot notation. 점 표기법을 사용하여 중첩된 설정 값을 설정합니다.
    Args:
    config: Configuration dictionary 설정 딕셔너리
    key_path: Dot-separated key path 점으로 구분된 키 경로
    value: Value to set 설정할 값
    Returns:
    True if successful, False otherwise 성공하면 True, 실패하면 False
    '''
    try:
        keys = key_path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        return True
    except Exception:
        return False


def merge_configs(base_config: Dict[str, Any], 
                  override_config: Dict[str, Any]) -> Dict[str, Any]:
    '''
    Merge two configuration dictionaries (override takes precedence). 두 설정 딕셔너리를 병합합니다 (override가 우선).
    Args:
    base_config: Base configuration 기본 설정
    override_config: Override configuration 오버라이드 설정
    Returns:
    Merged configuration 병합된 설정
    '''
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged


def validate_config(config: Dict[str, Any], 
                    required_keys: List[str]) -> tuple[bool, List[str]]:
    '''
    Validate that configuration contains required keys. 설정에 필수 키가 포함되어 있는지 검증합니다.
    Args:
    config: Configuration dictionary 설정 딕셔너리
    required_keys: List of required keys (supports dot notation) 필수 키 리스트 (점 표기법 지원)
    Returns:
    Tuple of (is_valid, missing_keys) (유효 여부, 누락된 키 리스트) 튜플
    '''
    missing_keys = []
    
    for key in required_keys:
        if get_config_value(config, key) is None:
            missing_keys.append(key)
    
    return len(missing_keys) == 0, missing_keys


def load_config_with_env_override(file_path: str, 
                                   env_prefix: str = '') -> Optional[Dict[str, Any]]:
    '''
    Load configuration from file and override with environment variables. 파일에서 설정을 로드하고 환경 변수로 오버라이드합니다.
    Args:
    file_path: Path to JSON config file JSON 설정 파일 경로
    env_prefix: Prefix for environment variables 환경 변수 접두사
    Returns:
    Configuration dictionary or None if error 설정 딕셔너리, 에러시 None
    '''
    config = read_json_config(file_path)
    if config is None:
        return None
    
    # Override with environment variables
    for key, value in os.environ.items():
        if env_prefix and key.startswith(env_prefix):
            config_key = key[len(env_prefix):].lower().replace('_', '.')
            set_config_value(config, config_key, value)
    
    return config


def create_default_config(file_path: str, defaults: Dict[str, Any]) -> bool:
    '''
    Create configuration file with default values if it doesn't exist. 설정 파일이 없으면 기본값으로 생성합니다.
    Args:
    file_path: Path to config file 설정 파일 경로
    defaults: Default configuration values 기본 설정 값
    Returns:
    True if created, False if already exists or error 생성되면 True, 이미 존재하거나 에러시 False
    '''
    if os.path.exists(file_path):
        return False
    
    return write_json_config(file_path, defaults)
