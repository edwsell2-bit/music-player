import json
import re
from pathlib import Path

BASE = Path(__file__).parent
MUSIC = BASE / "music"
CAT = BASE / "music.json"

MUSIC.mkdir(exist_ok=True)

def clean(txt):
    return re.sub(r'[<>:"/\\|?*]', '', txt).strip()

def load():
    if CAT.exists():
        try:
            return json.loads(CAT.read_text(encoding="utf-8"))
        except:
            return []
    return []

def save(data):
    CAT.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

print("Lendo pasta music...")

items = load()

for arquivo in MUSIC.glob("*.mp3"):
    name = arquivo.stem
    title = clean(name)

    capa = MUSIC / f"{name}.jpg"

    row = {
        "title": title,
        "artist": "Desconhecido",
        "file": f"music/{arquivo.name}",
        "cover": f"music/{capa.name}" if capa.exists() else ""
    }

    if not any(x["file"] == row["file"] for x in items):
        items.append(row)

save(items)

print("music.json atualizado com sucesso.")
input("ENTER...")