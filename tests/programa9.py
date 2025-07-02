# Generated Python code from ObsAct program
# Generated using SLY-based parser and code generator

# Import device control functions
from functions import ligar, desligar, alerta, alertavar

# Main program logic
def main():
    # Variable for device tempSensor observation
    temperatura = None  # Will be set by program
    # Variable for device dehumidifier observation
    umidade = None  # Will be set by program
    # Variable for device smartLights observation
    movimento = None  # Will be set by program

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