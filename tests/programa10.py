# Generated Python code from ObsAct program
# Generated using SLY-based parser and code generator

# Import device control functions
from functions import ligar, desligar, alerta, alertavar

# Main program logic
def main():
    # Variable for device sensor2 observation
    temp = None  # Will be set by program

    # set temp = 25
    temp = 25

    # se temp > 20 entao ...
    if temp > 20:
        # ligar sensor1
        ligar("sensor1")

    # enviar alerta ("Teste") sensor1
    alerta("sensor1", "Teste")

if __name__ == '__main__':
    main()