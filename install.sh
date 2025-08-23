#!/bin/bash

LOGFILE="install.log"
exec > >(tee -a "$LOGFILE") 2>&1
echo "📄 Log de instalação iniciado em $(date)"

echo "🎶 Jukebox RFID Setup"
echo "1) Instalar sistema"
echo "2) Reiniciar Raspberry Pi"
echo "3) Desinstalar Jukebox"
read -p "Escolha uma opção [1-3]: " opcao

if [ "$opcao" == "1" ]; then
    echo "🔧 Atualizando sistema..."
    sudo apt update && sudo apt upgrade -y || { echo "❌ Falha ao atualizar sistema"; exit 1; }

    echo "📦 Atualizando repositório..."
    git pull origin master || { echo "❌ Falha ao atualizar repositório"; exit 1; }

    echo "🐍 Instalando dependências Python..."
    sudo apt install python3 python3-pip python3-venv python3-dev -y || { echo "❌ Falha ao instalar pacotes Python"; exit 1; }

    echo "📁 Criando ambiente virtual..."
    python3 -m venv venv || { echo "❌ Falha ao criar venv"; exit 1; }
    source venv/bin/activate

    echo "📜 Instalando pacotes do requirements.txt..."
    pip install --upgrade pip || { echo "❌ Falha ao atualizar pip"; exit 1; }
    pip install -r requirements.txt || { echo "❌ Falha ao instalar requirements"; exit 1; }

    echo "📡 Instalando drivers RFID..."
    sudo apt install python3-spidev python3-rpi.gpio -y || { echo "❌ Falha ao instalar drivers RFID"; exit 1; }

    echo "🎧 Instalando Spotify Connect..."
    curl -sL https://dtcooper.github.io/raspotify/install.sh | sh || { echo "❌ Falha ao instalar Raspotify"; exit 1; }

    echo "🛠️ Configurando serviço..."
    # Obtém o diretório absoluto do script para evitar problemas com caminhos relativos.
    SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

    # Cria o arquivo de serviço do systemd dinamicamente com os caminhos corretos.
    # Isso torna a instalação independente do local onde o repositório foi clonado.
    sudo tee /etc/systemd/system/jukebox.service > /dev/null <<EOF
[Unit]
Description=Jukebox RFID Web Server
After=network.target

[Service]
# Executa o main.py usando o Python do ambiente virtual (venv).
ExecStart=$SCRIPT_DIR/venv/bin/python3 $SCRIPT_DIR/app/main.py
# Define o diretório de trabalho para a pasta da aplicação.
WorkingDirectory=$SCRIPT_DIR/app
Restart=always
# É recomendado rodar o serviço com um usuário não-root que tenha as permissões necessárias.
# O usuário 'pi' é o padrão no Raspberry Pi OS.
User=pi

[Install]
WantedBy=multi-user.target
EOF

    echo "🔄 Recarregando e reiniciando o serviço systemd..."
    # Recarrega o systemd para que ele leia o novo arquivo de serviço.
    sudo systemctl daemon-reload
    # Habilita o serviço para iniciar no boot.
    sudo systemctl enable jukebox.service
    # Reinicia o serviço para aplicar as novas configurações.
    sudo systemctl restart jukebox.service || { echo "❌ Falha ao iniciar serviço"; exit 1; }

    echo "📱 Gerando QR Code..."
    python3 qr_generator.py || { echo "❌ Falha ao gerar QR Code"; exit 1; }

    echo "✅ Instalação concluída!"

elif [ "$opcao" == "2" ]; then
    echo "🔁 Reiniciando..."
    sudo reboot

elif [ "$opcao" == "3" ]; then
    echo "🧹 Removendo Jukebox..."
    sudo systemctl stop jukebox.service
    sudo systemctl disable jukebox.service
    sudo rm /etc/systemd/system/jukebox.service
    sudo apt remove raspotify -y
    echo "❌ Jukebox removido."

else
    echo "⚠️ Opção inválida."
fi