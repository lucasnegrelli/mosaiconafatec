# Roteiro do dia — setup no notebook do Trinca

Documento seu. O dele é o `GUIA-TRINCA.md` / `guia-trinca.html`.

Objetivo do dia: o note dele sai rodando sozinho — Claude instalado e
autorizado, projeto na máquina, organizador funcionando, robô publicando.

---

## Antes de sair de casa

Manda essa lista pra ele agora, pra ele separar:

- [ ] Senha do **Gmail** dele (a senha mesmo, não a salva no navegador) + celular se tiver 2FA
- [ ] Senha do **Instagram** @mosaiconafatec + celular pra autorizar
- [ ] Conta no **Facebook** (pode ser pessoal — precisa pra criar o app da Meta)
- [ ] **Cartão** dele
- [ ] O **cabo** do celular
- [ ] Deixar o celular **com bateria** e não apagar nada dos takes

Você leva:
- [ ] Este roteiro em PDF no celular (caso o wi-fi lá esteja ruim)
- [ ] A pasta `Trinca` num pendrive — evita depender de download

---

## Decisões pra fechar antes (não resolva no meio)

**1. Contas no nome de quem?**
Hoje o repo é `github.com/lucasnegrelli/mosaiconafatec` — seu. Recomendo criar
tudo no e-mail dele e você entrar como colaborador. Custa 20 min e evita ele
ficar sem acesso ao próprio robô se vocês se desencontrarem.

**2. Quem paga o quê?**
Claude Pro e API da Anthropic são cobranças **separadas**. Combine antes.

**3. Repo público.** Actions é ilimitado em repo público; em privado o free dá
2.000 min/mês e o cron de 15 min estoura. As chaves ficam nos Secrets
(criptografados), não no código.

**4. Quem renova o token a cada 60 dias?** Se ninguém decidir, morre em silêncio.

---

## O dia (~6h30)

### Bloco 0 — Alinhamento · 15 min

Antes de tocar em tela, explique em 3 frases o que vai acontecer. Alguém de
nível básico vendo 5h de configuração sem entender o porquê fica ansioso e não
retém nada.

> "Vamos deixar um robô publicando no Instagram sozinho. Sua parte vai ser só
> ligar o celular no cabo e clicar num botão. Hoje eu monto tudo, e no fim eu
> te ensino a sua parte — que é a mais simples."

### Bloco 1 — Base do note · 50 min

- [ ] Login no Gmail dele no navegador
- [ ] **Claude Pro** — assinar em claude.ai com o e-mail e cartão dele
- [ ] Instalar **Claude Desktop** (claude.ai/download)
- [ ] Logar no Claude Desktop
- [ ] **Autorizar as permissões do Cowork** — acesso à pasta do projeto
- [ ] Instalar **Python** pela Microsoft Store (busca "Python 3.12")
- [ ] Instalar **ffmpeg**: abrir Prompt de Comando e rodar
      `winget install Gyan.FFmpeg` — depois **fechar e reabrir o Prompt**
- [ ] Copiar a pasta `Trinca` do pendrive pra Área de Trabalho dele
- [ ] Conectar a pasta no Cowork: apontar pra `Desktop\Trinca`

> Enquanto o Claude Desktop baixa, comece o Bloco 2 no seu note. Download é o
> tempo morto mais longo do dia.

**Teste rápido do Bloco 1:** duplo clique em `02-organizador-midia\ORGANIZAR.bat`.
Deve abrir a janela preta e dizer que não achou nada na entrada. Se disser isso,
Python está OK.

### Bloco 2 — Google Cloud e service account · 40 min

Segue `SETUP-SECRETS.md` seção 1. Resumo:

- [ ] Criar projeto no console.cloud.google.com
- [ ] Ativar **Google Drive API**
- [ ] Criar service account → chave **JSON** → baixar
- [ ] Abrir o JSON, copiar o `client_email`
- [ ] Compartilhar a pasta `MosaicoNaFATEC` com esse e-mail como **Editor**
- [ ] Guardar o JSON fora da Área de Trabalho

⚠️ Bloco onde mais se erra. Sem **Editor**, o robô publica mas não move o
arquivo pra `postado/` — e republica a mesma foto pra sempre.

### Bloco 3 — Cloudinary e Anthropic API · 25 min

- [ ] Conta no Cloudinary → anotar os 3 valores do Dashboard
- [ ] Conta em console.anthropic.com (**separada** do Claude Pro)
- [ ] Gerar API key
- [ ] **Limite de gasto** em Settings → Limits. Sugestão: US$ 5/mês

### Bloco 4 — Instagram e Meta · 60 min

Segue `SETUP-SECRETS.md` seções 6 e 7.

- [ ] Confirmar @mosaiconafatec como conta **Profissional**
- [ ] Criar app em developers.facebook.com
- [ ] Adicionar produto **Instagram**
- [ ] **API com login do Instagram** (não a com login do Facebook)
- [ ] Gerar token → trocar por token de **60 dias** (o comando está no
      `PLANO-SABADO.md`, seção Fase 1)
- [ ] Anotar token e o ID numérico da conta

> Reserve mais tempo do que parece. A interface do Meta muda direto e os nomes
> dos menus raramente batem com tutorial nenhum.

### Bloco 5 — GitHub e secrets · 40 min

- [ ] Criar conta GitHub no e-mail dele
- [ ] Adicionar ele como **colaborador** em `lucasnegrelli/mosaiconafatec`
      (Settings → Collaborators → Add people) — ou transferir o repo
- [ ] Cadastrar os 7 secrets restantes
- [ ] Conferir que `DRIVE_FOLDER_ID` já está lá

### Bloco 6 — Teste real, com ele olhando · 30 min

**Não pule e não faça sozinho.** É o momento em que a coisa abstrata vira
concreta pra ele.

- [ ] Colocar **uma foto** em `segunda-feira/08h00-corte-de-pastilhas/` no Drive
- [ ] Actions → Run workflow → dia `segunda-feira`, hora `08:00`
- [ ] Acompanhar o log até o fim
- [ ] Conferir o post no Instagram
- [ ] Conferir que o arquivo foi pra `postado/`

Tabela de erros comuns no fim do `SETUP-SECRETS.md`.

### Bloco 7 — Ensinar a rotina dele · 45 min

Aqui você vira professor. Abra o `guia-trinca.html` e **deixe ele no mouse**.

1. **Ciclo completo, ele fazendo (25 min)**
   - Liga o celular no cabo
   - Escolhe "Transferir arquivos" no celular
   - Copia uns arquivos pra `entrada`
   - Duplo clique em `ORGANIZAR`
   - Abre `para-revisar` e vê o resultado

   **Repita 3 vezes.** Não é exagero — repetição é o que fixa, e é a única
   coisa que ele vai precisar fazer sozinho pra sempre.

2. **Claude no dia a dia (20 min)** — três casos reais do trabalho dele,
   não exemplo genérico:
   - "Escreve um orçamento para um painel de 2m² em tons de azul"
   - "Monta o plano de uma oficina de 4 encontros"
   - "Deixa esse texto mais claro" (com texto real dele)

### Bloco 8 — Encerramento · 20 min

- [ ] Deixar o `guia-trinca.html` **fixado na barra de favoritos** dele
- [ ] Criar atalho do `ORGANIZAR.bat` na Área de Trabalho
- [ ] Anotar juntos onde ficam as senhas
- [ ] Combinar como ele te chama quando quebrar
- [ ] Marcar acompanhamento em 1 semana
- [ ] Colocar no **seu** calendário: renovar token em 55 dias

---

## Sobre ensinar cmd

Você falou em talvez ensinar a rodar no Prompt. Minha sugestão: **não ensine
hoje.**

O `.bat` existe justamente pra ele não precisar. Ensinar cmd no mesmo dia de
outras 8 coisas novas compete com o que realmente importa (o ciclo do cabo) e
aumenta a chance dele digitar algo errado depois, sozinho, e quebrar.

Se em algum momento ele demonstrar curiosidade, aí sim — mas como assunto
próprio, num outro dia, sem pressão de configuração.

---

## Se o dia atrasar, corte nesta ordem

1. Bloco 3 (Cloudinary/Anthropic) — dá pra fazer remoto depois
2. Caso de uso 2 e 3 do Bloco 7
3. **Nunca corte:** o teste do Bloco 6 com ele olhando, e as 3 repetições do
   ciclo do cabo no Bloco 7. Sem esses dois, o dia não serviu.

---

## O risco que vale dizer em voz alta

**Esse sistema depende de você.** O Trinca não vai consertar token vencido,
secret errado ou workflow quebrado — e tudo bem, não é o trabalho dele.

Decida hoje, conscientemente:

- você é o suporte técnico dele por tempo indeterminado; ou
- vocês combinam escopo e data de saída, com documentação suficiente pra outro
  assumir; ou
- você simplifica até o ponto em que ele se vira sozinho

A pior versão é a não-decidida: você some, o robô para em silêncio, e o
Instagram fica meses parado sem ninguém perceber.

Mitigação barata: o GitHub já manda e-mail quando o workflow falha (Settings →
Notifications). Confirme que está ligado **na conta dele também**, e combine
que ele te avisa se ficar 2 dias sem post.
