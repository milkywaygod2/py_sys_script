import os
import sys
from sys_util_core import cmd_utils
from sys_util_core.file_utils import LogSystem, CommandSystem, FileSystem, EnvvarSystem, GuiSystem

def main():
    try:
        LogSystem.start_logger()
        _success = False
        _exception = None

        # admin check
        if CommandSystem.ensure_admin_running():
            env_var_name = EnvvarSystem.generate_env_name_from_main_script(prefix="path")
            _success = EnvvarSystem.ensure_global_env_pair(env_var_name, FileSystem.get_main_script_path_name_extension()[0],  global_scope=True, permanent=True)
            LogSystem.log_info(f"global env var set: {_success}")    
    except Exception as e:
        LogSystem.log_error(f"환경변수 시스템 전역 설정 실패: {e}")
        _exception = e
    finally:
        LogSystem.end_logger()
        GuiSystem.show_msg_box(f"환경변수 '{env_var_name}'이(가) 시스템 전역에 설정되었습니다.") if _success else GuiSystem.show_msg_box(f"환경변수 설정 실패: {_exception}")

if __name__ == "__main__":
    main()