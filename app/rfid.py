# PT: Este arquivo contém a lógica para interagir com o leitor RFID RC522.
#     Ele foi refatorado para usar uma classe que gerencia o ciclo de vida do leitor
#     de forma mais eficiente.
# EN: This file contains the logic for interacting with the RC522 RFID reader.
#     It has been refactored to use a class that manages the reader's lifecycle
#     more efficiently.

import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import time
import atexit

class RFIDReader:
    """
    PT: Uma classe para gerenciar a comunicação com o leitor RFID MFRC522.
        Ela inicializa o leitor uma vez e garante que os pinos GPIO sejam
        limpos corretamente quando o programa termina.
    EN: A class to manage communication with the MFRC522 RFID reader.
        It initializes the reader once and ensures the GPIO pins are
        cleaned up correctly when the program exits.
    """
    def __init__(self):
        """
        PT: Inicializa o leitor MFRC522 e registra a função de limpeza
            para ser chamada na saída do programa.
        EN: Initializes the MFRC522 reader and registers the cleanup
            function to be called on program exit.
        """
        try:
            self.reader = MFRC522()
            print("Leitor RFID inicializado com sucesso. / RFID reader initialized successfully.")
            # PT: Registra a função de limpeza para ser chamada automaticamente na saída
            # EN: Registers the cleanup function to be called automatically on exit
            atexit.register(self.cleanup)
        except Exception as e:
            print(f"Falha ao inicializar o leitor RFID: {e}")
            print("Isso pode acontecer se o programa não estiver rodando em um Raspberry Pi ou se a interface SPI não estiver habilitada.")
            self.reader = None


    def read_uid(self):
        """
        PT: Aguarda a aproximação de um cartão RFID e lê o seu UID.
            Esta é uma função bloqueante que continuará em loop até que um cartão seja encontrado.
        EN: Waits for an RFID card to be presented and reads its UID.
            This is a blocking call that will loop until a card is found.

        Returns:
            str: O UID do cartão como uma string, ou None se o leitor não foi inicializado.
                 The card UID as a string, or None if the reader was not initialized.
        """
        if not self.reader:
            time.sleep(1) # Avoid busy-looping if reader failed to init
            return None

        # PT: Loop para detectar o cartão
        # EN: Loop to detect the card
        while True:
            # PT: MFRC522_Request procura por cartões
            # EN: MFRC522_Request scans for cards
            (status, TagType) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)

            if status == self.reader.MI_OK:
                # PT: MFRC522_Anticoll obtém o UID do cartão
                # EN: MFRC522_Anticoll gets the card's UID
                (status, uid_bytes) = self.reader.MFRC522_Anticoll()

                if status == self.reader.MI_OK:
                    # PT: Converte o UID de bytes para uma string hifenizada
                    # EN: Converts the UID from bytes to a hyphenated string
                    uid = "-".join(map(str, uid_bytes))
                    return uid

            # PT: Pequena pausa para não sobrecarregar a CPU
            # EN: Small pause to avoid overloading the CPU
            time.sleep(0.2)

    def cleanup(self):
        """
        PT: Libera os recursos do GPIO.
        EN: Releases GPIO resources.
        """
        print("Limpando pinos GPIO... / Cleaning up GPIO pins...")
        GPIO.cleanup()

# PT: O código abaixo serve para testar este módulo de forma independente.
# EN: The code below is for testing this module independently.
if __name__ == "__main__":
    print("Iniciando teste do leitor RFID...")
    reader = RFIDReader()
    if reader.reader:
        try:
            while True:
                print("\nAproxime um cartão para leitura... / Please scan a card...")
                uid = reader.read_uid()
                print(f"UID lido com sucesso (UID read successfully): {uid}")
                # PT: Aguarda um pouco para evitar leituras múltiplas do mesmo cartão
                # EN: Wait a bit to avoid multiple reads of the same card
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nTeste interrompido pelo usuário. / Test interrupted by user.")
    else:
        print("Não foi possível iniciar o teste pois o leitor RFID não foi inicializado.")