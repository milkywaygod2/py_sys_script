"""
System Utility Core Library

A comprehensive utility library for system automation tasks including:
- Command execution utilities
- Environment variable management
- File system operations
- Windows registry operations
- Web scraping and automation
- CSV and Excel file handling
- Batch file processing
- Configuration file management
- Logging utilities
- Network operations
- Text processing
- Archive and compression
- MS Word document automation
- PDF conversion
- Virtual environment management
- PyInstaller utilities for creating executables
"""

__version__ = '0.2.0'

# Add the current directory to Python path for imports
import os
import sys
import env_utils

reg_path_key = "path_jfw_py"
reg_path_value = env_utils.get_global_system_env_vars(reg_path_key)

if reg_path_value is None:
    reg_path_value = os.path.dirname(os.path.abspath(__file__))

if reg_path_value and os.path.isdir(reg_path_value):
    if reg_path_value in sys.path:
        env_utils.set_global_system_env_var(reg_path_key, reg_path_value, permanent=True)
else:
    print(f"[ERROR] 환경변수 '{reg_path_key}'에 py_sys_script 폴더 경로가 세팅되어 있지 않거나, 경로가 잘못되었습니다.")
    sys.exit(1)

# Import all utilities
from sys_util_core import cmd_utils
from sys_util_core import env_utils
from sys_util_core import file_utils
from sys_util_core import registry_utils
from sys_util_core import web_utils
from sys_util_core import excel_utils
from sys_util_core import batch_utils
from sys_util_core import config_utils
from sys_util_core import log_utils
from sys_util_core import network_utils
from sys_util_core import text_utils
from sys_util_core import archive_utils
from sys_util_core import word_utils
from sys_util_core import pdf_utils
from sys_util_core import venv_utils

# Expose commonly used functions at package level
# from .cmd_utils import (
#     run_cmd,
#     run_cmd_get_output,
#     run_cmd_with_input,
#     pause_exit,
# )

__all__ = [
    # Modules
    'archive_utils',
    'batch_utils',
    'cmd_utils',
    'config_utils',
    'env_utils',
    'excel_utils',
    'file_utils',
    'log_utils',
    'network_utils',
    'pdf_utils',
    'registry_utils',
    'text_utils',
    'venv_utils',
    'web_utils',
    'word_utils',
]
