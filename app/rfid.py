# Simulação de leitura RFID
def read_tag():
    return "TAG123"

def assign_playlist(tag_id, playlist_url):
    with open("tags.txt", "a") as f:
        f.write(f"{tag_id}:{playlist_url}\n")