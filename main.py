from sly import Lexer
from abc import ABC, abstractmethod
from typing import List, Optional, Union

class DeviceLexer(Lexer):
    ignore = " \t"
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

    # observation: começa com letra, pode ter letras, números e _
    OBSERVATION = r'[a-zA-Z][a-zA-Z0-9_]*'

    def OBSERVATION(self, t):
        keywords = {
            'dispositivo', 'set', 'se', 'entao', 'senao', 'enviar',
            'alerta', 'para', 'todos', 'ligar', 'desligar', 'true', 'false'
        }
        if t.value in keywords:
            t.type = t.value.upper()
        return t

    # nameDevice: só letras (mais restritivo que OBSERVATION)
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
# AST Node Classes
# ============================================================================

class ASTNode(ABC):
    """Base class for all AST nodes"""

    def __init__(self, line_number: int = 0):
        self.line_number = line_number

    @abstractmethod
    def __str__(self) -> str:
        pass

    def pretty_print(self, indent: int = 0) -> str:
        """Pretty print the AST with indentation"""
        return "  " * indent + str(self)


class Program(ASTNode):
    """Root node representing the entire program: PROGRAM → DEVICES CMDS"""

    def __init__(self, devices: 'DeviceList', commands: 'CommandList', line_number: int = 0):
        super().__init__(line_number)
        self.devices = devices
        self.commands = commands

    def __str__(self) -> str:
        return f"Program(devices={len(self.devices.devices)}, commands={len(self.commands.commands)})"

    def pretty_print(self, indent: int = 0) -> str:
        result = "  " * indent + "Program:\n"
        result += self.devices.pretty_print(indent + 1) + "\n"
        result += self.commands.pretty_print(indent + 1)
        return result


class DeviceList(ASTNode):
    """Node representing device declarations: DEVICES → DEVICE DEVICES | DEVICE"""

    def __init__(self, devices: List['Device'], line_number: int = 0):
        super().__init__(line_number)
        self.devices = devices

    def __str__(self) -> str:
        return f"DeviceList({len(self.devices)} devices)"

    def pretty_print(self, indent: int = 0) -> str:
        result = "  " * indent + "Devices:\n"
        for device in self.devices:
            result += device.pretty_print(indent + 1) + "\n"
        return result.rstrip()


class Device(ASTNode):
    """Node representing a device declaration: DEVICE → dispositivo : namedevice | dispositivo : namedevice, observation"""

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


class CommandList(ASTNode):
    """Node representing command list: CMDS → CMD. CMDS | CMD."""

    def __init__(self, commands: List['Command'], line_number: int = 0):
        super().__init__(line_number)
        self.commands = commands

    def __str__(self) -> str:
        return f"CommandList({len(self.commands)} commands)"

    def pretty_print(self, indent: int = 0) -> str:
        result = "  " * indent + "Commands:\n"
        for command in self.commands:
            result += command.pretty_print(indent + 1) + "\n"
        return result.rstrip()


class Command(ASTNode):
    """Base class for commands: CMD → ATTRIB | OBSACT | ACT"""
    pass


class Attribution(Command):
    """Node representing attribution: ATTRIB → set observation = VAR"""

    def __init__(self, observation: str, value: 'Variable', line_number: int = 0):
        super().__init__(line_number)
        self.observation = observation
        self.value = value

    def __str__(self) -> str:
        return f"Attribution({self.observation} = {self.value})"

    def pretty_print(self, indent: int = 0) -> str:
        return "  " * indent + f"Set: {self.observation} = {self.value}"


class ObservationAction(Command):
    """Node representing conditional: OBSACT → se OBS entao ACT | se OBS entao ACT senao ACT"""

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
    """Node representing observation: OBS → observation oplogic VAR | observation oplogic VAR && OBS"""

    def __init__(self, observation: str, operator: str, value: 'Variable',
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

    def pretty_print(self, indent: int = 0) -> str:
        result = "  " * indent + f"Observation: {self.observation} {self.operator} {self.value}"
        if self.next_obs:
            result += "\n" + "  " * indent + "AND\n" + self.next_obs.pretty_print(indent)
        return result


class Variable(ASTNode):
    """Node representing variable: VAR → num | bool"""

    def __init__(self, value: Union[int, bool], line_number: int = 0):
        super().__init__(line_number)
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def pretty_print(self, indent: int = 0) -> str:
        return "  " * indent + f"Value: {self.value}"


class Action(ASTNode):
    """Base class for actions: ACT → ACTION namedevice | enviar alerta (...) namedevice | enviar alerta (...) para todos : DEVICE_LIST"""
    pass


class SimpleAction(Action):
    """Node representing simple action: ACTION namedevice"""

    def __init__(self, action_type: str, device: str, line_number: int = 0):
        super().__init__(line_number)
        self.action_type = action_type  # 'ligar' or 'desligar'
        self.device = device

    def __str__(self) -> str:
        return f"{self.action_type} {self.device}"

    def pretty_print(self, indent: int = 0) -> str:
        return "  " * indent + f"Action: {self.action_type} {self.device}"


class AlertAction(Action):
    """Node representing alert action: enviar alerta (msg) namedevice | enviar alerta (msg, observation) namedevice"""

    def __init__(self, message: str, device: str, observation: Optional[str] = None, line_number: int = 0):
        super().__init__(line_number)
        self.message = message
        self.device = device
        self.observation = observation

    def __str__(self) -> str:
        if self.observation:
            return f"enviar alerta ({self.message}, {self.observation}) {self.device}"
        return f"enviar alerta ({self.message}) {self.device}"

    def pretty_print(self, indent: int = 0) -> str:
        result = "  " * indent + f"Alert: '{self.message}' to {self.device}"
        if self.observation:
            result += f" (observation: {self.observation})"
        return result


class BroadcastAlertAction(Action):
    """Node representing broadcast alert: enviar alerta (msg) para todos : DEVICE_LIST"""

    def __init__(self, message: str, devices: 'DeviceNameList', line_number: int = 0):
        super().__init__(line_number)
        self.message = message
        self.devices = devices

    def __str__(self) -> str:
        return f"enviar alerta ({self.message}) para todos : {self.devices}"

    def pretty_print(self, indent: int = 0) -> str:
        result = "  " * indent + f"Broadcast Alert: '{self.message}' to all:\n"
        result += self.devices.pretty_print(indent + 1)
        return result


class DeviceNameList(ASTNode):
    """Node representing device name list: DEVICE_LIST → namedevice, DEVICE_LIST | namedevice"""

    def __init__(self, devices: List[str], line_number: int = 0):
        super().__init__(line_number)
        self.devices = devices

    def __str__(self) -> str:
        return ", ".join(self.devices)

    def pretty_print(self, indent: int = 0) -> str:
        result = "  " * indent + "Device List:\n"
        for device in self.devices:
            result += "  " * (indent + 1) + f"- {device}\n"
        return result.rstrip()


# ============================================================================
# Parser Class
# ============================================================================

class ParseError(Exception):
    """Exception raised for parsing errors"""

    def __init__(self, message: str, line_number: int = 0, token: str = ""):
        super().__init__(message)
        self.line_number = line_number
        self.token = token
        self.message = message

    def __str__(self) -> str:
        if self.line_number > 0:
            return f"Erro sintático na linha {self.line_number}: {self.message}"
        return f"Erro sintático: {self.message}"


class DeviceParser:
    """Recursive descent parser for the device grammar"""

    def __init__(self, lexer: DeviceLexer):
        self.lexer = lexer
        self.tokens = []
        self.current_token_index = 0
        self.current_token = None
        self.errors = []  # Collect all errors for better reporting
        self.panic_mode = False  # For error recovery

    def parse(self, input_text: str) -> Program:
        """Parse the input text and return the AST"""
        # Reset parser state
        self.errors = []
        self.panic_mode = False

        # Tokenize the input
        self.tokens = list(self.lexer.tokenize(input_text))
        self.current_token_index = 0
        self.current_token = self.tokens[0] if self.tokens else None

        if not self.tokens:
            raise ParseError("Empty input - no tokens found")

        # Parse the program
        try:
            program = self.parse_program()
            if self.current_token is not None:
                self.add_error(f"Unexpected token '{self.current_token.value}' after end of program")

            # If we collected errors during parsing, report them
            if self.errors:
                error_msg = "Parsing completed with errors:\n" + "\n".join(self.errors)
                raise ParseError(error_msg)

            return program
        except IndexError:
            raise ParseError("Unexpected end of input")
        except ParseError as e:
            # Add any final error to the list
            if str(e) not in self.errors:
                self.errors.append(str(e))
            error_msg = "Parsing failed:\n" + "\n".join(self.errors)
            raise ParseError(error_msg)

    def add_error(self, message: str, line_number: int = None):
        """Add an error to the error list"""
        if line_number is None and self.current_token:
            line_number = self.current_token.lineno

        if line_number:
            error_msg = f"Linha {line_number}: {message}"
        else:
            error_msg = message

        if error_msg not in self.errors:
            self.errors.append(error_msg)

    def synchronize(self):
        """Synchronize parser after an error by finding a safe point to continue"""
        self.panic_mode = False

        # Skip tokens until we find a synchronization point
        sync_tokens = {'DISPOSITIVO', 'SET', 'SE', 'LIGAR', 'DESLIGAR', 'ENVIAR'}

        while self.current_token and self.current_token.type not in sync_tokens:
            self.current_token_index += 1
            self.current_token = self.tokens[self.current_token_index] if self.current_token_index < len(self.tokens) else None

    def peek_token(self, offset: int = 0) -> Optional[object]:
        """Look ahead at tokens without consuming them"""
        index = self.current_token_index + offset
        if index < len(self.tokens):
            return self.tokens[index]
        return None

    def consume_token(self, expected_type: str = None) -> object:
        """Consume the current token and advance to the next"""
        if self.current_token is None:
            if expected_type:
                raise ParseError(f"Expected '{expected_type}' but reached end of input")
            else:
                raise ParseError("Unexpected end of input")

        if expected_type and self.current_token.type != expected_type:
            error_msg = f"Expected '{expected_type}' but found '{self.current_token.type}' ('{self.current_token.value}')"

            # Provide helpful suggestions based on context
            if expected_type == 'PONTO':
                error_msg += ". Commands must end with a period (.)"
            elif expected_type == 'DOIS_PONTOS':
                error_msg += ". Device declarations require a colon (:)"
            elif expected_type == 'IGUAL':
                error_msg += ". Assignments require an equals sign (=)"

            raise ParseError(error_msg, self.current_token.lineno, str(self.current_token.value))

        token = self.current_token
        self.current_token_index += 1
        self.current_token = self.tokens[self.current_token_index] if self.current_token_index < len(self.tokens) else None
        return token

    def match_token(self, token_type: str) -> bool:
        """Check if current token matches the given type"""
        return self.current_token is not None and self.current_token.type == token_type

    def parse_program(self) -> Program:
        """Parse PROGRAM → DEVICES CMDS"""
        devices = self.parse_devices()
        commands = self.parse_commands()
        return Program(devices, commands)

    def parse_devices(self) -> DeviceList:
        """Parse DEVICES → DEVICE DEVICES | DEVICE"""
        devices = []

        # Parse first device
        if not self.match_token('DISPOSITIVO'):
            raise ParseError("Expected 'dispositivo' at start of program",
                           self.current_token.lineno if self.current_token else 0)

        devices.append(self.parse_device())

        # Parse additional devices
        while self.match_token('DISPOSITIVO'):
            devices.append(self.parse_device())

        return DeviceList(devices)

    def parse_device(self) -> Device:
        """Parse DEVICE → dispositivo : namedevice | dispositivo : namedevice, observation"""
        line_number = self.current_token.lineno if self.current_token else 0

        self.consume_token('DISPOSITIVO')
        self.consume_token('DOIS_PONTOS')

        # Accept either NAMEDEVICE or OBSERVATION for device names
        if self.match_token('NAMEDEVICE'):
            name_token = self.consume_token('NAMEDEVICE')
        elif self.match_token('OBSERVATION'):
            name_token = self.consume_token('OBSERVATION')
        else:
            raise ParseError(f"Expected device name but found '{self.current_token.value}'",
                           self.current_token.lineno, str(self.current_token.value))

        name = name_token.value

        observation = None
        if self.match_token('VIRGULA'):
            self.consume_token('VIRGULA')
            obs_token = self.consume_token('OBSERVATION')
            observation = obs_token.value

        return Device(name, observation, line_number)

    def parse_commands(self) -> CommandList:
        """Parse CMDS → CMD. CMDS | CMD."""
        commands = []

        while self.current_token and self.match_token_for_command():
            try:
                command = self.parse_command()
                self.consume_token('PONTO')  # Commands end with '.'
                commands.append(command)
                self.panic_mode = False  # Reset panic mode on successful parse
            except ParseError as e:
                self.add_error(str(e))
                self.panic_mode = True
                self.synchronize()
                # Try to continue parsing after synchronization
                continue

        if not commands:
            raise ParseError("Expected at least one command")

        return CommandList(commands)

    def match_token_for_command(self) -> bool:
        """Check if current token can start a command"""
        return self.match_token('SET') or self.match_token('SE') or \
               self.match_token('LIGAR') or self.match_token('DESLIGAR') or \
               self.match_token('ENVIAR')

    def parse_command(self) -> Command:
        """Parse CMD → ATTRIB | OBSACT | ACT"""
        if self.match_token('SET'):
            return self.parse_attribution()
        elif self.match_token('SE'):
            return self.parse_observation_action()
        elif self.match_token('LIGAR') or self.match_token('DESLIGAR') or self.match_token('ENVIAR'):
            return self.parse_action()
        else:
            raise ParseError(f"Unexpected token '{self.current_token.value}' in command",
                           self.current_token.lineno, str(self.current_token.value))

    def parse_attribution(self) -> Attribution:
        """Parse ATTRIB → set observation = VAR"""
        line_number = self.current_token.lineno if self.current_token else 0

        self.consume_token('SET')
        obs_token = self.consume_token('OBSERVATION')
        self.consume_token('IGUAL')
        value = self.parse_variable()

        return Attribution(obs_token.value, value, line_number)

    def parse_observation_action(self) -> ObservationAction:
        """Parse OBSACT → se OBS entao ACT | se OBS entao ACT senao ACT"""
        line_number = self.current_token.lineno if self.current_token else 0

        self.consume_token('SE')
        condition = self.parse_observation()
        self.consume_token('ENTAO')
        then_action = self.parse_action()

        else_action = None
        if self.match_token('SENAO'):
            self.consume_token('SENAO')
            else_action = self.parse_action()

        return ObservationAction(condition, then_action, else_action, line_number)

    def parse_observation(self) -> Observation:
        """Parse OBS → observation oplogic VAR | observation oplogic VAR && OBS"""
        line_number = self.current_token.lineno if self.current_token else 0

        obs_token = self.consume_token('OBSERVATION')
        op_token = self.consume_token('OPLOGIC')
        value = self.parse_variable()

        next_obs = None
        if self.match_token('AND'):
            self.consume_token('AND')
            next_obs = self.parse_observation()

        return Observation(obs_token.value, op_token.value, value, next_obs, line_number)

    def parse_variable(self) -> Variable:
        """Parse VAR → num | bool"""
        line_number = self.current_token.lineno if self.current_token else 0

        if self.match_token('NUM'):
            token = self.consume_token('NUM')
            return Variable(token.value, line_number)
        elif self.match_token('BOOL'):
            token = self.consume_token('BOOL')
            return Variable(token.value, line_number)
        else:
            raise ParseError(f"Expected number or boolean, found '{self.current_token.value}'",
                           self.current_token.lineno, str(self.current_token.value))

    def parse_action(self) -> Action:
        """Parse ACT → ACTION namedevice | enviar alerta (msg) namedevice | enviar alerta (msg, observation) namedevice | enviar alerta (msg) para todos : DEVICE_LIST"""
        line_number = self.current_token.lineno if self.current_token else 0

        if self.match_token('LIGAR') or self.match_token('DESLIGAR'):
            action_token = self.consume_token()
            # Accept either NAMEDEVICE or OBSERVATION for device names
            if self.match_token('NAMEDEVICE'):
                device_token = self.consume_token('NAMEDEVICE')
            elif self.match_token('OBSERVATION'):
                device_token = self.consume_token('OBSERVATION')
            else:
                raise ParseError(f"Expected device name but found '{self.current_token.value}'",
                               self.current_token.lineno, str(self.current_token.value))
            return SimpleAction(action_token.value, device_token.value, line_number)

        elif self.match_token('ENVIAR'):
            self.consume_token('ENVIAR')
            self.consume_token('ALERTA')
            self.consume_token('ABRE_PAREN')

            msg_token = self.consume_token('MSG')
            message = msg_token.value

            # Check for observation parameter
            observation = None
            if self.match_token('VIRGULA'):
                self.consume_token('VIRGULA')
                obs_token = self.consume_token('OBSERVATION')
                observation = obs_token.value

            self.consume_token('FECHA_PAREN')

            # Check for broadcast or single device
            if self.match_token('PARA'):
                self.consume_token('PARA')
                self.consume_token('TODOS')
                self.consume_token('DOIS_PONTOS')
                devices = self.parse_device_list()
                return BroadcastAlertAction(message, devices, line_number)
            else:
                # Accept either NAMEDEVICE or OBSERVATION for device names
                if self.match_token('NAMEDEVICE'):
                    device_token = self.consume_token('NAMEDEVICE')
                elif self.match_token('OBSERVATION'):
                    device_token = self.consume_token('OBSERVATION')
                else:
                    raise ParseError(f"Expected device name but found '{self.current_token.value}'",
                                   self.current_token.lineno, str(self.current_token.value))
                return AlertAction(message, device_token.value, observation, line_number)

        else:
            raise ParseError(f"Expected action, found '{self.current_token.value}'",
                           self.current_token.lineno, str(self.current_token.value))

    def parse_device_list(self) -> DeviceNameList:
        """Parse DEVICE_LIST → namedevice, DEVICE_LIST | namedevice"""
        line_number = self.current_token.lineno if self.current_token else 0
        devices = []

        # Accept either NAMEDEVICE or OBSERVATION for device names
        if self.match_token('NAMEDEVICE'):
            device_token = self.consume_token('NAMEDEVICE')
        elif self.match_token('OBSERVATION'):
            device_token = self.consume_token('OBSERVATION')
        else:
            raise ParseError(f"Expected device name but found '{self.current_token.value}'",
                           self.current_token.lineno, str(self.current_token.value))
        devices.append(device_token.value)

        while self.match_token('VIRGULA'):
            self.consume_token('VIRGULA')
            # Accept either NAMEDEVICE or OBSERVATION for device names
            if self.match_token('NAMEDEVICE'):
                device_token = self.consume_token('NAMEDEVICE')
            elif self.match_token('OBSERVATION'):
                device_token = self.consume_token('OBSERVATION')
            else:
                raise ParseError(f"Expected device name but found '{self.current_token.value}'",
                               self.current_token.lineno, str(self.current_token.value))
            devices.append(device_token.value)

        return DeviceNameList(devices, line_number)


# ============================================================================
# Unified Interface
# ============================================================================

class DeviceLanguageProcessor:
    """Unified interface for lexical analysis and parsing"""

    def __init__(self, debug_mode: bool = False):
        self.lexer = DeviceLexer()
        self.parser = DeviceParser(self.lexer)
        self.debug_mode = debug_mode

    def tokenize(self, input_text: str) -> list:
        """Tokenize input text and return list of tokens"""
        return list(self.lexer.tokenize(input_text))

    def parse(self, input_text: str) -> Program:
        """Parse input text and return AST"""
        return self.parser.parse(input_text)

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

        except ParseError as e:
            result['errors'].append(str(e))
            if show_ast:
                print(f"=== PARSE ERROR ===")
                print(str(e))
                print()
        except Exception as e:
            result['errors'].append(f"Unexpected error: {str(e)}")
            if show_ast:
                print(f"=== UNEXPECTED ERROR ===")
                print(str(e))
                print()

        return result

    def debug_tokens(self, input_text: str) -> None:
        """Print detailed token information for debugging"""
        print("=== DETAILED TOKEN ANALYSIS ===")
        tokens = self.tokenize(input_text)

        print(f"Total tokens: {len(tokens)}")
        print("-" * 80)
        print(f"{'Index':<5} {'Type':<15} {'Value':<25} {'Line':<5} {'Raw':<20}")
        print("-" * 80)

        for i, token in enumerate(tokens):
            raw_value = repr(token.value)
            print(f"{i:<5} {token.type:<15} {str(token.value):<25} {token.lineno:<5} {raw_value:<20}")

        print("-" * 80)

    def debug_parse_tree(self, ast: Program) -> None:
        """Print detailed AST structure for debugging"""
        print("=== DETAILED AST STRUCTURE ===")
        self._debug_node(ast, 0)

    def _debug_node(self, node: ASTNode, depth: int) -> None:
        """Recursively print AST node structure"""
        indent = "  " * depth
        node_type = type(node).__name__

        print(f"{indent}{node_type}:")

        # Print node-specific information
        if isinstance(node, Program):
            print(f"{indent}  - devices: {len(node.devices.devices)}")
            print(f"{indent}  - commands: {len(node.commands.commands)}")
            self._debug_node(node.devices, depth + 1)
            self._debug_node(node.commands, depth + 1)

        elif isinstance(node, DeviceList):
            print(f"{indent}  - count: {len(node.devices)}")
            for i, device in enumerate(node.devices):
                print(f"{indent}  - device[{i}]:")
                self._debug_node(device, depth + 2)

        elif isinstance(node, Device):
            print(f"{indent}  - name: '{node.name}'")
            print(f"{indent}  - observation: {node.observation}")
            print(f"{indent}  - line: {node.line_number}")

        elif isinstance(node, CommandList):
            print(f"{indent}  - count: {len(node.commands)}")
            for i, cmd in enumerate(node.commands):
                print(f"{indent}  - command[{i}]:")
                self._debug_node(cmd, depth + 2)

        elif isinstance(node, Attribution):
            print(f"{indent}  - observation: '{node.observation}'")
            print(f"{indent}  - value:")
            self._debug_node(node.value, depth + 2)

        elif isinstance(node, ObservationAction):
            print(f"{indent}  - condition:")
            self._debug_node(node.condition, depth + 2)
            print(f"{indent}  - then_action:")
            self._debug_node(node.then_action, depth + 2)
            if node.else_action:
                print(f"{indent}  - else_action:")
                self._debug_node(node.else_action, depth + 2)

        elif isinstance(node, Observation):
            print(f"{indent}  - observation: '{node.observation}'")
            print(f"{indent}  - operator: '{node.operator}'")
            print(f"{indent}  - value:")
            self._debug_node(node.value, depth + 2)
            if node.next_obs:
                print(f"{indent}  - next_obs:")
                self._debug_node(node.next_obs, depth + 2)

        elif isinstance(node, Variable):
            print(f"{indent}  - value: {node.value} ({type(node.value).__name__})")
            print(f"{indent}  - line: {node.line_number}")

        elif isinstance(node, SimpleAction):
            print(f"{indent}  - action_type: '{node.action_type}'")
            print(f"{indent}  - device: '{node.device}'")

        elif isinstance(node, AlertAction):
            print(f"{indent}  - message: '{node.message}'")
            print(f"{indent}  - device: '{node.device}'")
            print(f"{indent}  - observation: {node.observation}")

        elif isinstance(node, BroadcastAlertAction):
            print(f"{indent}  - message: '{node.message}'")
            print(f"{indent}  - devices:")
            self._debug_node(node.devices, depth + 2)

        elif isinstance(node, DeviceNameList):
            print(f"{indent}  - devices: {node.devices}")

    def generate_dot_graph(self, ast: Program, filename: str = "ast_graph.dot") -> str:
        """Generate a Graphviz DOT file for AST visualization"""
        dot_content = ["digraph AST {"]
        dot_content.append("  rankdir=TB;")
        dot_content.append("  node [shape=box, style=rounded];")

        node_counter = [0]  # Use list to allow modification in nested function

        def add_node(node: ASTNode, parent_id: str = None) -> str:
            node_id = f"node_{node_counter[0]}"
            node_counter[0] += 1

            # Create label based on node type
            if isinstance(node, Program):
                label = "Program"
            elif isinstance(node, DeviceList):
                label = f"DeviceList\\n({len(node.devices)} devices)"
            elif isinstance(node, Device):
                label = f"Device\\n{node.name}"
                if node.observation:
                    label += f"\\n({node.observation})"
            elif isinstance(node, CommandList):
                label = f"CommandList\\n({len(node.commands)} commands)"
            elif isinstance(node, Attribution):
                label = f"Attribution\\n{node.observation} = {node.value.value}"
            elif isinstance(node, ObservationAction):
                label = "If-Then"
                if node.else_action:
                    label += "-Else"
            elif isinstance(node, Observation):
                label = f"Observation\\n{node.observation} {node.operator} {node.value.value}"
            elif isinstance(node, Variable):
                label = f"Value\\n{node.value}"
            elif isinstance(node, SimpleAction):
                label = f"Action\\n{node.action_type} {node.device}"
            elif isinstance(node, AlertAction):
                label = f"Alert\\n'{node.message}'\\nto {node.device}"
            elif isinstance(node, BroadcastAlertAction):
                label = f"Broadcast\\n'{node.message}'"
            elif isinstance(node, DeviceNameList):
                label = f"DeviceList\\n{', '.join(node.devices)}"
            else:
                label = type(node).__name__

            dot_content.append(f'  {node_id} [label="{label}"];')

            if parent_id:
                dot_content.append(f"  {parent_id} -> {node_id};")

            # Add child nodes
            if isinstance(node, Program):
                add_node(node.devices, node_id)
                add_node(node.commands, node_id)
            elif isinstance(node, DeviceList):
                for device in node.devices:
                    add_node(device, node_id)
            elif isinstance(node, CommandList):
                for cmd in node.commands:
                    add_node(cmd, node_id)
            elif isinstance(node, Attribution):
                add_node(node.value, node_id)
            elif isinstance(node, ObservationAction):
                add_node(node.condition, node_id)
                add_node(node.then_action, node_id)
                if node.else_action:
                    add_node(node.else_action, node_id)
            elif isinstance(node, Observation):
                add_node(node.value, node_id)
                if node.next_obs:
                    add_node(node.next_obs, node_id)
            elif isinstance(node, BroadcastAlertAction):
                add_node(node.devices, node_id)

            return node_id

        add_node(ast)
        dot_content.append("}")

        # Write to file
        with open(filename, 'w') as f:
            f.write('\n'.join(dot_content))

        return filename


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
