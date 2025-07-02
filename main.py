from typing import List, Optional, Union
from ast_nodes import *
from lexer import DeviceLexer
from parser import DeviceParser

# Code Generator
class CodeGenerator:
    """Generates Python code from ObsAct AST"""

    def __init__(self):
        self.output_lines = []
        self.indent_level = 0
        self.devices = set()  
        self.variables = set()  

    def generate(self, ast: Program) -> str:
        """Generate Python code from AST"""
        self.output_lines = []
        self.indent_level = 0
        self.devices = set()
        self.variables = set()

        self.add_line("# Generated Python code from ObsAct program")
        self.add_line("# Generated using SLY-based parser and code generator")
        self.add_line("")
        self.add_line("# Import device control functions")
        self.add_line("from functions import ligar, desligar, alerta, alertavar")
        self.add_line("")

        # Collect device information
        for device in ast.devices:
            self.devices.add(device.name)
            if device.observation:
                self.variables.add(device.observation)

        # Generate main program logic
        self.add_line("# Main program logic")
        self.add_line("def main():")
        self.indent_level += 1

        # Initialize variables from device observations
        self.generate_variable_initializations(ast.devices)

        # Generate commands
        for command in ast.commands:
            self.generate_command(command)

        self.indent_level -= 1
        self.add_line("")
        self.add_line("if __name__ == '__main__':")
        self.add_line("    main()")

        return "\n".join(self.output_lines)

    def add_line(self, line: str = ""):
        """Add a line with proper indentation"""
        if line.strip():
            self.output_lines.append("    " * self.indent_level + line)
        else:
            self.output_lines.append("")



    def generate_variable_initializations(self, devices: List[Device]):
        """Generate variable initializations for device observations"""
        for device in devices:
            if device.observation:
                self.variables.add(device.observation)
                self.add_line(f"# Variable for device {device.name} observation")
                self.add_line(f"{device.observation} = None  # Will be set by program")

        if any(device.observation for device in devices):
            self.add_line("")

    def generate_command(self, command: Command):
        """Generate code for a command"""
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
            self.add_line(f"# Unknown command type: {type(command)}")

    def generate_attribution(self, attr: Attribution):
        """Generate code for attribution (set command)"""
        original_comment = f"# set {attr.observation} = {attr.value}"
        self.add_line(original_comment)
        self.add_line(f"{attr.observation} = {repr(attr.value)}")
        self.add_line("")

    def generate_observation_action(self, obs_act: ObservationAction):
        """Generate code for conditional statements"""
        # Generate condition
        condition_str = self.generate_observation_condition(obs_act.condition)
        original_comment = f"# se {condition_str} entao ..."

        self.add_line(original_comment)
        self.add_line(f"if {condition_str}:")
        self.indent_level += 1

        # Generate then action
        self.generate_action(obs_act.then_action)

        self.indent_level -= 1

        # Generate else action if present
        if obs_act.else_action:
            self.add_line("else:")
            self.indent_level += 1
            self.generate_action(obs_act.else_action)
            self.indent_level -= 1

        self.add_line("")

    def generate_observation_condition(self, obs: Observation) -> str:
        """Generate Python condition from observation"""
        condition = f"{obs.observation} {obs.operator} {repr(obs.value)}"

        if obs.next_obs:
            next_condition = self.generate_observation_condition(obs.next_obs)
            # Convert logical operator to Python equivalent
            python_op = "or" if obs.logical_op == "||" else "and"
            condition += f" {python_op} {next_condition}"

        return condition

    def generate_action(self, action: Action):
        """Generate code for an action"""
        if isinstance(action, SimpleAction):
            self.generate_simple_action(action)
        elif isinstance(action, AlertAction):
            self.generate_alert_action(action)
        elif isinstance(action, BroadcastAlertAction):
            self.generate_broadcast_alert_action(action)
        else:
            self.add_line(f"# Unknown action type: {type(action)}")

    def generate_simple_action(self, action: SimpleAction):
        """Generate code for simple actions (ligar/desligar)"""
        original_comment = f"# {action.action_type} {action.device}"
        self.add_line(original_comment)
        self.add_line(f'{action.action_type}("{action.device}")')

    def generate_alert_action(self, action: AlertAction):
        """Generate code for alert actions"""
        if action.observation:
            original_comment = f'# enviar alerta ("{action.message}", {action.observation}) {action.device}'
            self.add_line(original_comment)
            self.add_line(f'alertavar("{action.device}", "{action.message}", str({action.observation}))')
        else:
            original_comment = f'# enviar alerta ("{action.message}") {action.device}'
            self.add_line(original_comment)
            self.add_line(f'alerta("{action.device}", "{action.message}")')

    def generate_broadcast_alert_action(self, action: BroadcastAlertAction):
        """Generate code for broadcast alert actions"""
        original_comment = f'# enviar alerta ("{action.message}") para todos : {", ".join(action.devices)}'
        self.add_line(original_comment)
        self.add_line("# Broadcast alert to multiple devices")
        for device in action.devices:
            self.add_line(f'alerta("{device}", "{action.message}")')


class ObsActCompiler:
    """Main compiler class that handles .obs to .py conversion"""

    def __init__(self):
        self.processor = DeviceLanguageProcessor()
        self.code_generator = CodeGenerator()

    def compile_file(self, obs_file_path: str, py_file_path: str = None) -> bool:
        """Compile .obs file to .py file"""
        try:
            # Determine output file path
            if py_file_path is None:
                if obs_file_path.endswith('.obs'):
                    py_file_path = obs_file_path[:-4] + '.py'
                else:
                    py_file_path = obs_file_path + '.py'

            # Read input file
            with open(obs_file_path, 'r', encoding='utf-8') as f:
                obs_code = f.read()

            print(f"Reading ObsAct program from: {obs_file_path}")

            # Parse the ObsAct code
            result = self.processor.analyze(obs_code, show_tokens=False, show_ast=False)

            if not result['success']:
                print("Compilation failed due to syntax errors:")
                for error in result['errors']:
                    print(f"  {error}")
                return False

            # Generate Python code
            python_code = self.code_generator.generate(result['ast'])

            # Write output file
            with open(py_file_path, 'w', encoding='utf-8') as f:
                f.write(python_code)

            print(f"Successfully generated Python code: {py_file_path}")
            return True

        except FileNotFoundError:
            print(f"Error: File '{obs_file_path}' not found")
            return False
        except Exception as e:
            print(f"Error during compilation: {str(e)}")
            return False

    def compile_string(self, obs_code: str) -> str:
        """Compile ObsAct code string to Python code string"""
        result = self.processor.analyze(obs_code, show_tokens=False, show_ast=False)

        if not result['success']:
            raise Exception(f"Compilation failed: {result['errors']}")

        return self.code_generator.generate(result['ast'])


# ============================================================================
# Unified Interface for SLY Parser
# ============================================================================

class DeviceLanguageProcessor:
    """Unified interface for lexical analysis and parsing using SLY"""

    def __init__(self, debug_mode: bool = False):
        self.lexer = DeviceLexer()
        self.parser = DeviceParser()
        self.debug_mode = debug_mode

    def tokenize(self, input_text: str) -> list:
        """Tokenize input text and return list of tokens"""
        return list(self.lexer.tokenize(input_text))

    def parse(self, input_text: str) -> Program:
        """Parse input text and return AST"""
        try:
            # Reset parser error state
            self.parser.error_occurred = False
            self.parser.error_message = ""

            tokens = self.lexer.tokenize(input_text)
            result = self.parser.parse(tokens)

            # Check if parsing failed
            if result is None or self.parser.error_occurred:
                error_msg = self.parser.error_message if self.parser.error_message else "Parsing failed: No valid parse tree generated"
                raise Exception(error_msg)

            return result
        except Exception as e:
            raise Exception(f"Parsing failed: {str(e)}")

    def analyze(self, input_text: str, show_tokens: bool = False, show_ast: bool = True) -> dict:
        """Complete analysis: tokenization and parsing"""
        result = {
            'success': False,
            'tokens': [],
            'ast': None,
            'errors': []
        }

        try:
            # Tokenization
            result['tokens'] = self.tokenize(input_text)

            if show_tokens:
                print("=== TOKENS ===")
                for token in result['tokens']:
                    print(f"{token.type:12} | {repr(token.value):20} | Linha: {token.lineno}")
                print()

            # Parsing
            result['ast'] = self.parse(input_text)
            result['success'] = True

            if show_ast and result['ast']:
                print("=== AST ===")
                print(result['ast'].pretty_print())
                print()

        except Exception as e:
            result['errors'].append(str(e))
            if show_ast:
                print(f"=== PARSE ERROR ===")
                print(str(e))
                print()

        return result

def main():
    """Main function with command line interface"""
    import sys
    import os

    if len(sys.argv) > 1:
        # Command line mode - compile .obs file
        obs_file = sys.argv[1]

        if not os.path.exists(obs_file):
            print(f"Error: File '{obs_file}' not found")
            sys.exit(1)

        # Optional output file
        py_file = sys.argv[2] if len(sys.argv) > 2 else None

        compiler = ObsActCompiler()
        success = compiler.compile_file(obs_file, py_file)

        if success:
            print("Compilation completed successfully!")
            sys.exit(0)
        else:
            print("Compilation failed!")
            sys.exit(1)




if __name__ == "__main__":
    main()
