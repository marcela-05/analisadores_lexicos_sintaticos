#!/usr/bin/env python3
"""
Debug specific parser issues
"""

from main import DeviceLanguageProcessor

def test_broadcast_alert():
    processor = DeviceLanguageProcessor()

    # Test the exact problematic code from Example 3
    test_code = '''dispositivo : sensor1, temp
dispositivo : led1
dispositivo : led2
dispositivo : buzzer

set temp = 20.

se temp >= 35 entao enviar alerta ("Temperatura alta", temp) para todos : led1, led2, buzzer.'''

    print("Testing problematic code from Example 3:")
    print(repr(test_code))
    print()

    result = processor.analyze(test_code, show_tokens=True, show_ast=True)

    if result['success']:
        print("SUCCESS!")
    else:
        print("FAILED:")
        for error in result['errors']:
            print(f"  {error}")

if __name__ == "__main__":
    test_broadcast_alert()
