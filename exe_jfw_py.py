import os
import sys

# Add the current directory to Python path for imports
path_error = True
PATH_JFW_PY = "path_jfw_py"
if EnvvarSystem.ensure_env_var_set(EnvvarSystem.GLOBAL_SCOPE, PATH_JFW_PY):
    path_jfw_py = os.environ.get(PATH_JFW_PY)

    if path_jfw_py and os.path.isdir(path_jfw_py):
        path_error = False
        if path_jfw_py not in sys.path:
            sys.path.insert(0, path_jfw_py)
        try:
            from sys_util_core import gui_utils, cmd_utils
            from sys_util_core.file_utils import CommandSystem, ErrorCommandSystem
            from sys_util_core.file_utils import FileSystem, ErrorFileSystem
            from sys_util_core.file_utils import InstallSystem, ErrorInstallSystem
            from sys_util_core.file_utils import LogSystem, ErrorLogSystem
            from sys_util_core.file_utils import EnvvarSystem, ErrorEnvvarSystem

        except ImportError as e:
            print(f"[ERROR] py_sys_script 모듈 import 실패: {e}")
            sys.exit(1)

if path_error:
    print(f"[ERROR] 환경변수 '{PATH_JFW_PY}'에 경로가 세팅되어 있지 않거나, 경로가 잘못되었습니다.")
    sys.exit(1)

def main():
    # logger
    LogSystem.start_logger()

    # py to exe
    fullpath = FileSystem.get_main_script_fullpath()
    file_path, file_name, file_extension = FileSystem.get_main_script_path_name_extension()
    
    if file_name.startswith("exe_"):
        target_file_name = file_name[4:]  # Remove "exe_" prefix
        target_fullpath = os.path.join(file_path, target_file_name + '.' + file_extension)    
        #path_rsc = [(target_fullpath, ".")]
        
        _success = InstallSystem.PythonRelated.build_exe_with_pyinstaller(
            path_script=target_fullpath,  # 빌드할 스크립트 경로
            #path_rsc=path_rsc,
            related_install_global=False, 
            onefile=True, 
            console=False
        )
    else:
        LogSystem.log_error("Name of makingfile should be started with 'exe_' and it's not, Skipping build.")
        sys.exit(2)

    LogSystem.end_logger()
    gui_utils.show_msg_box(f"'{file_name}' 실행 파일 생성이 완료되었습니다.") if _success else gui_utils.show_msg_box(f"'{file_name}' 실행 파일 생성에 실패했습니다.")
    
if __name__ == "__main__":
    main()