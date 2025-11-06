"""
Tests for Windows registry utilities
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sys_util_core import registry_utils


class TestRegistryUtils(unittest.TestCase):
    
    def test_is_windows(self):
        """Test checking if running on Windows"""
        result = registry_utils.is_windows()
        
        if sys.platform == 'win32':
            self.assertTrue(result)
        else:
            self.assertFalse(result)
    
    @unittest.skipUnless(sys.platform == 'win32', "Windows-only test")
    def test_create_and_delete_key(self):
        """Test creating and deleting registry key"""
        test_key = r'Software\TestKey12345'
        
        # Create key
        result = registry_utils.create_registry_key(test_key)
        self.assertTrue(result)
        
        # Verify key exists
        exists = registry_utils.registry_key_exists(test_key)
        self.assertTrue(exists)
        
        # Delete key
        result = registry_utils.delete_registry_key(test_key)
        self.assertTrue(result)
        
        # Verify key doesn't exist
        exists = registry_utils.registry_key_exists(test_key)
        self.assertFalse(exists)
    
    @unittest.skipUnless(sys.platform == 'win32', "Windows-only test")
    def test_set_and_get_value(self):
        """Test setting and getting registry value"""
        import winreg
        
        test_key = r'Software\TestKey12345'
        test_value_name = 'TestValue'
        test_value_data = 'TestData'
        
        # Create key
        registry_utils.create_registry_key(test_key)
        
        # Set value
        result = registry_utils.set_registry_value(
            test_key, 
            test_value_name, 
            test_value_data,
            winreg.REG_SZ
        )
        self.assertTrue(result)
        
        # Get value
        value = registry_utils.get_registry_value(test_key, test_value_name)
        self.assertEqual(value, test_value_data)
        
        # Clean up
        registry_utils.delete_registry_value(test_key, test_value_name)
        registry_utils.delete_registry_key(test_key)
    
    @unittest.skipUnless(sys.platform == 'win32', "Windows-only test")
    def test_list_registry_subkeys(self):
        """Test listing registry subkeys"""
        # List subkeys under HKCU\Software (should exist on all Windows systems)
        subkeys = registry_utils.list_registry_subkeys(r'Software')
        
        # Should return a list
        self.assertIsInstance(subkeys, list)
        
        # Should have at least one subkey
        self.assertGreater(len(subkeys), 0)
    
    @unittest.skipUnless(sys.platform == 'win32', "Windows-only test")
    def test_get_registry_type_name(self):
        """Test getting registry type name"""
        import winreg
        
        type_name = registry_utils.get_registry_type_name(winreg.REG_SZ)
        self.assertEqual(type_name, 'REG_SZ')
        
        type_name = registry_utils.get_registry_type_name(winreg.REG_DWORD)
        self.assertEqual(type_name, 'REG_DWORD')


if __name__ == '__main__':
    unittest.main()
