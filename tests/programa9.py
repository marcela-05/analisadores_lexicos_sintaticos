# Código Python gerado a partir do programa ObsAct
# Gerado usando parser baseado em SLY e gerador de código

# Importa funções de controle de dispositivos
from functions import ligar, desligar, alerta, alertavar

# Lógica principal do programa
def main():
    # Variável para observação do dispositivo tempSensor
    temperatura = None  # Será definida pelo programa
    # Variável para observação do dispositivo dehumidifier
    umidade = None  # Será definida pelo programa
    # Variável para observação do dispositivo smartLights
    movimento = None  # Será definida pelo programa

    # set temperatura = 28
    temperatura = 28

    # set umidade = 75
    umidade = 75

    # set movimento = False
    movimento = False

    # se temperatura > 30 or umidade > 70 entao ...
    if temperatura > 30 or umidade > 70:
        # ligar airConditioner
        ligar("airConditioner")

    # se temperatura < 18 or umidade < 35 entao ...
    if temperatura < 18 or umidade < 35:
        # ligar heater
        ligar("heater")

    # se movimento == True entao ...
    if movimento == True:
        # ligar smartLights
        ligar("smartLights")

    # enviar alerta ("Sistema ativado", temperatura) painel
    alertavar("painel", "Sistema ativado", str(temperatura))

if __name__ == '__main__':
    main()