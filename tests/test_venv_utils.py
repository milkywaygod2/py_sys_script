"""
Tests for virtual environment utilities
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sys_util_core import venv_utils


class TestVenvUtils(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.venv_path = os.path.join(self.test_dir, 'test_venv')
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_create_venv(self):
        """Test creating a virtual environment"""
        success, message = venv_utils.create_venv(self.venv_path)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.venv_path))
        self.assertTrue(venv_utils.is_venv(self.venv_path))
    
    def test_create_venv_already_exists(self):
        """Test creating venv when it already exists"""
        # Create venv first time
        venv_utils.create_venv(self.venv_path)
        
        # Try to create again without clear flag
        success, message = venv_utils.create_venv(self.venv_path, clear=False)
        self.assertFalse(success)
        self.assertIn('already exists', message)
    
    def test_create_venv_with_clear(self):
        """Test recreating venv with clear flag"""
        # Create venv first time
        venv_utils.create_venv(self.venv_path)
        
        # Recreate with clear flag
        success, message = venv_utils.create_venv(self.venv_path, clear=True)
        self.assertTrue(success)
    
    def test_is_venv(self):
        """Test checking if directory is a venv"""
        # Non-existent path
        self.assertFalse(venv_utils.is_venv('/nonexistent/path'))
        
        # Create venv
        venv_utils.create_venv(self.venv_path)
        
        # Should be detected as venv
        self.assertTrue(venv_utils.is_venv(self.venv_path))
        
        # Regular directory should not be venv
        regular_dir = os.path.join(self.test_dir, 'regular')
        os.makedirs(regular_dir)
        self.assertFalse(venv_utils.is_venv(regular_dir))
    
    def test_get_venv_python(self):
        """Test getting Python executable from venv"""
        venv_utils.create_venv(self.venv_path)
        
        python_exe = venv_utils.get_venv_python(self.venv_path)
        
        self.assertIsNotNone(python_exe)
        self.assertTrue(os.path.exists(python_exe))
    
    def test_get_venv_pip(self):
        """Test getting pip executable from venv"""
        venv_utils.create_venv(self.venv_path)
        
        pip_exe = venv_utils.get_venv_pip(self.venv_path)
        
        self.assertIsNotNone(pip_exe)
        self.assertTrue(os.path.exists(pip_exe))
    
    def test_delete_venv(self):
        """Test deleting a virtual environment"""
        # Create venv
        venv_utils.create_venv(self.venv_path)
        self.assertTrue(os.path.exists(self.venv_path))
        
        # Delete venv
        success, message = venv_utils.delete_venv(self.venv_path)
        
        self.assertTrue(success)
        self.assertFalse(os.path.exists(self.venv_path))
    
    def test_delete_nonexistent_venv(self):
        """Test deleting non-existent venv"""
        success, message = venv_utils.delete_venv('/nonexistent/venv')
        
        self.assertFalse(success)
        self.assertIn('not found', message)
    
    def test_install_package(self):
        """Test installing a package in venv"""
        venv_utils.create_venv(self.venv_path)
        
        # Install a small package
        success, message = venv_utils.install_package(
            self.venv_path, 
            'six'  # Small, reliable package
        )
        
        self.assertTrue(success)
        
        # Verify package is installed
        success, output, packages = venv_utils.list_packages(
            self.venv_path, 
            format='json'
        )
        
        package_names = [p['name'] for p in packages]
        self.assertIn('six', package_names)
    
    def test_uninstall_package(self):
        """Test uninstalling a package from venv"""
        venv_utils.create_venv(self.venv_path)
        
        # Install package
        venv_utils.install_package(self.venv_path, 'six')
        
        # Uninstall package
        success, message = venv_utils.uninstall_package(self.venv_path, 'six')
        
        self.assertTrue(success)
        
        # Verify package is removed
        success, output, packages = venv_utils.list_packages(
            self.venv_path, 
            format='json'
        )
        
        package_names = [p['name'] for p in packages]
        self.assertNotIn('six', package_names)
    
    def test_list_packages(self):
        """Test listing packages in venv"""
        venv_utils.create_venv(self.venv_path)
        
        # List packages (should have at least pip and setuptools)
        success, output, packages = venv_utils.list_packages(
            self.venv_path, 
            format='json'
        )
        
        self.assertTrue(success)
        self.assertIsInstance(packages, list)
        self.assertGreater(len(packages), 0)
        
        # Check that pip is in the list
        package_names = [p['name'] for p in packages]
        self.assertIn('pip', package_names)
    
    def test_upgrade_pip(self):
        """Test upgrading pip in venv"""
        venv_utils.create_venv(self.venv_path)
        
        success, message = venv_utils.upgrade_pip(self.venv_path)
        
        self.assertTrue(success)
    
    def test_get_package_info(self):
        """Test getting package information"""
        venv_utils.create_venv(self.venv_path)
        
        # Get info about pip
        success, info = venv_utils.get_package_info(self.venv_path, 'pip')
        
        self.assertTrue(success)
        self.assertIsInstance(info, dict)
        self.assertIn('Name', info)
        self.assertIn('Version', info)
    
    def test_freeze_requirements(self):
        """Test freezing requirements to file"""
        venv_utils.create_venv(self.venv_path)
        
        # Install a package
        venv_utils.install_package(self.venv_path, 'six')
        
        # Freeze requirements
        req_file = os.path.join(self.test_dir, 'requirements.txt')
        success, message = venv_utils.freeze_requirements(self.venv_path, req_file)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(req_file))
        
        # Verify file contains the package
        with open(req_file, 'r') as f:
            content = f.read()
        
        self.assertIn('six', content)
    
    def test_get_venv_info(self):
        """Test getting venv information"""
        venv_utils.create_venv(self.venv_path)
        
        info = venv_utils.get_venv_info(self.venv_path)
        
        self.assertIsInstance(info, dict)
        self.assertEqual(info['path'], self.venv_path)
        self.assertTrue(info['exists'])
        self.assertTrue(info['is_venv'])
        self.assertIsNotNone(info['python'])
        self.assertIsNotNone(info['pip'])
    
    def test_run_in_venv(self):
        """Test running command in venv"""
        venv_utils.create_venv(self.venv_path)
        
        # Run python --version
        returncode, stdout, stderr = venv_utils.run_in_venv(
            self.venv_path,
            ['python', '--version']
        )
        
        self.assertEqual(returncode, 0)
        self.assertTrue('Python' in stdout or 'Python' in stderr)
    
    def test_venv_error_handling(self):
        """Test error handling in venv operations"""
        # Try to create venv with invalid path
        with self.assertRaises(venv_utils.VenvError):
            venv_utils.create_venv('/invalid/\x00/path')


if __name__ == '__main__':
    unittest.main()
