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
FileSystem.ensure_installed('google-gemini', global_check=True)
import google.generativeai as genai
import PIL.Image

def perform_ocr(image_path: str, model: genai.GenerativeModel) -> Optional[str]:
    FileSystem.file_exists(image_path, raise_on=True)
    img = PIL.Image.open(image_path)
    prompt = """
    이 문서의 모든 내용을 분석하여 구조화된 JSON 형식으로 추출해줘.
    - 텍스트는 단락별로 구분해줘.
    - 표가 있다면 구조를 유지해서 배열 형태로 표현해줘.
    """
    # 요청하기 전에 예상 토큰 수를 계산합니다.
    try:
        # [prompt, img] 리스트를 그대로 넣어주면 텍스트+이미지 합산 토큰을 알려줍니다.
        token_info = model.count_tokens([prompt, img])
        JLogger().log_info(f"Input Tokens: {token_info.total_tokens} (Image + Prompt)")
    except Exception as e:
        JLogger().log_warning(f"Token counting skipped (Not supported or error): {e}")

    response = model.generate_content([prompt, img]) # 결과 반환 (generation_config 덕분에 별도 파싱 없이 JSON 문자열임이 보장됨)
    return response.text

def main() -> Tuple[str, bool]:
    try:
        ###################### core-process ######################
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
        genai.configure(api_key=API_KEY)

        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                JLogger().log_info(f"Model: {m.name}")

        # 2. 모델 설정 
        # 핵심 수정: response_mime_type을 application/json으로 설정하여 순수한 JSON 응답을 강제합니다.
        generation_config = {
            "temperature": 1, # 0.0 ~ 2.0. 높을수록 창의적이고 다양한 결과, 낮을수록 결정적이고 일관된 결과. OCR 등 사실 추출에는 0에 가까운 값을 권장. (1.5 Flash 기본값 1.0)
            "top_p": 0.95, # 0.0 ~ 1.0. 누적 확률 p에 도달할 때까지 상위 토큰을 선택. 낮을수록 정확하고 좁은 범위의 단어 선택. (Nucleus sampling)
            "top_k": 64, # 1 이상. 상위 k개의 토큰 중에서만 샘플링. 낮을수록 엉뚱한 단어 생성 방지.
            "max_output_tokens": 8192, # 생성할 최대 토큰 길이 제한.
            "response_mime_type": "application/json", # 결과를 JSON 포맷으로 강제하여 파싱 용이성 확보.
        }
        # Initialize models /FreeTier
        model_pro = genai.GenerativeModel('gemini-2.5-pro', generation_config=generation_config)         # 5 rpm / 0rpd / 250,000 tpm
        model_flash = genai.GenerativeModel('gemini-flash-latest', generation_config=generation_config)     # 10 rpm / 20rpd / 250,000 tpm
        model_lite = genai.GenerativeModel('gemini-2.5-flash-lite', generation_config=generation_config) # 15 rpm / 20rpd / 250,000 tpm
        
        path_target = str(FileSystem.get_path_download()) + '/OCR'
        jpg_file_list = FileSystem.get_list(path_target, "*.jpg", target="file")
        txt_file_list = FileSystem.get_list(path_target, "*.txt", target="file")

        # 범위 설정 (0부터 시작)
        stt_idx = len(txt_file_list)
        end_idx = -1
        end_idx = len(jpg_file_list) if end_idx == -1 else min(end_idx, len(jpg_file_list))
        target_range_jpg = jpg_file_list[stt_idx:end_idx]        
        JLogger().log_info(f"Processing {len(target_range_jpg)} files ({stt_idx} ~ {end_idx}) / Total {len(jpg_file_list)} files")

        _success: bool = True
        for target_image in target_range_jpg:
            json_result = perform_ocr(target_image, model_flash)
            if json_result: # JSON 포맷팅하여 출력
                try:
                    parsed = json.loads(json_result)
                    # print(json.dumps(parsed, indent=4, ensure_ascii=False))

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
        _msg_failure: str = f"OCR 실패"
        return _msg_success if _success else _msg_failure, _success
    
    except Exception as _except:
        ###################### return-exception ######################
        _msg_exception = f"OCR 실패: {_except}"
        return _msg_exception, False

if __name__ == "__main__":
    try:
        SystemManager().launch_proper(admin=True)
        JLogger().log_info("OCR 시작")
        return_main: Tuple[str, bool] = GuiManager().run_with_loading(main, title="OCR")
    except Exception as _except:
        return_main: Tuple[str, bool] = (_except, False)
    finally:
        SystemManager().exit_proper(*return_main)