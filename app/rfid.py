# PT: Este arquivo contém a lógica para interagir com o leitor RFID RC522.
#     Ele usa a biblioteca mfrc522 e RPi.GPIO para comunicação com o hardware.
# EN: This file contains the logic for interacting with the RC522 RFID reader.
#     It uses the mfrc522 library and RPi.GPIO for hardware communication.

import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import time

def read_uid():
    """
    PT: Aguarda a aproximação de um cartão RFID e lê o seu UID.
        Esta função inicializa o leitor MFRC522, espera por um cartão,
        lê o UID, e depois limpa os pinos GPIO. Ela é projetada para ser
        chamada em um loop ou em uma thread separada.
    EN: Waits for an RFID card to be presented and reads its UID.
        This function initializes the MFRC522 reader, waits for a card,
        reads the UID, and then cleans up the GPIO pins. It is designed
        to be called in a loop or in a separate thread.

    Returns:
        str: PT: O UID do cartão lido, formatado como string (ex: "123-45-67-89"),
                 ou None se a leitura for interrompida.
             EN: The UID of the read card, formatted as a string (e.g., "123-45-67-89"),
                 or None if the reading is interrupted.
    """
    # PT: Instancia o leitor
    # EN: Instantiates the reader
    MIFAREReader = MFRC522()

    print("Aproxime o cartão RFID do leitor para leitura... / Approach the RFID card to the reader...")

    uid = None
    try:
        # PT: Loop contínuo para detectar o cartão
        # EN: Continuous loop to detect the card
        while True:
            # PT: MFRC522_Request procura por cartões do tipo PICC (Proximity Integrated Circuit Card)
            #     MI_OK é o status de sucesso
            # EN: MFRC522_Request looks for PICC type cards (Proximity Integrated Circuit Card)
            #     MI_OK is the success status
            (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

            if status == MIFAREReader.MI_OK:
                print("Cartão detectado! / Card detected!")

                # PT: MFRC522_Anticoll obtém o UID do cartão
                # EN: MFRC522_Anticoll gets the UID of the card
                (status, uid_bytes) = MIFAREReader.MFRC522_Anticoll()

                if status == MIFAREReader.MI_OK:
                    # PT: Converte o UID de uma lista de bytes para uma string hifenizada
                    # EN: Converts the UID from a list of bytes to a hyphenated string
                    uid = "-".join(map(str, uid_bytes))
                    print(f"UID do Cartão (Card UID): {uid}")
                    # PT: Retorna o UID e sai da função
                    # EN: Returns the UID and exits the function
                    return uid

            # PT: Pequena pausa para não sobrecarregar a CPU
            # EN: Small pause to avoid overloading the CPU
            time.sleep(0.2)

    except KeyboardInterrupt:
        # PT: Permite que o programa seja interrompido com Ctrl+C
        # EN: Allows the program to be interrupted with Ctrl+C
        print("Leitura de RFID interrompida pelo usuário. / RFID reading interrupted by user.")
        return None
    finally:
        # PT: Garante que os pinos GPIO sejam liberados ao final
        # EN: Ensures that the GPIO pins are released at the end
        GPIO.cleanup()

# PT: O código abaixo serve para testar este módulo de forma independente.
#     Se você executar `python3 app/rfid.py`, ele irá iniciar o processo de leitura.
# EN: The code below is for testing this module independently.
#     If you run `python3 app/rfid.py`, it will start the reading process.
if __name__ == "__main__":
    card_uid = read_uid()
    if card_uid:
        print(f"\nUID lido com sucesso (UID read successfully): {card_uid}")
    else:
        print("\nNenhum UID foi lido. (No UID was read.)")