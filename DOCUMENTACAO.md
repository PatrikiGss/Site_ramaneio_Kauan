# Documentação do Software — Sistema de Romaneio de Cargas

Documento de referência para manutenção e suporte futuro. Para instalar e
rodar, veja o [INSTALACAO.md](INSTALACAO.md).

## Visão geral

Sistema web responsivo para registro e consulta de carregamentos de maçãs.
Cada operador possui a própria conta e **enxerga apenas as cargas que ele
mesmo cadastrou**. Não há auto-cadastro público: contas novas são criadas por
usuários já cadastrados, com senha provisória trocada obrigatoriamente no
primeiro acesso.

**Stack:** Python + Django 6 (backend, templates renderizados no servidor),
PostgreSQL em produção e SQLite em desenvolvimento, Bootstrap 5 **servido localmente** (em
`cargas/static/vendor/` — o layout não depende de internet/CDN, essencial
para uso no celular), WhiteNoise (serve os arquivos estáticos em produção).
Não há build de frontend nem JavaScript próprio — toda a lógica é no servidor.

## Estrutura de pastas

```
site_ramaneio_kauan/
├── manage.py             # utilitário de linha de comando do Django
├── requirements.txt      # dependências do projeto
├── db.sqlite3            # banco de dados (não versionado)
├── staticfiles/          # estáticos coletados p/ produção (não versionado)
├── templates/            # páginas de erro: 404, 403, 400 e 500
├── config/               # configurações do projeto
│   ├── settings.py       # idioma pt-BR, DEBUG por variável de ambiente, login
│   └── urls.py           # rotas raiz: /admin/, /contas/, / (cargas)
├── cargas/               # app principal: CRUD de cargas
│   ├── models.py         # modelo Carga (a única tabela de negócio)
│   ├── forms.py          # CargaForm (cadastro/edição) e FiltroCargaForm (busca)
│   ├── views.py          # listagem, detalhe, criação, edição, exclusão
│   ├── urls.py           # rotas do CRUD
│   ├── admin.py          # configuração do painel /admin/
│   ├── migrations/       # histórico de alterações do banco
│   ├── tests/            # bateria de testes do app (ver "Testes automatizados")
│   ├── templates/        # base.html (layout geral) + telas do CRUD
│   └── static/           # cargas/style.css + vendor/ (Bootstrap local)
└── contas/               # app de autenticação
    ├── models.py         # Perfil (flag de troca obrigatória de senha)
    ├── middleware.py     # bloqueio de navegação até trocar a senha provisória
    ├── forms.py          # forms de login/registro/troca com visual Bootstrap
    ├── views.py          # RegistroView e TrocarSenhaView
    ├── urls.py           # /contas/entrar|sair|registrar|trocar-senha/
    ├── tests/            # testes de login, registro e troca de senha
    └── templates/contas/ # telas de login, registro e troca de senha
```

## Modelo de dados

Tabela de negócio `cargas_carga` (modelo `Carga`):

| Campo | Tipo | Observações |
|---|---|---|
| `usuario` | FK → `auth_user` | Dono do registro; base do isolamento de dados |
| `criado_em` | datetime | Preenchido automaticamente no cadastro (`auto_now_add`) |
| `atualizado_em` | datetime | Atualizado a cada edição (`auto_now`) |
| `tipo_maca` | choice | Fuji, Gala, Mishima, Golden, Outra |
| `tamanho` | choice | P (Pequena), M (Média), G (Grande), GG (Extra grande) |
| `quantidade_caixas` | inteiro ≥ 1 | Validado no formulário |
| `peso_total` | decimal (kg) | Deve ser > 0; validado no formulário |
| `observacoes` | texto | Opcional |

Tabela auxiliar `contas_perfil` (modelo `Perfil`): 1-para-1 com o usuário,
guarda a flag `trocar_senha_no_proximo_acesso`.

## Contas e senhas

**Criação de contas** — não é pública. Um usuário logado abre o menu
(ícone de pessoa) → *Criar conta para terceiro*, define usuário e uma senha
provisória e as repassa ao novo operador.

**Primeiro acesso** — a conta nasce com a flag "trocar senha no próximo
acesso" ligada. O middleware `TrocaSenhaObrigatoriaMiddleware`
([contas/middleware.py](contas/middleware.py)) redireciona qualquer página
para a troca de senha até o usuário definir a própria; depois disso a flag é
desligada e a navegação liberada.

**Trocar senha depois** — a qualquer momento pelo menu → *Trocar senha*.

**Esqueci a senha** — de propósito, não existe fluxo público (exigiria
servidor de e-mail). Redefinição é tarefa do administrador:

```powershell
.\venv\Scripts\python.exe manage.py changepassword nome_do_usuario
```

ou pelo painel `/admin/` → Usuários → (usuário) → link "este formulário".
Depois de redefinir, o suporte pode ligar a flag do perfil do usuário em
`/admin/` → Perfis, para forçá-lo a escolher a própria senha no próximo acesso.

## Isolamento de dados

- Todas as telas de cargas exigem login; anônimos vão para `/contas/entrar/`.
- O isolamento é feito no `CargaDoUsuarioMixin`
  ([cargas/views.py](cargas/views.py)): toda consulta filtra por
  `usuario=request.user`. Detalhe/edição/exclusão de carga alheia retornam
  **404** (como se não existisse), para não revelar que o registro existe.
- No cadastro, o dono é definido **no servidor** — nunca vem do formulário.
- Pela interface normal, até o superusuário vê só as próprias cargas; a visão
  geral de tudo é exclusiva do painel `/admin/`.

## Páginas de erro

Com `DEBUG` desligado (padrão), erros mostram páginas amigáveis em
[templates/](templates/): `404.html` (não encontrado), `403.html` (acesso
negado), `400.html` (requisição inválida) e `500.html` (erro interno — esta
não herda do layout de propósito, para funcionar mesmo se o problema for no
próprio layout). Para ver os erros técnicos durante o desenvolvimento, rode
com `DJANGO_DEBUG=1` (ver INSTALACAO.md).

## Celular

O site inteiro é responsivo (Bootstrap): no computador a lista é uma tabela;
no celular vira cartões, e o menu compacta para ícones. O painel `/admin/` do
Django também é responsivo por padrão nas versões atuais — funciona no
celular sem configuração extra (os estáticos dele são servidos pelo
WhiteNoise, por isso o `collectstatic` é obrigatório na instalação).

**Modo escuro:** há um botão de lua/sol na barra superior que alterna claro/
escuro (recurso nativo do Bootstrap 5.3 via `data-bs-theme` no `<html>`). A
escolha é salva no navegador (`localStorage`) e, na primeira visita, respeita
a preferência do sistema operacional. Toda a lógica é inline em
`cargas/templates/base.html`.

## Lixeira (exclusão reversível)

"Excluir" uma carga **não apaga na hora**: ela vai para a **lixeira** (o campo
`excluido_em` do modelo é preenchido). Cargas na lixeira somem das listas, dos
totais e do resumo. Na lixeira (menu do usuário → **Lixeira**, ou o botão
"Lixeira (N)" na lista) dá para **Restaurar** (volta para a lista) ou
**Excluir definitivamente** (aí sim apaga de vez, irreversível). O isolamento
por usuário também vale aqui — ninguém vê nem mexe na lixeira de outro.

## Resumo do período (fechamento)

Menu → **Resumo** (`/resumo/`): escolhe-se um intervalo de datas (com atalhos
Hoje / Últimos 7 dias / Este mês) e o sistema mostra os totais **agrupados por
tipo de maçã, por tamanho e por dia** (cargas, caixas e peso em cada grupo),
além do total geral. Tem botão **Imprimir** (a barra e o rodapé são omitidos na
impressão via `d-print-none`). Considera só cargas ativas (ignora a lixeira).

## Rotas

| URL | Tela | Acesso |
|---|---|---|
| `/` | Lista de cargas com filtros, totais e paginação | Logado (só as suas) |
| `/nova/` | Cadastro de carga | Logado |
| `/resumo/` | Fechamento por período (por tipo/tamanho/dia) | Logado (só as suas) |
| `/lixeira/` | Cargas excluídas (restaurar / apagar de vez) | Logado (só as suas) |
| `/<id>/` | Detalhes da carga | Logado (só as suas) |
| `/<id>/editar/` | Edição | Logado (só as suas) |
| `/<id>/excluir/` | Mover para a lixeira | Logado (só as suas) |
| `/<id>/restaurar/` | Restaurar da lixeira (POST) | Logado (só as suas) |
| `/<id>/excluir-definitivo/` | Exclusão definitiva (a partir da lixeira) | Logado (só as suas) |
| `/contas/entrar/` e `/contas/sair/` | Login / logout | Público / logado |
| `/contas/registrar/` | Criar conta para terceiro | Logado |
| `/contas/trocar-senha/` | Trocar a própria senha | Logado |
| `/admin/` | Painel administrativo | Superusuário |

## Tarefas comuns de suporte

Comandos executados na pasta do projeto, com o venv
(`.\venv\Scripts\python.exe` no Windows).

**Criar novo superusuário:**

```powershell
.\venv\Scripts\python.exe manage.py createsuperuser
```

**Ver/editar cargas de qualquer usuário** — apenas pelo `/admin/`, logado
como superusuário. A coluna "usuário" mostra o dono de cada carga.

**Backup do banco** — copiar o arquivo `db.sqlite3` com o servidor parado.
Restaurar = substituir o arquivo.

**Adicionar um novo tipo de maçã ou tamanho** — editar as classes
`TipoMaca`/`Tamanho` em [cargas/models.py](cargas/models.py) e rodar
`makemigrations` + `migrate`.

**Excluir um usuário** — pelo `/admin/`. Atenção: as cargas dele são
excluídas junto (`on_delete=CASCADE`). Para preservar os dados, desative a
conta (desmarcar "Ativo") em vez de excluir.

**Depois de atualizar o código** — se arquivos estáticos mudaram, rodar
`collectstatic --noinput`; se modelos mudaram, rodar `migrate`. Reiniciar o
servidor.

## Testes automatizados

O projeto tem uma bateria de **105 testes** que cobre as regras de negócio e,
principalmente, o **isolamento de dados entre usuários**. Rode-a sempre antes de
publicar uma alteração:

```powershell
.\venv\Scripts\python.exe manage.py test
```

Para rodar só uma parte (mais rápido durante o desenvolvimento):

```powershell
.\venv\Scripts\python.exe manage.py test cargas
.\venv\Scripts\python.exe manage.py test cargas.tests.test_resumo
```

Os testes usam um **banco de dados temporário**, criado e destruído a cada
execução — eles nunca tocam nos dados reais.

Onde ficam e o que cobrem:

| Arquivo | Cobre |
|---|---|
| `cargas/tests/base.py` | Helpers compartilhados (criar usuário/carga, datar registros no passado) |
| `cargas/tests/test_models.py` | Modelo `Carga`, ordenação e os métodos da lixeira |
| `cargas/tests/test_forms.py` | Validações (caixas ≥ 1, peso > 0) e as opções de tipo/tamanho |
| `cargas/tests/test_acesso.py` | Login obrigatório e **isolamento entre usuários** |
| `cargas/tests/test_crud.py` | Cadastro, edição e exclusão pelas telas |
| `cargas/tests/test_lista.py` | Filtros, busca, totais e paginação |
| `cargas/tests/test_lixeira.py` | Restaurar, excluir definitivo e o fluxo completo |
| `cargas/tests/test_resumo.py` | Agrupamentos por tipo, tamanho e dia |
| `contas/tests/test_login.py` | Login e logout |
| `contas/tests/test_registro.py` | Criação de contas restrita a usuários logados |
| `contas/tests/test_troca_senha.py` | Troca de senha e bloqueio de primeiro acesso |

**Ao criar uma funcionalidade nova**, acrescente testes no arquivo
correspondente (ou crie um `test_<assunto>.py` no pacote). Se a funcionalidade
lê ou grava cargas, **inclua sempre um teste de isolamento** — que um usuário
não alcança o dado de outro. É a regra mais crítica do sistema e a mais fácil
de quebrar sem perceber.

## Decisões de projeto (para quem for dar manutenção)

- **SQLite** atende o porte do sistema e simplifica backup; se crescer, basta
  trocar `DATABASES` em `settings.py` para PostgreSQL/MySQL e migrar os dados.
- **Sem API/JavaScript próprio**: telas renderizadas no servidor reduzem
  complexidade; o Bootstrap resolve a responsividade exigida.
- **404 em vez de 403** para registros alheios: não confirma a existência do
  registro a quem não é dono.
- **WhiteNoise + DEBUG desligado por padrão**: o sistema roda "como produção"
  direto do `runserver`, com páginas de erro amigáveis e estáticos servidos
  corretamente, sem depender de servidor web externo.
- Datas/números em formato brasileiro (`LANGUAGE_CODE = 'pt-br'`); fuso
  `America/Sao_Paulo`, banco em UTC (`USE_TZ = True`, padrão do Django).
