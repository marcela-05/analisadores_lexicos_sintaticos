# Código Python gerado a partir do programa ObsAct
# Gerado usando parser baseado em SLY e gerador de código

# Importa funções de controle de dispositivos
from functions import ligar, desligar, alerta, alertavar

# Lógica principal do programa
def main():
    # set umidade = 20
    umidade = 20

    # se umidade < 40 entao ...
    if umidade < 40:
        # enviar alerta (" Ar seco detectado ") Monitor
        alerta("Monitor", " Ar seco detectado ")


if __name__ == '__main__':
    main()