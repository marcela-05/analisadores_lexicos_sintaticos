#!/usr/bin/env python3
"""
Final demonstration of the ObsAct Code Generator
Shows the complete pipeline from .obs files to executable Python code
"""

from main import ObsActCompiler
import tempfile
import os

def demo_complete_pipeline():
    """Demonstrate the complete compilation pipeline"""
    compiler = ObsActCompiler()
    
    print("=" * 80)
    print("DEMONSTRAÇÃO COMPLETA DO GERADOR DE CÓDIGO OBSACT")
    print("=" * 80)
    
    # Demo 1: Simple device control
    print("\n1. CONTROLE SIMPLES DE DISPOSITIVOS")
    print("-" * 60)
    
    obs_code1 = '''dispositivo : sensor1, temp
dispositivo : led1
dispositivo : buzzer

set temp = 30.
ligar led1.
desligar buzzer.
enviar alerta ("Sistema iniciado") sensor1.'''
    
    print("Código ObsAct:")
    print(obs_code1)
    print("\nCódigo Python gerado:")
    python_code1 = compiler.compile_string(obs_code1)
    print(python_code1)
    
    # Demo 2: Complex conditionals and observations
    print("\n" + "=" * 80)
    print("2. CONDICIONAIS COMPLEXAS E OBSERVAÇÕES")
    print("-" * 60)
    
    obs_code2 = '''dispositivo : tempSensor, temperature
dispositivo : humSensor, humidity
dispositivo : redLED
dispositivo : greenLED
dispositivo : alarm

set temperature = 28.
set humidity = 65.

se temperature > 30 && humidity > 70 entao enviar alerta ("Condições críticas", temperature) para todos : redLED, alarm.
se temperature >= 25 && temperature <= 30 entao ligar redLED senao desligar redLED.
se humidity < 40 entao ligar greenLED.'''
    
    print("Código ObsAct:")
    print(obs_code2)
    print("\nCódigo Python gerado:")
    python_code2 = compiler.compile_string(obs_code2)
    print(python_code2)
    
    # Demo 3: File compilation and execution
    print("\n" + "=" * 80)
    print("3. COMPILAÇÃO DE ARQUIVO E EXECUÇÃO")
    print("-" * 60)
    
    obs_code3 = '''dispositivo : monitor, status
dispositivo : speaker

set status = true.
se status == true entao enviar alerta ("Sistema operacional") monitor.
ligar speaker.
enviar alerta ("Audio ativado", status) speaker.'''
    
    # Create temporary .obs file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.obs', delete=False) as f:
        f.write(obs_code3)
        obs_file = f.name
    
    try:
        py_file = obs_file.replace('.obs', '.py')
        
        print(f"Arquivo ObsAct criado: {obs_file}")
        print("Conteúdo:")
        print(obs_code3)
        
        # Compile
        success = compiler.compile_file(obs_file, py_file)
        
        if success:
            print(f"\nArquivo Python gerado: {py_file}")
            
            # Read and display generated code
            with open(py_file, 'r') as f:
                generated_code = f.read()
            
            print("Código gerado:")
            print(generated_code)
            
            print("\nExecutando o código gerado:")
            print("-" * 40)
            
            # Execute the generated code (with functions.py available)
            try:
                exec(f"exec(open('{py_file}').read())")
            except Exception as e:
                print(f"Erro na execução: {e}")
                print("(Isso é esperado se functions.py não estiver disponível)")
        
    finally:
        # Clean up
        if os.path.exists(obs_file):
            os.unlink(obs_file)
        if os.path.exists(py_file):
            os.unlink(py_file)
    
    # Demo 4: Error handling
    print("\n" + "=" * 80)
    print("4. TRATAMENTO DE ERROS")
    print("-" * 60)
    
    obs_code_error = '''dispositivo : sensor1
set temp = 25
ligar sensor1.'''  # Missing period
    
    print("Código ObsAct com erro sintático:")
    print(obs_code_error)
    print("\nResultado da compilação:")
    
    try:
        python_code_error = compiler.compile_string(obs_code_error)
        print("Código gerado (não deveria chegar aqui):")
        print(python_code_error)
    except Exception as e:
        print(f"Erro detectado corretamente: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("RESUMO DAS FUNCIONALIDADES IMPLEMENTADAS")
    print("=" * 80)
    
    print("\n✅ PARSER SLY:")
    print("  - Análise léxica completa")
    print("  - Análise sintática com gramática completa")
    print("  - Geração de AST (Abstract Syntax Tree)")
    print("  - Tratamento de erros sintáticos")
    
    print("\n✅ GERADOR DE CÓDIGO:")
    print("  - Conversão de .obs para .py")
    print("  - Uso de funções genéricas de functions.py")
    print("  - Preservação de comentários do código original")
    print("  - Suporte a todas as construções da gramática:")
    print("    * Declarações de dispositivos")
    print("    * Comandos de atribuição (set)")
    print("    * Ações simples (ligar/desligar)")
    print("    * Comandos condicionais (se/entao/senao)")
    print("    * Observações complexas com &&")
    print("    * Alertas simples e com parâmetros")
    print("    * Alertas broadcast (para todos)")
    
    print("\n✅ INTEGRAÇÃO:")
    print("  - Interface de linha de comando")
    print("  - Compilação de arquivos .obs")
    print("  - Geração de código Python executável")
    print("  - Uso das funções de functions.py")
    
    print("\n📝 USO:")
    print("  python main.py arquivo.obs [arquivo_saida.py]")
    print("  python main.py  # modo demonstração")

if __name__ == "__main__":
    demo_complete_pipeline()
