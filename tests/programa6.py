# Generated Python code from ObsAct program
# Generated using SLY-based parser and code generator

# Import device control functions
from functions import ligar, desligar, alerta, alertavar

# Main program logic
def main():
    # desligar ventilador
    desligar("ventilador")

if __name__ == '__main__':
    main()