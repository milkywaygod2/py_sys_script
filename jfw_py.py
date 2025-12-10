import os, sys
from typing import Tuple
from sys_util_core.jsystems import FileSystem, EnvvarSystem
from sys_util_core.jmanagers import SystemManager

def main() -> Tuple[str, bool]:
    try:
        ###################### core-process ######################
        env_var_name = EnvvarSystem.generate_env_name_from_main_script(prefix="path")
        _success = EnvvarSystem.ensure_global_env_pair(env_var_name, FileSystem.get_main_script_path_name_extension()[0],  global_scope=True, permanent=True)

        ###################### return-normal ######################
        _msg_success = f"환경변수 '{env_var_name}'이(가) 시스템 전역에 설정되었습니다."
        _msg_failure = f"환경변수 시스템 전역 설정 실패"
        return _msg_success if _success else _msg_failure, _success
    
    except Exception as _except:
        ###################### return-exception ######################
        _msg_exception = f"환경변수 시스템 전역 설정 실패: {_except}"
        return _msg_exception, False

if __name__ == "__main__":
    try:
        SystemManager().launch_proper(True)
        return_main = main()
    except Exception as _except:
        return_main = (_except, False)
    finally:
        SystemManager().exit_proper(*return_main)