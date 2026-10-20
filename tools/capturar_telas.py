"""Capturas das páginas e dos resultados SQLite.

Uso em ambiente sem Django: python tools/capturar_telas.py --preview
Uso com Django instalado: python tools/capturar_telas.py --django

Em --django, as páginas são entregues pelas views reais via Django test Client.
O Chromium/Chrome apenas transforma essas respostas HTML em screenshots.
"""
import argparse
import html
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs" / "capturas"
CSS = (ROOT / "static" / "css" / "style.css").read_text(encoding="utf-8")


def chromium_binary():
    for program in ["chromium", "chromium-browser", "google-chrome", "chrome"]:
        executable = shutil.which(program)
        if executable:
            return executable
    if sys.platform == "win32":
        paths = [Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe", Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Google/Chrome/Application/chrome.exe", Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe"]
        for path in paths:
            if path.is_file():
                return str(path)
    raise RuntimeError("Chrome/Chromium não encontrado; instale Google Chrome para as capturas.")


def screenshot(content, output, width=1440, height=1020):
    DEST.mkdir(parents=True, exist_ok=True)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        # Alternativa em computadores sem Playwright; Chrome/Chromium instalado basta.
        temp_dir = Path(tempfile.mkdtemp(prefix="radar-capture-"))
        try:
            webpage = temp_dir / "capture.html"
            webpage.write_text(content, encoding="utf-8")
            args = [chromium_binary(), "--headless", "--disable-gpu", "--disable-dev-shm-usage", "--hide-scrollbars", "--no-first-run", "--no-sandbox", f"--window-size={width},{height}", f"--screenshot={output.resolve()}", webpage.resolve().as_uri()]
            result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=35)
            if result.returncode != 0 or not output.is_file():
                raise RuntimeError(f"Chrome nao gerou captura: {result.stderr.decode(errors='replace')[-500:]}")
        finally:
            shutil.rmtree(temp_dir,ignore_errors=True)
        return
    # Playwright.set_content evita restricoes de acesso a file:// de ambientes gerenciados.
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chromium_binary(), headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        page.set_content(content, wait_until="load", timeout=12000)
        page.screenshot(path=str(output),full_page=False)
        browser.close()


def insert_css(rendered):
    rendered = re.sub(r'<link rel="stylesheet" href="[^"]*style\.css"\s*>', lambda _: "<style>"+CSS+"</style>", rendered)
    return rendered


def capture_sql():
    sys.path.insert(0, str(ROOT / "tools"))
    from verificar_sql import execute
    results = execute()
    descriptions = [
        "Todos os posts, do mais recente para o mais antigo",
        "Comentários do post 1",
        "Comentários com dados do post e data renomeada",
        "Todas as colunas de uma categoria e seus posts",
        "Categorias associadas a dois ou mais posts",
    ]
    table_css = """
    <style>
    *{box-sizing:border-box}body{margin:0;background:#edf1f6;font-family:Consolas,Menlo,monospace;color:#172332}.window{margin:30px auto;width:calc(100% - 62px);background:#fff;border:1px solid #ccd5e0;border-radius:10px;box-shadow:0 8px 24px #25364b17;overflow:hidden}.toolbar{background:#20344e;color:#fff;padding:17px 24px;font-family:Arial,sans-serif;font-size:19px;font-weight:bold}.toolbar span{opacity:.6;font-size:12px;font-weight:400;float:right}.wrap{padding:24px}.meta{font-family:Arial;font-size:14px;color:#5c6a77;margin:0 0 16px}.sql{font-family:Consolas,monospace;font-size:14px;line-height:1.55;background:#0e2139;color:#d8e8ff;padding:19px;border-radius:8px;white-space:pre-wrap;overflow-wrap:break-word}.subhead{display:flex;justify-content:space-between;font-family:Arial;align-items:center;margin:22px 0 11px;font-size:17px;font-weight:bold}.rows{font-size:13px;color:#137759}table{width:100%;border-collapse:collapse;table-layout:fixed;font-family:Consolas,monospace;font-size:12px}th,td{border:1px solid #d6dee7;text-align:left;padding:12px 10px;vertical-align:top;overflow-wrap:anywhere}th{background:#dfeaf1;color:#182d41;font-size:13px;white-space:normal}tr:nth-child(even){background:#f8fafc}.foot{font-family:Arial;font-size:12px;color:#788698;margin-top:15px}
    </style>
    """
    for result, desc in zip(results,descriptions):
        cols=result["columns"]
        def display(v):
            if v is None:return "NULL"
            value=str(v)
            if len(value)>85:value=value[:85]+"…"
            return html.escape(value)
        headers="".join(f"<th>{html.escape(col)}</th>" for col in cols)
        rows="".join("<tr>"+"".join(f"<td>{display(cell)}</td>" for cell in row)+"</tr>" for row in result["rows"])
        table=f"<table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>"
        page=f'''<!doctype html><html lang="pt-br"><head><meta charset="utf-8">{table_css}</head><body><div class="window"><div class="toolbar">SQLite - Consulta {result['id']} <span>db.sqlite3 &nbsp; ● SQL executado</span></div><div class="wrap"><p class="meta">{html.escape(desc)}</p><div class="sql">{html.escape(result['sql'])}</div><div class="subhead">Resultado da consulta <span class="rows">{result['total']} registro(s)</span></div>{table}<p class="foot">Fonte: execução local da consulta com sqlite3 (Python) sobre o banco db.sqlite3.</p></div></div></body></html>'''
        out=DEST/f"sql_{result['id']}.png"
        screenshot(page,out,width=1600,height=900 if result["id"]!=4 else 980)
        print(out.name, out.stat().st_size)


class PreviewField:
    def __init__(self,label,name,value="",kind="text",error="",help_text=""):
        self.label=label
        self.name=name
        self.id_for_label="id_"+name
        self.value=value
        self.kind=kind
        self.help_text=help_text
        self.errors=[error] if error else []

    def __html__(self):
        from markupsafe import Markup
        if self.kind=="textarea":
            return Markup(f'<textarea id="{self.id_for_label}" name="{self.name}" rows="10">{html.escape(self.value)}</textarea>')
        if self.kind=="select":
            return Markup('<select multiple id="id_categories" name="categories"><option value="1" selected>Inteligência Artificial</option><option value="2">Segurança Digital</option><option value="3" selected>Desenvolvimento Web</option></select>')
        return Markup(f'<input id="{self.id_for_label}" name="{self.name}" value="{html.escape(self.value)}">')


class PreviewForm:
    def __init__(self,post=None,comment=False):
        if comment:
            self.fields=[PreviewField("Texto", "text", "", "textarea")]
        else:
            self.fields=[PreviewField("Título","title",post.title if post else ""),PreviewField("Conteúdo HTML","content",post.content if post else "","textarea"),PreviewField("Categorias","categories",kind="select")]
        self.non_field_errors=""
        self.text=self.fields[0] if comment else None

    def __iter__(self):
        return iter(self.fields)


def objects():
    con=sqlite3.connect(ROOT/"db.sqlite3")
    con.row_factory=sqlite3.Row
    users={r["id"]:SimpleNamespace(username=r["username"]) for r in con.execute("SELECT id,username FROM auth_user")}
    cats={r["id"]:SimpleNamespace(**dict(r), pk=r["id"]) for r in con.execute("SELECT * FROM blog_category")}
    posts=[]
    for r in con.execute("SELECT * FROM blog_post ORDER BY published_at DESC"):
        post=SimpleNamespace(**dict(r))
        post.pk=post.id
        post.published_at=datetime.fromisoformat(post.published_at)
        selected=[cats[x[0]] for x in con.execute("SELECT category_id FROM blog_post_categories WHERE post_id=?",(post.id,))]
        post.categories=SimpleNamespace(all=selected)
        posts.append(post)
    comments=[]
    for r in con.execute("SELECT * FROM blog_comment WHERE post_id=1 ORDER BY published_at DESC"):
        comment=SimpleNamespace(**dict(r))
        comment.published_at=datetime.fromisoformat(comment.published_at)
        comment.author=users[comment.author_id]
        comments.append(comment)
    con.close()
    return posts, list(cats.values()),comments


def preview_render(template, context):
    from jinja2 import Environment,FileSystemLoader, select_autoescape
    templates=ROOT/"templates"
    def raw_text(filename):
        source=(templates/filename).read_text(encoding="utf-8")
        source=source.replace("{% load static %}","").replace("{% csrf_token %}",'<input type="hidden" name="csrfmiddlewaretoken" value="preview">')
        source=source.replace("{% empty %}","{% else %}")
        source=re.sub(r"\|date:'([^']+)'", lambda m:'|br_date("'+m.group(1)+'")',source)
        source=re.sub(r"\|truncatechars:(\d+)", r"|truncatechars(\1)",source)
        source=re.sub(r"\{% static '([^']+)' %\}",lambda m:'"/static/'+m.group(1)+'"',source)
        def url_template(match):
            name,args=match.group(1),match.group(2).strip()
            return "{{ url('"+name+"'"+(" ,"+args if args else "")+") }}"
        source=re.sub(r"\{% url '([\w:]+)'([^%]*)%\}",url_template,source)
        return source
    class DjangoishLoader(FileSystemLoader):
        def get_source(self, environment, template):
            file=templates/template
            return raw_text(template),str(file),lambda:file.exists()
    env=Environment(loader=DjangoishLoader(templates),autoescape=select_autoescape(enabled_extensions=("html",)),auto_reload=False)
    def url(name,pk=None):
        path={"post_list":"/","post_create":"/posts/novo/","category_list":"/categorias/","login":"/contas/login/","signup":"/contas/cadastrar/","logout":"/contas/logout/","admin:index":"/admin/"}
        if pk is not None:
            return {"post_detail":f"/posts/{pk}/","post_update":f"/posts/{pk}/editar/","post_delete":f"/posts/{pk}/remover/","comment_create":f"/posts/{pk}/comentar/","category_detail":f"/categorias/{pk}/"}.get(name,"#")
        return path.get(name,"#")
    env.globals["url"]=url
    env.filters["br_date"]=lambda d,fmt:d.strftime(fmt.replace("d","%d").replace("m","%m").replace("Y","%Y").replace("H","%H").replace("i","%M")) if isinstance(d,datetime) else str(d)
    env.filters["truncatechars"]=lambda v,n:v[:n-1]+"…" if len(v)>n else v
    env.filters["linebreaksbr"]=lambda v:v.replace("\n","<br>")
    ctx={"user":SimpleNamespace(is_authenticated=True,username="admin_local"), "messages":[], **context}
    rendered=env.get_template(template).render(**ctx)
    # O modo preview substitui apenas a folha de estilos externa pela identica folha local.
    rendered=rendered.replace('href=""/static/css/style.css""','href="/static/css/style.css"')
    return insert_css(rendered)


def capture_preview():
    posts,categories,comments=objects()
    p1=posts[0]
    category=next(c for c in categories if c.name=="Desenvolvimento Web")
    targets=[
       ("listagem_posts.png","blog/post_list.html",{"posts":posts},1380),
       ("post_individual.png","blog/post_detail.html",{"post":p1,"comments":comments,"comment_form":PreviewForm(comment=True)},970),
       ("criacao_post.png","blog/post_form.html",{"form":PreviewForm()},1000),
       ("edicao_post.png","blog/post_form.html",{"form":PreviewForm(post=p1),"object":p1},1050),
       ("remocao_post.png","blog/post_confirm_delete.html",{"post":p1},850),
       ("post_com_comentarios.png","blog/post_detail.html",{"post":p1,"comments":comments,"comment_form":PreviewForm(comment=True)},1440),
       ("criacao_comentario.png","blog/comment_form.html",{"post":p1,"form":PreviewForm(comment=True)},850),
       ("post_com_categorias.png","blog/post_detail.html",{"post":p1,"comments":comments,"comment_form":PreviewForm(comment=True)},900),
       ("categoria_individual.png","blog/post_list.html",{"posts":[p for p in posts if category in p.categories.all], "category":category},1380),
    ]
    for filename,template,context,h in targets:
        screenshot(preview_render(template,context),DEST/filename,1440,h)
        print(filename,(DEST/filename).stat().st_size)
    (DEST/"ORIGEM_DAS_CAPTURAS.txt").write_text("PREVIA ESTATICA: imagens geradas a partir de templates e dados reais SQLite; nao sao views servidas por Django.\nPara substitui-las por capturas de respostas reais, execute `python tools/capturar_telas.py --django` em ambiente com Django.\n",encoding="utf-8")


def capture_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
    sys.path.insert(0,str(ROOT))
    import django
    django.setup()
    from django.contrib.auth import get_user_model
    from django.test import Client
    from django.urls import reverse
    from blog.models import Post, Category
    c=Client()
    admin=get_user_model().objects.filter(is_superuser=True).first()
    if not admin:
        raise RuntimeError("Crie um superusuario com `python manage.py createsuperuser` para obter capturas autenticadas.")
    c.force_login(admin)
    p1=Post.objects.order_by("-published_at").first()
    category=Category.objects.get(name="Desenvolvimento Web")
    cases=[
       ("listagem_posts.png",reverse("post_list"),1380),
       ("post_individual.png",reverse("post_detail",args=[p1.pk]),970),
       ("criacao_post.png",reverse("post_create"),1000),
       ("edicao_post.png",reverse("post_update",args=[p1.pk]),1050),
       ("remocao_post.png",reverse("post_delete",args=[p1.pk]),850),
       ("post_com_comentarios.png",reverse("post_detail",args=[p1.pk]),1440),
       ("criacao_comentario.png",reverse("comment_create",args=[p1.pk]),850),
       ("post_com_categorias.png",reverse("post_detail",args=[p1.pk]),900),
       ("categoria_individual.png",reverse("category_detail",args=[category.pk]),1380),
    ]
    for name,path,h in cases:
        response=c.get(path)
        if response.status_code!=200:
            raise RuntimeError(f"Resposta HTTP {response.status_code} para {path}: {response.content[:250]!r}")
        screenshot(insert_css(response.content.decode("utf-8")),DEST/name,1440,h)
        print(name,"HTTP",response.status_code)
    (DEST/"ORIGEM_DAS_CAPTURAS.txt").write_text("CAPTURAS REAIS: HTML produzido por views Django via Django test Client autenticado, renderizado em Chromium/Chrome.\n",encoding="utf-8")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true",help="gera amostras estaticas dos templates")
    ap.add_argument("--django",action="store_true",help="captura respostas das views reais do Django")
    ap.add_argument("--sql",action="store_true",help="gera apenas os resultados reais SQLite")
    args=ap.parse_args()
    if args.django:
        capture_django()
    elif args.preview or not args.sql:
        capture_preview()
    capture_sql()


if __name__=="__main__":
    main()
