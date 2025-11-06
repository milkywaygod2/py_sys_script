#!/usr/bin/env python3
"""
Example usage of sys_util_core library

This script demonstrates various utility functions from the library.
"""

import sys
import os

# Add parent directory to path if running from examples directory
if os.path.basename(os.getcwd()) == 'examples':
    sys.path.insert(0, os.path.dirname(os.getcwd()))

from sys_util_core import (
    # Command utilities
    run_command, check_command_exists, get_process_list,
    # Environment utilities
    get_env_var, get_path_variable, env_var_exists,
    # File utilities
    create_temp_directory, create_temp_file, get_file_size,
    file_exists, list_files, get_file_hash,
    # Registry utilities
    is_windows
)


def demo_command_utilities():
    """Demonstrate command execution utilities"""
    print("\n=== Command Utilities Demo ===")
    
    # Check if a command exists
    print("\n1. Check if 'python' command exists:")
    if check_command_exists('python'):
        print("   ✓ Python is available")
        
        # Run a command
        returncode, stdout, stderr = run_command('python --version')
        print(f"   Python version: {stdout.strip()}")
    
    # Get process list
    print("\n2. List running processes (first 5):")
    processes = get_process_list()
    for proc in processes[:5]:
        print(f"   - {proc}")


def demo_environment_utilities():
    """Demonstrate environment variable utilities"""
    print("\n=== Environment Utilities Demo ===")
    
    # Get environment variable
    print("\n1. Get PATH environment variable:")
    path_dirs = get_path_variable()
    print(f"   Found {len(path_dirs)} directories in PATH")
    print(f"   First 3: {path_dirs[:3]}")
    
    # Check if variable exists
    print("\n2. Check if HOME/USERPROFILE exists:")
    home_var = 'USERPROFILE' if is_windows() else 'HOME'
    if env_var_exists(home_var):
        home_path = get_env_var(home_var)
        print(f"   ✓ {home_var} = {home_path}")


def demo_file_utilities():
    """Demonstrate file system utilities"""
    print("\n=== File Utilities Demo ===")
    
    # Create temporary directory
    print("\n1. Create temporary directory:")
    temp_dir = create_temp_directory(prefix='demo_')
    print(f"   Created: {temp_dir}")
    
    # Create temporary file
    print("\n2. Create temporary file:")
    temp_file = create_temp_file(suffix='.txt', dir=temp_dir)
    print(f"   Created: {temp_file}")
    
    # Write some content
    with open(temp_file, 'w') as f:
        f.write("Hello, sys_util_core!")
    
    # Get file size
    size = get_file_size(temp_file)
    print(f"   File size: {size} bytes")
    
    # Calculate hash
    hash_value = get_file_hash(temp_file, 'md5')
    print(f"   MD5 hash: {hash_value}")
    
    # List files in temp directory
    print("\n3. List files in temp directory:")
    files = list_files(temp_dir, '*')
    for f in files:
        print(f"   - {os.path.basename(f)}")
    
    # Clean up
    import shutil
    shutil.rmtree(temp_dir)
    print(f"\n   Cleaned up: {temp_dir}")


def demo_registry_utilities():
    """Demonstrate Windows registry utilities"""
    print("\n=== Registry Utilities Demo ===")
    
    print(f"\n1. Running on Windows: {is_windows()}")
    
    if is_windows():
        print("   Registry operations are available")
        print("   Note: Registry examples are skipped for safety")
    else:
        print("   Registry operations only available on Windows")


def main():
    """Main demonstration function"""
    print("=" * 60)
    print("sys_util_core Library - Usage Examples")
    print("=" * 60)
    
    demo_command_utilities()
    demo_environment_utilities()
    demo_file_utilities()
    demo_registry_utilities()
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
