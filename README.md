# 🎶 Jukebox RFID MP3 Player

Este projeto transforma um Raspberry Pi em uma Jukebox de MP3 controlada por cartões RFID. Use a interface web para fazer upload de suas músicas, associar cada música a um cartão RFID e, em seguida, simplesmente aproxime o cartão do leitor para tocar sua música.

---

### ✨ Funcionalidades

- **Playback por RFID:** Associe arquivos MP3 a cartões RFID e toque-os instantaneamente.
- **Interface Web Completa:** Controle a reprodução (play/pause), ajuste o volume e veja a música que está tocando.
- **Upload de Músicas:** Arraste e solte seus arquivos MP3 diretamente na interface web para adicioná-los à sua biblioteca.
- **Associação de Cartões Simplificada:** Após o upload de uma música, a interface pede que você escaneie um cartão para criar a associação.
- **Instalação Automatizada:** O script `install.sh` configura todas as dependências de software, incluindo `pygame` para áudio e as bibliotecas GPIO.
- **Serviço Autônomo:** Roda como um serviço de fundo (`systemd`) que inicia automaticamente com o Raspberry Pi.

### ✅ Requisitos de Hardware

- **Raspberry Pi:** Testado com Pi 2 W, mas deve funcionar em modelos mais recentes.
- **Leitor RFID:** Leitor RC522 conectado via SPI.
- **Cartões/Tags RFID:** Compatíveis com o leitor RC522 (ex: MIFARE Classic).
- **Saída de Áudio:**
    - A saída de áudio padrão do Pi (3.5mm ou HDMI).
    - Ou um DAC HAT, como o **Waveshare HiFi DAC HAT**.

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

#### Nota sobre o Waveshare HiFi HAT
Este projeto usa o `pygame.mixer` para controlar o áudio, que por sua vez usa o sistema ALSA no Linux. O controle de volume na interface web **não** usa `amixer` e deve funcionar com qualquer dispositivo de saída padrão. Se você precisar de controle de volume via linha de comando, pode precisar identificar o nome do controle do seu HAT com o comando `amixer` e ajustar os scripts conforme necessário.

### 🚀 Instalação de Software

1.  Clone o repositório no seu Raspberry Pi:
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd jukebox_rfid
    ```
2.  Execute o script de instalação. Ele cuidará de tudo.
    ```bash
    bash install.sh
    ```
    Escolha a opção **1** no menu para uma instalação completa. O script irá instalar pacotes do sistema, dependências Python em um ambiente virtual e configurar o serviço para iniciar no boot.

### 🎶 Como Usar

1.  **Acesse a Interface Web:** Após a instalação, o serviço iniciará automaticamente. Encontre o IP do seu Raspberry Pi e acesse `http://<IP-do-seu-Pi>:5000` em um navegador na mesma rede.
2.  **Faça o Upload de uma Música:** Na interface, arraste um arquivo MP3 para a área de upload designada.
3.  **Associe um Cartão:** Após o upload ser bem-sucedido, a interface mostrará a mensagem: *"Arquivo 'nome-da-musica.mp3' salvo. Aproxime um cartão para associar."*
4.  **Escaneie o Cartão:** Aproxime um cartão RFID do leitor. O sistema irá associar permanentemente esse cartão à música que você acabou de enviar.
5.  **Toque sua Música:** Agora, sempre que você aproximar esse cartão do leitor, a música associada começará a tocar.
6.  **Controle a Reprodução:** Use os botões de play/pause e o controle de volume na interface web para gerenciar a música.

### 📁 Estrutura do Projeto

```
.
├── app/
│   ├── main.py             # Aplicação principal (Flask), API e lógica de RFID.
│   ├── player.py           # Classe que gerencia a reprodução de áudio com pygame.
│   ├── rfid.py             # Módulo para comunicação de baixo nível com o leitor RC522.
│   ├── static/style.css    # Folha de estilos da interface web.
│   └── template/index.html # Estrutura HTML da interface web.
├── music/                  # Diretório onde os MP3s enviados são armazenados.
├── install.sh              # Script de instalação e configuração.
├── qr_generator.py         # Gera um QR code para acesso fácil à interface.
├── requirements.txt        # Dependências Python do projeto.
└── tags.txt                # Arquivo de texto que armazena as associações (UID -> MP3).
```
```
