# Generated Python code from ObsAct program
# Generated using SLY-based parser and code generator

# Import device control functions
from functions import ligar, desligar, alerta, alertavar

# Main program logic
def main():
    # Variable for device Termometro observation
    temperatura = None  # Will be set by program

    # se temperatura > 30 entao ...
    if temperatura > 30:
        # enviar alerta (" Temperatura em ") para todos : monitor, celular
        # Broadcast alert to multiple devices
        alerta("monitor", " Temperatura em ")
        alerta("celular", " Temperatura em ")


if __name__ == '__main__':
    main()