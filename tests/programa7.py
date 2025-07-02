# Generated Python code from ObsAct program
# Generated using SLY-based parser and code generator

# Import device control functions
from functions import ligar, desligar, alerta, alertavar

# Main program logic
def main():
    # enviar alerta (" Hora de acordar !") Celular
    alerta("Celular", " Hora de acordar !")

if __name__ == '__main__':
    main()