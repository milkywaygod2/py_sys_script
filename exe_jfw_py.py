import os, sys
from typing import Tuple

################################################################################################
########### import 'PATH_JFW_PY' from environment variable and add to sys.path #################
PATH_JFW_PY = "path_jfw_py"
path_jfw_py = os.environ.get(PATH_JFW_PY)
if path_jfw_py == None:
    print(f"[ERROR] 추가된 환경변수 '{PATH_JFW_PY}'를 IDE가 인식하지 못 할 수 있습니다. 재시작해보세요.")
    sys.exit(1)
else:
    if os.path.isdir(path_jfw_py):
        if path_jfw_py not in sys.path:
            sys.path.insert(0, path_jfw_py)
        try:
            from sys_util_core.jsystems import CmdSystem, ErrorCmdSystem
            from sys_util_core.jsystems import FileSystem, ErrorFileSystem
            from sys_util_core.jsystems import InstallSystem, ErrorInstallSystem
            from sys_util_core.jsystems import LogSystem, ErrorLogSystem
            from sys_util_core.jsystems import EnvvarSystem, ErrorEnvvarSystem
            from sys_util_core.jmanagers import SystemManager, ErrorSystemManager
            from sys_util_core.jmanagers import GuiManager, ErrorGuiManager
        except ImportError as e:
            print(f"[ERROR] py_sys_script 모듈 import 실패: {e}")
            sys.exit(1)
    else:
        print(f"[ERROR] 환경변수 '{PATH_JFW_PY}'에 경로가 세팅되어 있지 않거나, 경로가 잘못되었습니다.")
        sys.exit(1)
################################################################################################

def main() -> Tuple[str, bool]:
    try:
        ###################### core-process ######################
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
            _success = False
            LogSystem.log_error("Name of makingfile should be started with 'exe_' and it's not, Skipping build.")
        
        ###################### return-normal ######################
        _msg_success = f"실행 파일 '{target_file_name}.exe' 생성이 완료되었습니다."
        _msg_failure = f"실행 파일 생성 실패"
        return _msg_success if _success else _msg_failure, _success
    
    except Exception as _except:
        ###################### return-exception ######################
        _msg_exception = f"실행 파일 생성 실패: {_except}"
        return _msg_exception, False

if __name__ == "__main__":
    try:
        SystemManager().launch_proper()
        return_main = main()
    except Exception as _except:
        return_main = (_except, False)
    finally:
        SystemManager().exit_proper(*return_main)