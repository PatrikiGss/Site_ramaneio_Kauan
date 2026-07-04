# Guia de Instalação — Sistema de Romaneio de Cargas

Passo a passo para clonar o projeto e colocá-lo para rodar em outra máquina.

## Pré-requisitos

- **Python 3.12 ou superior** — https://www.python.org/downloads/
  (durante a instalação no Windows, marque a opção *"Add Python to PATH"*)
- **Git** — https://git-scm.com/downloads

Para conferir se estão instalados, abra o terminal e rode:

```powershell
py --version
git --version
```

## 1. Clonar o projeto

```powershell
git clone <URL-DO-REPOSITORIO>
cd site_ramaneio_kauan
```

## 2. Criar o ambiente virtual e instalar as dependências

O ambiente virtual (`venv`) isola as bibliotecas do projeto das demais do
computador. Ele **não** vai para o Git (está no `.gitignore`), por isso precisa
ser criado em cada máquina:

```powershell
py -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

No Linux/Mac:

```bash
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
```

> Nos comandos seguintes, use `.\venv\Scripts\python.exe` no Windows ou
> `./venv/bin/python` no Linux/Mac.

## 3. Criar o banco de dados

O banco (`db.sqlite3`) também não vai para o Git — cada instalação tem o seu.
Ele é criado ao aplicar as migrações:

```powershell
.\venv\Scripts\python.exe manage.py migrate
```

## 4. Reunir os arquivos estáticos

O sistema roda em modo produção (páginas de erro amigáveis), então o CSS do
site e do painel administrativo precisa ser coletado uma vez (e novamente a
cada atualização do código):

```powershell
.\venv\Scripts\python.exe manage.py collectstatic --noinput
```

## 5. Criar o usuário administrador

Necessário para acessar o painel administrativo (`/admin/`) e para criar as
primeiras contas de operadores:

```powershell
.\venv\Scripts\python.exe manage.py createsuperuser
```

Informe usuário, e-mail (opcional) e senha quando solicitado.

## 6. Rodar o sistema

```powershell
.\venv\Scripts\python.exe manage.py runserver
```

Acesse **http://127.0.0.1:8000** no navegador e entre com o usuário criado no
passo 5. Novas contas de operadores são criadas por quem já está logado, no
menu (ícone de pessoa) → **"Criar conta para terceiro"** — defina uma senha
provisória e repasse ao operador; no primeiro acesso ele será obrigado a
trocá-la.

## Acessar pelo celular (mesma rede Wi-Fi)

1. Descubra o IP do computador: `ipconfig` (Windows) — procure o "Endereço IPv4".
2. Em `config/settings.py`, adicione o IP à lista `ALLOWED_HOSTS`:
   ```python
   ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.0.10']  # troque pelo IP real
   ```
3. Rode o servidor aceitando conexões externas:
   ```powershell
   .\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
   ```
4. No celular, acesse `http://<ip-do-computador>:8000`.

## Problemas comuns

| Sintoma | Causa provável / solução |
|---|---|
| `'py' não é reconhecido` | Python não instalado ou fora do PATH; reinstale marcando *Add to PATH* |
| `No module named django` | Dependências não instaladas no venv — repita o passo 2 |
| `no such table: cargas_carga` | Migrações não aplicadas — repita o passo 3 |
| Erro "Requisição inválida" ao acessar pelo celular | IP não incluído em `ALLOWED_HOSTS` — veja seção acima |
| Página sem estilo (sem cores/ícones) | `collectstatic` não foi executado (passo 4) ou sem internet (Bootstrap vem de CDN) |
| Admin (`/admin/`) sem estilo | Mesmo caso: rode o passo 4 e reinicie o servidor |

## Modo de desenvolvimento

O sistema roda por padrão em modo produção (`DEBUG` desligado): erros mostram
páginas amigáveis em vez das telas técnicas do Django. Para desenvolver e ver
os erros detalhados, ligue a variável de ambiente antes de rodar:

```powershell
$env:DJANGO_DEBUG = '1'
.\venv\Scripts\python.exe manage.py runserver
```

## Aviso para uso em produção real (internet)

Para expor o sistema na internet (fora da rede local), gere uma nova
`SECRET_KEY`, sirva a aplicação com um servidor WSGI (ex.: waitress/gunicorn)
atrás de um proxy com HTTPS e revise:
https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/
