# 📋 Plano de Execução — Automação @mosaiconafatec

**Objetivo do sábado:** deixar o robô de postagens rodando sozinho, publicando a mídia certa, na pasta certa, no horário certo, com legenda gerada por IA.

**Quem faz o quê:**
- 🔧 **Dev** = configurações técnicas (Meta, Google Cloud, GitHub)
- 🎨 **Trinca** = organização das pastas/mídias + decisões de conteúdo
- 👤 **Você** = ponte entre os dois, validação do fluxo geral

---

## ⏱️ Linha do tempo sugerida

| Bloco | Duração | O que acontece |
|---|---|---|
| **1. Manhã** | ~1h30 | FASE 1 (Meta) + FASE 2 (Google) + FASE 3 (Cloudinary) — enquanto isso, Trinca segue populando as pastas |
| **2. Início da tarde** | ~45 min | FASE 4 (GitHub + Secrets) |
| **3. Tarde** | ~1h | FASE 5 (conferir pastas reais x `schedule.json`) — **esse é o passo que mais pode estourar o tempo**, depende de quanto o Trinca já organizou |
| **4. Fim da tarde** | ~45 min | FASE 6 (workflow) + FASE 7 (teste controlado) |
| **5. Noite** | — | FASE 8 (go-live) + ajustes finos |

Total ativo: **~4h**. Reserve mais 1-2h de gordura para imprevistos — é normal a primeira integração com a API da Meta dar uns erros de permissão na primeira tentativa.

---

## ⚠️ FASE 0 — Ler antes de começar (decisões importantes)

Pesquisei a documentação oficial da Meta e do GitHub agora (jun/2026) para confirmar tudo abaixo — são pontos que mudam o plano se ignorados.

### 1. Vocês NÃO precisam de Página do Facebook vinculada
A Meta tem dois jeitos de configurar a API do Instagram. O jeito antigo (que a maioria dos tutoriais na internet ainda ensina) exige uma Página do Facebook conectada à conta do Instagram. Desde 2024 existe o **"API setup with Instagram login"**, que loga direto com a conta do Instagram — essa configuração de API não exige que uma Página do Facebook esteja vinculada à conta profissional do Instagram. É esse caminho que vamos usar — mais rápido para fazer num sábado só.

### 2. Não precisam esperar "Aprovação de App" da Meta
Como o Trinca vai usar o app só para publicar na própria conta dele (`@mosaiconafatec`), basta adicioná-lo como conta de teste/admin do app — isso já libera o token para postar de verdade, sem passar pelo processo de App Review (que leva semanas e só é necessário se o app for usado por contas de terceiros).

### 3. Stories com enquete/pergunta NÃO dá pra automatizar
A API permite publicar stories estáticos (foto ou vídeo simples) via `media_type=STORIES`, mas **não** permite adicionar figurinhas interativas (enquete, caixa de pergunta, quiz). Isso é uma limitação da própria API, não nossa.

➡️ **Decisão prática que já apliquei no `schedule.json`:** separei os itens de Stories de cada dia em dois grupos:
- **Automatizáveis** (vídeos curtos, reposts, bastidores) → entram no fluxo normal, 2 horários sugeridos por dia (10h30 e 16h30, ajustável)
- **Manuais** (enquetes, perguntas, quiz) → o Trinca posta direto pelo app do Instagram. Listei quais são quais no final deste documento.

### 4. Limite de publicações por dia
O limite oficial atual é 100 publicações via API a cada 24 horas (carrossel conta como uma publicação só), mas encontrei relatos de desenvolvedores enfrentando limites mais restritivos na prática. O dia mais cheio de vocês (quinta-feira) tem 18 posts automatizados — folga confortável mesmo no cenário mais conservador. Ainda assim, vamos configurar uma verificação do limite real da conta de vocês via API antes do go-live (passo incluído na FASE 7).

### 5. Repositório do GitHub: público
GitHub Actions roda de graça e sem limite de minutos em **repositórios públicos**. Em repositório privado, o plano gratuito dá só 2.000 minutos/mês — e como o robô vai checar o horário a cada 15 minutos, 24h por dia, é fácil estourar essa cota. Como nenhum dado sensível vai ficar no código (as credenciais ficam em "Secrets", que são sempre privados mesmo em repo público), recomendo **repositório público**.

### 6. Token de acesso expira
O token de acesso de longa duração dura 60 dias. Vou indicar no passo a passo como gerá-lo e deixei uma nota de calendário pra vocês renovarem — depois, se quiserem, automatizamos a renovação também.

### 7. Horários de virada de dia (00h00 / 01h00)
Em quarta, quinta, sexta e domingo a pauta de vocês tem posts marcados para 00h00 e quinta tem um até a 01h00. Tecnicamente isso já é "o dia seguinte" no relógio. Deixei esses itens dentro do dia editorial a que pertencem (ex: o post de 00h00 da quinta fica nos dados de quinta-feira) — o desenvolvedor só precisa saber que, ao rodar às 00h05 de uma sexta-feira (calendário), o robô deve checar a agenda de **quinta-feira**, não de sexta. É um ajuste de poucas linhas, já vou sinalizar onde no `main.py`.

---

## 🔧 FASE 1 — Criar o App no Meta for Developers
**Quem:** Trinca (login) + Dev (configuração) · **Tempo:** ~40 min

1. Acesse [developers.facebook.com/apps](https://developers.facebook.com/apps) logado com a conta do Facebook do Trinca (pode ser pessoal, não precisa ser Página).
2. Clique em **Create App** (canto superior direito).
3. Em "Connect a business", pode **pular por agora** (Next) — só é obrigatório se quiserem publicar o app para outras contas usarem.
4. Em "Select your use case", escolha **Other** → Next.
5. Em "Select your app type", escolha **Business** → Next.
6. Preencha nome do app (ex: `MosaicoFatecBot`) e e-mail de contato → Next.
7. Você cai no painel do app. Role até achar o produto **Instagram** → clique **Set up**.
8. O sistema já adiciona automaticamente o **"API setup with Instagram login"** — é esse que queremos (não cliquem em "API setup with Facebook login").
9. Na seção **"Generate access tokens"**, clique em **Add Account**, faça login com a conta `@mosaiconafatec`, autorize.
10. Depois de logado, a tela mostra o **Instagram User ID** e um botão para **gerar o token de acesso**. Copie e guarde os dois em lugar seguro (vão virar Secrets no GitHub na FASE 4):
    - `INSTAGRAM_BUSINESS_ID` → o ID numérico
    - Token gerado → ainda precisa virar de longa duração (próximo passo)

### Trocar o token por um de longa duração (60 dias)
O token gerado no painel é curto. Para trocar por um de 60 dias, façam essa chamada (pode ser direto no navegador ou via `curl`):

```
GET https://graph.instagram.com/access_token
    ?grant_type=ig_exchange_token
    &client_secret=SEU_APP_SECRET
    &access_token=TOKEN_CURTO_GERADO_NO_PASSO_ANTERIOR
```

> `SEU_APP_SECRET` fica em **App settings → Basic**, no painel do app.

A resposta traz o `access_token` novo (válido por 60 dias) — esse é o `INSTAGRAM_ACCESS_TOKEN` que vai para os Secrets.

✅ **Checkpoint:** vocês devem sair desta fase com 2 valores anotados: `INSTAGRAM_BUSINESS_ID` e `INSTAGRAM_ACCESS_TOKEN` (o de 60 dias).

---

## ☁️ FASE 2 — Acesso ao Google Drive (Service Account)
**Quem:** Dev · **Tempo:** ~20 min

1. Acesse [console.cloud.google.com](https://console.cloud.google.com), crie um projeto novo (ex: `mosaiconafatec-bot`).
2. No menu lateral, vá em **APIs e serviços → Biblioteca**, procure **Google Drive API** e clique **Ativar**.
3. Vá em **APIs e serviços → Credenciais → Criar credenciais → Conta de serviço**.
4. Dê um nome (ex: `bot-postagem`), clique **Concluir** (não precisa de papéis/permissões nesta tela).
5. Clique na conta de serviço criada → aba **Chaves → Adicionar chave → Criar nova chave → JSON**. Um arquivo `.json` será baixado — **esse arquivo inteiro** vira o Secret `GOOGLE_SERVICE_ACCOUNT`.
6. Abra o arquivo JSON baixado e copie o campo `"client_email"` (algo como `bot-postagem@mosaiconafatec-bot.iam.gserviceaccount.com`).
7. No **Google Drive**, abra a pasta raiz do projeto (a que você já criou e o Trinca está populando) → botão **Compartilhar** → cole o e-mail da conta de serviço → permissão **Editor** → Enviar.
8. Pegue o **ID da pasta**: está na URL quando você abre a pasta no navegador —
   `drive.google.com/drive/folders/`**`AQUI_ESTA_O_ID`**. Esse é o `DRIVE_FOLDER_ID`.

✅ **Checkpoint:** vocês têm o arquivo `.json` da conta de serviço e o `DRIVE_FOLDER_ID`.

---

## 🌉 FASE 3 — Cloudinary (ponte para URLs públicas)
**Quem:** Dev · **Tempo:** ~10 min

**Por que isso é necessário:** a API do Instagram exige uma URL pública direta da imagem/vídeo (ela mesma busca o arquivo nessa URL). Um link de compartilhamento do Google Drive não funciona bem para isso. Por isso o fluxo baixa o arquivo do Drive, sobe rapidinho para o Cloudinary (que gera uma URL pública limpa), o Instagram busca de lá, e depois apagamos do Cloudinary.

1. Crie uma conta grátis em [cloudinary.com](https://cloudinary.com).
2. No painel (Dashboard), copie os 3 valores que já aparecem prontos:
   - `Cloud name` → `CLOUDINARY_CLOUD_NAME`
   - `API Key` → `CLOUDINARY_API_KEY`
   - `API Secret` → `CLOUDINARY_API_SECRET`

✅ O plano gratuito (25GB) é mais que suficiente — os arquivos ficam lá só segundos, até a postagem confirmar.

---

## 🐙 FASE 4 — Repositório no GitHub + Secrets
**Quem:** Dev · **Tempo:** ~25 min

1. Crie um repositório novo, **público**, ex: `mosaiconafatec-bot`.
2. Suba os arquivos que já deixei prontos para vocês (estão no pacote que vou compartilhar):
   - `main.py`
   - `requirements.txt`
   - `schedule.json`
   - o conteúdo de `.github-workflows-postar.yml` deve ir para o caminho `.github/workflows/postar.yml` dentro do repositório (crie essa pasta exatamente assim)
3. Vá em **Settings → Secrets and variables → Actions → New repository secret** e cadastre, um por um:

| Nome do Secret | Valor |
|---|---|
| `ANTHROPIC_API_KEY` | sua chave da API da Anthropic |
| `INSTAGRAM_ACCESS_TOKEN` | token de 60 dias da FASE 1 |
| `INSTAGRAM_BUSINESS_ID` | ID numérico da FASE 1 |
| `DRIVE_FOLDER_ID` | ID da pasta raiz da FASE 2 |
| `GOOGLE_SERVICE_ACCOUNT` | conteúdo **inteiro** do arquivo `.json` da FASE 2 (copiar e colar todo o JSON) |
| `CLOUDINARY_CLOUD_NAME` | da FASE 3 |
| `CLOUDINARY_API_KEY` | da FASE 3 |
| `CLOUDINARY_API_SECRET` | da FASE 3 |

✅ **Checkpoint:** 8 secrets cadastrados, arquivos no repositório.

---

## 📁 FASE 5 — Conferir a estrutura real de pastas
**Quem:** Você + Trinca · **Tempo:** ~30-60 min (o que mais pode variar)

Eu já transformei a pauta editorial completa que você me mandou no arquivo `schedule.json` — está pronto, com os 7 dias, ~15 categorias por dia, descrição de cada uma (para a IA usar de contexto na legenda) e horário.

**O que falta é só uma conferência:** o nome da pasta que está no `schedule.json` (campo `"pasta"`) precisa ser **idêntico** ao nome real da subpasta que o Trinca já criou no Drive.

No `schedule.json`, usei este padrão de nome: `HHhMM-tema-em-slug`, por exemplo:
```
08h00-corte-de-pastilhas
12h00-alunos-trabalhando
21h00-relato-do-projeto
```

**Passo a passo:**
1. Abram a pasta `segunda-feira` no Drive lado a lado com o `schedule.json`.
2. Para cada uma das 13 subpastas de conteúdo + 2 de stories, confiram se o nome bate com o campo `"pasta"` do JSON.
3. Se o Trinca nomeou diferente (ex: `Corte_pastilhas` em vez de `08h00-corte-de-pastilhas`), **não precisa renomear nada no Drive** — só editem o valor do campo `"pasta"` no JSON para o nome real.
4. Repitam para os outros 6 dias.

> 💡 Dica para ir mais rápido: peçam pro Trinca exportar a lista de nomes de pasta de cada dia (clique direito na pasta do dia → "Listar conteúdo" ou um print mesmo) e usem isso como checklist, em vez de abrir pasta por pasta no navegador.

✅ **Checkpoint:** `schedule.json` com os nomes de pasta 100% batendo com o Drive real.

---

## ⚙️ FASE 6 — Ativar o agendamento automático
**Quem:** Dev · **Tempo:** ~15 min

O workflow (`postar.yml`) já está configurado para rodar a cada 15 minutos, o ano inteiro, checando se há algo agendado para aquele exato horário (com tolerância de 5 min para cima ou para baixo, pra absorver pequenos atrasos do GitHub).

Único ponto de atenção: o cron do GitHub roda em **UTC**, mas o `main.py` já faz a conversão para horário de Brasília internamente — não precisa mexer em nada aqui, só confirmar que o workflow está ativo na aba **Actions** do repositório.

---

## 🧪 FASE 7 — Teste controlado (antes de ir ao ar de verdade)
**Quem:** Todos · **Tempo:** ~30-45 min

Não esperem o horário real — testem na hora, usando o disparo manual:

1. No repositório, aba **Actions** → workflow **"Postagem Automática - Mosaico na FATEC"** → botão **Run workflow**.
2. Preencham `dia` (ex: `segunda-feira`) e `hora` (ex: `08:00`) com um slot que já tenha mídia na pasta.
3. Rodem e acompanhem o log em tempo real (clicando no job que aparece).
4. Confirmem, nessa ordem:
   - ✅ Baixou o arquivo certo do Drive
   - ✅ Gerou uma legenda que faz sentido com a mídia
   - ✅ O post realmente apareceu no Instagram
   - ✅ O arquivo foi movido para a subpasta `/postado/`
5. **Verifiquem o limite real de publicações da conta** antes do go-live, consultando o endpoint oficial:
   ```
   GET https://graph.instagram.com/v25.0/{INSTAGRAM_BUSINESS_ID}/content_publishing_limit
       ?access_token={INSTAGRAM_ACCESS_TOKEN}
   ```
   Isso mostra quantas publicações a conta de vocês já fez nas últimas 24h e qual o teto real.
6. Testem também um item do tipo `stories` e, se já tiver vídeo numa pasta, um item `reels`.

Se algo falhar, o erro mais comum nessa primeira tentativa costuma ser permissão (token sem o escopo certo, ou a Service Account sem acesso à pasta) — o log do GitHub Actions mostra a mensagem de erro exata da API, o que ajuda a identificar rápido.

---

## 🚀 FASE 8 — Go-live
**Quem:** Todos

1. Confirmem que o workflow está ativo (não pausado) na aba Actions.
2. Nas primeiras 24-48h, deem uma olhada de vez em quando no histórico de execuções (Actions → lista de runs) — verde é sucesso, vermelho é falha.
3. Marquem no calendário: **renovar o token em ~55 dias** (antes dos 60 dias de validade).
4. Combinem entre vocês quem vai postar manualmente os stories interativos (enquetes/perguntas) listados abaixo.

---

## 📌 Anexo A — O que já está pronto no pacote de arquivos

| Arquivo | O que é |
|---|---|
| `main.py` | O script que faz o fluxo completo (Drive → Cloudinary → Claude → Instagram) |
| `requirements.txt` | Lista de dependências Python |
| `schedule.json` | Sua pauta editorial completa, já estruturada (109 slots automatizáveis) |
| `.github-workflows-postar.yml` | O agendador — mover para `.github/workflows/postar.yml` no repo |

## 📌 Anexo B — Itens de Stories que precisam ser postados manualmente

Estes contêm figurinha interativa (enquete/pergunta/quiz) e a API não publica isso — fica para o Trinca postar direto no app:

| Dia | Itens manuais |
|---|---|
| Segunda | Enquetes, Perguntas |
| Terça | Enquetes, Perguntas |
| Quarta | Enquete sobre combinação de cores, Escolha entre dois detalhes, Perguntas sobre técnicas |
| Quinta | Perguntas sobre o ateliê |
| Sexta | Quiz sobre mosaico, Perguntas para a próxima semana |
| Sábado | Caixa de perguntas sobre mosaico |
| Domingo | Votação das obras detalhadas |

## 📌 Anexo C — Perguntas para decidirem antes do go-live

1. Os 2 horários sugeridos para stories automatizados (10h30 e 16h30) servem, ou preferem outros?
2. Querem que eu configure também a renovação automática do token (evita ter que lembrar manualmente a cada 60 dias)?
3. As legendas geradas pela IA devem ter alguma assinatura fixa (ex: menção ao @trinca_mosaico, link na bio, etc.) além das hashtags?

---

Qualquer uma dessas fases, se travar em algum erro específico durante a execução, me chama que a gente resolve o pedaço técnico na hora.
