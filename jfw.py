import os
import sys
from sys_util_core import cmd_utils, env_utils
from sys_util_core.file_utils import CommandSystem, FileSystem, InstallSystem
import ctypes


def main():
    # admin check
    if not CommandSystem.ensure_admin_running():
        sys.exit(0)
    
    # setup
    env_var_name = env_utils.generate_env_var_name_from_this_file()
    is_success = env_utils.ensure_global_env_pair(env_var_name, os.path.dirname(os.path.abspath(__file__)),  global_scope=True, permanent=True)
    cmd_utils.print_info(f"환경변수 '{env_var_name}' 설정 {'성공' if is_success else '실패'}")


if __name__ == "__main__":
    main()