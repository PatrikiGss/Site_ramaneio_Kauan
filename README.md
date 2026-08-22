# Sistema de Romaneio de Cargas

🔗 **Acesse:** https://site-ramaneio-kauan.onrender.com

Aplicação web (SaaS) para **registro e controle dos carregamentos de maçã** do
dia a dia. Cada operador tem a própria conta e enxerga apenas as cargas que
cadastrou. Feito para uso tanto no **celular** quanto no computador.

## O que o sistema faz

Substitui a planilha/caderno do romaneio por um sistema online:

- **Registra** cada carga com data e hora automáticas, tipo da maçã, tamanho,
  quantidade de caixas, peso total e observações.
- **Consulta e organiza** os registros — com filtros, busca, totais e edição a
  qualquer momento.
- **Fecha o período** com um resumo agrupado: quanto foi carregado por tipo, por
  tamanho e por dia — o "quanto carreguei hoje / essa semana, de cada maçã".

## Funcionalidades

- **Cadastro de cargas** — tipo (Fuji, Gala, Mishima, Golden, Outra), tamanho
  (Pequena, Média, Grande, Extra grande), quantidade de caixas, peso total (kg)
  e observações. A data e a hora são gravadas automaticamente.
- **Consulta** — lista com filtros (tipo, tamanho, período e busca por texto ou
  nº da carga), **totais** do resultado filtrado e **paginação** (15 por página).
- **Resumo do período (fechamento)** — totais agrupados por tipo, por tamanho e
  por dia, com atalhos (Hoje / Últimos 7 dias / Este mês) e botão de
  **impressão**.
- **Lixeira (exclusão reversível)** — "excluir" move a carga para a lixeira; de
  lá é possível **restaurar** ou **apagar definitivamente**.
- **Contas de usuário** — login com **isolamento de dados** (cada um vê apenas
  as próprias cargas). Não há auto-cadastro público: contas novas são criadas
  por um usuário já logado, com senha provisória e **troca obrigatória no
  primeiro acesso**.
- **Modo escuro** — botão na barra superior; a preferência fica salva no
  navegador.
- **Responsivo** — no computador a lista é uma tabela; no celular, cartões.
- **Páginas de erro amigáveis** (404, 403, 400 e 500) — o usuário nunca vê
  telas técnicas.
- **Painel administrativo** em `/admin/`, para o superusuário dar suporte.

## Tecnologias

Python + **Django 6**, **PostgreSQL** em produção (SQLite em desenvolvimento),
Bootstrap 5 servido localmente, WhiteNoise para arquivos estáticos e Gunicorn.

## Produção

Publicado como SaaS na **Render** (aplicação) com banco de dados na **Neon**
(PostgreSQL), em https://site-ramaneio-kauan.onrender.com — o deploy é
automático a cada push na branch `main`.

> Nota do plano gratuito: após cerca de 15 minutos sem acesso, a aplicação
> "hiberna" e o primeiro acesso seguinte pode demorar ~50 segundos para
> responder. Os acessos seguintes ficam normais.

## Documentação

- **[INSTALACAO.md](INSTALACAO.md)** — como clonar o projeto e colocar para rodar.
- **[DOCUMENTACAO.md](DOCUMENTACAO.md)** — como o software funciona por dentro,
  modelo de dados e tarefas comuns de suporte.

## Licença

Software **proprietário** — não é open source. O uso é regido pela licença em
**[LICENSE](LICENSE)**. Todos os direitos reservados.

## Autor

**Patriki de Oliveira Góss**
📧 patrikigss321@gmail.com
