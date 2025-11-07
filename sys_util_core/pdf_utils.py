"""
PDF Conversion Utilities
PDF 변환 유틸리티

This module provides utility functions for converting various file formats to PDF.
다양한 파일 형식을 PDF로 변환하기 위한 유틸리티 함수들을 제공합니다.

Note: Some functions require external packages (pillow, reportlab, python-docx, openpyxl)
참고: 일부 함수는 외부 패키지가 필요합니다 (pillow, reportlab, python-docx, openpyxl)
"""

import os
from typing import List, Optional


"""
@brief Convert image file to PDF. 이미지 파일을 PDF로 변환합니다.
@param image_path Path to image file 이미지 파일 경로
@param output_pdf Output PDF file path 출력 PDF 파일 경로
@return True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def image_to_pdf(image_path: str, output_pdf: str) -> bool:
    try:
        from PIL import Image
        
        image = Image.open(image_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image.save(output_pdf, 'PDF', resolution=100.0)
        return True
    except Exception:
        return False


"""
@brief Convert multiple images to a single PDF. 여러 이미지를 하나의 PDF로 변환합니다.
@param image_paths List of image file paths 이미지 파일 경로 리스트
@param output_pdf Output PDF file path 출력 PDF 파일 경로
@return True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def images_to_pdf(image_paths: List[str], output_pdf: str) -> bool:
    try:
        from PIL import Image
        
        images = []
        
        for img_path in image_paths:
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)
        
        if images:
            images[0].save(output_pdf, 'PDF', resolution=100.0, 
                          save_all=True, append_images=images[1:])
            return True
        
        return False
    except Exception:
        return False


"""
@brief Convert text to PDF. 텍스트를 PDF로 변환합니다.
@param text Text content 텍스트 내용
@param output_pdf Output PDF file path 출력 PDF 파일 경로
@param font_name Font name 폰트 이름
@param font_size Font size 폰트 크기
@return True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def text_to_pdf(text: str, output_pdf: str, 
                font_name: str = 'Helvetica', font_size: int = 12) -> bool:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        
        c = canvas.Canvas(output_pdf, pagesize=letter)
        width, height = letter
        
        y = height - inch
        lines = text.split('\n')
        
        for line in lines:
            if y < inch:
                c.showPage()
                y = height - inch
            
            c.setFont(font_name, font_size)
            c.drawString(inch, y, line)
            y -= font_size + 4
        
        c.save()
        return True
    except Exception:
        return False


"""
@brief Convert Word document to PDF. Word 문서를 PDF로 변환합니다.
@param docx_path Path to Word document Word 문서 경로
@param output_pdf Output PDF file path 출력 PDF 파일 경로
@return True if successful, False otherwise 성공하면 True, 실패하면 False
@return Note: This requires MS Word or LibreOffice on the system 참고: 시스템에 MS Word 또는 LibreOffice가 필요합니다
"""
def word_to_pdf(docx_path: str, output_pdf: str) -> bool:
    try:
        import sys
        import subprocess
        
        if sys.platform == 'win32':
            # Try using Word COM automation on Windows
            try:
                import win32com.client
                
                word = win32com.client.Dispatch('Word.Application')
                word.Visible = False
                
                doc = word.Documents.Open(os.path.abspath(docx_path))
                doc.SaveAs(os.path.abspath(output_pdf), FileFormat=17)  # 17 = PDF
                doc.Close()
                word.Quit()
                
                return True
            except Exception:
                pass
        
        # Try LibreOffice
        try:
            subprocess.run([
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', os.path.dirname(output_pdf),
                docx_path
            ], check=True, capture_output=True)
            return True
        except Exception:
            pass
        
        return False
    except Exception:
        return False


"""
@brief Convert Excel file to PDF. Excel 파일을 PDF로 변환합니다.
@param excel_path Path to Excel file Excel 파일 경로
@param output_pdf Output PDF file path 출력 PDF 파일 경로
@return True if successful, False otherwise 성공하면 True, 실패하면 False
@return Note: This requires MS Excel or LibreOffice on the system 참고: 시스템에 MS Excel 또는 LibreOffice가 필요합니다
"""
def excel_to_pdf(excel_path: str, output_pdf: str) -> bool:
    try:
        import sys
        import subprocess
        
        if sys.platform == 'win32':
            # Try using Excel COM automation on Windows
            try:
                import win32com.client
                
                excel = win32com.client.Dispatch('Excel.Application')
                excel.Visible = False
                
                wb = excel.Workbooks.Open(os.path.abspath(excel_path))
                wb.ExportAsFixedFormat(0, os.path.abspath(output_pdf))  # 0 = PDF
                wb.Close()
                excel.Quit()
                
                return True
            except Exception:
                pass
        
        # Try LibreOffice
        try:
            subprocess.run([
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', os.path.dirname(output_pdf),
                excel_path
            ], check=True, capture_output=True)
            return True
        except Exception:
            pass
        
        return False
    except Exception:
        return False


"""
@brief Convert PowerPoint presentation to PDF. PowerPoint 프레젠테이션을 PDF로 변환합니다.
@param pptx_path Path to PowerPoint file PowerPoint 파일 경로
@param output_pdf Output PDF file path 출력 PDF 파일 경로
@return True if successful, False otherwise 성공하면 True, 실패하면 False
@return Note: This requires MS PowerPoint or LibreOffice on the system 참고: 시스템에 MS PowerPoint 또는 LibreOffice가 필요합니다
"""
def powerpoint_to_pdf(pptx_path: str, output_pdf: str) -> bool:
    try:
        import sys
        import subprocess
        
        if sys.platform == 'win32':
            # Try using PowerPoint COM automation on Windows
            try:
                import win32com.client
                
                powerpoint = win32com.client.Dispatch('PowerPoint.Application')
                powerpoint.Visible = 1
                
                presentation = powerpoint.Presentations.Open(os.path.abspath(pptx_path))
                presentation.SaveAs(os.path.abspath(output_pdf), 32)  # 32 = PDF
                presentation.Close()
                powerpoint.Quit()
                
                return True
            except Exception:
                pass
        
        # Try LibreOffice
        try:
            subprocess.run([
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', os.path.dirname(output_pdf),
                pptx_path
            ], check=True, capture_output=True)
            return True
        except Exception:
            pass
        
        return False
    except Exception:
        return False


"""
@brief Convert HTML content to PDF. HTML 콘텐츠를 PDF로 변환합니다.
@param html_content HTML content string HTML 콘텐츠 문자열
@param output_pdf Output PDF file path 출력 PDF 파일 경로
@return True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def html_to_pdf(html_content: str, output_pdf: str) -> bool:
    try:
        # Try using weasyprint if available
        try:
            from weasyprint import HTML
            HTML(string=html_content).write_pdf(output_pdf)
            return True
        except ImportError:
            pass
        
        # Fallback: save as HTML and try browser conversion
        html_file = output_pdf.replace('.pdf', '.html')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return False
    except Exception:
        return False


"""
@brief Merge multiple PDF files into one. 여러 PDF 파일을 하나로 병합합니다.
@param pdf_files List of PDF file paths PDF 파일 경로 리스트
@param output_pdf Output PDF file path 출력 PDF 파일 경로
@return True if successful, False otherwise 성공하면 True, 실패하면 False
"""
def merge_pdfs(pdf_files: List[str], output_pdf: str) -> bool:
    try:
        from PyPDF2 import PdfMerger
        
        merger = PdfMerger()
        
        for pdf_file in pdf_files:
            merger.append(pdf_file)
        
        merger.write(output_pdf)
        merger.close()
        
        return True
    except Exception:
        return False


"""
@brief Get number of pages in PDF file. PDF 파일의 페이지 수를 가져옵니다.
@param pdf_file Path to PDF file PDF 파일 경로
@return Number of pages or None if error 페이지 수, 에러시 None
"""
def get_pdf_page_count(pdf_file: str) -> Optional[int]:
    try:
        from PyPDF2 import PdfReader
        
        reader = PdfReader(pdf_file)
        return len(reader.pages)
    except Exception:
        return None
