# Código Python gerado a partir do programa ObsAct
# Gerado usando parser baseado em SLY e gerador de código

# Importa funções de controle de dispositivos
from functions import ligar, desligar, alerta, alertavar

# Lógica principal do programa
def main():
    # desligar ventilador
    desligar("ventilador")

if __name__ == '__main__':
    main()