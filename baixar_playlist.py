import subprocess
import sys
import json
import re
from pathlib import Path

# ==========================================
# USO:
# python baixar_playlist.py "URL"
# ==========================================

if len(sys.argv) < 2:
    print('Use: python baixar_playlist.py "URL_DA_PLAYLIST"')
    input("ENTER...")
    sys.exit()

url = sys.argv[1]

BASE = Path(__file__).parent
PASTA = BASE / "music"
JSON_FILE = BASE / "music.json"

PASTA.mkdir(exist_ok=True)


# ==========================================
# FUNÇÕES
# ==========================================

def limpar(txt):
    if not txt:
        return "Sem título"
    return re.sub(r'\s+', ' ', txt).strip()


def salvar_json(lista):
    JSON_FILE.write_text(
        json.dumps(lista, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def rodar(cmd):
    return subprocess.run(cmd, check=True)


# ==========================================
# PEGAR INFO DA PLAYLIST
# ==========================================

print("Lendo playlist...")

cmd = [
    sys.executable, "-m", "yt_dlp",
    "--flat-playlist",
    "--dump-single-json",
    url
]

saida_json = subprocess.check_output(
    cmd,
    text=True,
    encoding="utf-8"
)

playlist = json.loads(saida_json)
videos = playlist.get("entries", [])

catalogo = []

# ==========================================
# BAIXAR ITEM POR ITEM
# ==========================================

for i, video in enumerate(videos):

    vid = video.get("id")
    titulo = limpar(video.get("title", f"Faixa {i+1}"))
    artista = limpar(video.get("channel") or video.get("uploader") or "Desconhecido")

    link = f"https://www.youtube.com/watch?v={vid}"

    nome_mp3 = "track.mp3" if i == 0 else f"track{i}.mp3"
    nome_jpg = "cover.jpg" if i == 0 else f"cover{i}.jpg"

    print(f"[{i+1}/{len(videos)}] Baixando: {titulo}")

    cmd2 = [
        sys.executable, "-m", "yt_dlp",
        "-x",
        "--audio-format", "mp3",
        "--write-thumbnail",
        "--convert-thumbnails", "jpg",
        "-o", str(PASTA / f"temp_{i}.%(ext)s"),
        link
    ]

    try:
        rodar(cmd2)
    except:
        print("Falhou:", titulo)
        continue

    # ----------------------
    # renomeia mp3
    # ----------------------
    achou_mp3 = False
    for arq in PASTA.glob(f"temp_{i}.mp3"):
        arq.rename(PASTA / nome_mp3)
        achou_mp3 = True

    if not achou_mp3:
        print("MP3 não encontrado:", titulo)
        continue

    # ----------------------
    # renomeia jpg
    # ----------------------
    cover_path = ""

    for arq in PASTA.glob(f"temp_{i}.jpg"):
        arq.rename(PASTA / nome_jpg)
        cover_path = f"music/{nome_jpg}"

    # ----------------------
    # adiciona ao json
    # ----------------------
    catalogo.append({
        "title": titulo,
        "artist": artista,
        "file": f"music/{nome_mp3}",
        "cover": cover_path
    })

    salvar_json(catalogo)

# ==========================================
# FINAL
# ==========================================

print("\nTudo concluído com sucesso.")
print("Arquivos salvos em /music")
print("music.json criado.")
input("ENTER...")