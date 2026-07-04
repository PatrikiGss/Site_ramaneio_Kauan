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
SQLite (banco em arquivo único), Bootstrap 5 via CDN (layout responsivo),
WhiteNoise (serve os arquivos estáticos em produção). Não há build de
frontend nem JavaScript próprio — toda a lógica é no servidor.

## Estrutura de pastas

```
site_ramaneio_kauan/
├── manage.py             # utilitário de linha de comando do Django
├── requirements.txt      # dependências (Django + WhiteNoise)
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
│   ├── templates/        # base.html (layout geral) + telas do CRUD
│   └── static/cargas/    # style.css (ajustes finos sobre o Bootstrap)
└── contas/               # app de autenticação
    ├── models.py         # Perfil (flag de troca obrigatória de senha)
    ├── middleware.py     # bloqueio de navegação até trocar a senha provisória
    ├── forms.py          # forms de login/registro/troca com visual Bootstrap
    ├── views.py          # RegistroView e TrocarSenhaView
    ├── urls.py           # /contas/entrar|sair|registrar|trocar-senha/
    └── templates/contas/ # telas de login, registro e troca de senha
```

## Modelo de dados

Tabela de negócio `cargas_carga` (modelo `Carga`):

| Campo | Tipo | Observações |
|---|---|---|
| `usuario` | FK → `auth_user` | Dono do registro; base do isolamento de dados |
| `criado_em` | datetime | Preenchido automaticamente no cadastro (`auto_now_add`) |
| `atualizado_em` | datetime | Atualizado a cada edição (`auto_now`) |
| `tipo_maca` | choice | Gala, Fuji, Eva, Pink Lady, Cripps Pink, Granny Smith, Red Delicious, Outra |
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

## Rotas

| URL | Tela | Acesso |
|---|---|---|
| `/` | Lista de cargas com filtros, totais e paginação | Logado (só as suas) |
| `/nova/` | Cadastro de carga | Logado |
| `/<id>/` | Detalhes da carga | Logado (só as suas) |
| `/<id>/editar/` | Edição | Logado (só as suas) |
| `/<id>/excluir/` | Confirmação de exclusão | Logado (só as suas) |
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
