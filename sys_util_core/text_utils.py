"""
Text Processing Utilities
텍스트 처리 유틸리티

This module provides utility functions for text processing and manipulation.
텍스트 처리 및 조작을 위한 유틸리티 함수들을 제공합니다.
"""

import re
from typing import List, Optional


"""
@brief  Convert text from one encoding to another. 텍스트를 한 인코딩에서 다른 인코딩으로 변환합니다.
@param  text Text to convert 변환할 텍스트
@param  from_encoding Source encoding 소스 인코딩
@param  to_encoding Target encoding 대상 인코딩
@return  Converted text or None if error 변환된 텍스트, 에러시 None
"""
def convert_encoding(text: str, from_encoding: str, to_encoding: str = 'utf-8') -> Optional[str]:
    try:
        return text.encode(from_encoding).decode(to_encoding)
    except Exception:
        return None


"""
@brief  Remove all HTML tags from text. 텍스트에서 모든 HTML 태그를 제거합니다.
@param  html HTML text HTML 텍스트
@return  Text without HTML tags HTML 태그가 제거된 텍스트
"""
def remove_html_tags(html: str) -> str:
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html)


"""
@brief  Extract email addresses from text. 텍스트에서 이메일 주소를 추출합니다.
@param  text Text containing emails 이메일이 포함된 텍스트
@return  List of email addresses 이메일 주소 리스트
"""
def extract_emails(text: str) -> List[str]:
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, text)


"""
@brief  Extract URLs from text. 텍스트에서 URL을 추출합니다.
@param  text Text containing URLs URL이 포함된 텍스트
@return  List of URLs URL 리스트
"""
def extract_urls(text: str) -> List[str]:
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(pattern, text)


"""
@brief  Extract phone numbers from text. 텍스트에서 전화번호를 추출합니다.
@param  text Text containing phone numbers 전화번호가 포함된 텍스트
@param  country_code Country code for format (US, KR, etc.) 형식의 국가 코드 (US, KR 등)
@return  List of phone numbers 전화번호 리스트
"""
def extract_phone_numbers(text: str, country_code: str = 'US') -> List[str]:
    if country_code == 'KR':
        # Korean phone number format
        pattern = r'01[016789]-?\d{3,4}-?\d{4}'
    else:
        # US phone number format
        pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    
    return re.findall(pattern, text)


"""
@brief  Truncate text to maximum length. 텍스트를 최대 길이로 자릅니다.
@param  text Text to truncate 자를 텍스트
@param  max_length Maximum length 최대 길이
@param  suffix Suffix to add if truncated 잘린 경우 추가할 접미사
@return  Truncated text 잘린 텍스트
"""
def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


"""
@brief  Normalize whitespace in text (remove extra spaces, tabs, newlines). 텍스트의 공백을 정규화합니다 (여분의 스페이스, 탭, 개행 제거).
@param  text Text to normalize 정규화할 텍스트
@return  Normalized text 정규화된 텍스트
"""
def normalize_whitespace(text: str) -> str:
    # Replace multiple whitespaces with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


"""
@brief  Count words in text. 텍스트의 단어 수를 셉니다.
@param  text Text to count words 단어를 셀 텍스트
@return  Number of words 단어 수
"""
def count_words(text: str) -> int:
    words = text.split()
    return len(words)


"""
@brief  Reverse text. 텍스트를 뒤집습니다.
@param  text Text to reverse 뒤집을 텍스트
@return  Reversed text 뒤집힌 텍스트
"""
def reverse_text(text: str) -> str:
    return text[::-1]


"""
@brief  Remove special characters from text. 텍스트에서 특수 문자를 제거합니다.
@param  text Text to clean 정리할 텍스트
@param  keep_spaces Whether to keep spaces 공백을 유지할지 여부
@return  Cleaned text 정리된 텍스트
"""
def remove_special_characters(text: str, keep_spaces: bool = True) -> str:
    if keep_spaces:
        pattern = r'[^a-zA-Z0-9가-힣\s]'
    else:
        pattern = r'[^a-zA-Z0-9가-힣]'
    
    return re.sub(pattern, '', text)


"""
@brief  Capitalize first letter of each word. 각 단어의 첫 글자를 대문자로 만듭니다.
@param  text Text to capitalize 대문자화할 텍스트
@return  Capitalized text 대문자화된 텍스트
"""
def capitalize_words(text: str) -> str:
    return text.title()


"""
@brief  Find and replace text. 텍스트를 찾아 바꿉니다.
@param  text Text to process 처리할 텍스트
@param  find Text to find 찾을 텍스트
@param  replace Replacement text 교체할 텍스트
@param  case_sensitive Whether search is case sensitive 대소문자 구분 여부
@return  Processed text 처리된 텍스트
"""
def find_and_replace(text: str, find: str, replace: str, 
                     case_sensitive: bool = True) -> str:
    if case_sensitive:
        return text.replace(find, replace)
    else:
        pattern = re.compile(re.escape(find), re.IGNORECASE)
        return pattern.sub(replace, text)


"""
@brief  Split text into sentences. 텍스트를 문장으로 나눕니다.
@param  text Text to split 나눌 텍스트
@return  List of sentences 문장 리스트
"""
def split_into_sentences(text: str) -> List[str]:
    # Simple sentence splitting (can be improved with NLP)
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


"""
@brief  Remove duplicate words while preserving order. 순서를 유지하면서 중복 단어를 제거합니다.
@param  text Text with potential duplicate words 중복 단어가 있을 수 있는 텍스트
@return  Text with unique words 고유한 단어만 있는 텍스트
"""
def remove_duplicates_words(text: str) -> str:
    words = text.split()
    seen = set()
    unique_words = []
    
    for word in words:
        if word.lower() not in seen:
            seen.add(word.lower())
            unique_words.append(word)
    
    return ' '.join(unique_words)


"""
@brief  Convert text to URL-friendly slug. 텍스트를 URL 친화적 슬러그로 변환합니다.
@param  text Text to convert 변환할 텍스트
@return  URL slug URL 슬러그
"""
def convert_to_slug(text: str) -> str:
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    
    # Remove duplicate hyphens
    text = re.sub(r'-+', '-', text)
    
    return text.strip('-')
