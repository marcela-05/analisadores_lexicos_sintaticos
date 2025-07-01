#!/usr/bin/env python3
"""
Test suite for the SLY-based Device Language Parser
"""

import unittest
import sys
from main import DeviceLanguageProcessor


class TestSLYDeviceParser(unittest.TestCase):
    """Test cases for the SLY-based device language parser"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = DeviceLanguageProcessor()
    
    def test_simple_device_declaration(self):
        """Test basic device declaration"""
        code = '''
        dispositivo : sensor1
        
        set temp = 25.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")
        self.assertIsNotNone(result['ast'])
        self.assertEqual(len(result['ast'].devices), 1)
        self.assertEqual(result['ast'].devices[0].name, 'sensor1')
        self.assertIsNone(result['ast'].devices[0].observation)
    
    def test_device_with_observation(self):
        """Test device declaration with observation"""
        code = '''
        dispositivo : sensor1, temperature
        
        set temperature = 20.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")
        device = result['ast'].devices[0]
        self.assertEqual(device.name, 'sensor1')
        self.assertEqual(device.observation, 'temperature')
    
    def test_multiple_devices(self):
        """Test multiple device declarations"""
        code = '''
        dispositivo : sensor1
        dispositivo : led1, status
        dispositivo : buzzer
        
        set status = true.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")
        devices = result['ast'].devices
        self.assertEqual(len(devices), 3)
        self.assertEqual(devices[0].name, 'sensor1')
        self.assertEqual(devices[1].name, 'led1')
        self.assertEqual(devices[2].name, 'buzzer')
    
    def test_attribution_command(self):
        """Test attribution commands"""
        code = '''
        dispositivo : sensor1, temp
        
        set temp = 25.
        set temp = true.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")
        commands = result['ast'].commands
        self.assertEqual(len(commands), 2)
        
        # First command: set temp = 25
        cmd1 = commands[0]
        self.assertEqual(cmd1.observation, 'temp')
        self.assertEqual(cmd1.value, 25)
        
        # Second command: set temp = true
        cmd2 = commands[1]
        self.assertEqual(cmd2.observation, 'temp')
        self.assertEqual(cmd2.value, True)
    
    def test_simple_conditional(self):
        """Test simple conditional statements"""
        code = '''
        dispositivo : sensor1, temp
        dispositivo : led1
        
        se temp > 30 entao ligar led1.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")
        
        cmd = result['ast'].commands[0]
        self.assertEqual(cmd.condition.observation, 'temp')
        self.assertEqual(cmd.condition.operator, '>')
        self.assertEqual(cmd.condition.value, 30)
        self.assertEqual(cmd.then_action.action_type, 'ligar')
        self.assertEqual(cmd.then_action.device, 'led1')
        self.assertIsNone(cmd.else_action)
    
    def test_conditional_with_else(self):
        """Test conditional with else clause"""
        code = '''
        dispositivo : sensor1, temp
        dispositivo : led1
        dispositivo : led2
        
        se temp > 30 entao ligar led1 senao desligar led2.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")
        
        cmd = result['ast'].commands[0]
        self.assertIsNotNone(cmd.else_action)
        self.assertEqual(cmd.else_action.action_type, 'desligar')
        self.assertEqual(cmd.else_action.device, 'led2')
    
    def test_complex_observation(self):
        """Test complex observation with AND operator"""
        code = '''
        dispositivo : sensor1, temp
        dispositivo : led1
        
        se temp > 20 && temp < 30 entao ligar led1.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")
        
        condition = result['ast'].commands[0].condition
        self.assertEqual(condition.observation, 'temp')
        self.assertEqual(condition.operator, '>')
        self.assertEqual(condition.value, 20)
        
        # Check the AND part
        self.assertIsNotNone(condition.next_obs)
        self.assertEqual(condition.next_obs.observation, 'temp')
        self.assertEqual(condition.next_obs.operator, '<')
        self.assertEqual(condition.next_obs.value, 30)
    
    def test_alert_action(self):
        """Test alert actions"""
        code = '''
        dispositivo : sensor1
        
        enviar alerta ("Temperature high") sensor1.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")
        
        cmd = result['ast'].commands[0]
        self.assertEqual(cmd.message, 'Temperature high')
        self.assertEqual(cmd.device, 'sensor1')
        self.assertIsNone(cmd.observation)
    
    def test_alert_with_observation(self):
        """Test alert with observation parameter"""
        code = '''
        dispositivo : sensor1, temp
        
        enviar alerta ("Temperature is", temp) sensor1.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")
        
        cmd = result['ast'].commands[0]
        self.assertEqual(cmd.message, 'Temperature is')
        self.assertEqual(cmd.observation, 'temp')
        self.assertEqual(cmd.device, 'sensor1')
    
    def test_broadcast_alert(self):
        """Test broadcast alert to multiple devices"""
        code = '''
        dispositivo : sensor1
        dispositivo : led1
        dispositivo : buzzer
        
        enviar alerta ("Emergency") para todos : led1, buzzer.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")
        
        cmd = result['ast'].commands[0]
        self.assertEqual(cmd.message, 'Emergency')
        self.assertEqual(len(cmd.devices), 2)
        self.assertIn('led1', cmd.devices)
        self.assertIn('buzzer', cmd.devices)
    
    def test_complete_program(self):
        """Test a complete, complex program"""
        code = '''
        dispositivo : tempSensor, temperature
        dispositivo : humSensor, humidity
        dispositivo : redLED
        dispositivo : greenLED
        dispositivo : buzzer
        
        set temperature = 25.
        set humidity = 60.
        
        se temperature > 30 entao ligar redLED.
        se temperature < 15 && humidity > 80 entao enviar alerta ("Cold and humid") para todos : redLED, buzzer.
        se humidity < 40 entao ligar greenLED senao desligar greenLED.
        enviar alerta ("System initialized", temperature) tempSensor.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")
        
        # Verify structure
        ast = result['ast']
        self.assertEqual(len(ast.devices), 5)
        self.assertEqual(len(ast.commands), 6)


class TestSLYParserErrors(unittest.TestCase):
    """Test error handling in SLY parser"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = DeviceLanguageProcessor()
    
    def test_missing_period(self):
        """Test error when command is missing period"""
        code = '''
        dispositivo : sensor1
        
        set temp = 25
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertFalse(result['success'])
        self.assertTrue(len(result['errors']) > 0)
    
    def test_invalid_syntax(self):
        """Test error with invalid syntax"""
        code = '''
        dispositivo sensor1
        
        set temp = 25.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertFalse(result['success'])
        self.assertTrue(len(result['errors']) > 0)
    
    def test_empty_input(self):
        """Test error with empty input"""
        code = ''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertFalse(result['success'])
        self.assertTrue(len(result['errors']) > 0)


if __name__ == '__main__':
    # Run the tests with detailed output
    print("Running SLY Device Language Parser Test Suite")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSLYDeviceParser))
    suite.addTests(loader.loadTestsFromTestCase(TestSLYParserErrors))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
