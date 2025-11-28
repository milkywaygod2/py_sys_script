import os
import sys
from zipfile import Path

# Add the current directory to Python path for imports
path_jfw_py = os.environ.get("path_jfw_py")
if path_jfw_py and os.path.isdir(path_jfw_py):
    if path_jfw_py not in sys.path:
        sys.path.insert(0, path_jfw_py)
    # 이제 공통 모듈 import 시도
    try:
        from sys_util_core import env_utils, cmd_utils, file_utils
        from sys_util_core.file_utils import CommandSystem, FileSystem, InstallSystem, LogSystem
    except ImportError as e:
        print(f"[ERROR] py_sys_script 모듈 import 실패: {e}")
        sys.exit(1)
else:
    print(f"[ERROR] 환경변수 'path_jfw_py'에 path_jfw_py 폴더 경로가 세팅되어 있지 않거나, 경로가 잘못되었습니다.")
    sys.exit(1)

def main():
    # py to exe
    fullpath = FileSystem.get_main_script_fullpath()
    file_path, file_name, file_extension = FileSystem.get_main_script_path_name_extension()
    
    if file_name.startswith("exe_"):
        target_file_name = file_name[4:]  # Remove "exe_" prefix
        target_fullpath = os.path.join(file_path, target_file_name + '.' + file_extension)
    
        InstallSystem.PythonRelated.build_exe_with_pyinstaller(
            target_fullpath,  # 빌드할 스크립트 경로
            related_install_global=False, 
            onefile=True, 
            console=False
        )
    
    else:
        LogSystem.print_info("Name of makingfile should be started with 'exe_' and it's not, Skipping build.")
        sys.exit(2)
    
if __name__ == "__main__":
    main()