"""
Tests for web utilities
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sys_util_core import web_utils


class TestWebUtils(unittest.TestCase):
    
    def test_parse_url(self):
        """Test URL parsing"""
        url = "https://example.com:8080/path?query=value#fragment"
        parsed = web_utils.parse_url(url)
        
        self.assertEqual(parsed['scheme'], 'https')
        self.assertEqual(parsed['netloc'], 'example.com:8080')
        self.assertEqual(parsed['path'], '/path')
        self.assertEqual(parsed['query'], 'query=value')
        self.assertEqual(parsed['fragment'], 'fragment')
    
    def test_build_url(self):
        """Test URL building with parameters"""
        base_url = "https://example.com/search"
        params = {'q': 'test', 'page': '1'}
        
        result = web_utils.build_url(base_url, params)
        
        self.assertIn('q=test', result)
        self.assertIn('page=1', result)
        self.assertTrue(result.startswith(base_url))
    
    def test_extract_text_from_html(self):
        """Test extracting text from HTML"""
        html = "<html><body><p>Hello World</p><script>alert('test')</script></body></html>"
        text = web_utils.extract_text_from_html(html)
        
        self.assertIn('Hello World', text)
        self.assertNotIn('script', text.lower())
        self.assertNotIn('alert', text)
    
    def test_extract_links(self):
        """Test extracting links from HTML"""
        html = '<a href="/page1">Link 1</a><a href="http://example.com">Link 2</a>'
        links = web_utils.extract_links(html)
        
        self.assertEqual(len(links), 2)
        self.assertIn('/page1', links)
        self.assertIn('http://example.com', links)


if __name__ == '__main__':
    unittest.main()
