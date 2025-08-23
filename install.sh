#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

LOGFILE="install.log"
exec > >(tee -a "$LOGFILE") 2>&1
echo "📄 Log de instalação iniciado em $(date)"

echo "🎶 Jukebox RFID Setup"
echo "1) Instalação Completa"
echo "2) Instalar Driver do Audio HAT (Opcional)"
echo "3) Desinstalar Jukebox"
echo "4) Reiniciar Raspberry Pi"
read -p "Escolha uma opção [1-4]: " opcao

if [ "$opcao" == "1" ]; then
    echo "🔧 Atualizando sistema..."
    sudo rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock /var/cache/apt/archives/lock
    sudo apt-get update || { echo "❌ Falha ao atualizar sistema"; exit 1; }
    sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
        -o Dpkg::Options::="--force-confdef" \
        -o Dpkg::Options::="--force-confold" || { echo "❌ Falha ao atualizar sistema"; exit 1; }

    echo "📦 Atualizando repositório..."
    git pull origin master || { echo "❌ Falha ao atualizar repositório"; exit 1; }

    echo "🐍 Instalando dependências Python..."
    sudo apt-get -o Dpkg::Options::="--force-confdef" \
                 -o Dpkg::Options::="--force-confold" \
                 install python3 python3-pip python3-venv python3-dev -y || { echo "❌ Falha ao instalar pacotes Python"; exit 1; }

    echo "📁 Criando ambiente virtual..."
    python3 -m venv venv || { echo "❌ Falha ao criar venv"; exit 1; }
    source venv/bin/activate

    echo "📜 Instalando pacotes do requirements.txt..."
    pip install --upgrade pip || { echo "❌ Falha ao atualizar pip"; exit 1; }
    pip install -r requirements.txt || { echo "❌ Falha ao instalar requirements"; exit 1; }

    echo "📡 Instalando drivers RFID..."
    sudo apt-get -o Dpkg::Options::="--force-confdef" \
                 -o Dpkg::Options::="--force-confold" \
                 install python3-spidev python3-rpi.gpio -y || { echo "❌ Falha ao instalar drivers RFID"; exit 1; }

    echo "🎧 Instalando Spotify Connect..."
    curl -sL https://dtcooper.github.io/raspotify/install.sh | sh || { echo "❌ Falha ao instalar Raspotify"; exit 1; }

    echo "🛠️ Configurando serviço..."
    SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

    sudo tee /etc/systemd/system/jukebox.service > /dev/null <<EOF
[Unit]
Description=Jukebox RFID Web Server
After=network.target

[Service]
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/venv/bin/python3 -m app.main
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF

    echo "🔄 Recarregando e reiniciando o serviço systemd..."
    sudo systemctl daemon-reload
    sudo systemctl enable jukebox.service
    sudo systemctl restart jukebox.service || { echo "❌ Falha ao iniciar serviço"; exit 1; }

    echo "📱 Gerando QR Code..."
    python3 qr_generator.py || { echo "❌ Falha ao gerar QR Code"; exit 1; }

    echo "✅ Instalação concluída!"

elif [ "$opcao" == "2" ]; then
    echo "🎧 Instalando driver do WM8960 Audio HAT..."
    if [ -d "WM8960-Audio-HAT" ]; then
        echo "⚠️  Diretório WM8960-Audio-HAT já existe. Pulando o clone."
    else
        git clone https://github.com/waveshare/WM8960-Audio-HAT.git || { echo "❌ Falha ao clonar repositório do driver"; exit 1; }
    fi
    cd WM8960-Audio-HAT
    sudo ./install.sh
    echo "✅ Driver do HAT instalado. É necessário reiniciar para aplicar as alterações."
    echo "Use a opção 4 do menu para reiniciar."
    cd ..

elif [ "$opcao" == "3" ]; then
    echo "🧹 Removendo Jukebox..."
    sudo systemctl stop jukebox.service
    sudo systemctl disable jukebox.service
    sudo rm /etc/systemd/system/jukebox.service
    sudo apt-get remove raspotify -y
    echo "❌ Jukebox removido."

elif [ "$opcao" == "4" ]; then
    echo "🔁 Reiniciando..."
    sudo reboot

else
    echo "⚠️ Opção inválida."
fi