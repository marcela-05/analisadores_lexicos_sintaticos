#!/usr/bin/env python3
"""
Demonstration of the SLY-based Device Language Parser
Shows all features of the grammar working correctly
"""

from main import DeviceLanguageProcessor

def demo_parser():
    processor = DeviceLanguageProcessor()
    
    print("=" * 70)
    print("DEMONSTRAÇÃO DO PARSER SLY PARA LINGUAGEM DE DISPOSITIVOS")
    print("=" * 70)
    
    # Demo 1: Basic device declarations and simple commands
    print("\n1. DECLARAÇÕES BÁSICAS DE DISPOSITIVOS E COMANDOS SIMPLES")
    print("-" * 50)
    
    code1 = '''dispositivo : sensor1
dispositivo : led1, status

set status = true.
ligar led1.
desligar sensor1.'''
    
    print("Código:")
    print(code1)
    print("\nResultado:")
    result1 = processor.analyze(code1, show_tokens=False, show_ast=True)
    
    # Demo 2: Conditional statements with complex observations
    print("\n" + "=" * 70)
    print("2. COMANDOS CONDICIONAIS COM OBSERVAÇÕES COMPLEXAS")
    print("-" * 50)
    
    code2 = '''dispositivo : sensor1, temp
dispositivo : led1
dispositivo : led2

set temp = 25.

se temp > 30 entao ligar led1.
se temp < 10 && temp > 0 entao ligar led2 senao desligar led2.'''
    
    print("Código:")
    print(code2)
    print("\nResultado:")
    result2 = processor.analyze(code2, show_tokens=False, show_ast=True)
    
    # Demo 3: Alert actions (simple, with observation, broadcast)
    print("\n" + "=" * 70)
    print("3. AÇÕES DE ALERTA (SIMPLES, COM OBSERVAÇÃO, BROADCAST)")
    print("-" * 50)
    
    code3 = '''dispositivo : sensor1, temp
dispositivo : led1
dispositivo : buzzer
dispositivo : display

enviar alerta ("Sistema iniciado") sensor1.
enviar alerta ("Temperatura atual", temp) display.
enviar alerta ("Emergência") para todos : led1, buzzer, display.'''
    
    print("Código:")
    print(code3)
    print("\nResultado:")
    result3 = processor.analyze(code3, show_tokens=False, show_ast=True)
    
    # Demo 4: Complete complex program
    print("\n" + "=" * 70)
    print("4. PROGRAMA COMPLEXO COMPLETO")
    print("-" * 50)
    
    code4 = '''dispositivo : tempSensor, temperature
dispositivo : humSensor, humidity
dispositivo : redLED
dispositivo : greenLED
dispositivo : buzzer
dispositivo : display

set temperature = 22.
set humidity = 45.

se temperature > 35 entao enviar alerta ("Temperatura crítica", temperature) para todos : redLED, buzzer, display.
se temperature >= 25 && temperature <= 35 entao ligar redLED senao desligar redLED.
se humidity < 30 entao enviar alerta ("Umidade baixa") humSensor.
se humidity > 80 && temperature < 20 entao ligar greenLED.
enviar alerta ("Sistema monitorando", temperature) display.'''
    
    print("Código:")
    print(code4)
    print("\nResultado:")
    result4 = processor.analyze(code4, show_tokens=False, show_ast=True)
    
    # Demo 5: Error handling
    print("\n" + "=" * 70)
    print("5. TRATAMENTO DE ERROS")
    print("-" * 50)
    
    code5 = '''dispositivo : sensor1
set temp = 25
se temp > 30 entao ligar led1.'''
    
    print("Código com erro (falta ponto após 'set temp = 25'):")
    print(code5)
    print("\nResultado:")
    result5 = processor.analyze(code5, show_tokens=False, show_ast=True)
    
    # Summary
    print("\n" + "=" * 70)
    print("RESUMO DOS RESULTADOS")
    print("=" * 70)
    
    results = [result1, result2, result3, result4, result5]
    success_count = sum(1 for r in results if r['success'])
    
    print(f"Programas testados: {len(results)}")
    print(f"Sucessos: {success_count}")
    print(f"Erros: {len(results) - success_count}")
    
    print("\nCaracterísticas implementadas:")
    print("✓ Declarações de dispositivos (com e sem observações)")
    print("✓ Comandos de atribuição (set)")
    print("✓ Ações simples (ligar/desligar)")
    print("✓ Comandos condicionais (se/entao/senao)")
    print("✓ Observações complexas com operadores lógicos (&&)")
    print("✓ Alertas simples")
    print("✓ Alertas com parâmetros de observação")
    print("✓ Alertas broadcast (para todos)")
    print("✓ Tratamento de erros sintáticos")
    print("✓ Geração de AST (Abstract Syntax Tree)")
    
    print("\nParser implementado usando SLY (Sly Lex-Yacc) com:")
    print("- Lexer baseado em SLY Lexer")
    print("- Parser baseado em SLY Parser com decorador @_()")
    print("- Gramática completa conforme especificação")
    print("- Classes AST para representação da árvore sintática")
    print("- Interface unificada para análise léxica e sintática")

if __name__ == "__main__":
    demo_parser()
