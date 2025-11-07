# Quick Reference Guide

## sys_util_core - Function Reference

### Command Utilities (cmd_utils)

| Function | Description |
|----------|-------------|
| `run_command(cmd, shell, timeout, cwd, env)` | Execute a command and return exit code, stdout, stderr |
| `run_command_streaming(cmd, shell, cwd, env)` | Execute command and stream output in real-time |
| `check_command_exists(command)` | Check if command exists in PATH |
| `run_command_async(cmd, shell, cwd, env)` | Execute command asynchronously, returns process object |
| `kill_process_by_name(process_name)` | Kill all processes with given name |
| `get_command_output(cmd, shell)` | Execute command and return only stdout |
| `run_elevated_command(cmd)` | Execute with admin/sudo privileges |
| `run_command_with_input(cmd, input_data, shell)` | Execute command with stdin input |
| `get_process_list()` | Get list of running processes |
| `run_batch_commands(commands, stop_on_error, shell)` | Execute multiple commands in sequence |

### Environment Variable Utilities (env_utils)

| Function | Description |
|----------|-------------|
| `get_env_var(var_name, default)` | Get environment variable value |
| `set_env_var(var_name, value, permanent)` | Set environment variable (temporary or permanent) |
| `delete_env_var(var_name, permanent)` | Delete environment variable |
| `get_all_env_vars()` | Get all environment variables as dict |
| `env_var_exists(var_name)` | Check if environment variable exists |
| `get_path_variable()` | Get PATH as list of directories |
| `add_to_path(directory, permanent, position)` | Add directory to PATH |
| `remove_from_path(directory, permanent)` | Remove directory from PATH |
| `expand_env_vars(text)` | Expand environment variables in string |
| `get_system_env_vars()` | Get system-wide environment variables (Windows) |

### File System Utilities (file_utils)

| Function | Description |
|----------|-------------|
| `create_directory(path, exist_ok)` | Create directory with parent directories |
| `delete_directory(path, recursive)` | Delete directory |
| `copy_file(src, dst, overwrite)` | Copy file from source to destination |
| `copy_directory(src, dst, overwrite)` | Copy directory recursively |
| `move_file(src, dst)` | Move or rename file |
| `file_exists(path)` | Check if file exists |
| `directory_exists(path)` | Check if directory exists |
| `get_file_size(path)` | Get file size in bytes |
| `get_file_hash(path, algorithm)` | Calculate file hash (md5, sha1, sha256) |
| `list_files(directory, pattern, recursive)` | List files matching glob pattern |
| `find_files(directory, name_pattern, extension, recursive)` | Find files by name or extension |
| `get_file_modified_time(path)` | Get last modification timestamp |
| `set_file_permissions(path, permissions)` | Set file permissions (Unix) |
| `make_file_readonly(path)` | Make file read-only |
| `make_file_writable(path)` | Make file writable |
| `get_directory_size(path)` | Calculate total directory size |
| `create_temp_file(suffix, prefix, dir, text)` | Create temporary file |
| `create_temp_directory(suffix, prefix, dir)` | Create temporary directory |
| `walk_directory(directory, callback)` | Walk directory tree with callback |

### Windows Registry Utilities (registry_utils)

| Function | Description |
|----------|-------------|
| `is_windows()` | Check if running on Windows |
| `get_registry_value(key_path, value_name, root_key)` | Read registry value |
| `set_registry_value(key_path, value_name, value, value_type, root_key)` | Write registry value |
| `delete_registry_value(key_path, value_name, root_key)` | Delete registry value |
| `create_registry_key(key_path, root_key)` | Create registry key |
| `delete_registry_key(key_path, root_key)` | Delete registry key |
| `registry_key_exists(key_path, root_key)` | Check if registry key exists |
| `list_registry_subkeys(key_path, root_key)` | List all subkeys |
| `list_registry_values(key_path, root_key)` | List all values in key |
| `get_registry_type_name(type_code)` | Get registry value type name |
| `export_registry_key(key_path, output_file, root_key)` | Export key to .reg file |

### Virtual Environment Utilities (venv_utils)

| Function | Description |
|----------|-------------|
| `create_venv(venv_path, python_executable, system_site_packages, clear, with_pip)` | Create a Python virtual environment |
| `delete_venv(venv_path)` | Delete a virtual environment |
| `is_venv(path)` | Check if directory is a virtual environment |
| `get_venv_python(venv_path)` | Get Python executable path from venv |
| `get_venv_pip(venv_path)` | Get pip executable path from venv |
| `install_package(venv_path, package_name, version, upgrade, requirements_file)` | Install package in venv |
| `uninstall_package(venv_path, package_name, yes)` | Uninstall package from venv |
| `list_packages(venv_path, format)` | List all installed packages |
| `upgrade_pip(venv_path)` | Upgrade pip in venv |
| `get_package_info(venv_path, package_name)` | Get detailed package information |
| `freeze_requirements(venv_path, output_file)` | Export packages to requirements.txt |
| `run_in_venv(venv_path, command, cwd)` | Run command inside venv |
| `get_venv_info(venv_path)` | Get venv configuration details |

### PyInstaller Utilities (pyinstaller_utils)

| Function | Description |
|----------|-------------|
| `install_pyinstaller(venv_path, version, upgrade)` | Install PyInstaller in venv or globally |
| `check_pyinstaller_installed(venv_path)` | Check if PyInstaller is installed |
| `build_exe(script_path, output_dir, name, onefile, windowed, icon, console, hidden_imports, additional_data, exclude_modules, venv_path, clean, spec_file)` | Build executable from Python script |
| `generate_spec_file(script_path, output_path, onefile, windowed, icon, hidden_imports, additional_data, venv_path)` | Generate PyInstaller .spec file |
| `clean_build_files(script_path, remove_dist, remove_build, remove_spec)` | Clean PyInstaller build artifacts |
| `get_pyinstaller_version(venv_path)` | Get installed PyInstaller version |
| `analyze_script(script_path, venv_path)` | Analyze script imports and dependencies |
| `build_from_requirements(script_path, requirements_file, venv_path, output_dir, **build_options)` | Create venv, install deps, and build exe |

## Common Usage Patterns

### Execute a command
```python
from sys_util_core import run_command
returncode, stdout, stderr = run_command('ls -la')
```

### Manage environment variables
```python
from sys_util_core import get_env_var, set_env_var
home = get_env_var('HOME')
set_env_var('MY_VAR', 'value')
```

### Work with files
```python
from sys_util_core import copy_file, get_file_hash
copy_file('source.txt', 'dest.txt')
hash_value = get_file_hash('file.txt', 'sha256')
```

### Windows Registry (Windows only)
```python
from sys_util_core import get_registry_value, set_registry_value
value = get_registry_value('Software\\MyApp', 'Setting')
set_registry_value('Software\\MyApp', 'Setting', 'new_value')
```

### Manage virtual environments
```python
from sys_util_core import create_venv, install_package, freeze_requirements

# Create venv and install packages
create_venv('./my_venv')
install_package('./my_venv', 'requests')
freeze_requirements('./my_venv', 'requirements.txt')
```

### Build Python executable
```python
from sys_util_core import build_exe, build_from_requirements

# Simple build
success, exe_path, msg = build_exe('script.py', onefile=True)

# Complete workflow
success, exe_path, msg = build_from_requirements(
    'app.py', 'requirements.txt', './build_venv'
)
```
