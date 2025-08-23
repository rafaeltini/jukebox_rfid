# 🎶 Jukebox RFID

Sistema de jukebox controlado por cartões RFID, com interface web, integração com Spotify Connect e instalação automatizada.

---

## 🌐 Language / Idioma

- [🇧🇷 Português](#-português)
- [🇺🇸 English](#-english)

---

## 🇧🇷 Português

### 🚀 Instalação

#### ✅ Requisitos

- Raspberry Pi com Raspberry Pi OS
- Conexão à internet
- Leitor RFID RC522 conectado via SPI
- Conta Spotify Premium (para usar o Raspotify)

#### 📦 Passo a passo

```bash
git clone https://github.com/rafaeltini/jukebox_rfid.git
cd jukebox_rfid
bash install.sh

Escolha uma opção no menu:
- 1 – Instalar sistema completo
- 2 – Reiniciar Raspberry Pi
- 3 – Desinstalar Jukebox
🌐 Interface Web da Jukebox
Após a instalação, o servidor Flask será iniciado automaticamente via systemd.
Acesse via navegador:

http://<IP-do-RaspberryPi>:5000

Um QR Code será gerado para facilitar o acesso via celular.
🛠️ Serviço systemd
sudo systemctl restart jukebox
sudo systemctl stop jukebox
sudo systemctl status jukebox


🌐 Interface Web do Instalador (opcional)
source venv/bin/activate
python3 installer_web.py


Acesse:
http://<IP-do-RaspberryPi>:5001


🧹 Desinstalação
Execute novamente o instalador e escolha a opção 3.
📄 Logs
Todas as ações do instalador são registradas em install.log na raiz do projeto.
📬 Contato
Criado por rafaeltini.
Sugestões, melhorias ou bugs? Abra uma issue ou envie um pull request!

🇺🇸 English
🚀 Installation
✅ Requirements
- Raspberry Pi with Raspberry Pi OS
- Internet connection
- RC522 RFID reader connected via SPI
- Spotify Premium account (for Raspotify)
📦 Steps
git clone https://github.com/rafaeltini/jukebox_rfid.git
cd jukebox_rfid
bash install.sh


Choose an option from the menu:
- 1 – Full system installation
- 2 – Reboot Raspberry Pi
- 3 – Uninstall Jukebox
🌐 Jukebox Web Interface
After installation, the Flask server will start automatically via systemd.
Access via browser:
http://<RaspberryPi-IP>:5000


Example: http://192.168.0.105:5000

A QR Code will be generated for easy mobile access.
🛠️ systemd Service
sudo systemctl restart jukebox
sudo systemctl stop jukebox
sudo systemctl status jukebox


🌐 Web Installer Interface (optional)
source venv/bin/activate
python3 installer_web.py


Access:
http://<RaspberryPi-IP>:5001


🧹 Uninstallation
Run the installer again and choose option 3.
📄 Logs
All installer actions are logged in install.log at the project root.
📬 Contact
Created by rafaeltini.
Suggestions, improvements or bugs? Open an issue or submit a pull request!

---



