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
