# Mosaico na FATEC — Auto-poster

Repositório: https://github.com/lucasnegrelli/mosaiconafatec
Pasta no Drive: **Trinca > MosaicoNaFATEC** (`1_r6OVG-R-B8_oEhZrxiC0KVYwCW_jg-x`)

## Como funciona

O GitHub Actions roda a cada 15 minutos. Ele olha o `schedule.json`, vê se tem
alguma postagem marcada para aquele horário (fuso de Brasília) e, se tiver:

1. Procura a pasta `<dia-da-semana>/<horário>-<categoria>` no Drive
2. Pega o arquivo mais antigo que ainda não foi postado
3. Sobe no Cloudinary para gerar um link público temporário
4. Gera a legenda com o Claude (analisando a imagem, quando é foto)
5. Publica no Instagram
6. Move o arquivo para a subpasta `postado/` e limpa o Cloudinary

Se a pasta estiver vazia, ele simplesmente pula — não quebra nada.

## O que você faz no dia a dia

Só jogar as fotos e vídeos nas pastas certas do Drive. Cada pasta tem o nome do
horário + o tema. Exemplo:

```
MosaicoNaFATEC/
  segunda-feira/
    08h00-corte-de-pastilhas/     <- fotos de corte de pastilha aqui
    12h00-alunos-trabalhando/
    stories/
      10h30-videos-curtos/
```

Pode colocar vários arquivos na mesma pasta — ele posta um por vez, na ordem em
que foram enviados, e vai consumindo ao longo das semanas.

## Falta configurar (secrets do GitHub)

Em **Settings > Secrets and variables > Actions > New repository secret**:

| Secret | Onde pegar |
|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com > API Keys |
| `INSTAGRAM_ACCESS_TOKEN` | Meta for Developers > seu app > API setup with Instagram login |
| `INSTAGRAM_BUSINESS_ID` | mesma tela do token |
| `GOOGLE_SERVICE_ACCOUNT` | JSON inteiro da service account (Google Cloud Console) |
| `CLOUDINARY_CLOUD_NAME` | dashboard do Cloudinary |
| `CLOUDINARY_API_KEY` | dashboard do Cloudinary |
| `CLOUDINARY_API_SECRET` | dashboard do Cloudinary |

`DRIVE_FOLDER_ID` já está cadastrado.

**Importante:** depois de criar a service account, compartilhe a pasta
`MosaicoNaFATEC` do Drive com o e-mail dela (algo como
`nome@projeto.iam.gserviceaccount.com`), com permissão de **Editor** — senão o
script não enxerga nem consegue mover os arquivos para `postado/`.

## Testar sem esperar o horário

Aba **Actions** > "Postagem Automática - Mosaico na FATEC" > **Run workflow**.
Preencha `dia` (ex: `segunda-feira`) e `hora` (ex: `08:00`) para forçar um slot.

## Observação sobre o token do Instagram

O token de acesso do Instagram expira (60 dias no fluxo de longa duração). Vale
anotar no calendário para renovar, ou o robô para de postar silenciosamente.
