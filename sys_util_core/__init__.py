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

key_path_jfw_py = "path_py_sys_script" # path_jfw_py
value_path_jfw_py = env_utils.get_global_system_env_vars(key_path_jfw_py)

if value_path_jfw_py is None:
    value_path_jfw_py = os.path.dirname(os.path.abspath(__file__))

if value_path_jfw_py and os.path.isdir(value_path_jfw_py):
    if value_path_jfw_py in sys.path:
        env_utils.set_global_system_env_var(key_path_jfw_py, value_path_jfw_py, permanent=True)
else:
    print(f"[ERROR] 환경변수 '{key_path_jfw_py}'에 py_sys_script 폴더 경로가 세팅되어 있지 않거나, 경로가 잘못되었습니다.")
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
from .cmd_utils import (
    run_cmd,
    run_cmd_get_output,
    run_cmd_with_input,
    pause_exit,
)

from .env_utils import (
    get_global_system_env_vars,
    set_global_system_env_var,
)

from .file_utils import (
    FileSystem,
    InstallSystem,
)

from .registry_utils import (
    is_windows,
    get_registry_value,
    set_registry_value,
    delete_registry_value,
    create_registry_key,
    delete_registry_key,
    registry_key_exists,
    list_registry_subkeys,
    list_registry_values,
    get_registry_type_name,
    export_registry_key,
)

from .web_utils import (
    download_url,
    download_file,
    parse_url,
    build_url,
    extract_links,
    extract_text_from_html,
    get_html_element_by_id,
    get_html_elements_by_class,
    fetch_json_api,
    post_json_api,
    check_url_exists,
)

from .excel_utils import (
    read_csv,
    read_csv_as_dict,
    write_csv,
    write_csv_from_dict,
    append_to_csv,
    filter_csv_rows,
    merge_csv_files,
    get_csv_column,
    convert_csv_to_json,
    get_csv_statistics,
)

from .batch_utils import (
    batch_rename_files,
    batch_convert_extension,
    batch_move_by_extension,
    batch_copy_by_extension,
    batch_delete_by_extension,
    batch_process_files,
    organize_files_by_extension,
    find_duplicate_files,
    batch_compress_files,
)

from .venv_utils import (
    create_venv,
    delete_venv,
    is_venv,
    get_venv_python,
    get_venv_pip,
    install_package,
    uninstall_package,
    list_packages,
    upgrade_pip,
    get_package_info,
    freeze_requirements,
    run_in_venv,
    get_venv_info,
    venv_paths,
    install_requirements,
    ensure_pyinstaller,
    clean_build_dirs,
    VenvError,
)

__all__ = [
    # Modules
    'cmd_utils',
    'env_utils',
    'file_utils',
    'registry_utils',
    'web_utils',
    'excel_utils',
    'batch_utils',
    'config_utils',
    'log_utils',
    'network_utils',
    'text_utils',
    'archive_utils',
    'word_utils',
    'pdf_utils',
    'venv_utils',
    '_pyinstaller',
]
