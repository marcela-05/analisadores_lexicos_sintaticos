# Código Python gerado a partir do programa ObsAct
# Gerado usando parser baseado em SLY e gerador de código

# Importa funções de controle de dispositivos
from functions import ligar, desligar, alerta, alertavar

# Lógica principal do programa
def main():
    # Variável para observação do dispositivo sensor2
    temp = None  # Será definida pelo programa

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