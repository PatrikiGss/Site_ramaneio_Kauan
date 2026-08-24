# Sistema de Romaneio de Cargas

[![CI](https://github.com/PatrikiGss/Site_ramaneio_Kauan/actions/workflows/ci.yml/badge.svg)](https://github.com/PatrikiGss/Site_ramaneio_Kauan/actions/workflows/ci.yml)

Sistema web para **registro, consulta e controle de cargas de maçã**, desenvolvido para substituir o controle manual realizado em planilhas ou cadernos.

A aplicação funciona em computadores e dispositivos móveis e possui controle de acesso por usuário, garantindo que cada operador visualize apenas os registros vinculados à sua conta.

**Aplicação em produção:** [Ramaneio](https://site-ramaneio-kauan.onrender.com)

## Funcionalidades

### Cadastro de cargas

Permite registrar as principais informações de cada carregamento:

* Tipo de maçã: Fuji, Gala, Mishima, Golden ou Outra;
* Tamanho: Pequena, Média, Grande ou Extra grande;
* Quantidade de caixas;
* Peso total em kg;
* Observações;
* Data e hora registradas automaticamente.

### Consulta e controle

Os registros podem ser consultados e organizados por meio de:

* Filtro por tipo de maçã;
* Filtro por tamanho;
* Filtro por período;
* Busca por texto ou número da carga;
* Totais calculados de acordo com os filtros aplicados;
* Paginação de resultados;
* Edição dos registros.

### Fechamento do período

O sistema possui uma área de resumo para conferência dos carregamentos realizados em determinado período.

Os dados são agrupados por:

* Tipo de maçã;
* Tamanho;
* Dia.

Também estão disponíveis atalhos para **Hoje**, **Últimos 7 dias** e **Este mês**, além da opção de impressão do resumo.

### Lixeira

A exclusão de uma carga é reversível.

Ao excluir um registro, ele é enviado para a lixeira, onde pode ser:

* Restaurado;
* Excluído permanentemente.

### Usuários e controle de acesso

A aplicação possui autenticação e isolamento dos dados por usuário.

Cada operador possui sua própria conta e acessa somente as cargas cadastradas por ele.

Não existe cadastro público. Novas contas são criadas por um usuário autorizado, com senha provisória e **troca obrigatória da senha no primeiro acesso**.

### Interface

* Layout responsivo para computador e celular;
* Tabela de registros em telas maiores;
* Cards adaptados para dispositivos móveis;
* Modo escuro com preferência salva no navegador;
* Páginas personalizadas para os erros 400, 403, 404 e 500.

### Administração

O sistema conta com um painel administrativo em `/admin/` para gerenciamento e suporte da aplicação.

## Tecnologias

* **Python**
* **Django 6**
* **PostgreSQL** em produção
* **SQLite** para desenvolvimento
* **Bootstrap 5**
* **WhiteNoise**
* **Gunicorn**

## Arquitetura de produção

A aplicação está hospedada na **Render**, utilizando **Neon** como banco de dados PostgreSQL.

O deploy é realizado automaticamente a cada push na branch `main`.

**Aplicação:** [https://site-ramaneio-kauan.onrender.com](https://site-ramaneio-kauan.onrender.com)

> **Observação:** no plano gratuito da Render, a aplicação pode entrar em suspensão após um período de inatividade. Nesse caso, o primeiro acesso pode levar cerca de 50 segundos para responder. Após a inicialização, o acesso volta ao funcionamento normal.

## Testes

O projeto possui **105 testes automatizados**, cobrindo as principais regras de negócio, autenticação e isolamento de dados entre usuários.

Para executar a suíte de testes:

```powershell
.\venv\Scripts\python.exe manage.py test
```

Antes de publicar alterações, recomenda-se executar todos os testes para verificar possíveis regressões.

Mais informações sobre a estrutura e cobertura dos testes estão disponíveis em [DOCUMENTACAO.md](DOCUMENTACAO.md).

## Documentação

* **[INSTALACAO.md](INSTALACAO.md)** — instalação, configuração e execução do projeto.
* **[DOCUMENTACAO.md](DOCUMENTACAO.md)** — arquitetura, modelo de dados, funcionamento interno e procedimentos de suporte.

## Licença

Este software é **proprietário e não possui código aberto**.

Seu uso e distribuição são regidos pelos termos definidos no arquivo [LICENSE](LICENSE).

**Todos os direitos reservados.**

## Autor

**Patriki de Oliveira Góss**

[patrikigss321@gmail.com](mailto:patrikigss321@gmail.com)
