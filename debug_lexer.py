#!/usr/bin/env python3
"""
Debug script to test the lexer and parser
"""

from main import DeviceLanguageProcessor

def test_simple_case():
    processor = DeviceLanguageProcessor()

    # Simple test case
    test_code = """dispositivo : sensor1
set temp = 25."""

    print("Testing with:", repr(test_code))
    print()

    result = processor.analyze(test_code, show_tokens=True, show_ast=True)

    if result['success']:
        print("SUCCESS!")
    else:
        print("FAILED:")
        for error in result['errors']:
            print(f"  {error}")

if __name__ == "__main__":
    test_simple_case()
