#!/usr/bin/env python3
"""
🖼️  imaging.py
Tratamento de imagem ANTES de subir pro Instagram.

Por que isso importa (e não é só estético):
  • A API do Instagram só aceita JPEG. PNG, HEIC, WEBP quebram a postagem.
    Este módulo converte tudo pra JPEG automaticamente.
  • Fotos vêm em orientações e proporções variadas. Sem normalizar, o
    Instagram corta de forma feia. Aqui ajustamos pra 4:5 (feed) ou 9:16
    (stories), preenchendo as sobras com um fundo desfocado da própria foto.
  • Conserta a rotação automática via EXIF (foto "deitada" que era retrato).
  • Opcionalmente aplica uma marca d'água discreta (logo/@ no canto).

O que este módulo de propósito NÃO faz:
  • Não aplica filtros nem "melhora" cores da obra. A foto do mosaico é o
    produto do artista — deixar um robô mexer na estética da arte é risco,
    não ganho. Normalização de formato sim; reinterpretação visual não.
"""

import io
from PIL import Image, ImageOps, ImageFilter


ASPECT_MAP = {
    "1:1":  (1080, 1080),
    "4:5":  (1080, 1350),
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
}


def _fit_with_blur_background(img, target_w, target_h):
    """Encaixa a imagem no formato alvo sem cortar, preenchendo as bordas
    com uma versão desfocada e ampliada da própria foto."""
    # Fundo: a própria imagem ampliada pra cobrir o quadro, e borrada
    bg = ImageOps.fit(img, (target_w, target_h), method=Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(40))

    # Frente: a imagem inteira cabendo dentro do quadro (sem cortar)
    fg = img.copy()
    fg.thumbnail((target_w, target_h), Image.LANCZOS)

    x = (target_w - fg.width) // 2
    y = (target_h - fg.height) // 2
    bg.paste(fg, (x, y))
    return bg


def _crop_to_aspect(img, target_w, target_h):
    """Corta a imagem central pra preencher exatamente o formato alvo."""
    return ImageOps.fit(img, (target_w, target_h), method=Image.LANCZOS)


def _apply_watermark(img, wm_cfg):
    """Cola uma marca d'água PNG num canto, com opacidade e tamanho relativos."""
    try:
        wm = Image.open(wm_cfg["arquivo"]).convert("RGBA")
    except FileNotFoundError:
        print(f"⚠️  Marca d'água não encontrada em {wm_cfg['arquivo']} — pulando.")
        return img

    # Redimensiona a marca d'água relativa à largura da imagem
    alvo_w = int(img.width * wm_cfg.get("largura_relativa", 0.18))
    ratio = alvo_w / wm.width
    wm = wm.resize((alvo_w, int(wm.height * ratio)), Image.LANCZOS)

    # Aplica opacidade
    opac = wm_cfg.get("opacidade", 0.6)
    alpha = wm.split()[3].point(lambda p: int(p * opac))
    wm.putalpha(alpha)

    margem = wm_cfg.get("margem_px", 40)
    posicoes = {
        "inferior-direita": (img.width - wm.width - margem, img.height - wm.height - margem),
        "inferior-esquerda": (margem, img.height - wm.height - margem),
        "superior-direita": (img.width - wm.width - margem, margem),
        "superior-esquerda": (margem, margem),
    }
    pos = posicoes.get(wm_cfg.get("posicao", "inferior-direita"))

    base = img.convert("RGBA")
    base.paste(wm, pos, wm)
    return base.convert("RGB")


def process_image(image_bytes, config, is_story=False):
    """Pipeline completo. Recebe os bytes originais e devolve bytes JPEG prontos.

    Se config['imagem']['processar'] for False, apenas garante JPEG e retorna.
    """
    img_cfg = config.get("imagem", {})

    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img)      # conserta rotação via EXIF
    img = img.convert("RGB")                 # garante 3 canais (descarta alpha/CMYK)

    if not img_cfg.get("processar", True):
        # Modo mínimo: só converte pra JPEG
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=90)
        out.seek(0)
        return out

    # Define o formato alvo
    chave = "formato_stories" if is_story else "formato_feed"
    aspecto = img_cfg.get(chave, "9:16" if is_story else "4:5")
    target_w, target_h = ASPECT_MAP.get(aspecto, ASPECT_MAP["4:5"])

    # Encaixa no formato
    modo = img_cfg.get("fundo_preenchimento", "blur")
    if modo == "crop":
        img = _crop_to_aspect(img, target_w, target_h)
    else:  # "blur" (padrão) — não corta nada da obra
        img = _fit_with_blur_background(img, target_w, target_h)

    # Marca d'água opcional
    wm_cfg = img_cfg.get("watermark", {})
    if wm_cfg.get("ativo", False):
        img = _apply_watermark(img, wm_cfg)

    out = io.BytesIO()
    img.save(out, format="JPEG", quality=92)
    out.seek(0)
    return out


# Teste rápido local: gera uma imagem de exemplo e roda o pipeline
if __name__ == "__main__":
    demo = Image.new("RGB", (1600, 900), (120, 80, 200))
    buf = io.BytesIO()
    demo.save(buf, format="PNG")
    buf.seek(0)

    cfg = {"imagem": {"processar": True, "formato_feed": "4:5", "fundo_preenchimento": "blur"}}
    resultado = process_image(buf.read(), cfg, is_story=False)
    saida = Image.open(resultado)
    print(f"OK — imagem 1600x900 PNG virou {saida.size} JPEG (formato 4:5)")
