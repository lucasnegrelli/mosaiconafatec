# 🧱 Arquitetura escalável & guia de clonagem

Este documento é a camada "transformar em produto" — como deixar a automação
redonda e replicável para outros negócios. Ele complementa o `PLANO-SABADO.md`
(que é o passo a passo de colocar o primeiro no ar).

---

## 🎯 Princípio que organiza tudo: separar MOTOR de IDENTIDADE

A grande virada para ser clonável é não ter nada do "Mosaico na FATEC" escrito
dentro do código. O projeto se divide em duas camadas:

```
┌─────────────────────────────────────────────────────────┐
│  MOTOR (igual para todo cliente — nunca muda)           │
│  ─────────────────────────────────────────────────────  │
│  main.py          orquestra o fluxo                     │
│  imaging.py       trata as imagens                      │
│  criar_estrutura.py  cria as pastas no Drive            │
│  .github/workflows/postar.yml   o agendador             │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  IDENTIDADE (específico de cada cliente — você troca)   │
│  ─────────────────────────────────────────────────────  │
│  config.json      nome, voz, branding, formatos         │
│  schedule.json    a pauta editorial daquele negócio     │
│  assets/          logo/marca d'água daquele negócio     │
│  + os 8 Secrets   credenciais daquele negócio           │
│  + a pasta Drive  mídias daquele negócio                │
└─────────────────────────────────────────────────────────┘
```

Já testamos isso na prática: o `main.py` lê o `config.json` para montar o
prompt da legenda. Trocando só o `config.json` de "Mosaico na FATEC" para
"Padaria do Zé", o mesmo código passa a escrever legendas de padaria. Nenhuma
linha de Python muda.

---

## 🐑 Como clonar para um novo negócio (passo a passo)

A forma mais lisa de clonar no GitHub é transformar o repositório do Mosaico em
um **template repository** (Settings → marque "Template repository"). Aí, para
cada novo cliente:

1. **"Use this template"** → cria um repositório novo, cópia limpa do motor.
2. **Editar `config.json`** → nome, @, nicho, tom de voz, hashtags, branding.
3. **Editar `schedule.json`** → a pauta editorial do novo negócio (ou começar
   da do Mosaico e adaptar).
4. **Rodar `criar_estrutura.py`** → cria a árvore de pastas no Drive do cliente
   automaticamente, a partir do `schedule.json` dele.
5. **Cadastrar os 8 Secrets** do novo cliente (mesma lista do `PLANO-SABADO.md`).

Pronto — novo negócio no ar. Os passos 2 e 3 são edição de texto; o 1, 4 e 5
são mecânicos. Dá para clonar um cliente novo em menos de uma hora, sem
programar nada.

> 💡 Evolução natural depois: um pequeno formulário ou planilha onde o cliente
> preenche nome/voz/hashtags e um script gera o `config.json` sozinho. Mas isso
> é refinamento — o modelo de template já entrega a clonagem hoje.

---

## 🖼️ Sobre as edições de imagem — o que entra e o que NÃO entra

Você levantou a ideia de editar as imagens. Pensei nisso com cuidado e dividi em
"funcional" (vale muito) e "estético" (cuidado).

### ✅ O que vale — e já está no `imaging.py`

- **Conversão para JPEG.** Não é luxo, é necessidade: a API do Instagram só
  aceita JPEG. Se o Trinca subir um PNG ou HEIC (foto de iPhone), a postagem
  quebra. O módulo converte tudo automaticamente.
- **Normalização de formato (4:5 no feed, 9:16 nos stories).** Fotos vêm em
  proporções variadas; sem isso o Instagram corta torto. O módulo encaixa a foto
  inteira num fundo desfocado da própria imagem — **não corta nada da obra**.
- **Correção de rotação (EXIF).** Resolve aquela foto que era retrato e aparece
  deitada.
- **Marca d'água opcional.** Logo ou @ discreto num canto. Está desligada por
  padrão no `config.json` (`watermark.ativo: false`); para ligar, basta colocar
  o PNG em `assets/watermark.png` e mudar para `true`. Útil para a obra do
  Trinca não ser repostada sem crédito.

### ⚠️ O que eu deliberadamente NÃO coloquei — e acho que não devemos

- **Filtros automáticos / "melhorar" cor e contraste da obra.** Aqui vou ser
  honesto e te dar um contra: a foto do mosaico **é o produto do artista**.
  Deixar um robô reinterpretar a estética da arte do Trinca, em escala, sem ele
  ver cada uma, é mais risco do que ganho — pode descaracterizar a peça e ele só
  vai perceber depois de no ar. Normalização de formato é mecânica e segura;
  ajuste estético é decisão autoral, e essa deveria continuar com ele.

Se em algum momento ele quiser um "tratamento de cor" padrão, o caminho certo é
ele definir **um preset** que aprova visualmente antes, e a gente aplica só esse
— nunca uma "melhoria automática" decidida pela máquina.

---

## 🛣️ Roadmap — partes para incluir depois (com avaliação honesta de cada)

Você falou em ir melhorando por partes. Aqui vão as candidatas, em ordem do que
eu acho que mais compensa:

| Melhoria | Vale a pena? | Por quê |
|---|---|---|
| **Renovação automática do token** | 🟢 Alto | Hoje alguém precisa renovar a cada 60 dias na mão. Um workflow mensal que troca o token sozinho elimina o único ponto que "morre" sem aviso. |
| **Log/registro de postagens** | 🟢 Alto | Uma aba de planilha (ou Supabase) registrando o que foi postado, quando, qual legenda. Vira histórico e facilita auditar se algo falhou. |
| **Aviso de falha (Telegram/e-mail)** | 🟢 Alto | Se um post falhar às 3h da manhã, vocês querem saber. Um ping automático evita descobrir só dias depois. |
| **Painel simples de status** | 🟡 Médio | Uma página web mostrando "próximos posts", "pastas vazias", "quota da API". Bom quando virar vários clientes. |
| **Carrossel automático** | 🟡 Médio | Postar várias fotos de uma categoria num post só. A API suporta; é mais lógica de agrupamento. |
| **Reaproveitar legenda boa** | 🟡 Médio | Guardar as legendas mais curtidas e usar de referência pra IA manter o que funciona. |
| **Geração de imagem por IA** | 🔴 Baixo (por ora) | Tentador, mas o valor do perfil é a obra real do Trinca. Imagem sintética dilui isso. Deixaria fora, pelo menos enquanto for sobre o ateliê. |

Sugestão de ordem para o "depois do sábado": renovação de token → aviso de
falha → log. Esses três deixam a operação confiável o bastante para você não
precisar ficar de babá dela.

---

## 📂 Arquivos do projeto (estado atual)

| Arquivo | Camada | O que faz |
|---|---|---|
| `main.py` | motor | Fluxo completo: Drive → trata imagem → Cloudinary → Claude → Instagram |
| `imaging.py` | motor | Conversão JPEG, formato, EXIF, marca d'água |
| `criar_estrutura.py` | motor | Cria toda a árvore de pastas no Drive a partir do schedule |
| `.github/workflows/postar.yml` | motor | Agendador (roda a cada 15 min) |
| `requirements.txt` | motor | Dependências |
| `config.json` | identidade | Nome, voz, branding, formatos do negócio |
| `schedule.json` | identidade | Pauta editorial (109 slots) |
| `assets/` | identidade | Logo/marca d'água (criar quando for usar) |

---

## ▶️ Próximo passo imediato (não depende do token do Instagram)

Enquanto o SMS do Instagram não chega, dá pra adiantar duas coisas que só usam o
Drive (que você já tem):

1. **Rodar o `criar_estrutura.py`** para o Drive nascer com a árvore completa e
   o Trinca parar de criar pasta na mão.
2. **Conferir o `schedule.json`** contra o que ele já organizou (Fase 5 do
   plano).

Quando o token chegar, é só plugar os Secrets do Instagram e fazer o teste
controlado (Fase 7).
