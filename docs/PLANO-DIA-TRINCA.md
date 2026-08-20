# Roteiro do dia — implantação no notebook do Trinca

Documento seu, não dele. O guia dele é o `GUIA-TRINCA.md`.

---

## Antes de sair de casa (20 min)

- [ ] Confirmar com o Trinca que ele vai ter **o cartão dele em mãos** (3 contas
      cobram: Claude Pro, API Anthropic, e eventualmente Cloudinary se estourar
      o gratuito)
- [ ] Confirmar que ele lembra a **senha do Instagram @mosaiconafatec** e tem
      acesso ao celular com o app (vai precisar autorizar)
- [ ] Confirmar que ele sabe a **senha do Gmail dele** — não a do navegador
      salvo, a senha mesmo. Se tiver 2FA, o celular junto.
- [ ] Levar este roteiro offline (PDF no celular) caso o wi-fi lá seja ruim
- [ ] Perguntar se o notebook é Windows ou Mac (muda o instalador do Claude)

> A quantidade de senha que trava esse tipo de dia é absurda. Vale mandar essa
> lista por mensagem hoje à noite para ele já separar.

---

## Decisões que você precisa tomar ANTES de começar

Não deixe para resolver no meio. São três, e todas têm consequência de longo prazo.

### 1. As contas ficam no nome de quem?

Hoje o repositório está em `github.com/lucasnegrelli/mosaiconafatec` — no seu
nome. Se você e o Trinca se desencontrarem daqui a seis meses, ele fica sem
acesso ao robô que publica no Instagram dele.

**Recomendação:** criar tudo no e-mail do Trinca (GitHub, Cloudinary, Anthropic,
Google Cloud) e você entrar como colaborador. Dá 20 minutos a mais no dia e
resolve o problema de vez. O repo atual você transfere em
*Settings > General > Transfer ownership* — leva 2 minutos.

Se decidir manter no seu nome, tudo bem, mas **fale isso com ele em voz alta**
para não virar mal-entendido depois.

### 2. Quem paga o quê?

| Serviço | Custo | Quem |
|---|---|---|
| Claude Pro | mensalidade | ? |
| API Anthropic (robô) | uso, centavos/semana | ? |
| Cloudinary | grátis no plano free | — |
| GitHub Actions | grátis em repo público | — |

O robô roda a cada 15 min = ~2.900 execuções/mês. Em repositório **público** o
Actions é ilimitado. Se você tornar o repo privado, o plano free dá 2.000
minutos/mês e isso **estoura**. Deixe público (não tem segredo no código — as
chaves ficam nos Secrets, que são criptografados).

### 3. Quem renova o token do Instagram a cada 60 dias?

Se for você, coloque no seu calendário hoje. Se for ele, o guia precisa ensinar,
e é a parte mais difícil de ensinar para alguém de nível básico.

**Alternativa honesta:** me peça para montar a rotina de auto-renovação antes de
amanhã. É mais seguro do que depender de qualquer um dos dois lembrar.

---

## O dia (~6h com intervalos)

Ordem importa. Cada bloco desbloqueia o próximo.

### Bloco 0 — Alinhamento (15 min)

Antes de tocar em qualquer tela, explique para ele em 3 frases o que vai
acontecer. Alguém de nível básico assistindo você configurar coisa por 5 horas
sem entender o porquê fica ansioso e depois não retém nada.

Sugestão de frase: *"Vamos deixar um robô publicando no Instagram sozinho. Você
só vai precisar jogar as fotos numa pasta do Drive, e ele publica no horário
certo com legenda pronta. Hoje eu configuro, e no fim eu te ensino a parte que é
sua — que é só a das fotos."*

### Bloco 1 — Contas base (45 min)

- [ ] Login no Gmail dele no navegador do notebook
- [ ] Verificar acesso à pasta do Drive `Trinca > MosaicoNaFATEC`
- [ ] **Claude Pro:** claude.ai → assinar no e-mail dele, cartão dele
- [ ] Instalar o **Claude Desktop** (claude.ai/download) e logar
- [ ] Conta **GitHub** no e-mail dele (se seguir a recomendação da decisão 1)

> Enquanto o Claude Desktop baixa, comece o Bloco 2 em outra aba. O download é
> o momento morto mais longo do dia.

### Bloco 2 — Google Cloud e service account (40 min)

Segue o `SETUP-SECRETS.md`, seção 1. Resumo da ordem:

- [ ] Criar projeto no console.cloud.google.com
- [ ] Ativar a **Google Drive API**
- [ ] Criar service account → gerar chave **JSON** → baixar
- [ ] Abrir o JSON, copiar o `client_email`
- [ ] Compartilhar a pasta `MosaicoNaFATEC` com esse e-mail, como **Editor**
- [ ] Guardar o JSON num lugar seguro (não na Área de Trabalho dele)

⚠️ Esse é o bloco onde mais se erra. Se a pasta não for compartilhada com
permissão de **Editor**, o robô publica mas não consegue mover o arquivo para
`postado/` — e aí republica a mesma foto para sempre.

### Bloco 3 — Cloudinary e Anthropic API (25 min)

- [ ] Criar conta no Cloudinary, anotar os 3 valores do Dashboard
- [ ] Criar conta em console.anthropic.com (separada do Claude Pro!)
- [ ] Gerar API key
- [ ] **Colocar limite de gasto** em Settings > Limits — sugestão: US$ 5/mês.
      Sem limite, um bug em loop pode gerar conta alta.

### Bloco 4 — Instagram e Meta (60 min, o mais chato)

Segue `SETUP-SECRETS.md`, seção 6/7.

- [ ] Confirmar que @mosaiconafatec está como conta **Profissional**
- [ ] Criar app no developers.facebook.com
- [ ] Adicionar produto **Instagram**
- [ ] **API com login do Instagram** (não a com login do Facebook!)
- [ ] Gerar token → anotar token e o ID da conta

> Reserve mais tempo do que parece. A interface do Meta muda com frequência e
> os nomes dos menus raramente batem com tutorial nenhum. Se travar, procure
> pelo produto "Instagram" no painel do app e vá clicando — o fluxo está lá,
> só muda de lugar.

### Bloco 5 — Secrets e primeiro teste (30 min)

- [ ] Cadastrar os 7 secrets no GitHub
- [ ] Colocar **uma foto** de teste em `segunda-feira/08h00-corte-de-pastilhas/`
- [ ] Actions → Run workflow → dia `segunda-feira`, hora `08:00`
- [ ] Ver o log até o fim
- [ ] Conferir no Instagram se saiu

**Faça esse teste com o Trinca olhando.** É o momento em que a coisa abstrata
vira concreta pra ele, e é o que vai fazer ele confiar no sistema.

Se der erro, a tabela de erros comuns está no fim do `SETUP-SECRETS.md`.

### Bloco 6 — Organizar o Drive dele (30 min)

Já existe `Trinca > Curso de Mosaico > Forms` e `Trinca > MosaicoNaFATEC`.
Sugestão de estrutura para o resto:

```
Trinca/
  MosaicoNaFATEC/        <- pastas do robô (pronto)
    takes-brutos/        <- joga tudo aqui quando não souber classificar
  Curso de Mosaico/
    Forms/
    Materiais de aula/
    Listas de alunos/
  Administrativo/
    Contratos/
    Notas fiscais/
    Orçamentos/
  Portfólio/
    Fotos de obras/
```

Não invente pasta demais. Alguém de nível básico com 15 pastas usa duas e joga
o resto na Área de Trabalho. Menos é mais.

### Bloco 7 — Ensinar (60 min)

Aqui você para de configurar e vira professor. Abra o `GUIA-TRINCA.md` (ou a
página HTML) e passe **com ele mexendo no mouse, não você**.

Roteiro sugerido:

1. **A rotina das fotos (20 min)** — ele faz sozinho: pega uma foto do celular,
   sobe no Drive, escolhe a pasta certa. Repita 3 vezes com fotos diferentes até
   sair natural.
2. **Como usar o Claude no dia a dia (30 min)** — três casos concretos do
   trabalho dele, não exemplos genéricos. Sugestões:
   - "Escreve um orçamento para um painel de mosaico de 2m² para uma cliente"
   - "Me ajuda a montar o plano de aula da próxima oficina"
   - "Reescreve esse texto pra ficar mais claro" (com texto real dele)
3. **O que não mexer (10 min)** — GitHub, a pasta `postado/`, os nomes das
   pastas. Explique o porquê de cada um; proibição sem motivo não gruda.

### Encerramento (15 min)

- [ ] Mandar o link da página HTML por WhatsApp pra ele
- [ ] Anotar juntos, num papel ou no bloco de notas dele, **onde estão as senhas**
- [ ] Combinar o canal de socorro: como ele te chama quando quebrar
- [ ] Combinar uma data de acompanhamento (1 semana depois funciona bem)

---

## Se o dia atrasar, corte nesta ordem

1. Bloco 6 (organizar Drive) — dá pra fazer remoto depois
2. Caso de uso 2 e 3 do Bloco 7 — manda vídeo depois
3. **Nunca corte:** o teste do Bloco 5 com ele olhando, e a rotina das fotos
   do Bloco 7. Sem esses dois, o dia não serviu pra nada.

---

## O risco real deste projeto

Vale dizer isso em voz alta, porque é o que costuma matar automação em negócio
pequeno: **o sistema depende de você.** O Trinca não vai conseguir consertar um
token vencido, um secret errado ou um workflow quebrado sozinho — e não tem
problema nenhum nisso, não é o trabalho dele.

Então decida hoje, conscientemente, uma destas:

- Você fica como o suporte técnico dele por tempo indeterminado (tudo bem, mas
  saiba que é isso)
- Vocês combinam um escopo e uma data de saída, e você deixa documentado o
  suficiente pra outra pessoa assumir
- Você simplifica o sistema até o ponto em que ele se vira (menos automação,
  mais manual)

A pior versão é a que não é decidida: você some, o robô para em silêncio, e o
Instagram fica meses sem postar sem ninguém perceber.

Sugestão barata de mitigação: configurar o GitHub para te mandar e-mail quando
o workflow falhar (já vem ligado por padrão em *Settings > Notifications*) e
combinar com o Trinca que ele te avisa se ficar 2 dias sem post novo.
