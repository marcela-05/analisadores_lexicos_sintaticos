# Código Python gerado a partir do programa ObsAct
# Gerado usando parser baseado em SLY e gerador de código

# Importa funções de controle de dispositivos
from functions import ligar, desligar, alerta, alertavar

# Lógica principal do programa
def main():
    # Variável para observação do dispositivo Termometro
    temperatura = None  # Será definida pelo programa

    # set temperatura = 35
    temperatura = 35

    # se temperatura > 30 entao ...
    if temperatura > 30:
        # enviar alerta (" Temperatura em ") para todos : monitor, celular
        # Alerta broadcast para múltiplos dispositivos
        alerta("monitor", " Temperatura em ")
        alerta("celular", " Temperatura em ")


if __name__ == '__main__':
    main()