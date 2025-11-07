#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example: Complete Virtual Environment and PyInstaller Workflow
완전한 가상 환경 및 PyInstaller 워크플로우 예제

This example demonstrates how to:
이 예제는 다음을 보여줍니다:
1. Create a virtual environment | 가상 환경 생성
2. Install packages | 패키지 설치
3. Build an executable | 실행 파일 빌드
"""

from sys_util_core import (
    create_venv,
    install_package,
    list_packages,
    freeze_requirements,
    install_pyinstaller,
    build_exe,
    clean_build_files,
    delete_venv,
    VenvError,
    PyInstallerError
)


def example_venv_workflow():
    """
    Example: Virtual environment management workflow
    예제: 가상 환경 관리 워크플로우
    """
    print("="*60)
    print("Virtual Environment Management Example")
    print("가상 환경 관리 예제")
    print("="*60)
    
    venv_path = './example_venv'
    
    try:
        # Step 1: Create virtual environment
        # 단계 1: 가상 환경 생성
        print("\n1. Creating virtual environment...")
        print("   가상 환경 생성 중...")
        success, message = create_venv(venv_path, clear=True)
        if success:
            print(f"   ✓ {message}")
        else:
            raise VenvError(message)
        
        # Step 2: Install some packages
        # 단계 2: 패키지 설치
        print("\n2. Installing packages...")
        print("   패키지 설치 중...")
        
        packages_to_install = ['requests', 'colorama']
        for pkg in packages_to_install:
            print(f"   Installing {pkg}...")
            success, message = install_package(venv_path, pkg)
            if success:
                print(f"   ✓ {pkg} installed")
        
        # Step 3: List installed packages
        # 단계 3: 설치된 패키지 목록 조회
        print("\n3. Listing installed packages...")
        print("   설치된 패키지 목록:")
        success, output, packages = list_packages(venv_path, format='json')
        for pkg in packages:
            print(f"   - {pkg['name']}: {pkg['version']}")
        
        # Step 4: Freeze requirements
        # 단계 4: requirements 고정
        print("\n4. Freezing requirements...")
        print("   requirements 고정 중...")
        req_file = './example_requirements.txt'
        success, message = freeze_requirements(venv_path, req_file)
        if success:
            print(f"   ✓ {message}")
        
        # Step 5: Clean up
        # 단계 5: 정리
        print("\n5. Cleaning up...")
        print("   정리 중...")
        success, message = delete_venv(venv_path)
        if success:
            print(f"   ✓ {message}")
        
        print("\n✓ Virtual environment workflow completed successfully!")
        print("  가상 환경 워크플로우가 성공적으로 완료되었습니다!")
        
    except VenvError as e:
        print(f"\n✗ Error: {e}")


def example_build_executable():
    """
    Example: Build a simple Python script into an executable
    예제: 간단한 Python 스크립트를 실행 파일로 빌드
    """
    print("\n" + "="*60)
    print("PyInstaller Build Example")
    print("PyInstaller 빌드 예제")
    print("="*60)
    
    # Create a simple test script
    # 간단한 테스트 스크립트 생성
    test_script = './example_app.py'
    with open(test_script, 'w') as f:
        f.write('''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple example application
간단한 예제 애플리케이션
"""

def main():
    print("="*50)
    print("Hello from Example Application!")
    print("예제 애플리케이션에서 인사드립니다!")
    print("="*50)
    print()
    name = input("Enter your name (이름을 입력하세요): ")
    print(f"Nice to meet you, {name}!")
    print(f"{name}님 만나서 반갑습니다!")
    print()
    input("Press Enter to exit (종료하려면 Enter를 누르세요)...")

if __name__ == '__main__':
    main()
''')
    
    venv_path = './build_venv'
    
    try:
        # Step 1: Create build environment
        # 단계 1: 빌드 환경 생성
        print("\n1. Creating build environment...")
        print("   빌드 환경 생성 중...")
        success, message = create_venv(venv_path, clear=True)
        if success:
            print(f"   ✓ {message}")
        
        # Step 2: Install PyInstaller
        # 단계 2: PyInstaller 설치
        print("\n2. Installing PyInstaller...")
        print("   PyInstaller 설치 중...")
        success, message = install_pyinstaller(venv_path)
        if success:
            print("   ✓ PyInstaller installed")
        
        # Step 3: Clean previous builds
        # 단계 3: 이전 빌드 정리
        print("\n3. Cleaning previous builds...")
        print("   이전 빌드 정리 중...")
        clean_build_files(remove_dist=True, remove_build=True)
        
        # Step 4: Build executable
        # 단계 4: 실행 파일 빌드
        print("\n4. Building executable...")
        print("   실행 파일 빌드 중...")
        success, exe_path, message = build_exe(
            script_path=test_script,
            output_dir='./dist',
            name='ExampleApp',
            onefile=True,
            console=True,
            venv_path=venv_path
        )
        
        if success:
            print(f"   ✓ Executable built successfully!")
            print(f"     실행 파일이 성공적으로 빌드되었습니다!")
            print(f"   Location: {exe_path}")
            print(f"   위치: {exe_path}")
        
        # Step 5: Clean up
        # 단계 5: 정리
        print("\n5. Cleaning up build environment...")
        print("   빌드 환경 정리 중...")
        delete_venv(venv_path)
        print("   ✓ Build environment cleaned")
        
        print("\n✓ Build workflow completed successfully!")
        print("  빌드 워크플로우가 성공적으로 완료되었습니다!")
        print(f"\n  You can now run: {exe_path}")
        print(f"  다음을 실행할 수 있습니다: {exe_path}")
        
    except (VenvError, PyInstallerError) as e:
        print(f"\n✗ Error: {e}")


def example_complete_workflow():
    """
    Example: Complete workflow using build_from_requirements
    예제: build_from_requirements를 사용한 완전한 워크플로우
    """
    print("\n" + "="*60)
    print("Complete Workflow Example")
    print("완전한 워크플로우 예제")
    print("="*60)
    
    # Create a test script that uses external packages
    # 외부 패키지를 사용하는 테스트 스크립트 생성
    test_script = './complete_app.py'
    with open(test_script, 'w') as f:
        f.write('''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Complete application example
완전한 애플리케이션 예제
"""

try:
    from colorama import init, Fore, Style
    init()
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

def main():
    if HAS_COLORAMA:
        print(Fore.GREEN + "="*50)
        print("Application with Dependencies")
        print("종속성이 있는 애플리케이션")
        print("="*50 + Style.RESET_ALL)
    else:
        print("="*50)
        print("Application (no colorama)")
        print("="*50)
    
    print("This application was built with dependencies!")
    print("이 애플리케이션은 종속성과 함께 빌드되었습니다!")
    input("\\nPress Enter to exit...")

if __name__ == '__main__':
    main()
''')
    
    # Create requirements file
    # requirements 파일 생성
    requirements_file = './complete_requirements.txt'
    with open(requirements_file, 'w') as f:
        f.write('colorama>=0.4.0\n')
    
    try:
        from sys_util_core import build_from_requirements
        
        print("\n1. Building application with all dependencies...")
        print("   모든 종속성과 함께 애플리케이션 빌드 중...")
        
        success, exe_path, message = build_from_requirements(
            script_path=test_script,
            requirements_file=requirements_file,
            venv_path='./complete_venv',
            output_dir='./dist',
            name='CompleteApp',
            onefile=True
        )
        
        if success:
            print("\n✓ Complete workflow successful!")
            print("  완전한 워크플로우 성공!")
            print(f"  Executable: {exe_path}")
            print(f"  실행 파일: {exe_path}")
        else:
            print(f"\n✗ Build failed: {message}")
        
    except PyInstallerError as e:
        print(f"\n✗ Error: {e}")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("sys_util_core - Virtual Environment & PyInstaller Examples")
    print("sys_util_core - 가상 환경 및 PyInstaller 예제")
    print("="*60)
    
    # Run example workflows
    # 예제 워크플로우 실행
    
    print("\n[Example 1] Virtual Environment Management")
    print("[예제 1] 가상 환경 관리")
    example_venv_workflow()
    
    print("\n" + "="*60)
    input("\nPress Enter to continue to next example...")
    
    print("\n[Example 2] Building Executable")
    print("[예제 2] 실행 파일 빌드")
    example_build_executable()
    
    print("\n" + "="*60)
    input("\nPress Enter to continue to next example...")
    
    print("\n[Example 3] Complete Workflow")
    print("[예제 3] 완전한 워크플로우")
    example_complete_workflow()
    
    print("\n" + "="*60)
    print("\n✓ All examples completed!")
    print("  모든 예제가 완료되었습니다!")
    print("="*60)
