# Código Python gerado a partir do programa ObsAct
# Gerado usando parser baseado em SLY e gerador de código

# Importa funções de controle de dispositivos
from functions import ligar, desligar, alerta, alertavar

# Lógica principal do programa
def main():
    # Variável para observação do dispositivo lampada
    potencia = None  # Será definida pelo programa

    # set potencia = 100
    potencia = 100

    # ligar lampada
    ligar("lampada")

if __name__ == '__main__':
    main()