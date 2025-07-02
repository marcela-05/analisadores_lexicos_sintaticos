# Código Python gerado a partir do programa ObsAct
# Gerado usando parser baseado em SLY e gerador de código

# Importa funções de controle de dispositivos
from functions import ligar, desligar, alerta, alertavar

# Lógica principal do programa
def main():
    # Variável para observação do dispositivo Termometro
    temperatura = None  # Será definida pelo programa
    # Variável para observação do dispositivo ventilador
    potencia = None  # Será definida pelo programa

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