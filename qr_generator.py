# Importa a biblioteca qrcode para gerar o QR code e a biblioteca socket para obter o IP.
import qrcode
import socket

def get_local_ip():
    """
    Descobre o endereço IP local da máquina na rede.

    Cria um socket e o conecta a um endereço IP externo (o do Google DNS),
    sem de fato enviar dados. Isso força o sistema operacional a escolher a
    interface de rede correta, permitindo-nos obter o IP local.

    Returns:
        str: O endereço IP local da máquina.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Não é necessário enviar dados, apenas conectar.
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        print(f"Não foi possível obter o IP local: {e}")
        ip = "127.0.0.1" # Retorna o IP de loopback como fallback.
    finally:
        s.close()
    return ip

def generate_qr_code():
    """
    Gera um QR code que aponta para a interface web da Jukebox.
    """
    # Monta a URL da interface web usando o IP local e a porta do servidor Flask.
    ip_address = get_local_ip()
    url = f"http://{ip_address}:5000"

    print(f"Gerando QR Code para o endereço: {url}")

    # Cria a imagem do QR code a partir da URL.
    img = qrcode.make(url)

    # Salva a imagem gerada no arquivo 'qr_code.png' na raiz do projeto.
    img.save("qr_code.png")

    print(f"✅ QR Code salvo como 'qr_code.png'")

if __name__ == "__main__":
    generate_qr_code()