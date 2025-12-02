import os
import sys
from sys_util_core import cmd_utils, env_utils
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

if __name__ == "__main__":
    main()