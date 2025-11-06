"""
Tests for command utilities
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sys_util_core import cmd_utils


class TestCmdUtils(unittest.TestCase):
    
    def test_run_command_simple(self):
        """Test basic command execution"""
        returncode, stdout, stderr = cmd_utils.run_command('echo test')
        
        self.assertEqual(returncode, 0)
        self.assertIn('test', stdout)
    
    def test_check_command_exists(self):
        """Test checking if command exists"""
        # Python should exist
        self.assertTrue(cmd_utils.check_command_exists('python'))
        
        # Non-existent command
        self.assertFalse(cmd_utils.check_command_exists('nonexistentcommand12345'))
    
    def test_get_command_output(self):
        """Test getting command output"""
        output = cmd_utils.get_command_output('echo hello')
        
        self.assertIn('hello', output)
    
    def test_run_batch_commands(self):
        """Test running multiple commands"""
        commands = ['echo first', 'echo second']
        results = cmd_utils.run_batch_commands(commands, shell=True)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], 0)  # First command should succeed
        self.assertEqual(results[1][0], 0)  # Second command should succeed
    
    def test_get_process_list(self):
        """Test getting process list"""
        processes = cmd_utils.get_process_list()
        
        # Should return a list
        self.assertIsInstance(processes, list)
        
        # Should have at least one process
        self.assertGreater(len(processes), 0)
        
        # Each process should be a dict
        if processes:
            self.assertIsInstance(processes[0], dict)


if __name__ == '__main__':
    unittest.main()
