import os
import sys
from sys_util_core import cmd_utils, env_utils
from sys_util_core.file_utils import CommandSystem
import ctypes


def main():
    # admin check
    if not CommandSystem.ensure_admin_running():
        sys.exit(0)
    
    # admin syspath setup
    env_var_name = env_utils.generate_env_name_from_current_script("path")
    return env_utils.ensure_global_env_pair(env_var_name, os.path.dirname(os.path.abspath(__file__)),  global_scope=True, permanent=True)
    

if __name__ == "__main__":
    main()