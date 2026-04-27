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

def obter_proximo_indice():
    """Verifica a pasta e retorna o próximo número disponível"""
    maior_indice = -1
    if (PASTA / "track.mp3").exists():
        maior_indice = 0
    for arq in PASTA.glob("track*.mp3"):
        match = re.search(r'track(\d+)\.mp3', arq.name)
        if match:
            num = int(match.group(1))
            if num > maior_indice:
                maior_indice = num
    return maior_indice + 1

# ==========================================
# PEGAR INFO DA PLAYLIST E CARREGAR EXISTENTES
# ==========================================

# Carrega catálogo para verificar duplicados e manter o histórico
links_existentes = set()
if JSON_FILE.exists():
    try:
        catalogo = json.loads(JSON_FILE.read_text(encoding="utf-8"))
        # Extrai o ID do vídeo da URL salva para comparação precisa
        for item in catalogo:
            if "url" in item:
                links_existentes.add(item["url"])
    except:
        catalogo = []
else:
    catalogo = []

print("Lendo playlist...")

cmd = [
    sys.executable, "-m", "yt_dlp",
    "--flat-playlist",
    "--dump-single-json",
    url
]

try:
    saida_json = subprocess.check_output(cmd, text=True, encoding="utf-8")
    playlist = json.loads(saida_json)
    videos = playlist.get("entries", [])
except Exception as e:
    print(f"Erro ao ler playlist: {e}")
    sys.exit()

# ==========================================
# BAIXAR ITEM POR ITEM
# ==========================================

proximo_i = obter_proximo_indice()

for v_idx, video in enumerate(videos):
    
    vid = video.get("id")
    link_completo = f"https://www.youtube.com/watch?v={vid}"

    # --- VERIFICAÇÃO DE DUPLICADO ---
    if link_completo in links_existentes:
        print(f"[-] Pulando (já baixado): {video.get('title')}")
        continue
    # --------------------------------

    titulo = limpar(video.get("title", f"Faixa {v_idx+1}"))
    artista = limpar(video.get("channel") or video.get("uploader") or "Desconhecido")

    indice_atual = proximo_i
    nome_mp3 = "track.mp3" if indice_atual == 0 else f"track{indice_atual}.mp3"
    nome_jpg = "cover.jpg" if indice_atual == 0 else f"cover{indice_atual}.jpg"

    print(f"[{v_idx+1}/{len(videos)}] Baixando para {nome_mp3}: {titulo}")

    cmd2 = [
        sys.executable, "-m", "yt_dlp",
        "-x",
        "--audio-format", "mp3",
        "--write-thumbnail",
        "--convert-thumbnails", "jpg",
        "-o", str(PASTA / f"temp_download.%(ext)s"),
        link_completo
    ]

    try:
        rodar(cmd2)
        
        # Renomeia MP3
        mp3_temp = PASTA / "temp_download.mp3"
        if mp3_temp.exists():
            mp3_temp.replace(PASTA / nome_mp3)
        else:
            continue

        # Renomeia JPG
        cover_path = ""
        jpg_temp = PASTA / "temp_download.jpg"
        if jpg_temp.exists():
            jpg_temp.replace(PASTA / nome_jpg)
            cover_path = f"music/{nome_jpg}"

        # Adiciona ao catálogo incluindo a URL para futuras verificações
        catalogo.append({
            "title": titulo,
            "artist": artista,
            "file": f"music/{nome_mp3}",
            "cover": cover_path,
            "url": link_completo
        })

        salvar_json(catalogo)
        
        # Incrementa o índice global apenas após o sucesso
        proximo_i += 1

    except Exception as e:
        print(f"Falhou ao baixar {titulo}: {e}")
        continue

# ==========================================
# FINAL
# ==========================================

print("\nTudo concluído com sucesso.")
input("ENTER...")
