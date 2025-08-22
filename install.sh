#!/bin/bash

echo "🎶 Jukebox RFID Setup"
echo "1) Instalar sistema"
echo "2) Reiniciar Raspberry Pi"
echo "3) Desinstalar Jukebox"
read -p "Escolha uma opção [1-3]: " opcao

if [ "$opcao" == "1" ]; then
    echo "🔧 Atualizando sistema..."
    sudo apt update && sudo apt upgrade -y

    echo "🐍 Instalando dependências Python..."
    sudo apt install python3 python3-pip python3-flask python3-dev -y
    pip3 install -r requirements.txt

    echo "📡 Instalando drivers RFID..."
    sudo apt install python3-spidev python3-rpi.gpio -y

    echo "🎧 Instalando Spotify Connect (Raspotify)..."
    curl -sL https://dtcooper.github.io/raspotify/install.sh | sh

    echo "🛠️ Configurando serviço do Jukebox..."
    sudo cp jukebox.service /etc/systemd/system/
    sudo systemctl enable jukebox.service
    sudo systemctl start jukebox.service

    echo "📱 Gerando QR Code de acesso..."
    python3 qr_generator.py

    echo "✅ Instalação concluída!"
elif [ "$opcao" == "2" ]; then
    echo "🔁 Reiniciando..."
    sudo reboot
elif [ "$opcao" == "3" ]; then
    echo "🧹 Removendo arquivos e serviços..."
    sudo systemctl stop jukebox.service
    sudo systemctl disable jukebox.service
    sudo rm /etc/systemd/system/jukebox.service
    sudo apt remove raspotify -y
    echo "❌ Jukebox removido."
else
    echo "Opção inválida."
fi