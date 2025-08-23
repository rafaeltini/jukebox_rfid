# PT: Importa a biblioteca necessária para gerar o QR code.
# EN: Imports the necessary library to generate the QR code.
import qrcode

def generate_qr_code():
    """
    PT: Gera um QR code que aponta para a interface web da Jukebox,
        usando o endereço .local que é anunciado na rede.
    EN: Generates a QR code that points to the Jukebox web interface,
        using the .local address that is broadcast on the network.
    """
    # PT: URL fixa para o serviço anunciado por mDNS.
    # EN: Fixed URL for the service announced by mDNS.
    url = "http://rfidbox.local:5000"

    print(f"Gerando QR Code para o endereço (Generating QR Code for address): {url}")

    # PT: Cria e salva a imagem do QR code.
    # EN: Creates and saves the QR code image.
    img = qrcode.make(url)
    img.save("qr_code.png")

    print(f"✅ QR Code salvo como 'qr_code.png' (QR Code saved as 'qr_code.png')")

if __name__ == "__main__":
    generate_qr_code()