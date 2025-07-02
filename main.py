from typing import List, Optional, Union
from ast_nodes import *
from lexer import DeviceLexer
from parser import DeviceParser

# Gerador de Código
class CodeGenerator:
    """Gera código Python a partir da AST do ObsAct"""

    def __init__(self):
        self.output_lines = []
        self.indent_level = 0
        self.devices = set()
        self.variables = set()

    def generate(self, ast: Program) -> str:
        """Gera código Python a partir da AST"""
        self.output_lines = []
        self.indent_level = 0
        self.devices = set()
        self.variables = set()

        self.add_line("# Código Python gerado a partir do programa ObsAct")
        self.add_line("# Gerado usando parser baseado em SLY e gerador de código")
        self.add_line("")
        self.add_line("# Importa funções de controle de dispositivos")
        self.add_line("from functions import ligar, desligar, alerta, alertavar")
        self.add_line("")

        # Coleta informações dos dispositivos
        for device in ast.devices:
            self.devices.add(device.name)
            if device.observation:
                self.variables.add(device.observation)

        # Gera lógica principal do programa
        self.add_line("# Lógica principal do programa")
        self.add_line("def main():")
        self.indent_level += 1

        # Inicializa variáveis das observações dos dispositivos
        self.generate_variable_initializations(ast.devices)

        # Gera comandos
        for command in ast.commands:
            self.generate_command(command)

        self.indent_level -= 1
        self.add_line("")
        self.add_line("if __name__ == '__main__':")
        self.add_line("    main()")

        return "\n".join(self.output_lines)

    def add_line(self, line: str = ""):
        """Adiciona uma linha com indentação adequada"""
        if line.strip():
            self.output_lines.append("    " * self.indent_level + line)
        else:
            self.output_lines.append("")



    def generate_variable_initializations(self, devices: List[Device]):
        """Gera inicializações de variáveis para observações de dispositivos"""
        for device in devices:
            if device.observation:
                self.variables.add(device.observation)
                self.add_line(f"# Variável para observação do dispositivo {device.name}")
                self.add_line(f"{device.observation} = None  # Será definida pelo programa")

        if any(device.observation for device in devices):
            self.add_line("")

    def generate_command(self, command: Command):
        """Gera código para um comando"""
        if isinstance(command, Attribution):
            self.generate_attribution(command)
        elif isinstance(command, ObservationAction):
            self.generate_observation_action(command)
        elif isinstance(command, SimpleAction):
            self.generate_simple_action(command)
        elif isinstance(command, AlertAction):
            self.generate_alert_action(command)
        elif isinstance(command, BroadcastAlertAction):
            self.generate_broadcast_alert_action(command)
        else:
            self.add_line(f"# Tipo de comando desconhecido: {type(command)}")

    def generate_attribution(self, attr: Attribution):
        """Gera código para atribuição (comando set)"""
        original_comment = f"# set {attr.observation} = {attr.value}"
        self.add_line(original_comment)
        self.add_line(f"{attr.observation} = {repr(attr.value)}")
        self.add_line("")

    def generate_observation_action(self, obs_act: ObservationAction):
        """Gera código para declarações condicionais"""
        # Gera condição
        condition_str = self.generate_observation_condition(obs_act.condition)
        original_comment = f"# se {condition_str} entao ..."

        self.add_line(original_comment)
        self.add_line(f"if {condition_str}:")
        self.indent_level += 1

        # Gera ação then
        self.generate_action(obs_act.then_action)

        self.indent_level -= 1

        # Gera ação else se presente
        if obs_act.else_action:
            self.add_line("else:")
            self.indent_level += 1
            self.generate_action(obs_act.else_action)
            self.indent_level -= 1

        self.add_line("")

    def generate_observation_condition(self, obs: Observation) -> str:
        """Gera condição Python a partir da observação"""
        condition = f"{obs.observation} {obs.operator} {repr(obs.value)}"

        if obs.next_obs:
            next_condition = self.generate_observation_condition(obs.next_obs)
            # Converte operador lógico para equivalente Python
            python_op = "or" if obs.logical_op == "||" else "and"
            condition += f" {python_op} {next_condition}"

        return condition

    def generate_action(self, action: Action):
        """Gera código para uma ação"""
        if isinstance(action, SimpleAction):
            self.generate_simple_action(action)
        elif isinstance(action, AlertAction):
            self.generate_alert_action(action)
        elif isinstance(action, BroadcastAlertAction):
            self.generate_broadcast_alert_action(action)
        else:
            self.add_line(f"# Tipo de ação desconhecido: {type(action)}")

    def generate_simple_action(self, action: SimpleAction):
        """Gera código para ações simples (ligar/desligar)"""
        original_comment = f"# {action.action_type} {action.device}"
        self.add_line(original_comment)
        self.add_line(f'{action.action_type}("{action.device}")')

    def generate_alert_action(self, action: AlertAction):
        """Gera código para ações de alerta"""
        if action.observation:
            original_comment = f'# enviar alerta ("{action.message}", {action.observation}) {action.device}'
            self.add_line(original_comment)
            self.add_line(f'alertavar("{action.device}", "{action.message}", str({action.observation}))')
        else:
            original_comment = f'# enviar alerta ("{action.message}") {action.device}'
            self.add_line(original_comment)
            self.add_line(f'alerta("{action.device}", "{action.message}")')

    def generate_broadcast_alert_action(self, action: BroadcastAlertAction):
        """Gera código para ações de alerta broadcast"""
        original_comment = f'# enviar alerta ("{action.message}") para todos : {", ".join(action.devices)}'
        self.add_line(original_comment)
        self.add_line("# Alerta broadcast para múltiplos dispositivos")
        for device in action.devices:
            self.add_line(f'alerta("{device}", "{action.message}")')


class ObsActCompiler:
    """Classe principal do compilador que gerencia conversão de .obs para .py"""

    def __init__(self):
        self.processor = DeviceLanguageProcessor()
        self.code_generator = CodeGenerator()

    def compile_file(self, obs_file_path: str, py_file_path: str = None) -> bool:
        """Compila arquivo .obs para arquivo .py"""
        try:
            # Determina caminho do arquivo de saída
            if py_file_path is None:
                if obs_file_path.endswith('.obs'):
                    py_file_path = obs_file_path[:-4] + '.py'
                else:
                    py_file_path = obs_file_path + '.py'

            # Lê arquivo de entrada
            with open(obs_file_path, 'r', encoding='utf-8') as f:
                obs_code = f.read()

            print(f"Lendo programa ObsAct de: {obs_file_path}")

            # Analisa o código ObsAct
            result = self.processor.analyze(obs_code, show_tokens=False, show_ast=False)

            if not result['success']:
                print("Compilação falhou devido a erros de sintaxe:")
                for error in result['errors']:
                    print(f"  {error}")
                return False

            # Gera código Python
            python_code = self.code_generator.generate(result['ast'])

            # Escreve arquivo de saída
            with open(py_file_path, 'w', encoding='utf-8') as f:
                f.write(python_code)

            print(f"Código Python gerado com sucesso: {py_file_path}")
            return True

        except FileNotFoundError:
            print(f"Erro: Arquivo '{obs_file_path}' não encontrado")
            return False
        except Exception as e:
            print(f"Erro durante compilação: {str(e)}")
            return False

    def compile_string(self, obs_code: str) -> str:
        """Compila string de código ObsAct para string de código Python"""
        result = self.processor.analyze(obs_code, show_tokens=False, show_ast=False)

        if not result['success']:
            raise Exception(f"Compilação falhou: {result['errors']}")

        return self.code_generator.generate(result['ast'])


# ============================================================================
# Interface Unificada para Parser SLY
# ============================================================================

class DeviceLanguageProcessor:
    """Interface unificada para análise léxica e sintática usando SLY"""

    def __init__(self, debug_mode: bool = False):
        self.lexer = DeviceLexer()
        self.parser = DeviceParser()
        self.debug_mode = debug_mode

    def tokenize(self, input_text: str) -> list:
        """Tokeniza texto de entrada e retorna lista de tokens"""
        return list(self.lexer.tokenize(input_text))

    def parse(self, input_text: str) -> Program:
        """Analisa texto de entrada e retorna AST"""
        try:
            # Reseta estado de erro do parser
            self.parser.error_occurred = False
            self.parser.error_message = ""

            tokens = self.lexer.tokenize(input_text)
            result = self.parser.parse(tokens)

            # Verifica se a análise falhou
            if result is None or self.parser.error_occurred:
                error_msg = self.parser.error_message if self.parser.error_message else "Análise falhou: Nenhuma árvore de análise válida gerada"
                raise Exception(error_msg)

            return result
        except Exception as e:
            raise Exception(f"Análise falhou: {str(e)}")

    def analyze(self, input_text: str, show_tokens: bool = False, show_ast: bool = True) -> dict:
        """Análise completa: tokenização e análise sintática"""
        result = {
            'success': False,
            'tokens': [],
            'ast': None,
            'errors': []
        }

        try:
            # Tokenização
            result['tokens'] = self.tokenize(input_text)

            if show_tokens:
                print("=== TOKENS ===")
                for token in result['tokens']:
                    print(f"{token.type:12} | {repr(token.value):20} | Linha: {token.lineno}")
                print()

            # Análise sintática
            result['ast'] = self.parse(input_text)
            result['success'] = True

            if show_ast and result['ast']:
                print("=== AST ===")
                print(result['ast'].pretty_print())
                print()

        except Exception as e:
            result['errors'].append(str(e))
            if show_ast:
                print(f"=== ERRO DE ANÁLISE ===")
                print(str(e))
                print()

        return result

def main():
    """Função principal com interface de linha de comando"""
    import sys
    import os

    if len(sys.argv) > 1:
        # Modo linha de comando - compila arquivo .obs
        obs_file = sys.argv[1]

        if not os.path.exists(obs_file):
            print(f"Erro: Arquivo '{obs_file}' não encontrado")
            sys.exit(1)

        # Arquivo de saída opcional
        py_file = sys.argv[2] if len(sys.argv) > 2 else None

        compiler = ObsActCompiler()
        success = compiler.compile_file(obs_file, py_file)

        if success:
            print("Compilação concluída com sucesso!")
            sys.exit(0)
        else:
            print("Compilação falhou!")
            sys.exit(1)




if __name__ == "__main__":
    main()
