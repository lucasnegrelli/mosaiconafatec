#!/usr/bin/env python3
"""
🗂️  criar_estrutura.py
Cria automaticamente toda a árvore de pastas no Google Drive a partir do
schedule.json — dias da semana, categorias, subpastas de stories e a
subpasta /postado/ dentro de cada categoria.

É IDEMPOTENTE: rodar mais de uma vez não duplica nada. Pastas que já
existem são reaproveitadas. Pode rodar de novo sempre que adicionar
categorias novas no schedule.json.

Como rodar (uma vez só, na máquina do dev):
    export DRIVE_FOLDER_ID="id_da_pasta_raiz"
    export GOOGLE_SERVICE_ACCOUNT="$(cat caminho/para/service_account.json)"
    python criar_estrutura.py
"""

import os
import json

from googleapiclient.discovery import build
from google.oauth2 import service_account


DRIVE_FOLDER_ID = os.environ["DRIVE_FOLDER_ID"]
GOOGLE_SA_JSON  = os.environ["GOOGLE_SERVICE_ACCOUNT"]

FOLDER_MIME = "application/vnd.google-apps.folder"

# Cache para não consultar a mesma pasta duas vezes na mesma execução
_cache = {}


def get_drive():
    sa_info = json.loads(GOOGLE_SA_JSON)
    creds = service_account.Credentials.from_service_account_info(
        sa_info, scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)


def get_or_create_folder(drive, parent_id, name):
    """Retorna o ID da subpasta `name` dentro de `parent_id`, criando se necessário."""
    cache_key = (parent_id, name)
    if cache_key in _cache:
        return _cache[cache_key]

    # Procura se já existe
    safe_name = name.replace("'", "\\'")
    query = (
        f"'{parent_id}' in parents "
        f"and name='{safe_name}' "
        f"and mimeType='{FOLDER_MIME}' "
        f"and trashed=false"
    )
    result = drive.files().list(q=query, fields="files(id, name)").execute()
    files = result.get("files", [])

    if files:
        folder_id = files[0]["id"]
        status = "já existe"
    else:
        metadata = {"name": name, "mimeType": FOLDER_MIME, "parents": [parent_id]}
        folder = drive.files().create(body=metadata, fields="id").execute()
        folder_id = folder["id"]
        status = "criada ✨"

    _cache[cache_key] = folder_id
    return folder_id, status


def main():
    print("=" * 60)
    print("🗂️  Criando estrutura de pastas no Drive")
    print("=" * 60)

    drive = get_drive()

    with open("schedule.json", "r", encoding="utf-8") as f:
        schedule = json.load(f)

    # Considera apenas as chaves que são dias (ignora _leiame, configuracao, etc.)
    dias = [k for k, v in schedule.items() if isinstance(v, list) and not k.startswith("_")]

    total_criadas = 0

    for dia in dias:
        dia_id, status = get_or_create_folder(drive, DRIVE_FOLDER_ID, dia)
        print(f"\n📅 {dia}  ({status})")

        for slot in schedule[dia]:
            pasta = slot["pasta"]

            # Stories vêm com caminho aninhado, ex: "stories/10h30-reposts"
            partes = pasta.split("/")
            parent_id = dia_id
            for parte in partes:
                folder_id, st = get_or_create_folder(drive, parent_id, parte)
                if st.startswith("criada"):
                    total_criadas += 1
                parent_id = folder_id

            # Subpasta /postado/ dentro da categoria final
            _, st_post = get_or_create_folder(drive, parent_id, "postado")
            if st_post.startswith("criada"):
                total_criadas += 1

            marca = "🎬" if slot["tipo"] == "stories" else "🖼️ " if slot["tipo"] == "feed" else "📹"
            print(f"   {marca} {pasta}/  (+ /postado/)")

    print("\n" + "=" * 60)
    print(f"✅ Concluído! {total_criadas} pastas novas criadas.")
    print("   Agora é só o Trinca jogar as mídias dentro de cada categoria.")
    print("=" * 60)


if __name__ == "__main__":
    main()
