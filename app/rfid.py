# Este arquivo contém a lógica para interagir com o leitor RFID RC522.
# Ele usa a biblioteca mfrc522 e RPi.GPIO para comunicação com o hardware.

import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import time

def read_uid():
    """
    Aguarda a aproximação de um cartão RFID e lê o seu UID.

    Esta função inicializa o leitor MFRC522, espera por um cartão,
    lê o UID, e depois limpa os pinos GPIO. Ela é projetada para ser
    chamada em um loop ou em uma thread separada.

    Returns:
        str: O UID do cartão lido, formatado como uma string (ex: "123-45-67-89"),
             ou None se a leitura for interrompida.
    """
    # Instancia o leitor
    MIFAREReader = MFRC522()

    print("Aproxime o cartão RFID do leitor para leitura...")

    uid = None
    try:
        # Loop contínuo para detectar o cartão
        while True:
            # MFRC522_Request procura por cartões do tipo PICC (Proximity Integrated Circuit Card)
            # MI_OK é o status de sucesso
            (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

            if status == MIFAREReader.MI_OK:
                print("Cartão detectado!")

                # MFRC522_Anticoll obtém o UID do cartão
                (status, uid_bytes) = MIFAREReader.MFRC522_Anticoll()

                if status == MIFAREReader.MI_OK:
                    # Converte o UID de uma lista de bytes para uma string hifenizada
                    uid = "-".join(map(str, uid_bytes))
                    print(f"UID do Cartão: {uid}")
                    # Retorna o UID e sai da função
                    return uid

            # Pequena pausa para não sobrecarregar a CPU
            time.sleep(0.2)

    except KeyboardInterrupt:
        # Permite que o programa seja interrompido com Ctrl+C
        print("Leitura de RFID interrompida pelo usuário.")
        return None
    finally:
        # Garante que os pinos GPIO sejam liberados ao final
        GPIO.cleanup()

# O código abaixo serve para testar este módulo de forma independente.
# Se você executar `python3 app/rfid.py`, ele irá iniciar o processo de leitura.
if __name__ == "__main__":
    card_uid = read_uid()
    if card_uid:
        print(f"\nUID lido com sucesso: {card_uid}")
        # Exemplo de como usar a função de associação (que ainda está neste arquivo, mas pode ser movida)
        playlist = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" # Exemplo
        # assign_playlist(card_uid, playlist)
    else:
        print("\nNenhum UID foi lido.")