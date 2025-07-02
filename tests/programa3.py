# Generated Python code from ObsAct program
# Generated using SLY-based parser and code generator

# Import device control functions
from functions import ligar, desligar, alerta, alertavar

# Main program logic
def main():
    # Variable for device celular observation
    movimento = None  # Will be set by program
    # Variable for device higrmetro observation
    umidade = None  # Will be set by program
    # Variable for device lampada observation
    potencia = None  # Will be set by program

    # set potencia = 100
    potencia = 100

    # se umidade < 40 entao ...
    if umidade < 40:
        # enviar alerta (" Ar seco detectado ") Monitor
        alerta("Monitor", " Ar seco detectado ")

    # se movimento == True entao ...
    if movimento == True:
        # ligar lampada
        ligar("lampada")
    else:
        # desligar lampada
        desligar("lampada")


if __name__ == '__main__':
    main()