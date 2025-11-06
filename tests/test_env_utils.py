"""
Tests for environment variable utilities
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sys_util_core import env_utils


class TestEnvUtils(unittest.TestCase):
    
    def test_get_env_var(self):
        """Test getting environment variable"""
        # PATH should exist on all systems
        path = env_utils.get_env_var('PATH')
        self.assertIsNotNone(path)
        
        # Non-existent variable with default
        value = env_utils.get_env_var('NONEXISTENT_VAR_12345', 'default')
        self.assertEqual(value, 'default')
    
    def test_set_and_get_env_var(self):
        """Test setting and getting environment variable"""
        test_var = 'TEST_VAR_12345'
        test_value = 'test_value'
        
        # Set variable
        result = env_utils.set_env_var(test_var, test_value)
        self.assertTrue(result)
        
        # Get variable
        value = env_utils.get_env_var(test_var)
        self.assertEqual(value, test_value)
        
        # Clean up
        env_utils.delete_env_var(test_var)
    
    def test_env_var_exists(self):
        """Test checking if environment variable exists"""
        # PATH should exist
        self.assertTrue(env_utils.env_var_exists('PATH'))
        
        # Non-existent variable
        self.assertFalse(env_utils.env_var_exists('NONEXISTENT_VAR_12345'))
    
    def test_get_all_env_vars(self):
        """Test getting all environment variables"""
        all_vars = env_utils.get_all_env_vars()
        
        # Should return a dictionary
        self.assertIsInstance(all_vars, dict)
        
        # Should have at least one variable
        self.assertGreater(len(all_vars), 0)
        
        # PATH should be in the dictionary
        self.assertIn('PATH', all_vars)
    
    def test_get_path_variable(self):
        """Test getting PATH as list"""
        path_list = env_utils.get_path_variable()
        
        # Should return a list
        self.assertIsInstance(path_list, list)
        
        # Should have at least one entry
        self.assertGreater(len(path_list), 0)
    
    def test_expand_env_vars(self):
        """Test expanding environment variables in text"""
        # Set a test variable
        test_var = 'TEST_EXPAND_VAR'
        test_value = 'expanded_value'
        env_utils.set_env_var(test_var, test_value)
        
        # Expand variable
        if sys.platform == 'win32':
            text = f'%{test_var}%'
        else:
            text = f'${test_var}'
        
        expanded = env_utils.expand_env_vars(text)
        self.assertIn(test_value, expanded)
        
        # Clean up
        env_utils.delete_env_var(test_var)


if __name__ == '__main__':
    unittest.main()
