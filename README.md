# Sistema de Romaneio de Cargas

Sistema web responsivo para registro e consulta de carregamentos de maçãs,
desenvolvido em Django. Cada operador tem a própria conta e vê apenas as
cargas que cadastrou.

## Funcionalidades

- **Contas de usuário** — login/logout; os dados de cada usuário são isolados
  dos demais. Sem auto-cadastro público: contas novas são criadas por um
  usuário já logado, com senha provisória e troca obrigatória no primeiro
  acesso. Troca de senha disponível no menu; "esqueci a senha" é tarefa do
  administrador (ver DOCUMENTACAO.md).
- **Cadastro de carga** — data e hora registradas automaticamente; tipo da
  maçã, tamanho, quantidade de caixas, peso total (kg) e observações (opcional).
- **Consulta** — listagem com paginação, filtros por tipo, tamanho, período e
  busca por texto, com totais (cargas, caixas e peso) do resultado filtrado.
- **Detalhes, edição e exclusão** de cada carga (exclusão com confirmação).
- **Responsivo** — tabela no computador, cartões no celular; o painel
  administrativo também funciona no celular.
- **Páginas de erro amigáveis** (404/403/400/500) — o usuário nunca vê telas
  técnicas do Django.
- **Painel administrativo** em `/admin/` para suporte (superusuário).

## Documentação

- [INSTALACAO.md](INSTALACAO.md) — como clonar o projeto e colocar para rodar.
- [DOCUMENTACAO.md](DOCUMENTACAO.md) — como o software funciona por dentro:
  estrutura, modelo de dados, regras de acesso e tarefas comuns de suporte.

## Início rápido (ambiente já instalado)

```powershell
.\venv\Scripts\python.exe manage.py runserver
```

Acesse http://127.0.0.1:8000 e entre com sua conta. Contas novas são criadas
por um usuário já logado (menu → "Criar conta para terceiro").

> Nota desta máquina de desenvolvimento: o Python 3.12 instalado está
> bloqueado por política do Windows; o venv local foi criado com `py -3.14`.
