"""Gera PDF acadêmico da Segunda Entrega. Uso:

python tools/gerar_relatorio.py
python tools/gerar_relatorio.py --github-url https://github.com/... --render-url https://....onrender.com

O script distingue honestamente capturas de views Django das prévias estáticas.
"""
import argparse
import html
import json
import subprocess
from pathlib import Path
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
CAPTURAS = ROOT / "docs" / "capturas"
VERSOES = ROOT / "docs" / "versoes"
DOC = ROOT / "docs" / "sql"
OUTPUT = ROOT.parent / "relatorio_segunda_entrega_django.pdf"


def esc(txt):
    return html.escape(str(txt), quote=True)


def code_file(title, filename, note):
    code=(VERSOES / filename).read_text(encoding="utf-8")
    return f'''<section class="listing"><h4>{esc(title)}</h4><p class="filename">{esc(filename)} &mdash; {esc(note)}</p><pre>{esc(code)}</pre></section>'''


def figure(filename, caption,alt, preview):
    source=CAPTURAS / filename
    if not source.exists():
        raise FileNotFoundError(source)
    label="Prévia visual" if preview else "Captura de tela"
    return f'''<figure><img src="{source.resolve().as_uri()}" alt="{esc(alt)}"><figcaption><strong>{label}.</strong> {esc(caption)}</figcaption></figure>'''


def make(github_url="",render_url="",output=OUTPUT):
    capture_notice=(CAPTURAS / "ORIGEM_DAS_CAPTURAS.txt").read_text(encoding="utf-8")
    preview = capture_notice.startswith("PREVIA")
    src_sql=json.loads((DOC / "resultados.json").read_text(encoding="utf-8"))
    graph=subprocess.check_output(["git","log","--graph","--oneline","--all","--decorate","-8"],cwd=ROOT,text=True)
    names=["Todos os posts em ordem decrescente de data", "Comentários do post selecionado", "Comentários com colunas do post e post_date", "Categoria com todas as colunas dos posts", "Categorias que possuem dois ou mais posts"]
    sql_html=""
    for idx,(name,data) in enumerate(zip(names,src_sql),1):
        sql_html += f'''<section class="query-block"><h3>Consulta {idx} &mdash; {esc(name)}</h3><div class="sqlcode"><pre>{esc(data['sql'])}</pre></div><p class="result">Resultado obtido: <b>{data['total']} linha(s)</b>.</p>{figure(f"sql_{idx}.png",f"Execução SQL da consulta {idx} sobre db.sqlite3.",f"Resultado SQL {idx}",False)}</section>'''
    urls=""
    if github_url:
        urls+=f'<p><strong>Repositório GitHub:</strong> <a href="{esc(github_url)}">{esc(github_url)}</a></p>'
    else:
        urls+='<p><strong>GitHub:</strong> publicação ainda pendente. O link pode ser adicionado aos comentários da entrega no Moodle, como autoriza o enunciado.</p>'
    if render_url:
        urls+=f'<p><strong>Página no Render:</strong> <a href="{esc(render_url)}">{esc(render_url)}</a></p>'
    else:
        urls+='<p><strong>Render:</strong> publicação ainda pendente. Inserir o URL nos comentários da entrega no Moodle, como autoriza o enunciado.</p>'
    observations='''<div class="note warn"><strong>Validação pendente:</strong> o ambiente utilizado para produzir este relatório não pôde instalar Django. As imagens das interfaces exibidas nesta versão são pré-visualizações estáticas derivadas dos próprios templates e dos dados SQLite. Não devem ser apresentadas como evidência de execução das views. Para finalizar a validação, instalar as dependências em um ambiente com internet, executar <code>python manage.py test</code> e <code>python tools/capturar_telas.py --django</code>, e regenerar o relatório ou fornecer as novas imagens para substituição.</div>''' if preview else '''<div class="note success"><strong>Evidências de interface:</strong> capturas geradas a partir do HTML fornecido pelas views reais do Django por meio do test client autenticado, renderizado em Chrome/Chromium. Os resultados SQL foram executados em SQLite.</div>'''
    html_body=f'''<!doctype html><html lang="pt-br"><head><meta charset="utf-8">
<style>
@page {{ size:A4; margin:18mm 18mm 19mm 18mm; @top-right {{content:"RADAR TECH  /  LABORATÓRIO DJANGO";font-family:'DejaVu Sans',Arial,sans-serif;font-size:8pt;color:#6d7d8a;}} @bottom-left {{content:"Segunda Entrega de Laboratório";font-family:'DejaVu Sans',Arial,sans-serif;font-size:8pt;color:#728091;}} @bottom-right {{content:counter(page);font-family:'DejaVu Sans',Arial,sans-serif;font-size:8pt;color:#728091;}} }}
*{{box-sizing:border-box}}body{{font-family:'DejaVu Sans',Arial,sans-serif;font-size:10.3pt;line-height:1.60;color:#202d3b;margin:0}}
h1,h2,h3,h4{{line-height:1.25;color:#132c42}}h1{{font-size:30pt;letter-spacing:-.8pt;margin:0 0 14pt}}h2{{font-size:17pt;margin:25pt 0 11pt;padding-bottom:6pt;border-bottom:1pt solid #ced9de}}h3{{font-size:12.5pt;margin:18pt 0 8pt}}h4{{font-size:10.5pt;margin:13pt 0 6pt}}p{{margin:0 0 11pt}}ul{{padding-left:18pt;margin:5pt 0 12pt}}li{{margin-bottom:4pt}}
a{{color:#0a7670;word-break:break-word}}.cover{{height:244mm;padding:30mm 2mm 20mm;position:relative;page-break-after:always}}.cover-label{{color:#087a75;font-size:11pt;font-weight:bold;letter-spacing:2.0pt;margin:0 0 20pt}}.cover h1{{font-size:37pt;max-width:145mm}}.cover-summary{{font-size:14pt;color:#5d6d7a;max-width:140mm;margin-top:20pt;line-height:1.7}}.cover-line{{height:4pt;width:65mm;background:#0a817c;margin:34pt 0}}.cover-details{{margin-top:48pt;border-top:1pt solid #d9e2e7;padding-top:17pt;font-size:10pt;color:#63748a}}.cover-foot{{position:absolute;bottom:13mm;left:2mm;font-size:9.5pt;color:#768592}}.intro-label{{font-size:8.5pt;text-transform:uppercase;color:#00766c;font-weight:800;letter-spacing:1.2pt}}.figure-section{{margin-bottom:4pt}}figure{{margin:18pt 0 21pt;break-inside:avoid;page-break-inside:avoid}}figure img{{width:100%;max-height:143mm;object-fit:contain;border:1px solid #dee5ea;border-radius:4pt}}figcaption{{font-size:8pt;line-height:1.5;color:#647487;margin-top:5pt;text-align:left}}.note{{border-left:3pt solid #107773;background:#eef7f6;padding:12pt 13pt;margin:16pt 0;line-height:1.55;font-size:9pt}}.warn{{background:#fff9ee;border-color:#b38836}}.success{{background:#eff8f5;border-color:#288567}}.listing{{margin:16pt 0 25pt}}.listing h4{{margin-bottom:3pt}}.filename{{font-family:'DejaVu Sans Mono',monospace;color:#667588;font-size:8pt;margin:3pt 0 7pt}}pre{{font-family:'DejaVu Sans Mono',monospace;font-size:7pt;line-height:1.44;white-space:pre-wrap;overflow-wrap:anywhere;margin:0}}.listing pre{{background:#f3f6f7;border-left:2pt solid #8cafb6;padding:10pt}}.sqlcode{{background:#f3f6f7;padding:10pt;border-left:2pt solid #007c77}}.sqlcode pre{{font-size:8pt}}.result{{font-size:9pt;margin-top:9pt;color:#516477}}.query-block{{margin:15pt 0 28pt}}.chip{{display:inline-block;color:#006e68;background:#e7f3f1;padding:3pt 8pt;border-radius:4pt;font-size:8.3pt;margin-right:6pt}}.stats{{width:100%;border-collapse:collapse;margin:13pt 0 18pt}}.stats th,.stats td{{border-bottom:.7pt solid #d6e0e4;padding:9pt 8pt;text-align:left;font-size:9pt}}.stats th{{background:#f2f7f8;color:#1b4755}}.tiny{{font-size:8.5pt;color:#5f7183}}.spacer{{margin-top:21pt}}.section-break{{page-break-before:always}}.git{{font-family:'DejaVu Sans Mono',monospace;white-space:pre-wrap;font-size:8pt;background:#f3f6f7;padding:9pt}}code{{font-family:'DejaVu Sans Mono',monospace;font-size:.85em;background:#edf1f4;padding:1pt}}.key-points{{margin-top:10pt}}.link-block{{margin:15pt 0;border:1px solid #d7e0e5;padding:13pt;border-radius:5pt}}
</style></head><body>
<section class="cover"><p class="cover-label">RELATÓRIO TÉCNICO &nbsp; / &nbsp; DESENVOLVIMENTO WEB</p><h1>Segunda Entrega de Laboratório</h1><p class="cover-summary">Aplicação CRUD com Django: blog dinâmico, comentários, categorias, controle de versões e consultas SQL.</p><div class="cover-line"></div><p><span class="chip">Django</span><span class="chip">SQLite</span><span class="chip">Git</span><span class="chip">SQL</span></p><div class="cover-details">Projeto: <strong>Radar Tech</strong><br>Tipo de entrega: relatório em PDF + banco de dados <strong>db.sqlite3</strong><br>Data de elaboração: <strong>20 de outubro de 2026</strong></div><div class="cover-foot">Trabalho acadêmico &nbsp; • &nbsp; Aplicação web dinâmica</div></section>
<h2>1. Introdução</h2>
<p>Um website estático não oferece, por si só, persistência de informações nem meios simples de interação para usuários comuns. Este trabalho apresenta a construção de um blog dinâmico denominado <strong>Radar Tech</strong>, desenvolvido com o framework Django, que permite criar, consultar, editar e remover publicações por meio de uma interface web.</p>
<p>O projeto foi estruturado de forma incremental, incorporando comentários associados a usuários e uma classificação de posts por múltiplas categorias. As informações são persistidas em um banco de dados relacional, o que também permite demonstrar consultas SQL com filtros, ordenação, junções e agrupamento.</p>
<h2>2. Objetivo</h2>
<p>Desenvolver uma aplicação CRUD com o Django, demonstrando as diferenças entre views funcionais e baseadas em classes genéricas, implementando modelos relacionados e organizando a evolução do projeto com branches e commits Git.</p>
<ul><li>Implementar cinco operações/páginas de post com URLs nomeadas, templates reutilizáveis, resposta HTTP 404 para recursos ausentes e confirmação de remoção.</li><li>Registrar comentários relacionados a posts e ao usuário autenticado e exibir os mais recentes primeiro.</li><li>Permitir que um post pertença a várias categorias e apresentar uma página de posts por categoria.</li><li>Popular um banco SQLite e executar as cinco consultas exigidas no enunciado.</li><li>Preparar a publicação do código no GitHub e da aplicação no Render.</li></ul>
<h2>3. Metodologia</h2>
<p>A aplicação foi separada em um projeto Django (<code>config/</code>) e uma aplicação de domínio (<code>blog/</code>). Os templates de interface residem em <code>templates/</code>, incluindo o arquivo <code>templates/base.html</code>. O modelo <code>Post</code> armazena o conteúdo como texto HTML, renderizado com <code>|safe</code> na página individual, e sua data em um <code>DateTimeField</code>, formatada por <code>|date</code>.</p>
<p>A primeira parte foi implementada em três etapas: funções sem forms nem validação dos campos; funções com <code>ModelForm</code>; e as classes genéricas <code>ListView</code>, <code>DetailView</code>, <code>CreateView</code>, <code>UpdateView</code> e <code>DeleteView</code>. Foram utilizados CSRF e autenticação nas operações que modificam dados.</p>
<p>Em seguida, a funcionalidade de comentários foi desenvolvida no branch <code>comments</code> e integrada ao branch <code>main</code>. O mesmo processo foi realizado no branch <code>categories</code>, criado após o primeiro merge. Os models foram registrados no Django Admin; o preenchimento de dados é reproduzível por <code>seed_demo</code>. Não foram utilizadas extensões do Django em <code>INSTALLED_APPS</code>.</p>
<h3>3.1. Estrutura relacional</h3>
<table class="stats"><thead><tr><th>Modelo</th><th>Campos e relações principais</th></tr></thead><tbody><tr><td><strong>Post</strong></td><td>title, content (HTML), published_at (DateTimeField), categories (N:N)</td></tr><tr><td><strong>Comment</strong></td><td>text, published_at (DateTimeField), post (N:1), author (FK AUTH_USER_MODEL)</td></tr><tr><td><strong>Category</strong></td><td>name, description, relação reversa com posts (N:N)</td></tr></tbody></table>
<h3>3.2. Histórico Git</h3><p>O histórico abaixo documenta os três commits distintos de implementação do CRUD e os merges de comentários e categorias:</p><pre class="git">{esc(graph)}</pre>
{observations}
<div class="section-break"></div><h2>4. Resultados</h2>
<h3>4.1. Parte 1 &mdash; Aplicação CRUD de posts</h3>
<p>As cinco operações CRUD foram expostas por URLs com nomes próprios. As três versões completas de <code>blog/views.py</code> aparecem a seguir, conforme exigido. O Django Admin inclui o modelo de posts e a exclusão solicita confirmação antes da operação POST.</p>
{code_file('Versão 1: views funcionais, sem forms e sem validação', 'views_v1.py', 'commit 4174c58')}
{code_file('Versão 2: views funcionais com ModelForm', 'views_v2.py', 'commit eb49043')}
{code_file('Versão 3: views genéricas baseadas em classes', 'views_v3.py', 'commit ce6eec7')}
<h3>4.1.1. Evidências das páginas de posts</h3>
{figure('listagem_posts.png','Página de listagem com títulos de posts, datas e links para os artigos.','Listagem de posts',preview)}
{figure('post_individual.png','Página de post individual, exibindo o conteúdo HTML renderizado e data formatada.','Post individual',preview)}
{figure('criacao_post.png','Formulário de criação de posts acessível por URL nomeada.','Criar post',preview)}
{figure('edicao_post.png','Formulário de atualização dos dados de uma publicação existente.','Editar post',preview)}
{figure('remocao_post.png','Confirmação antes da exclusão de um post.','Confirmar remoção',preview)}
<div class="section-break"></div><h3>4.2. Parte 2 &mdash; Comentários em posts</h3>
<p>O modelo <code>Comment</code> guarda o texto, a data da postagem e as referências a <code>Post</code> e ao usuário do Django. Os comentários são exibidos na página individual em ordem decrescente de data. A criação é possível tanto diretamente na página do post quanto em uma página própria, por usuários autenticados.</p>
{code_file('Listagem de views após a implementação dos comentários', 'views_part2.py', 'branch comments, antes do primeiro merge')}
{figure('post_com_comentarios.png','Publicação individual exibindo comentários associados, mais recentes primeiro.','Post com comentários',preview)}
{figure('criacao_comentario.png','Formulário de criação de comentário com vínculo automático ao usuário logado.','Criar comentário',preview)}
<div class="section-break"></div><h3>4.3. Parte 3 &mdash; Categorias</h3>
<p>Foi criado o modelo <code>Category</code> com nome e descrição. A relação entre posts e categorias é muitos-para-muitos. A listagem de posts por categoria reutiliza <code>blog/post_list.html</code>, agora exibindo o nome e a descrição da categoria selecionada. O administrador permite a manutenção de categorias.</p>
{code_file('Listagem de views após a implementação das categorias', 'views_part3.py', 'branch categories, antes do segundo merge')}
{figure('post_com_categorias.png','Post individual com links para suas categorias associadas.','Post com categorias',preview)}
{figure('categoria_individual.png','Página da categoria Desenvolvimento Web, listando os posts correspondentes.','Categoria individual',preview)}
<h3>4.3.1. Publicação do projeto</h3><div class="link-block">{urls}</div><p class="tiny">O projeto contém um <code>render.yaml</code> para implantação, uma configuração PostgreSQL para uso remoto e um arquivo <code>.gitignore</code> que exclui <code>db.sqlite3</code> e <code>__pycache__/</code>.</p>
<div class="section-break"></div><h3>4.4. Parte 4 &mdash; Consultas SQL</h3>
<p>O arquivo <code>db.sqlite3</code> foi preenchido com três posts, três categorias e quatro comentários. Dois posts possuem duas categorias cada; o terceiro não possui comentários. Cada um dos dois posts comentados apresenta dois comentários. Todos os posts pertencem a pelo menos uma categoria.</p>
<table class="stats"><thead><tr><th>Elemento</th><th>Quantidade</th><th>Condição atendida</th></tr></thead><tbody><tr><td>Posts</td><td>3</td><td>1 post sem comentários</td></tr><tr><td>Comentários</td><td>4</td><td>2 comentários por post comentado</td></tr><tr><td>Categorias</td><td>3</td><td>2 posts com múltiplas categorias</td></tr><tr><td>Associações post-categoria</td><td>5</td><td>Todos os posts categorizados</td></tr><tr><td>Usuários</td><td>3</td><td>2 demonstrativos e 1 superusuário local</td></tr></tbody></table>
<p>As cinco consultas foram executadas diretamente no SQLite e seus resultados registrados em capturas. A terceira consulta seleciona todas as colunas do comentário exceto <code>post_id</code> e inclui <code>title</code> e <code>post_date</code>. A quarta retorna todas as colunas de ambas as tabelas relacionadas; a quinta aplica <code>GROUP BY</code> e <code>HAVING</code>.</p>
{sql_html}
<div class="spacer"></div><h3>Síntese da entrega</h3><p>O código-fonte e o histórico Git estão reunidos no repositório local do projeto; o SQLite com os dados exigidos é disponibilizado separadamente para submissão ao Moodle. As consultas SQL foram validadas em banco íntegro. A comprovação de funcionamento das views Django e a publicação pública devem ser confirmadas antes do envio definitivo.</p>
</body></html>'''
    output=Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_body,base_url=str(ROOT)).write_pdf(str(output))
    print("PDF:",output,"bytes:",output.stat().st_size)
    print("Mode:","PREVIA" if preview else "DJANGO")


if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--github-url",default="")
    ap.add_argument("--render-url",default="")
    ap.add_argument("--output",default=str(OUTPUT))
    ns=ap.parse_args()
    make(ns.github_url,ns.render_url,ns.output)
