"""
Tests for file system utilities
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sys_util_core import file_utils


class TestFileUtils(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_create_directory(self):
        """Test creating directory"""
        new_dir = os.path.join(self.test_dir, 'test_dir')
        result = file_utils.create_directory(new_dir)
        
        self.assertTrue(result)
        self.assertTrue(os.path.isdir(new_dir))
    
    def test_file_exists(self):
        """Test checking file existence"""
        # Create a test file
        test_file = os.path.join(self.test_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        
        self.assertTrue(file_utils.file_exists(test_file))
        self.assertFalse(file_utils.file_exists('/nonexistent/file.txt'))
    
    def test_directory_exists(self):
        """Test checking directory existence"""
        self.assertTrue(file_utils.directory_exists(self.test_dir))
        self.assertFalse(file_utils.directory_exists('/nonexistent/directory'))
    
    def test_copy_file(self):
        """Test copying file"""
        # Create source file
        src_file = os.path.join(self.test_dir, 'source.txt')
        with open(src_file, 'w') as f:
            f.write('test content')
        
        # Copy file
        dst_file = os.path.join(self.test_dir, 'dest.txt')
        result = file_utils.copy_file(src_file, dst_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(dst_file))
        
        # Verify content
        with open(dst_file, 'r') as f:
            self.assertEqual(f.read(), 'test content')
    
    def test_get_file_size(self):
        """Test getting file size"""
        # Create test file
        test_file = os.path.join(self.test_dir, 'test.txt')
        content = 'test content'
        with open(test_file, 'w') as f:
            f.write(content)
        
        size = file_utils.get_file_size(test_file)
        self.assertEqual(size, len(content))
    
    def test_get_file_hash(self):
        """Test calculating file hash"""
        # Create test file
        test_file = os.path.join(self.test_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        hash_value = file_utils.get_file_hash(test_file, 'md5')
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 32)  # MD5 hash is 32 characters
    
    def test_list_files(self):
        """Test listing files"""
        # Create test files
        for i in range(3):
            with open(os.path.join(self.test_dir, f'test{i}.txt'), 'w') as f:
                f.write(f'content {i}')
        
        files = file_utils.list_files(self.test_dir, '*.txt')
        self.assertEqual(len(files), 3)
    
    def test_find_files(self):
        """Test finding files by extension"""
        # Create test files
        with open(os.path.join(self.test_dir, 'test.txt'), 'w') as f:
            f.write('text file')
        with open(os.path.join(self.test_dir, 'test.py'), 'w') as f:
            f.write('python file')
        
        txt_files = file_utils.find_files(self.test_dir, extension='txt', recursive=False)
        self.assertEqual(len(txt_files), 1)
        self.assertTrue(txt_files[0].endswith('.txt'))
    
    def test_create_temp_file(self):
        """Test creating temporary file"""
        temp_file = file_utils.create_temp_file(suffix='.txt')
        
        self.assertTrue(os.path.exists(temp_file))
        self.assertTrue(temp_file.endswith('.txt'))
        
        # Clean up
        os.remove(temp_file)
    
    def test_create_temp_directory(self):
        """Test creating temporary directory"""
        temp_dir = file_utils.create_temp_directory()
        
        self.assertTrue(os.path.isdir(temp_dir))
        
        # Clean up
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()
