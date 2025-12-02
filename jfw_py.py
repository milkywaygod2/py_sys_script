import os
import sys
from sys_util_core import cmd_utils, env_utils, gui_utils
from sys_util_core.file_utils import CommandSystem, LogSystem, FileSystem
import ctypes


def main():
    # logger
    LogSystem.start_logger()

    # admin check
    if not CommandSystem.ensure_admin_running():
        sys.exit(0)
    
    # admin syspath setup
    env_var_name = env_utils.generate_env_name_from_main_script(prefix="path")
    _success = env_utils.ensure_global_env_pair(env_var_name, FileSystem.get_main_script_path_name_extension()[0],  global_scope=True, permanent=True)
    LogSystem.log_info(f"global env var set: {_success}")    
    
    LogSystem.end_logger()
    gui_utils.show_msg_box(f"환경변수 '{env_var_name}'이(가) 시스템 전역에 설정되었습니다.")

if __name__ == "__main__":
    main()