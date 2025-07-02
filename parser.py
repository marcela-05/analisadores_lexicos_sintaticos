from sly import Lexer, Parser
from typing import List, Optional, Union
from lexer import DeviceLexer
from ast_nodes import Program, Device, Command, Attribution, ObservationAction, SimpleAction, AlertAction, BroadcastAlertAction, Observation

# Função decoradora do Parser SLY
def _(rule):
    """Decorador para regras do parser SLY"""
    def decorator(func):
        func._grammar = (rule,) if isinstance(rule, str) else rule
        return func
    return decorator


class DeviceParser(Parser):
    """Parser baseado em SLY para a gramática de dispositivos"""

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

    # dispositivo : { nome }
    @_('DISPOSITIVO DOIS_PONTOS ABRE_CHAVE device_name FECHA_CHAVE')
    def device(self, p):
        return Device(p.device_name, line_number=p.lineno)

    # dispositivo : { nome, observacao }
    @_('DISPOSITIVO DOIS_PONTOS ABRE_CHAVE device_name VIRGULA OBSERVATION FECHA_CHAVE')
    def device(self, p):
        return Device(p.device_name, p.OBSERVATION, line_number=p.lineno)

    @_('DISPOSITIVO DOIS_PONTOS device_name')
    def device(self, p):
        return Device(p.device_name, line_number=p.lineno)

    # dispositivo : nome, observacao (old syntax without braces)
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
        return Observation(p.OBSERVATION, p.OPLOGIC, p.variable, p.observation, "&&", line_number=p.lineno)

    @_('OBSERVATION OPLOGIC variable OR observation')
    def observation(self, p):
        return Observation(p.OBSERVATION, p.OPLOGIC, p.variable, p.observation, "||", line_number=p.lineno)

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
