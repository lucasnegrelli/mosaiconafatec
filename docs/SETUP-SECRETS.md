# Passo a passo dos 7 secrets

Todos vão em: https://github.com/lucasnegrelli/mosaiconafatec/settings/secrets/actions
→ **New repository secret** → cola o nome exato e o valor → **Add secret**.

O nome tem que bater **exatamente** (maiúsculas, underscores). Um nome errado
faz o robô quebrar com "KeyError".

---

## 1. GOOGLE_SERVICE_ACCOUNT

Comece por este, porque ele gera o e-mail que você vai usar pra compartilhar a
pasta do Drive.

1. Vá em https://console.cloud.google.com/
2. No topo, crie um projeto novo (nome: `mosaico-na-fatec`, por exemplo)
3. Com o projeto selecionado, ative a API do Drive:
   **APIs e serviços > Biblioteca** → busque **Google Drive API** → **Ativar**
4. **APIs e serviços > Credenciais** → **Criar credenciais** →
   **Conta de serviço**
   - Nome: `mosaico-poster`
   - Pode pular as etapas 2 e 3 (permissões e usuários) — clique em Concluir
5. Clique na conta de serviço recém-criada → aba **Chaves** →
   **Adicionar chave > Criar nova chave** → tipo **JSON** → Criar
6. Um arquivo `.json` baixa no seu computador. Abra no bloco de notas.
7. **Copie o conteúdo inteiro do arquivo** (do `{` até o `}` final, tudo) e cole
   no campo Secret do GitHub, com o nome `GOOGLE_SERVICE_ACCOUNT`.

   Não é só o e-mail nem só a chave — é o JSON completo, de uma vez.

### Agora sim: compartilhar a pasta

Dentro desse JSON tem uma linha assim:

```
"client_email": "mosaico-poster@mosaico-na-fatec-123456.iam.gserviceaccount.com",
```

Copie esse e-mail. Vá na pasta **MosaicoNaFATEC** no Drive:

https://drive.google.com/drive/folders/1_r6OVG-R-B8_oEhZrxiC0KVYwCW_jg-x

Botão direito → **Compartilhar** → cola o e-mail → permissão **Editor** →
desmarque "Notificar pessoas" (é um robô, não lê e-mail) → Enviar.

Editor, não Leitor: o script precisa mover os arquivos pra subpasta `postado/`
depois de publicar.

---

## 2. ANTHROPIC_API_KEY

1. https://console.anthropic.com/settings/keys
2. **Create Key** → dá um nome (`mosaico-poster`) → copia
3. Cola no GitHub como `ANTHROPIC_API_KEY`

A chave começa com `sk-ant-`. Ela só aparece uma vez — se perder, cria outra.

Custo: o script usa o Haiku, que é o modelo mais barato. Umas 100 legendas por
semana sai por centavos. Mas coloque um limite de gasto em
**Settings > Limits** pra dormir tranquilo.

---

## 3, 4 e 5. Cloudinary (3 secrets)

O Cloudinary serve só de "ponte": o Instagram exige uma URL pública da imagem,
e o script apaga o arquivo de lá logo depois de postar. O plano gratuito dá e
sobra.

1. Crie a conta em https://cloudinary.com/users/register_free
2. Entre no **Dashboard** (a primeira tela depois do login)
3. Lá tem um bloco com três valores. Copie cada um pro secret correspondente:

| No Cloudinary aparece como | Nome do secret no GitHub |
|---|---|
| Cloud Name | `CLOUDINARY_CLOUD_NAME` |
| API Key | `CLOUDINARY_API_KEY` |
| API Secret (precisa clicar no olho pra revelar) | `CLOUDINARY_API_SECRET` |

O Cloud Name é uma palavra curta, tipo `dxk2p9abc`. A API Key é um número longo.
O Secret é uma sequência de letras e números.

---

## 6 e 7. Instagram (token + business ID)

Esta é a parte mais chata. Requisitos antes de começar:

- A conta @mosaiconafatec precisa estar como **Profissional** (Empresa ou
  Criador de conteúdo) — dá pra mudar em Configurações do Instagram > Tipo de conta
- Você precisa de uma conta no Facebook para criar o app (não precisa vincular
  Página nenhuma, só a conta de desenvolvedor)

Passos:

1. https://developers.facebook.com/ → **Meus apps** → **Criar app**
2. Caso de uso: escolha a opção relacionada ao **Instagram** / "Outro" → tipo
   **Empresa**
3. No painel do app, adicione o produto **Instagram**
4. Vá em **Instagram > Configuração da API com login do Instagram**
   (em inglês: *API setup with Instagram login*)

   ⚠️ **Não** escolha a opção com login do Facebook — o `main.py` está escrito
   para o fluxo do Instagram (`graph.instagram.com`). Se você usar o outro
   fluxo, o host muda e o script não funciona.

5. No passo **"Gerar token de acesso"**, clique em conectar e faça login com a
   conta @mosaiconafatec. Vai aparecer:
   - um **token de acesso** (string longa, começa com `IGAA...`) →
     secret `INSTAGRAM_ACCESS_TOKEN`
   - o **ID da conta do Instagram** (número, ~17 dígitos) →
     secret `INSTAGRAM_BUSINESS_ID`

### Sobre a validade do token

O token que aparece nessa tela dura **60 dias**. Depois disso o robô para de
postar — e ele para em silêncio, sem avisar ninguém. Vale colocar um lembrete
no calendário pra renovar antes de vencer, ou me pedir depois pra montar uma
rotina que renova sozinha (a API tem um endpoint de refresh).

---

## Conferindo se deu certo

Depois de cadastrar os 8 (os 7 acima + o `DRIVE_FOLDER_ID` que já está lá):

1. Coloque **uma foto** numa pasta de teste, por exemplo
   `segunda-feira/08h00-corte-de-pastilhas/`
2. Vá na aba **Actions** do repositório
3. Clique no workflow **"Postagem Automática - Mosaico na FATEC"**
4. **Run workflow** → preencha `dia` = `segunda-feira` e `hora` = `08:00` → Run
5. Acompanhe o log. Se der tudo certo, aparece `🎉 Postagem concluída` e a foto
   sai no Instagram (e some da pasta, indo pra `postado/`).

### Erros mais prováveis

| O que aparece no log | O que é |
|---|---|
| `KeyError: 'ALGUMA_COISA'` | Faltou cadastrar esse secret, ou o nome está diferente |
| `Pasta do dia 'segunda-feira' não encontrada` | A pasta do Drive não foi compartilhada com a service account |
| `Erro ao criar container: ... OAuthException` | Token do Instagram inválido ou vencido |
| `Nenhuma mídia disponível` | Não é erro — a pasta está vazia, ele só pulou |
