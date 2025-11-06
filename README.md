# py_sys_script - System Utility Core Library

A comprehensive Python utility library for system automation tasks, providing easy-to-use functions for command execution, environment variable management, file system operations, and Windows registry manipulation.

## Features

The library is organized into four main modules:

### 1. Command Utilities (`cmd_utils`)
Execute and manage system commands with ease.

**10 Representative Functions:**
1. `run_command()` - Execute commands and get output
2. `run_command_streaming()` - Stream command output in real-time
3. `check_command_exists()` - Verify if a command is available
4. `run_command_async()` - Run commands asynchronously
5. `kill_process_by_name()` - Terminate processes by name
6. `get_command_output()` - Get stdout from command execution
7. `run_elevated_command()` - Execute with admin/sudo privileges
8. `run_command_with_input()` - Send input to commands
9. `get_process_list()` - List running processes
10. `run_batch_commands()` - Execute multiple commands in sequence

### 2. Environment Variable Utilities (`env_utils`)
Manage environment variables and system paths.

**10 Representative Functions:**
1. `get_env_var()` - Get environment variable value
2. `set_env_var()` - Set environment variable (temporary or permanent)
3. `delete_env_var()` - Remove environment variable
4. `get_all_env_vars()` - Get all environment variables
5. `env_var_exists()` - Check if variable exists
6. `get_path_variable()` - Get PATH as list of directories
7. `add_to_path()` - Add directory to PATH
8. `remove_from_path()` - Remove directory from PATH
9. `expand_env_vars()` - Expand variables in strings
10. `get_system_env_vars()` - Get system-wide variables (Windows)

### 3. File System Utilities (`file_utils`)
Perform common file and directory operations.

**19 Representative Functions:**
1. `create_directory()` - Create directory with parents
2. `delete_directory()` - Delete directory recursively
3. `copy_file()` - Copy files with options
4. `copy_directory()` - Copy directories recursively
5. `move_file()` - Move or rename files
6. `file_exists()` - Check file existence
7. `directory_exists()` - Check directory existence
8. `get_file_size()` - Get file size in bytes
9. `get_file_hash()` - Calculate file hash (MD5/SHA)
10. `list_files()` - List files matching pattern
11. `find_files()` - Search files by name/extension
12. `get_file_modified_time()` - Get modification timestamp
13. `set_file_permissions()` - Set file permissions
14. `make_file_readonly()` - Make file read-only
15. `make_file_writable()` - Make file writable
16. `get_directory_size()` - Calculate directory size
17. `create_temp_file()` - Create temporary file
18. `create_temp_directory()` - Create temporary directory
19. `walk_directory()` - Walk directory tree with callback

### 4. Windows Registry Utilities (`registry_utils`)
Manage Windows Registry (Windows-only features).

**11 Representative Functions:**
1. `is_windows()` - Check if running on Windows
2. `get_registry_value()` - Read registry value
3. `set_registry_value()` - Write registry value
4. `delete_registry_value()` - Delete registry value
5. `create_registry_key()` - Create registry key
6. `delete_registry_key()` - Delete registry key
7. `registry_key_exists()` - Check if key exists
8. `list_registry_subkeys()` - List all subkeys
9. `list_registry_values()` - List all values in key
10. `get_registry_type_name()` - Get value type name
11. `export_registry_key()` - Export key to .reg file

## Installation

### From source:
```bash
git clone https://github.com/milkywaygod2/py_sys_script.git
cd py_sys_script
pip install -e .
```

### Using pip (when published):
```bash
pip install sys_util_core
```

## Usage Examples

### Command Execution
```python
from sys_util_core import run_command, check_command_exists

# Check if a command exists
if check_command_exists('python'):
    # Run a command
    returncode, stdout, stderr = run_command('python --version')
    print(f"Output: {stdout}")

# Stream command output
from sys_util_core import run_command_streaming
for line in run_command_streaming('pip list'):
    print(line)
```

### Environment Variables
```python
from sys_util_core import get_env_var, set_env_var, add_to_path

# Get environment variable
home = get_env_var('HOME')

# Set environment variable
set_env_var('MY_VAR', 'my_value', permanent=False)

# Add to PATH
add_to_path('/usr/local/bin', position='start')
```

### File Operations
```python
from sys_util_core import copy_file, find_files, get_file_hash

# Copy a file
copy_file('/path/to/source.txt', '/path/to/dest.txt')

# Find all Python files
python_files = find_files('/my/project', extension='py', recursive=True)

# Calculate file hash
hash_value = get_file_hash('/path/to/file.txt', algorithm='sha256')
```

### Windows Registry
```python
from sys_util_core import get_registry_value, set_registry_value

# Read from registry (Windows only)
value = get_registry_value('Software\\MyApp', 'Setting1')

# Write to registry
set_registry_value('Software\\MyApp', 'Setting1', 'new_value')
```

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library)

## Platform Support

- **Command utilities**: Cross-platform (Windows, Linux, macOS)
- **Environment utilities**: Cross-platform
- **File utilities**: Cross-platform
- **Registry utilities**: Windows only

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

milkywaygod2
