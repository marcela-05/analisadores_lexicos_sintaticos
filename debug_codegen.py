#!/usr/bin/env python3
"""
Debug the code generation issue
"""

from main import ObsActCompiler

def debug_generation():
    compiler = ObsActCompiler()
    
    obs_code = '''dispositivo : sensor1, temp
dispositivo : led1

set temp = 25.
se temp > 20 entao ligar led1.
enviar alerta ("Test completed") sensor1.'''
    
    print("ObsAct code:")
    print(obs_code)
    print("\nGenerated Python code:")
    
    try:
        python_code = compiler.compile_string(obs_code)
        print(python_code)
        
        print("\nTrying to execute...")
        exec(python_code)
        print("Execution successful!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_generation()
