import os, sys
import json
from typing import Optional, Dict, Any

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

# 1. API 키 설정
API_KEY = os.environ.get("GOOGLE_API_KEY") or "AIzaSyBVA_Hqg54kM8FcPrUFlJq-2z9WtYGRZzs"
genai.configure(api_key=API_KEY)

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)

# 2. 모델 설정 
# 핵심 수정: response_mime_type을 application/json으로 설정하여 순수한 JSON 응답을 강제합니다.
generation_config = {
    "temperature": 1, # 0.0 ~ 2.0. 높을수록 창의적이고 다양한 결과, 낮을수록 결정적이고 일관된 결과. OCR 등 사실 추출에는 0에 가까운 값을 권장. (1.5 Flash 기본값 1.0)
    "top_p": 0.95, # 0.0 ~ 1.0. 누적 확률 p에 도달할 때까지 상위 토큰을 선택. 낮을수록 정확하고 좁은 범위의 단어 선택. (Nucleus sampling)
    "top_k": 64, # 1 이상. 상위 k개의 토큰 중에서만 샘플링. 낮을수록 엉뚱한 단어 생성 방지.
    "max_output_tokens": 8192, # 생성할 최대 토큰 길이 제한.
    "response_mime_type": "application/json", # 결과를 JSON 포맷으로 강제하여 파싱 용이성 확보.
}

model = genai.GenerativeModel(
    model_name="models/gemini-3-pro-image-preview", # models/gemini-3-flash-preview
    generation_config=generation_config,
)

def perform_ocr(image_path: str) -> Optional[str]:
    """이미지에서 텍스트와 표를 추출하여 JSON 문자열로 반환합니다."""
    if not os.path.exists(image_path):
        print(f"Error: 파일을 찾을 수 없습니다. -> {image_path}")
        return None

    try:
        # 이미지 로드
        img = PIL.Image.open(image_path)
        
        # 프롬프트 전달
        # 팁: 원하는 JSON 스키마를 예시로 제공하면 더 정확한 구조로 나옵니다.
        prompt = """
        이 문서의 모든 내용을 분석하여 구조화된 JSON 형식으로 추출해줘.
        - 텍스트는 단락별로 구분해줘.
        - 표가 있다면 구조를 유지해서 배열 형태로 표현해줘.
        """
        
        # 실행
        response = model.generate_content([prompt, img])
        
        # 결과 반환 (generation_config 덕분에 별도 파싱 없이 JSON 문자열임이 보장됨)
        return response.text
        
    except Exception as e:
        print(f"OCR 처리 중 오류 발생: {e}")
        return None

if __name__ == "__main__":
    # 실행 예시
    target_image = "my_document.jpg"
    
    # 테스트를 위해 더미 파일이 없으면 경고 출력
    if os.path.exists(target_image):
        print(f"Analyzing {target_image}...")
        json_result = perform_ocr(target_image)
        
        if json_result:
            # JSON 포맷팅하여 출력
            try:
                parsed = json.loads(json_result)
                print(json.dumps(parsed, indent=4, ensure_ascii=False))
            except json.JSONDecodeError:
                print("Raw Result:", json_result)
    else:
        print(f"테스트용 이미지 '{target_image}'가 없어서 실행하지 않았습니다.")
        print("이미지 경로를 수정하거나 파일을 준비해주세요.")