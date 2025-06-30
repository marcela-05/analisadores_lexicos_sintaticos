#!/usr/bin/env python3
"""
Comprehensive test suite for the Device Language Parser
Tests lexical analysis, syntax parsing, AST construction, and error handling
"""

import unittest
import sys
from main import DeviceLanguageProcessor, ParseError


class TestDeviceParser(unittest.TestCase):
    """Test cases for the device language parser"""
    
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
        self.assertEqual(len(result['ast'].devices.devices), 1)
        self.assertEqual(result['ast'].devices.devices[0].name, 'sensor1')
        self.assertIsNone(result['ast'].devices.devices[0].observation)
    
    def test_device_with_observation(self):
        """Test device declaration with observation"""
        code = '''
        dispositivo : sensor1, temperature
        
        set temperature = 20.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")
        device = result['ast'].devices.devices[0]
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
        devices = result['ast'].devices.devices
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
        commands = result['ast'].commands.commands
        self.assertEqual(len(commands), 2)
        
        # First command: set temp = 25
        cmd1 = commands[0]
        self.assertEqual(cmd1.observation, 'temp')
        self.assertEqual(cmd1.value.value, 25)
        
        # Second command: set temp = true
        cmd2 = commands[1]
        self.assertEqual(cmd2.observation, 'temp')
        self.assertEqual(cmd2.value.value, True)
    
    def test_simple_conditional(self):
        """Test simple conditional statements"""
        code = '''
        dispositivo : sensor1, temp
        dispositivo : led1
        
        se temp > 30 entao ligar led1.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")
        
        cmd = result['ast'].commands.commands[0]
        self.assertEqual(cmd.condition.observation, 'temp')
        self.assertEqual(cmd.condition.operator, '>')
        self.assertEqual(cmd.condition.value.value, 30)
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
        
        cmd = result['ast'].commands.commands[0]
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
        
        condition = result['ast'].commands.commands[0].condition
        self.assertEqual(condition.observation, 'temp')
        self.assertEqual(condition.operator, '>')
        self.assertEqual(condition.value.value, 20)
        
        # Check the AND part
        self.assertIsNotNone(condition.next_obs)
        self.assertEqual(condition.next_obs.observation, 'temp')
        self.assertEqual(condition.next_obs.operator, '<')
        self.assertEqual(condition.next_obs.value.value, 30)
    
    def test_alert_action(self):
        """Test alert actions"""
        code = '''
        dispositivo : sensor1
        
        enviar alerta ("Temperature high") sensor1.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")
        
        cmd = result['ast'].commands.commands[0]
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
        
        cmd = result['ast'].commands.commands[0]
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
        
        cmd = result['ast'].commands.commands[0]
        self.assertEqual(cmd.message, 'Emergency')
        self.assertEqual(len(cmd.devices.devices), 2)
        self.assertIn('led1', cmd.devices.devices)
        self.assertIn('buzzer', cmd.devices.devices)


class TestParserErrors(unittest.TestCase):
    """Test error handling and recovery"""
    
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
        self.assertTrue(any('Expected \'PONTO\'' in error for error in result['errors']))
    
    def test_missing_colon_in_device(self):
        """Test error when device declaration is missing colon"""
        code = '''
        dispositivo sensor1
        
        set temp = 25.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertFalse(result['success'])
        self.assertTrue(any('Expected \'DOIS_PONTOS\'' in error for error in result['errors']))
    
    def test_missing_equals_in_attribution(self):
        """Test error when attribution is missing equals sign"""
        code = '''
        dispositivo : sensor1, temp
        
        set temp 25.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertFalse(result['success'])
        self.assertTrue(any('Expected \'IGUAL\'' in error for error in result['errors']))
    
    def test_invalid_token_in_command(self):
        """Test error with invalid token in command"""
        code = '''
        dispositivo : sensor1
        
        invalid_command temp = 25.
        '''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertFalse(result['success'])
        self.assertTrue(len(result['errors']) > 0)
    
    def test_empty_input(self):
        """Test error with empty input"""
        code = ''
        
        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertFalse(result['success'])
        self.assertTrue(any('Empty input' in error for error in result['errors']))


class TestComplexPrograms(unittest.TestCase):
    """Test complex program structures"""

    def setUp(self):
        """Set up test fixtures"""
        self.processor = DeviceLanguageProcessor()

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
        self.assertEqual(len(ast.devices.devices), 5)
        self.assertEqual(len(ast.commands.commands), 6)

    def test_nested_conditions(self):
        """Test deeply nested AND conditions"""
        code = '''
        dispositivo : sensor, temp
        dispositivo : led

        se temp > 20 && temp < 30 && temp != 25 entao ligar led.
        '''

        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")

        # Verify the nested structure
        condition = result['ast'].commands.commands[0].condition
        self.assertIsNotNone(condition.next_obs)
        self.assertIsNotNone(condition.next_obs.next_obs)

    def test_all_operators(self):
        """Test all logical operators"""
        code = '''
        dispositivo : sensor, value
        dispositivo : led

        se value == 10 entao ligar led.
        se value != 20 entao ligar led.
        se value < 30 entao ligar led.
        se value > 40 entao ligar led.
        se value <= 50 entao ligar led.
        se value >= 60 entao ligar led.
        '''

        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")

        commands = result['ast'].commands.commands
        operators = [cmd.condition.operator for cmd in commands]
        expected_ops = ['==', '!=', '<', '>', '<=', '>=']
        self.assertEqual(operators, expected_ops)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def setUp(self):
        """Set up test fixtures"""
        self.processor = DeviceLanguageProcessor()

    def test_single_device_single_command(self):
        """Test minimal valid program"""
        code = '''
        dispositivo : led

        ligar led.
        '''

        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")

    def test_boolean_values(self):
        """Test boolean value handling"""
        code = '''
        dispositivo : sensor, flag

        set flag = true.
        set flag = false.
        se flag == true entao ligar sensor.
        '''

        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")

        commands = result['ast'].commands.commands
        self.assertTrue(commands[0].value.value)  # true
        self.assertFalse(commands[1].value.value)  # false

    def test_numeric_values(self):
        """Test numeric value handling"""
        code = '''
        dispositivo : sensor, temp

        set temp = 0.
        set temp = 100.
        se temp >= 50 entao ligar sensor.
        '''

        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")

        commands = result['ast'].commands.commands
        self.assertEqual(commands[0].value.value, 0)
        self.assertEqual(commands[1].value.value, 100)

    def test_long_device_names(self):
        """Test handling of longer device and observation names"""
        code = '''
        dispositivo : temperatureSensorOutside, currentTemperatureReading

        set currentTemperatureReading = 25.
        se currentTemperatureReading > 30 entao enviar alerta ("Hot outside") temperatureSensorOutside.
        '''

        result = self.processor.analyze(code, show_tokens=False, show_ast=False)
        self.assertTrue(result['success'], f"Parsing failed: {result['errors']}")


if __name__ == '__main__':
    # Run the tests with detailed output
    print("Running Device Language Parser Test Suite")
    print("=" * 50)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDeviceParser))
    suite.addTests(loader.loadTestsFromTestCase(TestParserErrors))
    suite.addTests(loader.loadTestsFromTestCase(TestComplexPrograms))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

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
