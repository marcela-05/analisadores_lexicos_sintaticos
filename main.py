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
# Example Usage and Testing
# ============================================================================

if __name__ == "__main__":
    processor = DeviceLanguageProcessor()

    # Example 1: Valid program
    print("=" * 60)
    print("EXEMPLO 1: Programa válido")
    print("=" * 60)

    codigo_exemplo1 = '''
    dispositivo : sensorTemp
    dispositivo : ledVermelho, temperatura2

    set temperatura2 = 25.

    se temperatura2 > 30 entao ligar ledVermelho.
    se temperatura2 < 10 && temperatura2 > 0 entao enviar alerta ("Temperatura baixa") sensorTemp.
    '''

    result1 = processor.analyze(codigo_exemplo1, show_tokens=True, show_ast=True)

    # Example 2: Program with syntax error
    print("\n" + "=" * 60)
    print("EXEMPLO 2: Programa com erro sintático")
    print("=" * 60)

    codigo_exemplo2 = '''
    dispositivo : sensor1

    set temperatura = 25
    se temperatura > 30 entao ligar led.
    '''

    result2 = processor.analyze(codigo_exemplo2, show_tokens=False, show_ast=True)

    # Example 3: Complex valid program
    print("\n" + "=" * 60)
    print("EXEMPLO 3: Programa complexo válido")
    print("=" * 60)

    codigo_exemplo3 = '''
    dispositivo : sensor1, temp
    dispositivo : led1
    dispositivo : led2
    dispositivo : buzzer

    set temp = 20.

    se temp > 25 && temp < 35 entao ligar led1.
    se temp >= 35 entao enviar alerta ("Temperatura alta", temp) para todos : led1, led2, buzzer.
    se temp < 10 entao desligar led1 senao ligar led2.
    '''

    result3 = processor.analyze(codigo_exemplo3, show_tokens=False, show_ast=True)
