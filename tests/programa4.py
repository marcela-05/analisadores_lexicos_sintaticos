# Generated Python code from ObsAct program
# Generated using SLY-based parser and code generator

# Import device control functions
from functions import ligar, desligar, alerta, alertavar

# Main program logic
def main():
    # se umidade < 40 entao ...
    if umidade < 40:
        # enviar alerta (" Ar seco detectado ") Monitor
        alerta("Monitor", " Ar seco detectado ")


if __name__ == '__main__':
    main()