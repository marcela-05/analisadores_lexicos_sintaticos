from typing import List, Optional, Union

# Função decoradora do Parser SLY
def _(rule):
    """Decorador para regras do parser SLY"""
    def decorator(func):
        func._grammar = (rule,) if isinstance(rule, str) else rule
        return func
    return decorator


class ASTNode:
    """Classe base para todos os nós da AST"""

    def __init__(self, line_number: int = 0):
        self.line_number = line_number

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

    def pretty_print(self, indent: int = 0) -> str:
        """Imprime a AST de forma organizada com indentação"""
        return "  " * indent + str(self)


class Program(ASTNode):
    """Nó raiz representando o programa inteiro"""

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
    """Nó representando uma declaração de dispositivo"""

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
    """Classe base para comandos"""
    pass


class Attribution(Command):
    """Nó representando atribuição"""

    def __init__(self, observation: str, value: Union[int, bool], line_number: int = 0):
        super().__init__(line_number)
        self.observation = observation
        self.value = value

    def __str__(self) -> str:
        return f"Attribution({self.observation} = {self.value})"

    def pretty_print(self, indent: int = 0) -> str:
        return "  " * indent + f"Set: {self.observation} = {self.value}"


class ObservationAction(Command):
    """Nó representando condicional"""

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
    """Nó representando observação"""

    def __init__(self, observation: str, operator: str, value: Union[int, bool],
                 next_obs: Optional['Observation'] = None, logical_op: str = "&&", line_number: int = 0):
        super().__init__(line_number)
        self.observation = observation
        self.operator = operator
        self.value = value
        self.next_obs = next_obs
        self.logical_op = logical_op  # "&&" (AND) ou "||" (OR)

    def __str__(self) -> str:
        result = f"{self.observation} {self.operator} {self.value}"
        if self.next_obs:
            result += f" {self.logical_op} {self.next_obs}"
        return result


class Action(ASTNode):
    """Classe base para ações"""
    pass


class SimpleAction(Action):
    """Nó representando ação simples"""

    def __init__(self, action_type: str, device: str, line_number: int = 0):
        super().__init__(line_number)
        self.action_type = action_type
        self.device = device

    def __str__(self) -> str:
        return f"{self.action_type} {self.device}"


class AlertAction(Action):
    """Nó representando ação de alerta"""

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
    """Nó representando alerta broadcast"""

    def __init__(self, message: str, devices: List[str], line_number: int = 0):
        super().__init__(line_number)
        self.message = message
        self.devices = devices

    def __str__(self) -> str:
        return f"enviar alerta ({self.message}) para todos : {', '.join(self.devices)}"
