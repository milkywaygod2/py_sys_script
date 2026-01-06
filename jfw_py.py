from typing import Tuple
from sys_util_core.jsystems import FileSystem, EnvvarSystem
from sys_util_core.jmanagers import SystemManager, GuiManager

def main() -> Tuple[str, bool]:
    try:
        ###################### core-process ######################
        envvar_name: str = EnvvarSystem.generate_env_name_from_main_script(prefix="path")
        _success: bool = EnvvarSystem.ensure_global_envvar(envvar_name, FileSystem.get_main_script_path_name_extension()[0],  global_scope=True, permanent=True)

        ###################### return-normal ######################
        _msg_success: str = f"환경변수 '{envvar_name}'이(가) 시스템 전역에 설정되었습니다."
        _msg_failure: str = f"환경변수 시스템 전역 설정 실패"
        return _msg_success if _success else _msg_failure, _success
    
    except Exception as _except:
        ###################### return-exception ######################
        _msg_exception = f"환경변수 시스템 전역 설정 실패: {_except}"
        return _msg_exception, False

if __name__ == "__main__":
    try:
        SystemManager().launch_proper(admin=True)
        return_main = GuiManager().run_with_loading(main, title="Initializing System")
    except Exception as _except:
        return_main = (_except, False)
    finally:
        SystemManager().exit_proper(*return_main)