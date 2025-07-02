# Generated Python code from ObsAct program
# Generated using SLY-based parser and code generator

# Import device control functions
from functions import ligar, desligar, alerta, alertavar

# Main program logic
def main():
    # Variable for device Termometro observation
    temperatura = None  # Will be set by program
    # Variable for device ventilador observation
    potencia = None  # Will be set by program

    # set temperatura = 40
    temperatura = 40

    # set potencia = 90
    potencia = 90

    # se temperatura > 30 entao ...
    if temperatura > 30:
        # ligar ventilador
        ligar("ventilador")


if __name__ == '__main__':
    main()