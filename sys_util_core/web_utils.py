"""
Web Scraping and Automation Utilities
웹 스크래핑 및 자동화 유틸리티

This module provides utility functions for web scraping and browser automation.
웹 스크래핑과 브라우저 자동화를 위한 유틸리티 함수들을 제공합니다.

Note: Some functions require external packages like requests, beautifulsoup4, selenium
참고: 일부 함수는 requests, beautifulsoup4, selenium과 같은 외부 패키지가 필요합니다
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import re
from typing import Optional, Dict, List, Any
from html.parser import HTMLParser


def download_url(url: str, timeout: int = 30) -> Optional[str]:
    '''
    Download content from a URL. URL에서 콘텐츠를 다운로드합니다.
    Args:
    url: URL to download from 다운로드할 URL
    timeout: Request timeout in seconds 요청 타임아웃 (초 단위)
    Returns:
    Content as string or None if error 문자열 콘텐츠, 에러시 None
    '''
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.read().decode('utf-8')
    except Exception:
        return None


def download_file(url: str, save_path: str, timeout: int = 30) -> bool:
    '''
    Download a file from URL and save to disk. URL에서 파일을 다운로드하고 디스크에 저장합니다.
    Args:
    url: URL to download from 다운로드할 URL
    save_path: Path to save the file 파일을 저장할 경로
    timeout: Request timeout in seconds 요청 타임아웃 (초 단위)
    Returns:
    True if successful, False otherwise 성공하면 True, 실패하면 False
    '''
    try:
        urllib.request.urlretrieve(url, save_path)
        return True
    except Exception:
        return False


def parse_url(url: str) -> Dict[str, str]:
    '''
    Parse a URL into its components. URL을 구성 요소로 파싱합니다.
    Args:
    url: URL to parse 파싱할 URL
    Returns:
    Dictionary with URL components (scheme, netloc, path, params, query, fragment) URL 구성 요소를 담은 딕셔너리 (scheme, netloc, path, params, query, fragment)
    '''
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    return {
        'scheme': parsed.scheme,
        'netloc': parsed.netloc,
        'path': parsed.path,
        'params': parsed.params,
        'query': parsed.query,
        'fragment': parsed.fragment
    }


def build_url(base_url: str, params: Dict[str, str]) -> str:
    '''
    Build a URL with query parameters. 쿼리 파라미터를 포함한 URL을 생성합니다.
    Args:
    base_url: Base URL 기본 URL
    params: Query parameters 쿼리 파라미터
    Returns:
    Complete URL with parameters 파라미터가 포함된 완전한 URL
    '''
    query_string = urllib.parse.urlencode(params)
    separator = '&' if '?' in base_url else '?'
    return f"{base_url}{separator}{query_string}"


def extract_links(html: str, base_url: Optional[str] = None) -> List[str]:
    '''
    Extract all links from HTML content. HTML 콘텐츠에서 모든 링크를 추출합니다.
    Args:
    html: HTML content HTML 콘텐츠
    base_url: Base URL for resolving relative links 상대 링크를 해결하기 위한 기본 URL
    Returns:
    List of URLs found in HTML HTML에서 발견된 URL 리스트
    '''
    import re
    from urllib.parse import urljoin
    
    # Find all href attributes
    pattern = r'href=["\']([^"\']+)["\']'
    links = re.findall(pattern, html)
    
    if base_url:
        links = [urljoin(base_url, link) for link in links]
    
    return links


def extract_text_from_html(html: str) -> str:
    '''
    Extract plain text from HTML, removing all tags. HTML에서 순수 텍스트를 추출하고 모든 태그를 제거합니다.
    Args:
    html: HTML content HTML 콘텐츠
    Returns:
    Plain text content 순수 텍스트 콘텐츠
    '''
    import re
    
    # Remove script and style elements
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def get_html_element_by_id(html: str, element_id: str) -> Optional[str]:
    '''
    Extract HTML element with specific ID. 특정 ID를 가진 HTML 요소를 추출합니다.
    Args:
    html: HTML content HTML 콘텐츠
    element_id: Element ID to find 찾을 요소 ID
    Returns:
    Element HTML or None if not found 요소 HTML, 찾을 수 없으면 None
    '''
    import re
    
    pattern = rf'<[^>]+id=["\']?{re.escape(element_id)}["\']?[^>]*>.*?</[^>]+>'
    match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
    
    return match.group(0) if match else None


def get_html_elements_by_class(html: str, class_name: str) -> List[str]:
    '''
    Extract HTML elements with specific class. 특정 클래스를 가진 HTML 요소들을 추출합니다.
    Args:
    html: HTML content HTML 콘텐츠
    class_name: Class name to find 찾을 클래스 이름
    Returns:
    List of matching element HTML 일치하는 요소 HTML 리스트
    '''
    import re
    
    pattern = rf'<[^>]+class=["\']?[^"\']*{re.escape(class_name)}[^"\']*["\']?[^>]*>.*?</[^>]+>'
    matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
    
    return matches


def fetch_json_api(url: str, headers: Optional[Dict[str, str]] = None, 
                   timeout: int = 30) -> Optional[Dict[str, Any]]:
    '''
    Fetch JSON data from an API endpoint. API 엔드포인트에서 JSON 데이터를 가져옵니다.
    Args:
    url: API URL
    API URL
    headers: HTTP headers HTTP 헤더
    timeout: Request timeout in seconds 요청 타임아웃 (초 단위)
    Returns:
    Parsed JSON data or None if error 파싱된 JSON 데이터, 에러시 None
    '''
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except Exception:
        return None


def post_json_api(url: str, data: Dict[str, Any], 
                  headers: Optional[Dict[str, str]] = None,
                  timeout: int = 30) -> Optional[Dict[str, Any]]:
    '''
    Post JSON data to an API endpoint. API 엔드포인트에 JSON 데이터를 전송합니다.
    Args:
    url: API URL
    API URL
    data: Data to post 전송할 데이터
    headers: HTTP headers HTTP 헤더
    timeout: Request timeout in seconds 요청 타임아웃 (초 단위)
    Returns:
    Response JSON data or None if error 응답 JSON 데이터, 에러시 None
    '''
    try:
        json_data = json.dumps(data).encode('utf-8')
        
        req_headers = {'Content-Type': 'application/json'}
        if headers:
            req_headers.update(headers)
        
        req = urllib.request.Request(url, data=json_data, headers=req_headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except Exception:
        return None


def check_url_exists(url: str, timeout: int = 10) -> bool:
    '''
    Check if a URL exists (returns 2xx status code). URL이 존재하는지 확인합니다 (2xx 상태 코드 반환).
    Args:
    url: URL to check 확인할 URL
    timeout: Request timeout in seconds 요청 타임아웃 (초 단위)
    Returns:
    True if URL exists, False otherwise URL이 존재하면 True, 아니면 False
    '''
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return 200 <= response.status < 300
    except Exception:
        return False
