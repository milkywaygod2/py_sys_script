"""
System Utility Core Library

A comprehensive utility library for system automation tasks including:
- Command execution utilities
- Environment variable management
- File system operations
- Windows registry operations
"""

__version__ = '0.1.0'

# Import all utilities
from . import cmd_utils
from . import env_utils
from . import file_utils
from . import registry_utils

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

__all__ = [
    # Modules
    'cmd_utils',
    'env_utils',
    'file_utils',
    'registry_utils',
    
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
]
