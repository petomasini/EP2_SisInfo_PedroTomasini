# Radar Tech - Segunda Entrega de Laboratório Django

Blog com CRUD, comentários de usuários, categorias e consultas SQL. A pasta `templates/` contém o template base, e a implementação não usa aplicativos de extensão Django.

## Requisitos

- Python 3.13 (também compatível com versões que suportem Django 5.2)
- Git e conexão à internet **no computador em que você executará** para instalar dependências

## Iniciar localmente

### Windows / PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Se você já recebeu um `db.sqlite3` preenchido, coloque-o na raiz do projeto **antes** do `migrate`; o comando `migrate` não deve apagar os dados. O banco **não** está no Git por exigência do enunciado.

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Visite `http://127.0.0.1:8000/` e `http://127.0.0.1:8000/admin/`. O comando `seed_demo` é idempotente, cria três posts, três categorias, quatro comentários e duas contas demonstrativas com **senhas desabilitadas**. Crie seu superusuário com uma senha privada via `createsuperuser`.

## Histórico exigido

As três versões de `blog/views.py` estão registradas em commits separados. Em seguida, os branches `comments` e `categories` são integrados ao branch `main` por merge. As cópias em `docs/versoes/` são para consulta e relatório.

```bash
git log --graph --oneline --all --decorate
git branch -a
```

## Enviar para o GitHub (depois de criar um repositório **vazio**)

```bash
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
git push origin comments categories
```

Não crie README ou `.gitignore` pela interface do GitHub: esses arquivos já estão no histórico deste projeto. Não envie `db.sqlite3` ao GitHub; entregue-o separadamente ao Moodle.

## Publicar no Render

1. Autorize o acesso do Render ao repositório do GitHub.
2. Em **Blueprints > New Blueprint Instance**, escolha esse repositório e aplique o `render.yaml`.
3. O Blueprint cria aplicação Web e PostgreSQL; o projeto usa SQLite apenas localmente.
4. Configure, se necessário, `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` ou domínio customizado.
5. Registre URL pública do Render e URL GitHub no relatório final. **Não inclua credenciais.**

O comando de inicialização usa `migrate` e `seed_demo`, que pode ser executado repetidamente. Para criar conta administrativa no Render, use o Shell do serviço, caso esteja disponível, ou configure de forma temporária `DEMO_ADMIN_USERNAME` e `DEMO_ADMIN_PASSWORD` e redeploy; remova a senha do painel depois. Nunca coloque senhas em arquivos enviados ao GitHub ou no PDF.

## Dados e SQL

- Scripts SQL: `docs/sql/consultas.sql`.
- O arquivo `db.sqlite3` é entregue separadamente.
- O seed satisfaz: 3 posts, 3 categorias, 4 comentários; post 3 sem comentários, posts 1 e 2 com 2 categorias cada.

## Segurança e limites

- Para escrever, editar, remover e comentar, é necessário fazer login.
- O campo `Post.content` é armazenado como HTML e renderizado com `|safe`, como solicitado. Portanto, apenas usuários confiáveis devem poder escrever HTML; no mundo real, sanitizar esse conteúdo.
- O SQLite local não é indicado para armazenamento persistente em hospedagem com filesystem efêmero; por isso Render usa PostgreSQL.
- O banco entregue contém usuários demonstrativos com senhas desabilitadas, sem credenciais expostas.

## Correções de compatibilidade e testes

Após a primeira execução no Windows, foram corrigidas duas falhas identificadas nos testes: (1) a view `CommentCreateView` não deve usar o atributo `self.post`, pois isso substitui o método HTTP `post()` da classe; (2) os testes locais utilizam o backend `StaticFilesStorage`, dispensando o manifesto de `collectstatic`. A configuração de produção mantém `CompressedManifestStaticFilesStorage` com `DEBUG=False`. O script Windows força `DJANGO_DEBUG=1` apenas durante a validação local.

## Validação automatizada de baixa intervenção

O ZIP de distribuição inclui `db.sqlite3` como arquivo **não rastreado no Git**. Em Windows, basta extrair o ZIP e executar `INICIAR_AQUI_WINDOWS.bat` para instalar dependências em `.venv`, aplicar migrações, executar os testes, gerar capturas reais das páginas com o Chrome/Chromium e criar o pacote `CAPTURAS_PARA_RELATORIO.zip` para enviar aqui. Linux/macOS: execute `bash INICIAR_AQUI_LINUX_MAC.sh`.

Se Chrome não estiver disponível para gerar capturas, os comandos `python manage.py check`, `python manage.py migrate` e `python manage.py test` ainda permitem verificar o código. A validação no Windows foi concluída com 7 testes aprovados; foram obtidas 9 capturas de páginas Django com HTTP 200 e 5 capturas das consultas SQL. O relatório foi atualizado com as capturas recebidas.

O gerador opcional de relatório, `tools/gerar_relatorio.py`, usa WeasyPrint. Caso essa dependência não esteja disponível em sua máquina, compartilhe as capturas reais para atualização externa do PDF, sem precisar editar o documento manualmente.
