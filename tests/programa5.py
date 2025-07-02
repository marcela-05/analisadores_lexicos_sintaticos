# Generated Python code from ObsAct program
# Generated using SLY-based parser and code generator

# Import device control functions
from functions import ligar, desligar, alerta, alertavar

# Main program logic
def main():
    # Variable for device lampada observation
    potencia = None  # Will be set by program

    # set potencia = 100
    potencia = 100

    # ligar lampada
    ligar("lampada")

if __name__ == '__main__':
    main()