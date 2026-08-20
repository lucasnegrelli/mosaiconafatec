#!/usr/bin/env python3
"""
🎨 MosaicoNaFATEC - Instagram Auto-Poster
Automatiza postagens no Instagram com legendas geradas por Claude AI.
Roda via GitHub Actions com base no schedule.json.

Autor: gerado com Claude (Anthropic) para o projeto @mosaiconafatec
"""

import os
import json
import base64
import datetime
import time
import io

import anthropic
import cloudinary
import cloudinary.uploader
import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload

import imaging  # módulo local de tratamento de imagem


def load_config(path="config.json"):
    """Carrega a identidade do negócio (nome, voz, branding, formatos)."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÃO (via variáveis de ambiente / GitHub Secrets)
# ─────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY     = os.environ["ANTHROPIC_API_KEY"]
INSTAGRAM_TOKEN       = os.environ["INSTAGRAM_ACCESS_TOKEN"]
INSTAGRAM_BUSINESS_ID = os.environ["INSTAGRAM_BUSINESS_ID"]
DRIVE_FOLDER_ID       = os.environ["DRIVE_FOLDER_ID"]
GOOGLE_SA_JSON        = os.environ["GOOGLE_SERVICE_ACCOUNT"]

# Sobrescritas para testes manuais via GitHub Actions (workflow_dispatch)
DAY_OVERRIDE  = os.environ.get("DAY_OVERRIDE",  "").strip()
HOUR_OVERRIDE = os.environ.get("HOUR_OVERRIDE", "").strip()

cloudinary.config(
    cloud_name = os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key    = os.environ["CLOUDINARY_API_KEY"],
    api_secret = os.environ["CLOUDINARY_API_SECRET"],
    secure     = True,
)

INSTAGRAM_GRAPH_URL = "https://graph.instagram.com/v25.0"
# Nota: usamos graph.instagram.com porque o app foi criado com o fluxo
# "API setup with Instagram login" (não precisa de Página do Facebook vinculada).
# Se vocês optarem pelo fluxo antigo via Página, o host correto é graph.facebook.com.


# ─────────────────────────────────────────────────────────────
# GOOGLE DRIVE
# ─────────────────────────────────────────────────────────────

def get_drive_service():
    """Autenticação com a Service Account do Google."""
    sa_info = json.loads(GOOGLE_SA_JSON)
    creds = service_account.Credentials.from_service_account_info(
        sa_info, scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)


def find_folder(drive, parent_id, name):
    """Busca uma pasta pelo nome dentro de um diretório pai.

    Aceita caminhos aninhados separados por '/', necessário para os slots de
    stories, que no schedule.json vêm como 'stories/10h30-videos-curtos'.
    """
    current = {"id": parent_id, "name": ""}
    for part in name.split("/"):
        q = (
            f"'{current['id']}' in parents "
            f"and name='{part}' "
            f"and mimeType='application/vnd.google-apps.folder' "
            f"and trashed=false"
        )
        results = drive.files().list(q=q, fields="files(id, name)").execute()
        folders = results.get("files", [])
        if not folders:
            return None
        current = folders[0]
    return current


def get_next_media(drive, category_folder_id):
    """Retorna o próximo arquivo de mídia disponível na pasta da categoria."""
    q = (
        f"'{category_folder_id}' in parents "
        f"and mimeType != 'application/vnd.google-apps.folder' "
        f"and trashed=false"
    )
    results = drive.files().list(
        q=q,
        orderBy="createdTime",
        fields="files(id, name, mimeType)",
    ).execute()
    files = results.get("files", [])

    # Filtra apenas imagens e vídeos
    media = [
        f for f in files
        if f["mimeType"].startswith("image/") or f["mimeType"].startswith("video/")
    ]
    return media[0] if media else None


def download_to_buffer(drive, file_id):
    """Baixa um arquivo do Drive para um buffer em memória."""
    request = drive.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buffer.seek(0)
    return buffer


def ensure_posted_folder(drive, category_folder_id):
    """Cria (ou localiza) a subpasta /postado/ dentro da categoria."""
    existing = find_folder(drive, category_folder_id, "postado")
    if existing:
        return existing["id"]

    folder_metadata = {
        "name": "postado",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [category_folder_id],
    }
    folder = drive.files().create(body=folder_metadata, fields="id").execute()
    return folder["id"]


def move_to_posted(drive, file_id, category_folder_id):
    """Move o arquivo para a subpasta /postado/ após postagem bem-sucedida."""
    posted_id = ensure_posted_folder(drive, category_folder_id)
    drive.files().update(
        fileId=file_id,
        addParents=posted_id,
        removeParents=category_folder_id,
        fields="id, parents",
    ).execute()
    print("📦 Arquivo movido para /postado/")


# ─────────────────────────────────────────────────────────────
# CLOUDINARY (hospedagem temporária para URLs públicas)
# ─────────────────────────────────────────────────────────────

def upload_to_cloudinary(buffer, filename, is_video=False):
    """Faz upload para Cloudinary e retorna (url_publica, public_id)."""
    resource_type = "video" if is_video else "image"
    public_id = f"mosaiconafatec/{filename.rsplit('.', 1)[0].replace(' ', '_')}"

    result = cloudinary.uploader.upload(
        buffer.read(),
        public_id=public_id,
        resource_type=resource_type,
        overwrite=True,
    )
    return result["secure_url"], public_id


def delete_from_cloudinary(public_id, is_video=False):
    """Remove a mídia do Cloudinary após postagem bem-sucedida."""
    resource_type = "video" if is_video else "image"
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    except Exception as e:
        print(f"⚠️  Cloudinary cleanup: {e}")


# ─────────────────────────────────────────────────────────────
# CLAUDE AI — ANÁLISE VISUAL E GERAÇÃO DE LEGENDA
# ─────────────────────────────────────────────────────────────

def _build_prompt(config, category_desc, post_type, com_imagem):
    """Monta o prompt da legenda a partir do config.json do negócio.
    É aqui que a automação deixa de ser 'do mosaico' e passa a servir
    qualquer nicho: tudo vem do config, nada fica cravado no código."""
    neg = config["negocio"]
    voz = config["voz"]
    hashtags_fixas = config["hashtags_fixas"]
    max_extras = config.get("max_hashtags_extras", 10)

    assinatura = voz.get("assinatura", "").strip()
    extra = voz.get("instrucoes_extra", "").strip()

    abertura = (
        f'Você é o social media de "{neg["nome"]}" ({neg["handle"]}) — '
        f'{neg["nicho"]}, criado por {neg["criador"]}. '
        f'O público é {neg.get("publico", "o público do negócio")}.'
    )
    acao = "Analise a imagem e crie" if com_imagem else "Crie"

    linhas = [
        abertura,
        "",
        f"{acao} uma legenda para o Instagram.",
        "",
        f"Contexto da categoria: {category_desc}",
        f"Tipo de post: {post_type}",
        f"Hashtags fixas que DEVEM aparecer no final: {hashtags_fixas}",
        "",
        "Diretrizes:",
        f"- Idioma: {voz['idioma']}",
        f"- Tom: {voz['tom']}",
        f"- Emojis: {voz['uso_emojis']}",
        "- Inclua uma chamada para ação natural",
        f"- Máximo de {voz.get('tamanho_max_caracteres', 2000)} caracteres",
        f"- Finalize com as hashtags fixas + até {max_extras} hashtags relevantes ao conteúdo",
    ]
    if assinatura:
        linhas.append(f"- Inclua esta assinatura ao final (antes das hashtags): {assinatura}")
    if extra:
        linhas.append(f"- {extra}")
    linhas += ["", "Responda APENAS com a legenda pronta, sem comentários adicionais."]
    return "\n".join(linhas)


def generate_caption_with_image(image_bytes, category_desc, post_type, config):
    """Analisa a imagem com Claude Vision e gera legenda personalizada pelo config."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    prompt = _build_prompt(config, category_desc, post_type, com_imagem=True)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )
    return response.content[0].text


def generate_caption_text_only(category_desc, post_type, config):
    """Gera legenda baseada apenas na descrição da categoria (para vídeos)."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = _build_prompt(config, category_desc, post_type, com_imagem=False)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# ─────────────────────────────────────────────────────────────
# INSTAGRAM GRAPH API
# ─────────────────────────────────────────────────────────────

def create_media_container(media_url, caption, post_type, is_video):
    """Cria o container de mídia no Instagram (primeiro passo da publicação)."""
    endpoint = f"{INSTAGRAM_GRAPH_URL}/{INSTAGRAM_BUSINESS_ID}/media"
    params = {"access_token": INSTAGRAM_TOKEN}

    if post_type == "stories":
        params["media_type"] = "STORIES"
        params["video_url" if is_video else "image_url"] = media_url
        # Stories não levam caption pela API
    elif post_type == "reels":
        params["media_type"] = "REELS"
        params["video_url"] = media_url
        params["caption"] = caption
    else:  # post normal (feed)
        if is_video:
            params["media_type"] = "VIDEO"
            params["video_url"] = media_url
        else:
            params["image_url"] = media_url
        params["caption"] = caption

    response = requests.post(endpoint, data=params)
    result = response.json()

    if "id" not in result:
        raise Exception(f"Erro ao criar container: {result}")

    return result["id"]


def wait_for_video_processing(container_id, max_wait_seconds=300):
    """Aguarda o Instagram processar o vídeo antes de publicar."""
    endpoint = f"{INSTAGRAM_GRAPH_URL}/{container_id}"
    print("⏳ Aguardando processamento do vídeo", end="", flush=True)

    for _ in range(max_wait_seconds // 10):
        response = requests.get(
            endpoint,
            params={"fields": "status_code", "access_token": INSTAGRAM_TOKEN},
        )
        status = response.json().get("status_code", "")

        if status == "FINISHED":
            print(" ✅")
            return
        elif status == "ERROR":
            raise Exception(f"Erro no processamento do vídeo: {response.json()}")

        print(".", end="", flush=True)
        time.sleep(10)

    raise Exception(f"Timeout: vídeo não processou em {max_wait_seconds}s")


def publish_container(container_id):
    """Publica o container no Instagram e retorna o ID do post."""
    endpoint = f"{INSTAGRAM_GRAPH_URL}/{INSTAGRAM_BUSINESS_ID}/media_publish"
    response = requests.post(
        endpoint,
        data={"creation_id": container_id, "access_token": INSTAGRAM_TOKEN},
    )
    result = response.json()

    if "id" not in result:
        raise Exception(f"Erro ao publicar: {result}")

    return result["id"]


# ─────────────────────────────────────────────────────────────
# AGENDAMENTO
# ─────────────────────────────────────────────────────────────

def get_current_day_and_time():
    """Retorna (dia_semana, HH:MM) no fuso horário de Brasília (UTC-3)."""
    now_brt = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
    days_map = {
        0: "segunda-feira",
        1: "terca-feira",
        2: "quarta-feira",
        3: "quinta-feira",
        4: "sexta-feira",
        5: "sabado",
        6: "domingo",
    }
    return days_map[now_brt.weekday()], now_brt.strftime("%H:%M")


def find_current_slot(schedule_data, day, current_time):
    """Encontra o slot da agenda para o horário atual (tolerância de ±5 min)."""
    day_slots = schedule_data.get(day, [])
    fmt = "%H:%M"
    current = datetime.datetime.strptime(current_time, fmt)

    for slot in day_slots:
        scheduled = datetime.datetime.strptime(slot["hora"], fmt)
        diff_minutes = abs((scheduled - current).total_seconds() / 60)
        if diff_minutes <= 5:
            return slot

    return None


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("🎨  MosaicoNaFATEC Auto-Poster")
    print("=" * 55)

    # Carregar agenda e identidade do negócio
    with open("schedule.json", "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    config = load_config()
    print(f"🏷️  Negócio: {config['negocio']['nome']} ({config['negocio']['handle']})")

    # Determinar dia e hora (modo teste ou produção)
    if DAY_OVERRIDE and HOUR_OVERRIDE:
        day, current_time = DAY_OVERRIDE, HOUR_OVERRIDE
        print(f"🔧 MODO TESTE — dia: {day} | hora: {current_time}")
    else:
        day, current_time = get_current_day_and_time()
        print(f"📅 Dia: {day} | Hora BRT: {current_time}")

    # Encontrar slot na agenda
    slot = find_current_slot(schedule_data, day, current_time)
    if not slot:
        print(f"ℹ️  Sem postagem agendada para {day} às {current_time}. Nada a fazer.")
        return

    print(f"📌 Categoria: {slot['pasta']} | Tipo: {slot['tipo']}")

    # ── Google Drive ──────────────────────────────────────────
    drive = get_drive_service()

    day_folder = find_folder(drive, DRIVE_FOLDER_ID, day)
    if not day_folder:
        raise Exception(f"Pasta do dia '{day}' não encontrada no Drive")

    category_folder = find_folder(drive, day_folder["id"], slot["pasta"])
    if not category_folder:
        print(f"⚠️  Pasta '{slot['pasta']}' não encontrada. Pulando.")
        return

    media_file = get_next_media(drive, category_folder["id"])
    if not media_file:
        print(f"⚠️  Nenhuma mídia disponível em '{slot['pasta']}'. Pulando.")
        return

    is_video = media_file["mimeType"].startswith("video/")
    print(f"📁 Arquivo: {media_file['name']} ({'vídeo' if is_video else 'imagem'})")

    # ── Download ──────────────────────────────────────────────
    print("⬇️  Baixando do Drive...")
    buffer = download_to_buffer(drive, media_file["id"])

    is_story = slot["tipo"] == "stories"

    # ── Tratamento de imagem (só para imagens) ────────────────
    if not is_video:
        print("🎨 Tratando imagem (formato/JPEG/marca d'água)...")
        raw = buffer.read()
        buffer = imaging.process_image(raw, config, is_story=is_story)

    # ── Cloudinary ────────────────────────────────────────────
    print("☁️  Enviando para Cloudinary...")
    public_url, cloudinary_id = upload_to_cloudinary(buffer, media_file["name"], is_video)
    print(f"   URL pública: {public_url}")

    # ── Claude AI — Legenda ───────────────────────────────────
    print("🤖 Gerando legenda com Claude AI...")
    if is_video:
        caption = generate_caption_text_only(
            slot.get("descricao", ""), slot["tipo"], config
        )
    else:
        buffer.seek(0)
        image_bytes = buffer.read()
        caption = generate_caption_with_image(
            image_bytes, slot.get("descricao", ""), slot["tipo"], config
        )
    print(f"✍️  Legenda: {caption[:120].strip()}...")

    # ── Instagram ─────────────────────────────────────────────
    print(f"📱 Criando container ({slot['tipo']})...")
    container_id = create_media_container(public_url, caption, slot["tipo"], is_video)

    if is_video:
        wait_for_video_processing(container_id)

    print("🚀 Publicando no Instagram...")
    post_id = publish_container(container_id)
    print(f"✅ Publicado! Post ID: {post_id}")

    # ── Limpeza ───────────────────────────────────────────────
    move_to_posted(drive, media_file["id"], category_folder["id"])
    delete_from_cloudinary(cloudinary_id, is_video)

    print("=" * 55)
    print("🎉 Postagem concluída com sucesso!")
    print("=" * 55)


if __name__ == "__main__":
    main()
