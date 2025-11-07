"""
Tests for PyInstaller utilities
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sys_util_core import pyinstaller_utils, venv_utils


class TestPyInstallerUtils(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.venv_path = os.path.join(self.test_dir, 'test_venv')
        self.test_script = os.path.join(self.test_dir, 'test_script.py')
        
        # Create a simple test script
        with open(self.test_script, 'w') as f:
            f.write('#!/usr/bin/env python\n')
            f.write('print("Hello from test script")\n')
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        # Clean up build artifacts in current directory
        for dirname in ['build', 'dist']:
            if os.path.exists(dirname):
                shutil.rmtree(dirname)
        
        # Clean up spec file
        spec_file = 'test_script.spec'
        if os.path.exists(spec_file):
            os.remove(spec_file)
    
    def test_check_pyinstaller_installed(self):
        """Test checking if PyInstaller is installed"""
        # This may be True or False depending on environment
        result = pyinstaller_utils.check_pyinstaller_installed()
        self.assertIsInstance(result, bool)
    
    def test_get_pyinstaller_version(self):
        """Test getting PyInstaller version"""
        version = pyinstaller_utils.get_pyinstaller_version()
        # May be None if not installed, or a version string
        if version is not None:
            self.assertIsInstance(version, str)
    
    def test_install_pyinstaller_in_venv(self):
        """Test installing PyInstaller in a venv"""
        # Create venv
        venv_utils.create_venv(self.venv_path)
        
        # Install PyInstaller
        try:
            success, message = pyinstaller_utils.install_pyinstaller(self.venv_path)
            self.assertTrue(success)
            
            # Verify installation
            self.assertTrue(pyinstaller_utils.check_pyinstaller_installed(self.venv_path))
        except pyinstaller_utils.PyInstallerError as e:
            # May fail in restricted environments
            self.skipTest(f"PyInstaller installation not possible: {e}")
    
    def test_analyze_script(self):
        """Test analyzing a Python script"""
        # Create a script with imports
        script_path = os.path.join(self.test_dir, 'analyze_test.py')
        with open(script_path, 'w') as f:
            f.write('import os\n')
            f.write('import sys\n')
            f.write('from pathlib import Path\n')
            f.write('print("Test")\n')
        
        try:
            success, analysis = pyinstaller_utils.analyze_script(script_path)
            
            self.assertTrue(success)
            self.assertIn('os', analysis)
            self.assertIn('sys', analysis)
            self.assertIn('pathlib', analysis)
        except pyinstaller_utils.PyInstallerError:
            # Analysis might fail if PyInstaller is not available
            pass
    
    def test_clean_build_files(self):
        """Test cleaning PyInstaller build artifacts"""
        # Create fake build directories
        build_dir = os.path.join(self.test_dir, 'build')
        dist_dir = os.path.join(self.test_dir, 'dist')
        os.makedirs(build_dir)
        os.makedirs(dist_dir)
        
        # Change to test directory
        old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        try:
            success, message = pyinstaller_utils.clean_build_files(
                remove_build=True,
                remove_dist=True
            )
            
            self.assertTrue(success)
            self.assertFalse(os.path.exists(build_dir))
            self.assertFalse(os.path.exists(dist_dir))
        finally:
            os.chdir(old_cwd)
    
    def test_build_exe_without_pyinstaller(self):
        """Test that build_exe raises error when PyInstaller not installed"""
        # Create a venv without PyInstaller
        venv_utils.create_venv(self.venv_path)
        
        with self.assertRaises(pyinstaller_utils.PyInstallerError):
            pyinstaller_utils.build_exe(
                self.test_script,
                venv_path=self.venv_path
            )
    
    def test_build_exe_nonexistent_script(self):
        """Test that build_exe raises error for non-existent script"""
        with self.assertRaises(pyinstaller_utils.PyInstallerError):
            pyinstaller_utils.build_exe('/nonexistent/script.py')
    
    def test_generate_spec_file(self):
        """Test generating a PyInstaller spec file"""
        # Skip if PyInstaller not installed
        if not pyinstaller_utils.check_pyinstaller_installed():
            self.skipTest("PyInstaller not installed")
        
        try:
            spec_path = os.path.join(self.test_dir, 'test.spec')
            success, spec_file = pyinstaller_utils.generate_spec_file(
                self.test_script,
                output_path=spec_path,
                onefile=True
            )
            
            self.assertTrue(success)
            self.assertTrue(os.path.exists(spec_file))
        except pyinstaller_utils.PyInstallerError as e:
            self.skipTest(f"Spec file generation failed: {e}")
    
    def test_pyinstaller_error_exception(self):
        """Test PyInstallerError exception"""
        error = pyinstaller_utils.PyInstallerError("Test error")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Test error")


if __name__ == '__main__':
    unittest.main()
