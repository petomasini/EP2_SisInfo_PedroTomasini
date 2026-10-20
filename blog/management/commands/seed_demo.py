"""Dados reproduzíveis para o laboratório, sem senhas pré-definidas."""
import os
from datetime import datetime, timezone
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from blog.models import Category, Comment, Post

CATEGORIES = [
    ("Inteligência Artificial", "Aplicações de IA, automação e pensamento crítico."),
    ("Segurança Digital", "Boas práticas de privacidade, proteção e identidade digital."),
    ("Desenvolvimento Web", "Práticas modernas para construir experiências na web."),
]
POSTS = [
    ("IA generativa no cotidiano", """
<p>Ferramentas de inteligência artificial já fazem parte de tarefas como organizar ideias, estudar, programar e resumir documentos.</p>
<h2>O que muda no dia a dia?</h2>
<p>A velocidade aumenta, mas a revisão humana continua essencial. Respostas produzidas automaticamente podem conter erros e precisam ser verificadas.</p>
<h2>Como começar com responsabilidade</h2>
<ul><li>Defina claramente o objetivo.</li><li>Confira fatos importantes.</li><li>Não compartilhe dados sensíveis sem autorização.</li></ul>
<p>O uso produtivo de IA combina experimentação, transparência e senso crítico.</p>
""".strip(), datetime(2026, 10, 18, 18, 0, tzinfo=timezone.utc), ["Inteligência Artificial", "Desenvolvimento Web"]),
    ("Segurança digital: hábitos que protegem", """
<p>A proteção de contas começa com decisões simples e consistentes. Senhas reutilizadas e links suspeitos continuam sendo riscos frequentes.</p>
<h2>Checklist de proteção</h2>
<ul><li>Use senhas únicas e extensas.</li><li>Ative autenticação de múltiplos fatores.</li><li>Mantenha aplicativos atualizados.</li></ul>
<p>Também é importante revisar permissões de aplicativos e reconhecer tentativas de phishing.</p>
""".strip(), datetime(2026, 10, 16, 17, 30, tzinfo=timezone.utc), ["Segurança Digital", "Desenvolvimento Web"]),
    ("Como criar interfaces mais acessíveis", """
<p>Acessibilidade significa projetar para pessoas com necessidades, dispositivos e contextos diferentes.</p>
<h2>Boas práticas</h2>
<p>Use HTML semântico, rótulos claros para formulários, contraste adequado e navegação por teclado.</p>
<p>Testar com usuários reais e tecnologias assistivas melhora a experiência de todos.</p>
""".strip(), datetime(2026, 10, 14, 15, 15, tzinfo=timezone.utc), ["Desenvolvimento Web"]),
]
COMMENTS = [
    ("IA generativa no cotidiano", "ana_demo", "Ótimo resumo! A verificação das fontes faz toda a diferença.", datetime(2026, 10, 19, 10, 0, tzinfo=timezone.utc)),
    ("IA generativa no cotidiano", "bruno_demo", "Gostei das recomendações para uso responsável.", datetime(2026, 10, 18, 22, 30, tzinfo=timezone.utc)),
    ("Segurança digital: hábitos que protegem", "bruno_demo", "A autenticação em duas etapas já virou hábito por aqui.", datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)),
    ("Segurança digital: hábitos que protegem", "ana_demo", "Um gerenciador de senhas também ajuda bastante.", datetime(2026, 10, 17, 11, 15, tzinfo=timezone.utc)),
]


class Command(BaseCommand):
    help = "Cria 3 posts, 3 categorias, 4 comentários e contas demo sem senhas válidas; idempotente."

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        users = {}
        for username, email in [("ana_demo", "ana@example.invalid"), ("bruno_demo", "bruno@example.invalid")]:
            user, created = User.objects.get_or_create(username=username, defaults={"email": email})
            if created:
                user.set_unusable_password()
                user.save(update_fields=["password"])
            users[username] = user
        categories = {}
        for name, description in CATEGORIES:
            category, _ = Category.objects.get_or_create(name=name, defaults={"description": description})
            categories[name] = category
        posts = {}
        for title, content, date, tags in POSTS:
            post, _ = Post.objects.get_or_create(title=title, defaults={"content": content, "published_at": date})
            post.categories.set([categories[t] for t in tags])
            posts[title] = post
        for title, username, text, date in COMMENTS:
            Comment.objects.get_or_create(post=posts[title], author=users[username], text=text, defaults={"published_at": date})
        admin_password = os.environ.get("DEMO_ADMIN_PASSWORD")
        if admin_password:
            admin_username = os.environ.get("DEMO_ADMIN_USERNAME", "admin")
            admin_user, _ = User.objects.get_or_create(username=admin_username)
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.is_active = True
            admin_user.set_password(admin_password)
            admin_user.save()
            self.stdout.write("Conta administrativa configurada por variáveis de ambiente.")
        self.stdout.write(self.style.SUCCESS(
            f"Banco pronto: {Post.objects.count()} posts, {Category.objects.count()} categorias, "
            f"{Comment.objects.count()} comentarios."
        ))
