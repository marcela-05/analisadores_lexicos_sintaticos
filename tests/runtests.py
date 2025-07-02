import os
import sys

# Adiciona o diretório pai ao path para importar o módulo main
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from main import ObsActCompiler

def run_test(file_path):
    compiler = ObsActCompiler()
    print("=" * 70)
    print(f"Testando: {file_path}")
    print("-" * 70)
    try:
        with open(file_path, "r") as f:
            content = f.read()
        output = compiler.compile_string(content)
        print("Código gerado:\n")
        print(output)
    except Exception as e:
        print(f"Erro durante compilação: {e}")

if __name__ == "__main__":
    pasta_tests = "tests"
    for arquivo in sorted(os.listdir(pasta_tests)):
        if arquivo.endswith(".obs"):
            run_test(os.path.join(pasta_tests, arquivo))
