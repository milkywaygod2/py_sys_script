import os, sys
import json
from typing import Optional, Dict, Any, Tuple


################################################################################################
########### import 'PATH_JFW_PY' from environment variable and add to sys.path #################
PATH_JFW_PY = "path_jfw_py"
path_jfw_py = os.environ.get(PATH_JFW_PY)
if path_jfw_py == None:
    print(f"[ERROR] 환경변수 '{PATH_JFW_PY}'를 IDE가 인식하지 못 할 수 있습니다. 재시작해보세요.")
    sys.exit(1)
else:
    if os.path.isdir(path_jfw_py):
        if path_jfw_py not in sys.path:
            sys.path.insert(0, path_jfw_py)
        try:
            from sys_util_core.jsystems import CmdSystem, ErrorCmdSystem
            from sys_util_core.jsystems import FileSystem, ErrorFileSystem
            from sys_util_core.jsystems import InstallSystem, ErrorInstallSystem
            from sys_util_core.jsystems import JLogger, ErrorJLogger
            from sys_util_core.jsystems import EnvvarSystem, ErrorEnvvarSystem
            from sys_util_core.jsystems import JTracer, ErrorJTracer
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
        FileSystem.ensure_installed('google-gemini', global_execute=True)
        import google.genai as genai
        import PIL.Image

        FileSystem.ensure_installed('ollama', global_execute=True)
        FileSystem.ensure_installed('ollama-lib', global_execute=True)
        import ollama

        def perform_ocr_ollama(image_path: str) -> Optional[str]:
            try:
                prompt = """
                이 문서의 모든 내용을 분석하여 구조화된 JSON 형식으로 추출해줘.
                - 텍스트는 단락별로 구분해줘.
                - 표가 있다면 구조를 유지해서 배열 형태로 표현해줘.
                """
                response = ollama.chat(
                    model="deepsick-ocr", 
                    messages=[{"role": "user", "content": prompt, "images": [image_path]}]
                )
                return response['message']['content']
            except Exception as e:
                JLogger().log_error(f"Ollama OCR Error: {e}")
                return None

        def perform_ocr_genai(client: genai.Client, model_name: str, image_path: str) -> Optional[str]:
            try:
                FileSystem.file_exists(image_path, raise_on=True)
                img = PIL.Image.open(image_path)
                prompt = """
                이 문서의 모든 내용을 분석하여 구조화된 JSON 형식으로 추출해줘.
                - 텍스트는 단락별로 구분해줘.
                - 표가 있다면 구조를 유지해서 배열 형태로 표현해줘.
                """
                response = client.models.generate_content(
                    model=model_name,
                    contents=[prompt, img],
                    config={
                        'response_mime_type': 'application/json',
                        'temperature': 1.0,
                        'top_p': 0.95,
                        'top_k': 64,
                        'max_output_tokens': 8192,
                    }
                )
                return response.text
            except Exception as e:
                JLogger().log_error(f"OCR Error: {e}")
                return None

        ###################### core-process ######################
        ocr_support = 'ollama'
        if ocr_support == 'genai':            
            # 1. API 키 설정
            script_dir = FileSystem.get_main_script_path_name_extension()[0]
            key_file_path = os.path.join(script_dir, "gemini-apikey.txt")
            
            try:
                with open(key_file_path, "r", encoding="utf-8") as f:
                    file_api_key = f.read().strip()
                    JLogger().log_info(f"Loaded API Key from: {key_file_path}")
            except FileNotFoundError:
                file_api_key = None
                JLogger().log_warning(f"API Key file not found: {key_file_path}")

            API_KEY = file_api_key or os.environ.get("GOOGLE_API_KEY")
            
            # New SDK Client Initialization
            client = genai.Client(api_key=API_KEY)

            # 2. 모델 설정 (사용할 모델명 정의)
            # Initialize models /FreeTier
            model_pro = "gemini-2.5-pro"         # 5 rpm / 0rpd / 250,000 tpm
            model_flash = "gemini-flash-latest"  # 10 rpm / 20rpd / 250,000 tpm
            model_lite = "gemini-2.5-flash-lite" # 15 rpm / 20rpd / 250,000 tpm
        elif ocr_support == 'ollama':
            pass    
        else:
            JLogger().log_error(f"Invalid OCR support: {ocr_support}")
            return "Invalid OCR support", False

        # 파일 설정
        path_target = str(FileSystem.get_path_download()) + '/OCR'
        if not os.path.isdir(path_target):
             JLogger().log_warning(f"Target directory not found: {path_target}")
             return "OCR 폴더 없음 (Downloads/OCR)", False

        jpg_file_list = FileSystem.get_list(path_target, "*.jpg", target="file")
        txt_file_list = FileSystem.get_list(path_target, "*.txt", target="file")

        # 범위 설정 (0부터 시작)
        stt_idx = len(txt_file_list)
        end_idx = -1
        end_idx = len(jpg_file_list) if end_idx == -1 else min(end_idx, len(jpg_file_list))
        target_range_jpg = jpg_file_list[stt_idx:end_idx]        
        
        if not target_range_jpg:
            JLogger().log_info("No new files to process.")
            return "처리할 파일 없음", True

        JLogger().log_info(f"Processing {len(target_range_jpg)} files ({stt_idx} ~ {end_idx}) / Total {len(jpg_file_list)} files")

        _success: bool = True
        for target_image in target_range_jpg:
            json_result = perform_ocr_genai(client, model_flash, target_image)
            if json_result: # JSON 포맷팅하여 출력
                try:
                    parsed = json.loads(json_result)
                    
                    # 원본 이미지와 같은 이름의 .txt 파일로 저장
                    output_path = os.path.splitext(target_image)[0] + ".txt"
                    content_text = json.dumps(parsed, indent=4, ensure_ascii=False)
                    
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(content_text)
                        
                    JLogger().log_info(f"Saved to: {output_path}")

                except json.JSONDecodeError:
                    _success = False
                    JLogger().log_error(f"Failed to parse JSON result from {target_image}")
            else:
                _success = False
                JLogger().log_error(f"Failed to perform OCR on {target_image}")
        
        ###################### return-normal ######################
        _msg_success: str = f"OCR 완료"
        _msg_failure: str = f"OCR 실패 (일부 파일)"
        return _msg_success if _success else _msg_failure, _success
    
    except Exception as _except:
        ###################### return-exception ######################
        _msg_exception = f"OCR 실패: {_except}"
        return _msg_exception, False

if __name__ == "__main__":
    try:
        SystemManager().launch_proper(admin=True)
        return_main: Tuple[str, bool] = GuiManager().run_with_loading(main, title="OCR")
    except Exception as _except:
        return_main: Tuple[str, bool] = (_except, False)
    finally:
        SystemManager().exit_proper(*return_main)