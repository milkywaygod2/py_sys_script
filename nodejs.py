from typing import Tuple
from sys_util_core.jsystems import InstallSystem, EnvvarSystem, FileSystem
from sys_util_core.jmanagers import SystemManager, GuiManager
from pathlib import Path

def main() -> Tuple[str, bool]:
    try:
        ###################### core-process ######################
        nodejs_folder = Path(InstallSystem.WingetRelated.install_nodejs_global()).parent
        _success_nodejs = EnvvarSystem.ensure_global_envvar("path_nodejs", str(nodejs_folder),  global_scope=True, permanent=True)
        npm_folder = FileSystem.get_path_appdata_roaming() / "npm"
        _success_npm = EnvvarSystem.ensure_global_envvar("path_npm", str(npm_folder),  global_scope=False, permanent=True)
        _success = _success_nodejs and _success_npm
        ###################### return-normal ######################
        _msg_success = f"node.js 설치 성공"
        _msg_failure = f"node.js 설치 실패"
        return _msg_success if _success else _msg_failure, _success
    
    except Exception as _except:
        ###################### return-exception ######################
        _msg_exception = f"node.js 설치 실패: {_except}"
        return _msg_exception, False

if __name__ == "__main__":
    try:
        SystemManager().launch_proper(admin=True)
        return_main = GuiManager().run_with_loading(main, title="Initializing System")
    except Exception as _except:
        return_main = (_except, False)
    finally:
        SystemManager().exit_proper(*return_main)