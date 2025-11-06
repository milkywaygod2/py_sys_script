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
"""

__version__ = '0.1.0'

# Import all utilities
from . import cmd_utils
from . import env_utils
from . import file_utils
from . import registry_utils
from . import web_utils
from . import excel_utils
from . import batch_utils

# Expose commonly used functions at package level
from .cmd_utils import (
    run_command,
    run_command_streaming,
    check_command_exists,
    run_command_async,
    kill_process_by_name,
    get_command_output,
    run_elevated_command,
    run_command_with_input,
    get_process_list,
    run_batch_commands,
)

from .env_utils import (
    get_env_var,
    set_env_var,
    delete_env_var,
    get_all_env_vars,
    env_var_exists,
    get_path_variable,
    add_to_path,
    remove_from_path,
    expand_env_vars,
    get_system_env_vars,
)

from .file_utils import (
    create_directory,
    delete_directory,
    copy_file,
    copy_directory,
    move_file,
    file_exists,
    directory_exists,
    get_file_size,
    get_file_hash,
    list_files,
    find_files,
    get_file_modified_time,
    set_file_permissions,
    make_file_readonly,
    make_file_writable,
    get_directory_size,
    create_temp_file,
    create_temp_directory,
    walk_directory,
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

__all__ = [
    # Modules
    'cmd_utils',
    'env_utils',
    'file_utils',
    'registry_utils',
    'web_utils',
    'excel_utils',
    'batch_utils',
    
    # Command utilities
    'run_command',
    'run_command_streaming',
    'check_command_exists',
    'run_command_async',
    'kill_process_by_name',
    'get_command_output',
    'run_elevated_command',
    'run_command_with_input',
    'get_process_list',
    'run_batch_commands',
    
    # Environment utilities
    'get_env_var',
    'set_env_var',
    'delete_env_var',
    'get_all_env_vars',
    'env_var_exists',
    'get_path_variable',
    'add_to_path',
    'remove_from_path',
    'expand_env_vars',
    'get_system_env_vars',
    
    # File utilities
    'create_directory',
    'delete_directory',
    'copy_file',
    'copy_directory',
    'move_file',
    'file_exists',
    'directory_exists',
    'get_file_size',
    'get_file_hash',
    'list_files',
    'find_files',
    'get_file_modified_time',
    'set_file_permissions',
    'make_file_readonly',
    'make_file_writable',
    'get_directory_size',
    'create_temp_file',
    'create_temp_directory',
    'walk_directory',
    
    # Registry utilities
    'is_windows',
    'get_registry_value',
    'set_registry_value',
    'delete_registry_value',
    'create_registry_key',
    'delete_registry_key',
    'registry_key_exists',
    'list_registry_subkeys',
    'list_registry_values',
    'get_registry_type_name',
    'export_registry_key',
    
    # Web utilities
    'download_url',
    'download_file',
    'parse_url',
    'build_url',
    'extract_links',
    'extract_text_from_html',
    'get_html_element_by_id',
    'get_html_elements_by_class',
    'fetch_json_api',
    'post_json_api',
    'check_url_exists',
    
    # Excel/CSV utilities
    'read_csv',
    'read_csv_as_dict',
    'write_csv',
    'write_csv_from_dict',
    'append_to_csv',
    'filter_csv_rows',
    'merge_csv_files',
    'get_csv_column',
    'convert_csv_to_json',
    'get_csv_statistics',
    
    # Batch utilities
    'batch_rename_files',
    'batch_convert_extension',
    'batch_move_by_extension',
    'batch_copy_by_extension',
    'batch_delete_by_extension',
    'batch_process_files',
    'organize_files_by_extension',
    'find_duplicate_files',
    'batch_compress_files',
]
