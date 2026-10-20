"""Dados reproduzíveis para o laboratório, sem senhas pré-definidas."""
import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from blog.models import Category, Comment, Post

from blog.demo_data import CATEGORIES, POSTS, COMMENTS


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
