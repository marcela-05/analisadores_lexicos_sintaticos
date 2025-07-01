from sly import Lexer, Parser
from typing import List, Optional, Union

# SLY Parser decorator function
def _(rule):
    """Decorator for SLY parser rules"""
    def decorator(func):
        func._grammar = (rule,) if isinstance(rule, str) else rule
        return func
    return decorator

class DeviceLexer(Lexer):
    ignore = " \t\r"
    literals = { }

    tokens = {
        'DISPOSITIVO', 'SET', 'SE', 'ENTAO', 'SENAO', 'ENVIAR', 'ALERTA',
        'PARA', 'TODOS', 'LIGAR', 'DESLIGAR',
        'OPLOGIC', 'AND',
        'DOIS_PONTOS', 'PONTO', 'VIRGULA', 'IGUAL',
        'ABRE_CHAVE', 'FECHA_CHAVE', 'ABRE_PAREN', 'FECHA_PAREN',
        'NAMEDEVICE', 'OBSERVATION', 'NUM', 'BOOL', 'MSG'
    }

    # Palavras-chave
    DISPOSITIVO = r'dispositivo\b'
    SET         = r'set\b'
    SE          = r'se\b'
    ENTAO       = r'entao\b'
    SENAO       = r'senao\b'
    ENVIAR      = r'enviar\b'
    ALERTA      = r'alerta\b'
    PARA        = r'para\b'
    TODOS       = r'todos\b'
    LIGAR       = r'ligar\b'
    DESLIGAR    = r'desligar\b'

    # Operadores
    AND     = r'&&'
    OPLOGIC = r'(==|!=|<=|>=|<|>)'

    # Símbolos
    DOIS_PONTOS  = r':'
    PONTO        = r'\.'
    VIRGULA      = r','
    IGUAL        = r'='
    ABRE_CHAVE   = r'\{'
    FECHA_CHAVE  = r'\}'
    ABRE_PAREN   = r'\('
    FECHA_PAREN  = r'\)'

    # Literais
    NUM = r'\d+'

    def NUM(self, t):
        t.value = int(t.value)
        return t

    BOOL = r'(true|false)'

    def BOOL(self, t):
        t.value = t.value == 'true'
        return t

    MSG = r'"[^"]*"'

    def MSG(self, t):
        t.value = t.value[1:-1]  # Remove aspas
        return t

    # observation: começa com letra, pode ter letras, números e _ (mais geral primeiro)
    OBSERVATION = r'[a-zA-Z][a-zA-Z0-9_]*'

    def OBSERVATION(self, t):
        keywords = {
            'dispositivo', 'set', 'se', 'entao', 'senao', 'enviar',
            'alerta', 'para', 'todos', 'ligar', 'desligar', 'true', 'false'
        }
        if t.value in keywords:
            t.type = t.value.upper()
        return t

    # nameDevice: só letras (mais restritivo)
    NAMEDEVICE = r'[a-zA-Z]+'

    def NAMEDEVICE(self, t):
        keywords = {
            'dispositivo', 'set', 'se', 'entao', 'senao', 'enviar',
            'alerta', 'para', 'todos', 'ligar', 'desligar', 'true', 'false'
        }
        if t.value in keywords:
            t.type = t.value.upper()
        return t

    ignore_newline = r'\n+'

    def ignore_newline(self, t):
        self.lineno += len(t.value)

    def error(self, t):
        print(f"Erro léxico: caractere ilegal '{t.value[0]}' na linha {self.lineno}")
        self.index += 1


# ============================================================================
# AST Node Classes (Simplified for SLY Parser)
# ============================================================================

class ASTNode:
    """Base class for all AST nodes"""

    def __init__(self, line_number: int = 0):
        self.line_number = line_number

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

    def pretty_print(self, indent: int = 0) -> str:
        """Pretty print the AST with indentation"""
        return "  " * indent + str(self)


class Program(ASTNode):
    """Root node representing the entire program"""

    def __init__(self, devices: List['Device'], commands: List['Command'], line_number: int = 0):
        super().__init__(line_number)
        self.devices = devices
        self.commands = commands

    def __str__(self) -> str:
        return f"Program(devices={len(self.devices)}, commands={len(self.commands)})"

    def pretty_print(self, indent: int = 0) -> str:
        result = "  " * indent + "Program:\n"
        result += "  " * (indent + 1) + "Devices:\n"
        for device in self.devices:
            result += device.pretty_print(indent + 2) + "\n"
        result += "  " * (indent + 1) + "Commands:\n"
        for command in self.commands:
            result += command.pretty_print(indent + 2) + "\n"
        return result.rstrip()


class Device(ASTNode):
    """Node representing a device declaration"""

    def __init__(self, name: str, observation: Optional[str] = None, line_number: int = 0):
        super().__init__(line_number)
        self.name = name
        self.observation = observation

    def __str__(self) -> str:
        if self.observation:
            return f"Device({self.name}, {self.observation})"
        return f"Device({self.name})"

    def pretty_print(self, indent: int = 0) -> str:
        base = "  " * indent + f"Device: {self.name}"
        if self.observation:
            base += f" (observation: {self.observation})"
        return base


class Command(ASTNode):
    """Base class for commands"""
    pass


class Attribution(Command):
    """Node representing attribution"""

    def __init__(self, observation: str, value: Union[int, bool], line_number: int = 0):
        super().__init__(line_number)
        self.observation = observation
        self.value = value

    def __str__(self) -> str:
        return f"Attribution({self.observation} = {self.value})"

    def pretty_print(self, indent: int = 0) -> str:
        return "  " * indent + f"Set: {self.observation} = {self.value}"


class ObservationAction(Command):
    """Node representing conditional"""

    def __init__(self, condition: 'Observation', then_action: 'Action',
                 else_action: Optional['Action'] = None, line_number: int = 0):
        super().__init__(line_number)
        self.condition = condition
        self.then_action = then_action
        self.else_action = else_action

    def __str__(self) -> str:
        if self.else_action:
            return f"If({self.condition}) Then({self.then_action}) Else({self.else_action})"
        return f"If({self.condition}) Then({self.then_action})"

    def pretty_print(self, indent: int = 0) -> str:
        result = "  " * indent + f"If: {self.condition}\n"
        result += "  " * (indent + 1) + f"Then: {self.then_action}"
        if self.else_action:
            result += "\n" + "  " * (indent + 1) + f"Else: {self.else_action}"
        return result


class Observation(ASTNode):
    """Node representing observation"""

    def __init__(self, observation: str, operator: str, value: Union[int, bool],
                 next_obs: Optional['Observation'] = None, line_number: int = 0):
        super().__init__(line_number)
        self.observation = observation
        self.operator = operator
        self.value = value
        self.next_obs = next_obs

    def __str__(self) -> str:
        result = f"{self.observation} {self.operator} {self.value}"
        if self.next_obs:
            result += f" && {self.next_obs}"
        return result


class Action(ASTNode):
    """Base class for actions"""
    pass


class SimpleAction(Action):
    """Node representing simple action"""

    def __init__(self, action_type: str, device: str, line_number: int = 0):
        super().__init__(line_number)
        self.action_type = action_type
        self.device = device

    def __str__(self) -> str:
        return f"{self.action_type} {self.device}"


class AlertAction(Action):
    """Node representing alert action"""

    def __init__(self, message: str, device: str, observation: Optional[str] = None, line_number: int = 0):
        super().__init__(line_number)
        self.message = message
        self.device = device
        self.observation = observation

    def __str__(self) -> str:
        if self.observation:
            return f"enviar alerta ({self.message}, {self.observation}) {self.device}"
        return f"enviar alerta ({self.message}) {self.device}"


class BroadcastAlertAction(Action):
    """Node representing broadcast alert"""

    def __init__(self, message: str, devices: List[str], line_number: int = 0):
        super().__init__(line_number)
        self.message = message
        self.devices = devices

    def __str__(self) -> str:
        return f"enviar alerta ({self.message}) para todos : {', '.join(self.devices)}"


# ============================================================================
# SLY Parser Implementation
# ============================================================================

class DeviceParser(Parser):
    """SLY-based parser for the device grammar"""

    debugfile = "parser.out"
    tokens = DeviceLexer.tokens

    def __init__(self):
        super().__init__()
        self.error_occurred = False
        self.error_message = ""

    def error(self, p):
        self.error_occurred = True
        if p:
            self.error_message = f"Erro sintático na linha {p.lineno}: token inesperado '{p.value}' ({p.type})"
            print(self.error_message)
        else:
            self.error_message = "Erro sintático: fim de arquivo inesperado"
            print(self.error_message)

    # PROGRAM → DEVICES CMDS
    @_('devices commands')
    def program(self, p):
        return Program(p.devices, p.commands)

    # DEVICES → DEVICE DEVICES | DEVICE
    @_('device devices')
    def devices(self, p):
        return [p.device] + p.devices

    @_('device')
    def devices(self, p):
        return [p.device]

    # DEVICE → dispositivo : namedevice | dispositivo : namedevice, observation
    @_('DISPOSITIVO DOIS_PONTOS device_name')
    def device(self, p):
        return Device(p.device_name, line_number=p.lineno)

    @_('DISPOSITIVO DOIS_PONTOS device_name VIRGULA OBSERVATION')
    def device(self, p):
        return Device(p.device_name, p.OBSERVATION, line_number=p.lineno)

    # Helper rule for device names (can be NAMEDEVICE or OBSERVATION)
    @_('NAMEDEVICE')
    def device_name(self, p):
        return p.NAMEDEVICE

    @_('OBSERVATION')
    def device_name(self, p):
        return p.OBSERVATION

    # CMDS → CMD. CMDS | CMD.
    @_('command PONTO commands')
    def commands(self, p):
        return [p.command] + p.commands

    @_('command PONTO')
    def commands(self, p):
        return [p.command]

    # CMD → ATTRIB | OBSACT | ACT
    @_('attribution')
    def command(self, p):
        return p.attribution

    @_('observation_action')
    def command(self, p):
        return p.observation_action

    @_('action')
    def command(self, p):
        return p.action

    # ATTRIB → set observation = VAR
    @_('SET OBSERVATION IGUAL variable')
    def attribution(self, p):
        return Attribution(p.OBSERVATION, p.variable, line_number=p.lineno)

    # VAR → num | bool
    @_('NUM')
    def variable(self, p):
        return p.NUM

    @_('BOOL')
    def variable(self, p):
        return p.BOOL

    # OBSACT → se OBS entao ACT | se OBS entao ACT senao ACT
    @_('SE observation ENTAO action')
    def observation_action(self, p):
        return ObservationAction(p.observation, p.action, line_number=p.lineno)

    @_('SE observation ENTAO action SENAO action')
    def observation_action(self, p):
        return ObservationAction(p.observation, p.action0, p.action1, line_number=p.lineno)

    # OBS → observation oplogic VAR | observation oplogic VAR && OBS
    @_('OBSERVATION OPLOGIC variable')
    def observation(self, p):
        return Observation(p.OBSERVATION, p.OPLOGIC, p.variable, line_number=p.lineno)

    @_('OBSERVATION OPLOGIC variable AND observation')
    def observation(self, p):
        return Observation(p.OBSERVATION, p.OPLOGIC, p.variable, p.observation, line_number=p.lineno)

    # ACT → ACTION namedevice | enviar alerta (msg) namedevice | enviar alerta (msg, observation) namedevice | enviar alerta (msg) para todos : DEVICE_LIST
    # Note: Order matters in SLY - more specific rules should come first

    @_('ENVIAR ALERTA ABRE_PAREN MSG VIRGULA OBSERVATION FECHA_PAREN PARA TODOS DOIS_PONTOS device_list')
    def action(self, p):
        # This handles: enviar alerta (msg, observation) para todos : device_list
        return BroadcastAlertAction(p.MSG, p.device_list, line_number=p.lineno)

    @_('ENVIAR ALERTA ABRE_PAREN MSG FECHA_PAREN PARA TODOS DOIS_PONTOS device_list')
    def action(self, p):
        return BroadcastAlertAction(p.MSG, p.device_list, line_number=p.lineno)

    @_('ENVIAR ALERTA ABRE_PAREN MSG VIRGULA OBSERVATION FECHA_PAREN device_name')
    def action(self, p):
        return AlertAction(p.MSG, p.device_name, p.OBSERVATION, line_number=p.lineno)

    @_('ENVIAR ALERTA ABRE_PAREN MSG FECHA_PAREN device_name')
    def action(self, p):
        return AlertAction(p.MSG, p.device_name, line_number=p.lineno)

    @_('action_type device_name')
    def action(self, p):
        return SimpleAction(p.action_type, p.device_name, line_number=p.lineno)

    # ACTION → ligar | desligar
    @_('LIGAR')
    def action_type(self, p):
        return p.LIGAR

    @_('DESLIGAR')
    def action_type(self, p):
        return p.DESLIGAR

    # DEVICE_LIST → namedevice, DEVICE_LIST | namedevice
    @_('device_name VIRGULA device_list')
    def device_list(self, p):
        return [p.device_name] + p.device_list

    @_('device_name')
    def device_list(self, p):
        return [p.device_name]


# ============================================================================
# Code Generator
# ============================================================================

class CodeGenerator:
    """Generates Python code from ObsAct AST"""

    def __init__(self):
        self.output_lines = []
        self.indent_level = 0
        self.devices = set()  # Track declared devices
        self.variables = set()  # Track declared variables

    def generate(self, ast: Program) -> str:
        """Generate Python code from AST"""
        self.output_lines = []
        self.indent_level = 0
        self.devices = set()
        self.variables = set()

        # Add header comment and imports
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
            condition += f" and {next_condition}"

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


# ============================================================================
# Command Line Interface and Examples
# ============================================================================

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

    else:
        # Demo mode - show examples
        demo_parser_and_generator()


def demo_parser_and_generator():
    """Demonstrate both parser and code generator"""
    compiler = ObsActCompiler()

    print("=" * 70)
    print("DEMONSTRAÇÃO DO PARSER E GERADOR DE CÓDIGO SLY")
    print("=" * 70)

    # Example 1: Simple program
    print("\n1. PROGRAMA SIMPLES")
    print("-" * 50)

    codigo_exemplo1 = '''dispositivo : sensor1, temp
dispositivo : led1

set temp = 25.
se temp > 30 entao ligar led1.
enviar alerta ("Sistema iniciado") sensor1.'''

    print("Código ObsAct:")
    print(codigo_exemplo1)
    print("\nCódigo Python gerado:")
    try:
        python_code1 = compiler.compile_string(codigo_exemplo1)
        print(python_code1)
    except Exception as e:
        print(f"Erro: {e}")

    # Example 2: Complex program with conditionals
    print("\n" + "=" * 70)
    print("2. PROGRAMA COMPLEXO COM CONDICIONAIS")
    print("-" * 50)

    codigo_exemplo2 = '''dispositivo : tempSensor, temperature
dispositivo : humSensor, humidity
dispositivo : redLED
dispositivo : greenLED
dispositivo : buzzer

set temperature = 22.
set humidity = 45.

se temperature > 35 entao enviar alerta ("Temperatura crítica", temperature) para todos : redLED, buzzer.
se temperature >= 25 && temperature <= 35 entao ligar redLED senao desligar redLED.
se humidity < 30 entao enviar alerta ("Umidade baixa") humSensor.'''

    print("Código ObsAct:")
    print(codigo_exemplo2)
    print("\nCódigo Python gerado:")
    try:
        python_code2 = compiler.compile_string(codigo_exemplo2)
        print(python_code2)
    except Exception as e:
        print(f"Erro: {e}")

    # Example 3: Error handling
    print("\n" + "=" * 70)
    print("3. TRATAMENTO DE ERROS")
    print("-" * 50)

    codigo_exemplo3 = '''dispositivo : sensor1
set temp = 25
se temp > 30 entao ligar led1.'''

    print("Código ObsAct com erro (falta ponto):")
    print(codigo_exemplo3)
    print("\nResultado:")
    try:
        python_code3 = compiler.compile_string(codigo_exemplo3)
        print(python_code3)
    except Exception as e:
        print(f"Erro de compilação: {e}")

    print("\n" + "=" * 70)
    print("INSTRUÇÕES DE USO")
    print("=" * 70)
    print("Para compilar um arquivo .obs:")
    print("  python main.py arquivo.obs [arquivo_saida.py]")
    print("")
    print("Exemplo:")
    print("  python main.py programa.obs")
    print("  python main.py programa.obs meu_programa.py")


if __name__ == "__main__":
    main()
