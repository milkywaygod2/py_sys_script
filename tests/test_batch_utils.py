"""
Tests for batch utilities
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sys_util_core import batch_utils


class TestBatchUtils(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_batch_rename_files(self):
        """Test batch renaming files"""
        # Create test files
        for i in range(3):
            with open(os.path.join(self.test_dir, f'old_name_{i}.txt'), 'w') as f:
                f.write('test')
        
        # Rename files
        renamed = batch_utils.batch_rename_files(
            self.test_dir, 'old_name', 'new_name', ['txt']
        )
        
        self.assertEqual(len(renamed), 3)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'new_name_0.txt')))
    
    def test_batch_move_by_extension(self):
        """Test moving files by extension"""
        target_dir = os.path.join(self.test_dir, 'target')
        
        # Create test files
        for ext in ['txt', 'pdf', 'doc']:
            with open(os.path.join(self.test_dir, f'file.{ext}'), 'w') as f:
                f.write('test')
        
        # Move txt files
        result = batch_utils.batch_move_by_extension(
            self.test_dir, target_dir, ['txt']
        )
        
        self.assertEqual(result['txt'], 1)
        self.assertTrue(os.path.exists(os.path.join(target_dir, 'file.txt')))
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, 'file.txt')))
    
    def test_batch_copy_by_extension(self):
        """Test copying files by extension"""
        target_dir = os.path.join(self.test_dir, 'target')
        
        # Create test files
        with open(os.path.join(self.test_dir, 'file.txt'), 'w') as f:
            f.write('test')
        
        # Copy txt files
        result = batch_utils.batch_copy_by_extension(
            self.test_dir, target_dir, ['txt']
        )
        
        self.assertEqual(result['txt'], 1)
        self.assertTrue(os.path.exists(os.path.join(target_dir, 'file.txt')))
        # Original should still exist
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'file.txt')))
    
    def test_organize_files_by_extension(self):
        """Test organizing files into subdirectories"""
        # Create test files
        for ext in ['txt', 'pdf', 'doc']:
            with open(os.path.join(self.test_dir, f'file.{ext}'), 'w') as f:
                f.write('test')
        
        # Organize files
        result = batch_utils.organize_files_by_extension(self.test_dir)
        
        self.assertTrue('txt' in result)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'txt', 'file.txt')))
    
    def test_find_duplicate_files(self):
        """Test finding duplicate files"""
        # Create duplicate files with same content
        content = 'duplicate content'
        with open(os.path.join(self.test_dir, 'file1.txt'), 'w') as f:
            f.write(content)
        with open(os.path.join(self.test_dir, 'file2.txt'), 'w') as f:
            f.write(content)
        with open(os.path.join(self.test_dir, 'file3.txt'), 'w') as f:
            f.write('different content')
        
        # Find duplicates
        duplicates = batch_utils.find_duplicate_files(self.test_dir)
        
        # Should find one set of duplicates (file1 and file2)
        self.assertEqual(len(duplicates), 1)
        duplicate_list = list(duplicates.values())[0]
        self.assertEqual(len(duplicate_list), 2)


if __name__ == '__main__':
    unittest.main()
