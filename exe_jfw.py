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
    file_name, file_extension = FileSystem.get_current_script_name() # TODO: 경로 조회함수추가후 대체
    if FileSystem.check_file(file_name):
        InstallSystem.PythonRelated.build_exe_with_pyinstaller(
            path_script=Path('vcpkg_install_script.py'),  # 빌드할 스크립트 경로
            related_install_global=False, 
            onefile=True, 
            noconsole=False
        )
    else:
        print(f"[ERROR] src not found: {src}")
        sys.exit(2)
    

if __name__ == "__main__":
    main()