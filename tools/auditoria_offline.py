"""Auditoria técnica sem dependências externas (substitui, não, testes Django)."""
import ast
import sqlite3
import subprocess
from pathlib import Path
from verificar_sql import execute

ROOT=Path(__file__).resolve().parents[1]


def verify():
    django_files=list(ROOT.rglob('*.py'))
    for file in django_files:
        if '.venv' in file.parts or '__pycache__' in file.parts:continue
        ast.parse(file.read_text(encoding='utf-8'),filename=str(file))
    print(f'Sintaxe Python: OK ({len(django_files)} arquivos)')
    content=(ROOT/'blog/models.py').read_text(encoding='utf-8')
    for name in ['class Post(models.Model)','class Comment(models.Model)','class Category(models.Model)','settings.AUTH_USER_MODEL','models.DateTimeField','models.ManyToManyField']:
        assert name in content,name
    print('Models e relacionamentos: presentes')
    views=(ROOT/'blog/views.py').read_text(encoding='utf-8')
    for name in ['ListView','DetailView','CreateView','UpdateView','DeleteView','get_object_or_404','CommentCreateView','CategoryListView','CategoryDetailView']:
        assert name in views,name
    base=(ROOT/'templates/base.html').read_text(encoding='utf-8')
    assert "{% url 'category_list' %}" in base
    detail=(ROOT/'templates/blog/post_detail.html').read_text(encoding='utf-8')
    assert '|safe' in detail and '|date:' in detail and 'comment_create' in detail and 'category_detail' in detail
    print('Views, templates e URLs nomeadas: presentes')
    history=subprocess.check_output(['git','log','--oneline','--all'],cwd=ROOT,text=True)
    for required in ['Parte 1 (v1)','Parte 1 (v2)','Parte 1 (v3)','Merge comments','Merge categories']:
        assert required in history,required
    for branch in ['comments','categories']:
        assert subprocess.run(['git','rev-parse','--verify',branch],cwd=ROOT,capture_output=True).returncode==0
    print('Branches, commits e merges: presentes')
    sql=execute()
    print('SQL executado e contagens conferidas:',[r['total'] for r in sql])
    c=sqlite3.connect(ROOT/'db.sqlite3')
    try:
        assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert not c.execute('PRAGMA foreign_key_check').fetchall()
        cats=c.execute('SELECT COUNT(*) FROM blog_post_categories').fetchone()[0]
        assert cats==5
        assert c.execute('SELECT COUNT(*) FROM auth_user WHERE is_superuser=1').fetchone()[0]>=1
        assert c.execute("SELECT COUNT(*) FROM django_migrations WHERE app='blog'").fetchone()[0]==3
    finally:c.close()
    print('SQLite: integridade, chaves estrangeiras, migracoes e dados verificados')
    print('ATENCAO: nao substitui `python manage.py check`, `migrate` ou `test` com Django instalado.')


if __name__=='__main__':verify()
