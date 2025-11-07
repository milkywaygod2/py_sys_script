# Virtual Environment & PyInstaller Utilities Documentation
# 가상 환경 및 PyInstaller 유틸리티 문서

## Overview | 개요

This document provides comprehensive documentation for managing Python virtual environments and converting Python scripts to standalone executables.

이 문서는 파이썬 가상 환경 관리 및 파이썬 스크립트를 독립 실행형 실행 파일로 변환하는 것에 대한 포괄적인 문서를 제공합니다.

## Virtual Environment Management | 가상 환경 관리

### Creating a Virtual Environment | 가상 환경 생성

```python
from sys_util_core import create_venv

# Basic usage | 기본 사용법
success, message = create_venv('./my_project_venv')

# Advanced options | 고급 옵션
success, message = create_venv(
    venv_path='./my_venv',
    python_executable='/usr/bin/python3.9',  # Specific Python version
    system_site_packages=False,              # Isolate from system packages
    clear=True,                              # Recreate if exists
    with_pip=True                            # Install pip
)

# Exception handling | 예외 처리
from sys_util_core import VenvError

try:
    success, message = create_venv('./my_venv')
    print(message)
except VenvError as e:
    print(f"Error creating venv: {e}")
```

### Managing Packages | 패키지 관리

#### Installing Packages | 패키지 설치

```python
from sys_util_core import install_package

# Install latest version | 최신 버전 설치
success, message = install_package('./my_venv', 'requests')

# Install specific version | 특정 버전 설치
success, message = install_package('./my_venv', 'numpy', version='1.21.0')

# Upgrade existing package | 기존 패키지 업그레이드
success, message = install_package('./my_venv', 'requests', upgrade=True)

# Install from requirements.txt | requirements.txt에서 설치
success, message = install_package(
    './my_venv',
    package_name='',  # Not used when using requirements_file
    requirements_file='requirements.txt'
)

# Exception handling | 예외 처리
try:
    success, message = install_package('./my_venv', 'nonexistent-package')
except VenvError as e:
    print(f"Installation failed: {e}")
```

#### Listing Packages | 패키지 목록 조회

```python
from sys_util_core import list_packages

# List in columns format | 컬럼 형식으로 나열
success, output, packages = list_packages('./my_venv', format='columns')
print(output)

# List in JSON format | JSON 형식으로 나열
success, output, packages = list_packages('./my_venv', format='json')
for pkg in packages:
    print(f"{pkg['name']}: {pkg['version']}")

# List in freeze format | freeze 형식으로 나열
success, output, packages = list_packages('./my_venv', format='freeze')
print(output)
```

#### Uninstalling Packages | 패키지 제거

```python
from sys_util_core import uninstall_package

# Uninstall a package | 패키지 제거
success, message = uninstall_package('./my_venv', 'requests')

# Auto-confirm uninstallation | 자동으로 제거 확인
success, message = uninstall_package('./my_venv', 'numpy', yes=True)
```

#### Getting Package Information | 패키지 정보 조회

```python
from sys_util_core import get_package_info

# Get detailed package info | 상세 패키지 정보 조회
success, info = get_package_info('./my_venv', 'requests')

print(f"Name: {info.get('Name')}")
print(f"Version: {info.get('Version')}")
print(f"Summary: {info.get('Summary')}")
print(f"Location: {info.get('Location')}")
```

### Working with Requirements | Requirements 작업

```python
from sys_util_core import freeze_requirements

# Export installed packages to requirements.txt
# 설치된 패키지를 requirements.txt로 내보내기
success, message = freeze_requirements('./my_venv', 'requirements.txt')

# Later, install from this file | 나중에 이 파일에서 설치
from sys_util_core import install_package
success, message = install_package(
    './new_venv',
    package_name='',
    requirements_file='requirements.txt'
)
```

### Running Commands in Virtual Environment | 가상 환경에서 명령 실행

```python
from sys_util_core import run_in_venv

# Run a Python script | 파이썬 스크립트 실행
returncode, stdout, stderr = run_in_venv(
    './my_venv',
    ['python', 'my_script.py']
)

if returncode == 0:
    print("Success!")
    print(stdout)
else:
    print("Error!")
    print(stderr)

# Run in specific directory | 특정 디렉토리에서 실행
returncode, stdout, stderr = run_in_venv(
    './my_venv',
    ['python', 'test.py'],
    cwd='/path/to/project'
)
```

### Getting Virtual Environment Information | 가상 환경 정보 조회

```python
from sys_util_core import get_venv_info, is_venv

# Check if directory is a venv | 디렉토리가 venv인지 확인
if is_venv('./my_venv'):
    info = get_venv_info('./my_venv')
    
    print(f"Path: {info['path']}")
    print(f"Python: {info['python']}")
    print(f"Pip: {info['pip']}")
    print(f"Home: {info.get('home')}")
```

### Cleaning Up | 정리

```python
from sys_util_core import delete_venv

# Delete virtual environment | 가상 환경 삭제
success, message = delete_venv('./my_venv')

# Exception handling | 예외 처리
try:
    success, message = delete_venv('./my_venv')
    if success:
        print("Virtual environment deleted successfully")
except VenvError as e:
    print(f"Error deleting venv: {e}")
```

## PyInstaller Utilities | PyInstaller 유틸리티

### Installing PyInstaller | PyInstaller 설치

```python
from sys_util_core import install_pyinstaller, check_pyinstaller_installed

# Install in virtual environment | 가상 환경에 설치
success, message = install_pyinstaller('./my_venv')

# Install specific version | 특정 버전 설치
success, message = install_pyinstaller('./my_venv', version='5.0.0')

# Upgrade PyInstaller | PyInstaller 업그레이드
success, message = install_pyinstaller('./my_venv', upgrade=True)

# Install globally (not recommended) | 전역 설치 (권장하지 않음)
success, message = install_pyinstaller()

# Check if installed | 설치 확인
if check_pyinstaller_installed('./my_venv'):
    print("PyInstaller is installed")
```

### Building Executables | 실행 파일 빌드

#### Basic Build | 기본 빌드

```python
from sys_util_core import build_exe

# Simple one-file executable | 간단한 단일 파일 실행 파일
success, exe_path, message = build_exe(
    'my_script.py',
    onefile=True
)

if success:
    print(f"Executable created at: {exe_path}")
```

#### Simplified Build Interface | 간소화된 빌드 인터페이스

```python
from sys_util_core import build_with_pyinstaller
from pathlib import Path
import sys

# Simple build using PyInstaller directly
# PyInstaller를 직접 사용하는 간단한 빌드
build_with_pyinstaller(
    py_path=Path(sys.executable),
    src=Path('my_script.py'),
    onefile=True,
    noconsole=False
)

# Build with icon and data files | 아이콘과 데이터 파일로 빌드
build_with_pyinstaller(
    py_path=Path(sys.executable),
    src=Path('my_app.py'),
    onefile=True,
    noconsole=True,  # No console window for GUI apps
    add_data=[
        ('data/', 'data'),      # OS-specific separator is handled automatically
        ('config.ini', '.')     # OS별 구분자가 자동으로 처리됨
    ],
    icon=Path('app_icon.ico')
)

# Note: build_with_pyinstaller prints output directly and raises
# subprocess.CalledProcessError if build fails
# 참고: build_with_pyinstaller는 출력을 직접 출력하고
# 빌드 실패 시 subprocess.CalledProcessError를 발생시킵니다
```

#### Advanced Build Options | 고급 빌드 옵션

```python
from sys_util_core import build_exe

# Build with all options | 모든 옵션으로 빌드
success, exe_path, message = build_exe(
    script_path='my_app.py',
    output_dir='./dist',              # Output directory
    name='MyApplication',             # Executable name
    onefile=True,                     # Single file bundle
    windowed=True,                    # No console window (GUI apps)
    console=False,                    # Same as windowed
    icon='app_icon.ico',              # Application icon
    hidden_imports=['pkg_resources', 'configparser'],  # Imports PyInstaller might miss
    additional_data=[                 # Include data files
        ('data/', 'data'),            # Copy data/ folder to data/ in exe
        ('config.ini', '.'),          # Copy config.ini to root in exe
    ],
    exclude_modules=['tkinter'],      # Exclude unnecessary modules
    venv_path='./my_venv',           # Use specific venv
    clean=True                        # Clean cache before building
)

# Exception handling | 예외 처리
from sys_util_core import PyInstallerError

try:
    success, exe_path, message = build_exe('my_script.py')
except PyInstallerError as e:
    print(f"Build failed: {e}")
```

#### Platform-Specific Icons | 플랫폼별 아이콘

```python
import sys
from sys_util_core import build_exe

# Use platform-specific icon | 플랫폼별 아이콘 사용
if sys.platform == 'win32':
    icon_file = 'icon.ico'
elif sys.platform == 'darwin':
    icon_file = 'icon.icns'
else:
    icon_file = None

success, exe_path, message = build_exe(
    'my_app.py',
    icon=icon_file
)
```

### Using Spec Files | Spec 파일 사용

```python
from sys_util_core import generate_spec_file, build_exe

# Generate a spec file | spec 파일 생성
success, spec_file = generate_spec_file(
    'my_app.py',
    output_path='custom_build.spec',
    onefile=True,
    windowed=True,
    icon='icon.ico',
    hidden_imports=['hidden_module'],
    additional_data=[('data/', 'data')]
)

# Edit the spec file manually if needed
# 필요한 경우 spec 파일을 수동으로 편집

# Build using the spec file | spec 파일을 사용하여 빌드
success, exe_path, message = build_exe(
    'my_app.py',  # Still needed as reference
    spec_file=spec_file,
    venv_path='./my_venv'
)
```

### Analyzing Scripts | 스크립트 분석

```python
from sys_util_core import analyze_script

# Analyze script to see what will be included
# 포함될 항목을 확인하기 위해 스크립트 분석
success, analysis = analyze_script('my_script.py')
print(analysis)

# This helps identify hidden imports
# 숨겨진 임포트를 식별하는 데 도움
```

### Complete Workflow | 완전한 워크플로우

```python
from sys_util_core import build_from_requirements

# All-in-one: create venv, install dependencies, build exe
# 올인원: venv 생성, 종속성 설치, exe 빌드
success, exe_path, message = build_from_requirements(
    script_path='my_application.py',
    requirements_file='requirements.txt',
    venv_path='./build_env',
    output_dir='./dist',
    name='MyApp',
    onefile=True,
    icon='icon.ico',
    windowed=True,
    hidden_imports=['pkg_resources']
)

if success:
    print(f"Build complete! Executable: {exe_path}")
    print(message)
```

### Cleaning Build Artifacts | 빌드 아티팩트 정리

```python
from sys_util_core import clean_build_files

# Clean all build files | 모든 빌드 파일 정리
success, message = clean_build_files(
    script_path='my_app.py',
    remove_dist=True,      # Remove dist/ directory
    remove_build=True,     # Remove build/ directory
    remove_spec=True       # Remove .spec file
)

# Clean only build directory | build 디렉토리만 정리
success, message = clean_build_files(
    remove_build=True,
    remove_dist=False,
    remove_spec=False
)
```

## Complete Examples | 완전한 예제

### Example 1: Development Environment Setup | 예제 1: 개발 환경 설정

```python
from sys_util_core import (
    create_venv, install_package, list_packages, 
    freeze_requirements, VenvError
)

def setup_project_environment(project_path, requirements):
    """Setup a complete project environment"""
    venv_path = f"{project_path}/.venv"
    
    try:
        # Create virtual environment
        print("Creating virtual environment...")
        success, msg = create_venv(venv_path)
        if not success:
            raise VenvError(msg)
        
        # Install requirements
        print("Installing requirements...")
        success, msg = install_package(
            venv_path,
            package_name='',
            requirements_file=requirements
        )
        if not success:
            raise VenvError(msg)
        
        # List installed packages
        print("\nInstalled packages:")
        success, output, packages = list_packages(venv_path, format='json')
        for pkg in packages:
            print(f"  {pkg['name']}: {pkg['version']}")
        
        # Freeze to verify
        freeze_file = f"{project_path}/requirements_frozen.txt"
        freeze_requirements(venv_path, freeze_file)
        print(f"\nRequirements frozen to {freeze_file}")
        
        return True
        
    except VenvError as e:
        print(f"Error: {e}")
        return False

# Usage
setup_project_environment('./my_project', './my_project/requirements.txt')
```

### Example 2: Building and Distributing Application | 예제 2: 애플리케이션 빌드 및 배포

```python
from sys_util_core import (
    create_venv, install_pyinstaller, build_exe,
    clean_build_files, PyInstallerError
)
import os

def build_application(script, app_name, icon=None):
    """Build a standalone executable"""
    build_venv = './build_env'
    
    try:
        # Setup build environment
        print("Setting up build environment...")
        create_venv(build_venv, clear=True)
        
        # Install PyInstaller
        print("Installing PyInstaller...")
        install_pyinstaller(build_venv)
        
        # Clean previous builds
        print("Cleaning previous builds...")
        clean_build_files(remove_dist=True, remove_build=True)
        
        # Build executable
        print("Building executable...")
        success, exe_path, msg = build_exe(
            script_path=script,
            output_dir='./release',
            name=app_name,
            onefile=True,
            windowed=True,
            icon=icon,
            venv_path=build_venv,
            clean=True
        )
        
        if success:
            print(f"\n✓ Build successful!")
            print(f"  Executable: {exe_path}")
            print(f"  Size: {os.path.getsize(exe_path) / 1024 / 1024:.2f} MB")
            return exe_path
        else:
            print(f"Build failed: {msg}")
            return None
            
    except PyInstallerError as e:
        print(f"Error during build: {e}")
        return None

# Usage
exe = build_application('my_app.py', 'MyApplication', 'icon.ico')
```

### Example 3: Error Handling Best Practices | 예제 3: 오류 처리 모범 사례

```python
from sys_util_core import (
    create_venv, install_package, build_exe,
    VenvError, PyInstallerError
)

def safe_build_workflow(script, requirements):
    """Build workflow with comprehensive error handling"""
    venv_path = './safe_venv'
    
    # Step 1: Create venv with error handling
    try:
        success, msg = create_venv(venv_path, clear=True)
        if not success:
            raise VenvError(f"Failed to create venv: {msg}")
        print("✓ Virtual environment created")
    except VenvError as e:
        print(f"✗ Error creating venv: {e}")
        return False
    
    # Step 2: Install packages with error handling
    try:
        success, msg = install_package(
            venv_path,
            package_name='',
            requirements_file=requirements
        )
        if not success:
            raise VenvError(f"Failed to install packages: {msg}")
        print("✓ Packages installed")
    except VenvError as e:
        print(f"✗ Error installing packages: {e}")
        return False
    
    # Step 3: Build executable with error handling
    try:
        success, exe_path, msg = build_exe(
            script_path=script,
            venv_path=venv_path,
            onefile=True
        )
        if not success:
            raise PyInstallerError(f"Build failed: {msg}")
        print(f"✓ Executable built: {exe_path}")
        return exe_path
    except PyInstallerError as e:
        print(f"✗ Error building executable: {e}")
        return False

# Usage
result = safe_build_workflow('app.py', 'requirements.txt')
```

## Tips and Best Practices | 팁 및 모범 사례

### Virtual Environments | 가상 환경

1. **Always use virtual environments for projects** - Isolate dependencies
   프로젝트에는 항상 가상 환경 사용 - 종속성 격리

2. **Keep requirements.txt updated** - Use `freeze_requirements()` regularly
   requirements.txt 최신 유지 - 정기적으로 `freeze_requirements()` 사용

3. **Use specific Python versions** - Specify `python_executable` parameter
   특정 파이썬 버전 사용 - `python_executable` 매개변수 지정

4. **Clean up unused venvs** - Delete old environments to save space
   사용하지 않는 venv 정리 - 공간 절약을 위해 오래된 환경 삭제

### Building Executables | 실행 파일 빌드

1. **Test in the target environment** - Build on the OS you're targeting
   대상 환경에서 테스트 - 대상 OS에서 빌드

2. **Use hidden_imports for dynamic imports** - PyInstaller can't detect these automatically
   동적 임포트에 hidden_imports 사용 - PyInstaller는 이를 자동으로 감지할 수 없음

3. **Include all data files** - Use `additional_data` parameter
   모든 데이터 파일 포함 - `additional_data` 매개변수 사용

4. **Test the executable** - Always test the built exe before distribution
   실행 파일 테스트 - 배포 전에 항상 빌드된 exe 테스트

5. **Use .spec files for complex builds** - Easier to maintain and reproduce
   복잡한 빌드에 .spec 파일 사용 - 유지 관리 및 재현이 더 쉬움

## Troubleshooting | 문제 해결

### Common Issues | 일반적인 문제

#### Virtual Environment Won't Create | 가상 환경이 생성되지 않음

```python
# Solution: Use clear=True to recreate
# 해결책: clear=True를 사용하여 재생성
success, msg = create_venv('./my_venv', clear=True)
```

#### Package Installation Fails | 패키지 설치 실패

```python
# Solution: Upgrade pip first
# 해결책: 먼저 pip 업그레이드
from sys_util_core import upgrade_pip
success, msg = upgrade_pip('./my_venv')

# Then try installing again
# 그런 다음 다시 설치 시도
success, msg = install_package('./my_venv', 'package_name')
```

#### Executable Missing Modules | 실행 파일에 모듈 누락

```python
# Solution: Add to hidden_imports
# 해결책: hidden_imports에 추가
success, exe_path, msg = build_exe(
    'script.py',
    hidden_imports=['missing_module1', 'missing_module2']
)
```

#### Executable Too Large | 실행 파일이 너무 큼

```python
# Solution: Exclude unnecessary modules
# 해결책: 불필요한 모듈 제외
success, exe_path, msg = build_exe(
    'script.py',
    exclude_modules=['tkinter', 'matplotlib', 'test']
)
```

## See Also | 참조

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [Python venv Documentation](https://docs.python.org/3/library/venv.html)
- [pip Documentation](https://pip.pypa.io/)
