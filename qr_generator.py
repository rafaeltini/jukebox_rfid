import qrcode
import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

url = f"http://{get_ip()}:5000"
img = qrcode.make(url)
img.save("qr_code.png")
print(f"QR Code gerado para: {url}")