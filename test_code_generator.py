#!/usr/bin/env python3
"""
Test suite for the ObsAct Code Generator
"""

import unittest
import tempfile
import os
from main import ObsActCompiler


class TestCodeGenerator(unittest.TestCase):
    """Test cases for the code generator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.compiler = ObsActCompiler()
    
    def test_simple_program_generation(self):
        """Test generation of simple program"""
        obs_code = '''dispositivo : sensor1, temp
dispositivo : led1

set temp = 25.
ligar led1.'''

        python_code = self.compiler.compile_string(obs_code)

        # Check that essential elements are present
        self.assertIn("from functions import ligar, desligar, alerta, alertavar", python_code)
        self.assertIn("temp = 25", python_code)
        self.assertIn('ligar("led1")', python_code)
        self.assertIn("def main():", python_code)
    
    def test_conditional_generation(self):
        """Test generation of conditional statements"""
        obs_code = '''dispositivo : sensor1, temp
dispositivo : led1

set temp = 30.
se temp > 25 entao ligar led1 senao desligar led1.'''
        
        python_code = self.compiler.compile_string(obs_code)
        
        self.assertIn("if temp > 25:", python_code)
        self.assertIn('ligar("led1")', python_code)
        self.assertIn("else:", python_code)
        self.assertIn('desligar("led1")', python_code)
    
    def test_complex_observation_generation(self):
        """Test generation of complex observations with &&"""
        obs_code = '''dispositivo : sensor1, temp
dispositivo : led1

set temp = 25.
se temp > 20 && temp < 30 entao ligar led1.'''
        
        python_code = self.compiler.compile_string(obs_code)
        
        self.assertIn("if temp > 20 and temp < 30:", python_code)
        self.assertIn('ligar("led1")', python_code)
    
    def test_alert_generation(self):
        """Test generation of alert actions"""
        obs_code = '''dispositivo : sensor1, temp

enviar alerta ("Test message") sensor1.
enviar alerta ("Temp value", temp) sensor1.'''
        
        python_code = self.compiler.compile_string(obs_code)
        
        self.assertIn('alerta("sensor1", "Test message")', python_code)
        self.assertIn('alertavar("sensor1", "Temp value", str(temp))', python_code)
    
    def test_broadcast_alert_generation(self):
        """Test generation of broadcast alerts"""
        obs_code = '''dispositivo : sensor1
dispositivo : led1
dispositivo : buzzer

enviar alerta ("Emergency") para todos : sensor1, led1, buzzer.'''
        
        python_code = self.compiler.compile_string(obs_code)
        
        # Check that broadcast alerts are generated as individual calls
        self.assertIn('alerta("sensor1", "Emergency")', python_code)
        self.assertIn('alerta("led1", "Emergency")', python_code)
        self.assertIn('alerta("buzzer", "Emergency")', python_code)
    
    def test_file_compilation(self):
        """Test file-to-file compilation"""
        obs_code = '''dispositivo : sensor1, temp

set temp = 25.
ligar sensor1.'''
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.obs', delete=False) as obs_file:
            obs_file.write(obs_code)
            obs_file_path = obs_file.name
        
        try:
            # Compile to Python
            py_file_path = obs_file_path.replace('.obs', '.py')
            success = self.compiler.compile_file(obs_file_path, py_file_path)
            
            self.assertTrue(success)
            self.assertTrue(os.path.exists(py_file_path))
            
            # Check generated content
            with open(py_file_path, 'r') as f:
                python_code = f.read()
            
            self.assertIn('ligar("sensor1")', python_code)
            self.assertIn("temp = 25", python_code)
            
        finally:
            # Clean up
            if os.path.exists(obs_file_path):
                os.unlink(obs_file_path)
            if os.path.exists(py_file_path):
                os.unlink(py_file_path)
    
    def test_error_handling(self):
        """Test error handling for invalid ObsAct code"""
        obs_code = '''dispositivo : sensor1
set temp = 25
ligar sensor1.'''  # Missing period after set command
        
        with self.assertRaises(Exception):
            self.compiler.compile_string(obs_code)
    
    def test_variable_initialization(self):
        """Test that variables are properly initialized"""
        obs_code = '''dispositivo : sensor1, temp
dispositivo : sensor2, humidity

set temp = 25.
set humidity = 60.'''
        
        python_code = self.compiler.compile_string(obs_code)
        
        self.assertIn("temp = None  # Will be set by program", python_code)
        self.assertIn("humidity = None  # Will be set by program", python_code)
        self.assertIn("temp = 25", python_code)
        self.assertIn("humidity = 60", python_code)
    
    def test_comments_preservation(self):
        """Test that original ObsAct statements are preserved as comments"""
        obs_code = '''dispositivo : sensor1, temp

set temp = 25.
se temp > 30 entao ligar sensor1.'''
        
        python_code = self.compiler.compile_string(obs_code)
        
        self.assertIn("# set temp = 25", python_code)
        self.assertIn("# se temp > 30 entao", python_code)
        self.assertIn("# ligar sensor1", python_code)


class TestCodeGeneratorIntegration(unittest.TestCase):
    """Integration tests for the complete compilation process"""
    
    def test_complete_program_execution(self):
        """Test that generated code can be executed without errors"""
        obs_code = '''dispositivo : sensor1, temp
dispositivo : led1

set temp = 25.
se temp > 20 entao ligar led1.
enviar alerta ("Test completed") sensor1.'''

        compiler = ObsActCompiler()
        python_code = compiler.compile_string(obs_code)

        # Create mock functions for testing
        mock_functions = {
            'ligar': lambda device: print(f"{device} ligado !"),
            'desligar': lambda device: print(f"{device} desligado !"),
            'alerta': lambda device, msg: print(f"{device} recebeu o alerta :\n{msg}"),
            'alertavar': lambda device, msg, var: print(f"{device} recebeu o alerta :\n{msg} {var}")
        }

        # Execute the generated code with mock functions
        try:
            # Replace the import with our mock functions
            modified_code = python_code.replace(
                "from functions import ligar, desligar, alerta, alertavar",
                ""
            )

            # Execute with mock functions in the namespace
            exec(modified_code, mock_functions)
        except Exception as e:
            self.fail(f"Generated code failed to execute: {e}")


if __name__ == '__main__':
    # Run the tests
    print("Running Code Generator Test Suite")
    print("=" * 50)
    
    unittest.main(verbosity=2)
