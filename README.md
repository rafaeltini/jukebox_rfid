# 🎶 Jukebox RFID MP3 Player

## 🌐 Language / Idioma

- [🇧🇷 Português](#-português)
- [🇺🇸 English](#-english)

---
## 🇧🇷 Português

Este projeto transforma um Raspberry Pi em uma Jukebox de MP3 controlada por cartões RFID. Use a interface web para fazer upload de suas músicas, associar cada música a um cartão RFID e, em seguida, simplesmente aproxime o cartão do leitor para tocar sua música.

### ✨ Funcionalidades

- **Playback por RFID:** Associe arquivos MP3 a cartões RFID e toque-os instantaneamente.
- **Interface Web Completa:** Controle a reprodução (play/pause), ajuste o volume e veja a música que está tocando.
- **Interface Multilíngue:** Alterne entre Português e Inglês com um clique.
- **Upload de Músicas:** Arraste e solte seus arquivos MP3 diretamente na interface web para adicioná-los à sua biblioteca.
- **Associação de Cartões Simplificada:** Após o upload de uma música, a interface pede que você escaneie um cartão para criar a associação.
- **Instalação Automatizada:** O script `install.sh` configura todas as dependências de software, incluindo `pygame` para áudio e as bibliotecas GPIO.
- **Serviço Autônomo:** Roda como um serviço de fundo (`systemd`) que inicia automaticamente com o Raspberry Pi.

### 📦 Componentes e Dependências

Esta seção detalha o hardware e o software necessários para o projeto.

#### Componentes de Hardware

- **Raspberry Pi:** O cérebro da operação. Testado no Raspberry Pi 2 W, mas qualquer modelo mais recente com Wi-Fi e pinos GPIO deve funcionar.
- **Leitor RFID MFRC522:** Um leitor de baixo custo para cartões e tags de 13.56MHz. É a interface física para selecionar as músicas.
- **Cartões ou Tags RFID:** Qualquer cartão compatível com o padrão MIFARE Classic. Você precisará de um para cada música ou playlist que desejar adicionar.
- **Cartão MicroSD:** Para o sistema operacional e armazenamento das músicas. Um cartão de 16GB ou mais é recomendado.
- **Fonte de Alimentação:** Uma fonte de alimentação USB-C ou Micro USB de boa qualidade, apropriada para o seu modelo de Raspberry Pi.
- **Alto-falantes ou Fones de Ouvido:** Para ouvir a música. Podem ser conectados à saída de áudio de 3.5mm do Pi.

#### Dependências de Software

O projeto utiliza as seguintes bibliotecas Python, que são instaladas automaticamente pelo script `install.sh`:

- **Flask:** Um micro-framework web usado para criar o servidor que hospeda a interface de usuário.
- **Flask-SocketIO:** Fornece comunicação em tempo real entre o servidor e a interface web, essencial para atualizar o status do player e do leitor RFID instantaneamente.
- **pygame:** Uma biblioteca multimídia usada here para tocar os arquivos de áudio MP3 de forma eficiente.
- **mfrc522:** Uma biblioteca Python de baixo nível para se comunicar com o leitor de RFID MFRC522 através da interface SPI do Raspberry Pi.
- **qrcode[pil]:** Usado para gerar o QR code que facilita o acesso à interface web. A opção `[pil]` garante que a biblioteca de manipulação de imagens `Pillow` seja instalada junto.
- **zeroconf:** Permite que a Jukebox anuncie sua presença na rede local como `rfidbox.local` usando o protocolo mDNS (Bonjour/Avahi), eliminando a necessidade de saber o endereço IP do dispositivo.

### 🔧 Configuração do Hardware

#### Pinagem do Leitor RFID RC522
Conecte o leitor ao Raspberry Pi usando os seguintes pinos GPIO:

| Pino do RC522 | GPIO do Raspberry Pi | Nome no Pi  | Função                |
|---------------|----------------------|-------------|-----------------------|
| SDA (CS)      | GPIO 8               | SPI0_CE0    | Chip Select           |
| SCK (CLK)     | GPIO 11              | SPI0_SCLK   | Clock                 |
| MOSI          | GPIO 10              | SPI0_MOSI   | Master Out Slave In   |
| MISO          | GPIO 9               | SPI0_MISO   | Master In Slave Out   |
| IRQ           | -                    | -           | (não usado)           |
| GND           | GND                  | GND         | Terra (Ground)        |
| RST           | GPIO 25              | GPIO 25     | Reset                 |
| 3.3V          | 3.3V                 | 3.3V        | Alimentação (Power)   |

**Importante:** A biblioteca RFID usada neste projeto não utiliza o pino `RST`. Ele pode ser deixado desconectado.

#### Opcional: Configuração do Waveshare WM8960 Audio HAT

Se você estiver usando o **WM8960 Audio HAT** para uma qualidade de áudio superior, ele precisa de um driver específico para funcionar.

1.  **Instale o Driver do HAT:** No terminal do seu Raspberry Pi, execute os seguintes comandos para baixar e instalar o driver da Waveshare.
    ```bash
    git clone https://github.com/waveshare/WM8960-Audio-HAT.git
    cd WM8960-Audio-HAT
    sudo ./install.sh
    ```
2.  **Reinicie o Pi:** Após a instalação, o sistema precisa ser reiniciado para que o novo driver de áudio seja carregado.
    ```bash
    sudo reboot
    ```
3.  **Verificação (Opcional):** Após reiniciar, você pode verificar se a nova placa de som foi detectada com o comando `aplay -l`. Você deverá ver um dispositivo chamado `wm8960-soundcard`.
4.  **Controle de Volume:** O volume do HAT pode ser controlado pelo sistema usando o `alsamixer`. A interface web deste projeto controlará o volume da aplicação (`pygame`), que por sua vez usa o dispositivo de som padrão do sistema (que agora será o HAT).

**Nota Importante:** As instruções de instalação do driver podem variar dependendo da sua versão do Kernel ou do Raspberry Pi OS. Se encontrar problemas, consulte a [wiki oficial da Waveshare](https://www.waveshare.com/wiki/WM8960_Audio_HAT) para obter informações de troubleshooting e compatibilidade.

### 🚀 Guia de Instalação Completo

Siga estes passos para configurar sua Jukebox do zero.

#### Passo 1: Preparando o Raspberry Pi

1.  **Instale o Raspberry Pi OS:** Use o [Raspberry Pi Imager](https://www.raspberrypi.com/software/) para instalar a versão mais recente do Raspberry Pi OS em um cartão SD.
2.  **Primeiro Boot e Configuração:** Inicie seu Raspberry Pi, conecte-o à sua rede Wi-Fi e conclua a configuração inicial.
3.  **Abra o Terminal:** Você pode fazer isso diretamente no desktop do Pi ou via SSH.
4.  **Atualize o Sistema:** É sempre uma boa prática garantir que seu sistema esteja atualizado.
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```
#### Passo 2: Conectando o Hardware

1.  **Desligue o Raspberry Pi:** Antes de conectar qualquer componente, desligue o Pi completamente.
    ```bash
    sudo shutdown -h now
    ```
2.  **Conecte o Leitor RC522:** Use a tabela de pinagem na seção "Configuração do Hardware" acima para conectar o leitor aos pinos GPIO do seu Raspberry Pi.

#### Passo 3: Instalando o Software da Jukebox

1.  **Ligue o Raspberry Pi:** Reconecte a energia para ligar o Pi.
2.  **Clone o Repositório:** Abra o terminal e clone este projeto.
    ```bash
    git clone https://github.com/rafaeltini/jukebox_rfid.git
    cd jukebox_rfid
    ```
3.  **Execute o Script de Instalação:** Este script automatiza todo o processo.
    ```bash
    bash install.sh
    ```
    - No menu, digite `1` e pressione Enter para iniciar a instalação completa.
    - O script irá instalar todas as dependências necessárias e configurar o software da Jukebox para iniciar automaticamente com o sistema.

#### Passo 4: Encontrando e Usando a Jukebox

1.  **Encontre o Endereço IP do Pi:** Você precisará do IP para acessar a interface web.
    ```bash
    hostname -I
    ```
    Anote o primeiro endereço IP que aparecer (ex: `192.168.1.15`).
2.  **Acesse a Interface:** Em outro dispositivo na mesma rede (seu computador ou celular), abra um navegador e acesse `http://<IP-do-seu-Pi>:5000`, substituindo `<IP-do-seu-Pi>` pelo endereço que você anotou.
3.  **Comece a Usar:** Agora você está pronto! Siga as instruções na seção "Como Usar" abaixo para adicionar suas músicas.

### 🎶 Como Usar

1.  **Acesse a Interface Web:** Após a instalação, o serviço iniciará automaticamente. Encontre o IP do seu Raspberry Pi e acesse `http://<IP-do-seu-Pi>:5000` em um navegador na mesma rede.
2.  **Escolha o Idioma:** Use as bandeiras 🇧🇷 / 🇺🇸 no canto superior direito para alternar o idioma da interface.
3.  **Faça o Upload de uma Música:** Na interface, arraste um arquivo MP3 para a área de upload designada.
4.  **Associe um Cartão:** Após o upload ser bem-sucedido, a interface mostrará a mensagem: *"Arquivo 'nome-da-musica.mp3' salvo. Aproxime um cartão para associar."*
5.  **Escaneie o Cartão:** Aproxime um cartão RFID do leitor. O sistema irá associar permanentemente esse cartão à música que você acabou de enviar.
6.  **Toque sua Música:** Agora, sempre que você aproximar esse cartão do leitor, a música associada começará a tocar.
7.  **Controle a Reprodução:** Use os botões de play/pause e o controle de volume na interface web para gerenciar a música.

### 📁 Estrutura do Projeto

```
.
├── app/
│   ├── main.py             # Aplicação principal (Flask), API e lógica de RFID.
│   ├── player.py           # Classe que gerencia a reprodução de áudio com pygame.
│   ├── rfid.py             # Módulo para comunicação de baixo nível com o leitor RC522.
│   ├── static/style.css    # Folha de estilos da interface web.
│   ├── template/index.html # Estrutura HTML da interface web.
│   └── translations.json   # Arquivo com as traduções da UI.
├── music/                  # Diretório onde os MP3s enviados são armazenados.
├── install.sh              # Script de instalação e configuração.
├── qr_generator.py         # Gera um QR code para acesso fácil à interface.
├── requirements.txt        # Dependências Python do projeto.
└── tags.txt                # Arquivo de texto que armazena as associações (UID -> MP3).
```

---
## 🇺🇸 English

This project transforms a Raspberry Pi into an MP3 Jukebox controlled by RFID cards. Use the web interface to upload your music, associate each song with an RFID card, and then simply tap the card on the reader to play your music.

### ✨ Features

- **RFID Playback:** Associate MP3 files with RFID cards and play them instantly.
- **Complete Web Interface:** Control playback (play/pause), adjust the volume, and see the currently playing song.
- **Multilingual Interface:** Switch between Portuguese and English with one click.
- **Music Upload:** Drag and drop your MP3 files directly into the web interface to add them to your library.
- **Simplified Card Association:** After uploading a song, the interface prompts you to scan a card to create the association.
- **Automated Installation:** The `install.sh` script configures all software dependencies, including `pygame` for audio and GPIO libraries.
- **Standalone Service:** Runs as a background service (`systemd`) that starts automatically with the Raspberry Pi.

### 📦 Components and Dependencies

This section details the hardware and software required for the project.

#### Hardware Components

- **Raspberry Pi:** The brains of the operation. Tested on a Raspberry Pi 2 W, but any newer model with Wi-Fi and GPIO pins should work.
- **MFRC522 RFID Reader:** A low-cost reader for 13.56MHz cards and tags. It's the physical interface for selecting music.
- **RFID Cards or Tags:** Any card compatible with the MIFARE Classic standard. You will need one for each song or playlist you want to add.
- **MicroSD Card:** For the operating system and music storage. A 16GB card or larger is recommended.
- **Power Supply:** A good quality USB-C or Micro USB power supply, appropriate for your Raspberry Pi model.
- **Speakers or Headphones:** To listen to the music. They can be connected to the Pi's 3.5mm audio jack.

#### Software Dependencies

The project uses the following Python libraries, which are automatically installed by the `install.sh` script:

- **Flask:** A web micro-framework used to create the server that hosts the user interface.
- **Flask-SocketIO:** Provides real-time communication between the server and the web interface, essential for instantly updating the player and RFID reader status.
- **pygame:** A multimedia library used here to efficiently play MP3 audio files.
- **mfrc522:** A low-level Python library for communicating with the MFRC522 RFID reader via the Raspberry Pi's SPI interface.
- **qrcode[pil]:** Used to generate the QR code that provides easy access to the web interface. The `[pil]` option ensures the `Pillow` image manipulation library is installed along with it.
- **zeroconf:** Allows the Jukebox to announce its presence on the local network as `rfidbox.local` using the mDNS (Bonjour/Avahi) protocol, eliminating the need to know the device's IP address.

### 🔧 Hardware Setup

#### RFID RC522 Reader Pinout
Connect the reader to the Raspberry Pi using the following GPIO pins:

| RC522 Pin  | Raspberry Pi GPIO | Pi Name     | Function              |
|------------|-------------------|-------------|-----------------------|
| SDA (CS)   | GPIO 8            | SPI0_CE0    | Chip Select           |
| SCK (CLK)  | GPIO 11           | SPI0_SCLK   | Clock                 |
| MOSI       | GPIO 10           | SPI0_MOSI   | Master Out Slave In   |
| MISO       | GPIO 9            | SPI0_MISO   | Master In Slave Out   |
| IRQ        | -                 | -           | (not used)            |
| GND        | GND               | GND         | Ground                |
| RST        | GPIO 25           | GPIO 25     | Reset                 |
| 3.3V       | 3.3V              | 3.3V        | Power                 |

**Important:** The RFID library used in this project does not utilize the `RST` pin. It can be left disconnected.

#### Optional: Waveshare WM8960 Audio HAT Setup

If you are using the **WM8960 Audio HAT** for superior audio quality, it requires a specific driver to function.

1.  **Install the HAT Driver:** In your Raspberry Pi terminal, run the following commands to download and install the Waveshare driver.
    ```bash
    git clone https://github.com/waveshare/WM8960-Audio-HAT.git
    cd WM8960-Audio-HAT
    sudo ./install.sh
    ```
2.  **Reboot the Pi:** After the installation, the system must be rebooted for the new audio driver to be loaded.
    ```bash
    sudo reboot
    ```
3.  **Verification (Optional):** After rebooting, you can check if the new sound card was detected with the command `aplay -l`. You should see a device named `wm8960-soundcard`.
4.  **Volume Control:** The HAT's system volume can be controlled using `alsamixer`. This project's web interface will control the application volume (`pygame`), which in turn uses the system's default sound device (which will now be the HAT).

**Important Note:** The driver installation instructions may vary depending on your Kernel or Raspberry Pi OS version. If you encounter issues, please refer to the [official Waveshare wiki](https://www.waveshare.com/wiki/WM8960_Audio_HAT) for troubleshooting and compatibility information.

### 🚀 Complete Installation Guide

Follow these steps to set up your Jukebox from scratch.

#### Step 1: Preparing the Raspberry Pi

1.  **Install Raspberry Pi OS:** Use the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to install the latest version of Raspberry Pi OS on an SD card.
2.  **First Boot and Setup:** Start your Raspberry Pi, connect it to your Wi-Fi network, and complete the initial setup.
3.  **Open the Terminal:** You can do this directly on the Pi's desktop or via SSH.
4.  **Update Your System:** It's always good practice to ensure your system is up to date.
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```
#### Step 2: Connecting the Hardware

1.  **Shut Down the Raspberry Pi:** Before connecting any components, shut down the Pi completely.
    ```bash
    sudo shutdown -h now
    ```
2.  **Connect the RC522 Reader:** Use the pinout table in the "Hardware Setup" section above to connect the reader to your Raspberry Pi's GPIO pins.

#### Step 3: Installing the Jukebox Software

1.  **Power On the Raspberry Pi:** Reconnect the power to turn on the Pi.
2.  **Clone the Repository:** Open the terminal and clone this project.
    ```bash
    git clone https://github.com/rafaeltini/jukebox_rfid.git
    cd jukebox_rfid
    ```
3.  **Run the Install Script:** This script automates the entire process.
    ```bash
    bash install.sh
    ```
    - In the menu, type `1` and press Enter to start the full installation.
    - The script will install all necessary dependencies and set up the Jukebox software to start automatically with the system.

#### Step 4: Finding and Using the Jukebox

1.  **Find the Pi's IP Address:** You'll need the IP to access the web interface.
    ```bash
    hostname -I
    ```
    Note the first IP address that appears (e.g., `192.168.1.15`).
2.  **Access the Interface:** On another device on the same network (your computer or phone), open a browser and go to `http://<Your-Pi-IP>:5000`, replacing `<Your-Pi-IP>` with the address you noted.
3.  **Start Using:** You're all set! Follow the instructions in the "How to Use" section below to add your music.

### 🎶 How to Use

1.  **Access the Web Interface:** After installation, the service will start automatically. Find your Raspberry Pi's IP address and go to `http://<Your-Pi-IP>:5000` in a browser on the same network.
2.  **Choose the Language:** Use the 🇧🇷 / 🇺🇸 flags in the top-right corner to switch the interface language.
3.  **Upload a Song:** In the interface, drag and drop an MP3 file into the designated upload area.
4.  **Associate a Card:** After a successful upload, the interface will display the message: *"File 'song-name.mp3' saved. Scan a card to associate."*
5.  **Scan the Card:** Tap an RFID card on the reader. The system will permanently associate that card with the song you just uploaded.
6.  **Play Your Music:** Now, whenever you tap that card on the reader, its associated song will begin to play.
7.  **Control Playback:** Use the play/pause buttons and the volume slider in the web interface to manage the music.

### 📁 Project Structure

```
.
├── app/
│   ├── main.py             # Main application (Flask), API, and RFID logic.
│   ├── player.py           # Class that manages audio playback with pygame.
│   ├── rfid.py             # Low-level communication module for the RC522 reader.
│   ├── static/style.css    # Stylesheet for the web interface.
│   ├── template/index.html # HTML structure for the web interface.
│   └── translations.json   # File with the UI translations.
├── music/                  # Directory where uploaded MP3s are stored.
├── install.sh              # Installation and setup script.
├── qr_generator.py         # Generates a QR code for easy access to the interface.
├── requirements.txt        # Python project dependencies.
└── tags.txt                # Text file that stores the associations (UID -> MP3).
```
```
