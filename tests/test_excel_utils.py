"""
Tests for Excel/CSV utilities
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sys_util_core import excel_utils


class TestExcelUtils(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_write_and_read_csv(self):
        """Test writing and reading CSV"""
        csv_file = os.path.join(self.test_dir, 'test.csv')
        data = [['Name', 'Age'], ['Alice', '30'], ['Bob', '25']]
        
        # Write CSV
        result = excel_utils.write_csv(csv_file, data)
        self.assertTrue(result)
        
        # Read CSV
        read_data = excel_utils.read_csv(csv_file)
        self.assertEqual(len(read_data), 3)
        self.assertEqual(read_data[0], ['Name', 'Age'])
    
    def test_write_and_read_csv_as_dict(self):
        """Test writing and reading CSV as dictionaries"""
        csv_file = os.path.join(self.test_dir, 'test_dict.csv')
        data = [
            {'name': 'Alice', 'age': '30'},
            {'name': 'Bob', 'age': '25'}
        ]
        
        # Write CSV
        result = excel_utils.write_csv_from_dict(csv_file, data)
        self.assertTrue(result)
        
        # Read CSV
        read_data = excel_utils.read_csv_as_dict(csv_file)
        self.assertEqual(len(read_data), 2)
        self.assertEqual(read_data[0]['name'], 'Alice')
    
    def test_append_to_csv(self):
        """Test appending to CSV"""
        csv_file = os.path.join(self.test_dir, 'append.csv')
        
        # Initial data
        initial_data = [['Name', 'Age'], ['Alice', '30']]
        excel_utils.write_csv(csv_file, initial_data)
        
        # Append data
        new_rows = [['Bob', '25'], ['Charlie', '35']]
        result = excel_utils.append_to_csv(csv_file, new_rows)
        self.assertTrue(result)
        
        # Verify
        data = excel_utils.read_csv(csv_file)
        self.assertEqual(len(data), 4)
    
    def test_get_csv_column(self):
        """Test getting a column from CSV"""
        csv_file = os.path.join(self.test_dir, 'columns.csv')
        data = [
            {'name': 'Alice', 'age': '30'},
            {'name': 'Bob', 'age': '25'}
        ]
        excel_utils.write_csv_from_dict(csv_file, data)
        
        # Get column
        names = excel_utils.get_csv_column(csv_file, 'name')
        self.assertEqual(len(names), 2)
        self.assertIn('Alice', names)
        self.assertIn('Bob', names)
    
    def test_get_csv_statistics(self):
        """Test getting CSV statistics"""
        csv_file = os.path.join(self.test_dir, 'stats.csv')
        data = [['A', 'B', 'C'], ['1', '2', '3'], ['4', '5', '6']]
        excel_utils.write_csv(csv_file, data)
        
        stats = excel_utils.get_csv_statistics(csv_file)
        self.assertEqual(stats['row_count'], 3)
        self.assertEqual(stats['column_count'], 3)
        self.assertTrue(stats['file_size'] > 0)


if __name__ == '__main__':
    unittest.main()
