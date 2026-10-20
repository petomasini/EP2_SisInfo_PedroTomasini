"""Testes de integração para rodar com `python manage.py test`."""
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Category, Comment, Post


class BlogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="teste", password="UmaSenhaForte123!")
        cls.post = Post.objects.create(title="Teste", content="<p>Post HTML</p>", published_at=timezone.now())
        cls.category = Category.objects.create(name="Web", description="Sites")
        cls.post.categories.add(cls.category)
        cls.comment = Comment.objects.create(post=cls.post, author=cls.user, text="Comentário teste")

    def test_listagem_e_detalhe(self):
        self.assertContains(self.client.get(reverse("post_list")), "Teste")
        self.assertContains(self.client.get(reverse("post_detail", args=[self.post.pk])), "<p>Post HTML</p>", html=True)

    def test_404_post_e_categoria(self):
        self.assertEqual(self.client.get(reverse("post_detail", args=[99999])).status_code, 404)
        self.assertEqual(self.client.get(reverse("category_detail", args=[99999])).status_code, 404)

    def test_listagem_categoria_reusa_template(self):
        response = self.client.get(reverse("category_detail", args=[self.category.pk]))
        self.assertTemplateUsed(response, "blog/post_list.html")
        self.assertContains(response, "Teste")

    def test_crud_requer_login(self):
        self.assertEqual(self.client.get(reverse("post_create")).status_code, 302)
        self.assertEqual(self.client.get(reverse("post_update", args=[self.post.pk])).status_code, 302)
        self.assertEqual(self.client.get(reverse("post_delete", args=[self.post.pk])).status_code, 302)

    def test_criar_editar_e_confirmar_remocao(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("post_create"), {"title": "Novo", "content": "<p>Novo</p>", "categories": [self.category.pk]})
        self.assertEqual(response.status_code, 302)
        novo = Post.objects.get(title="Novo")
        self.assertEqual(list(novo.categories.all()), [self.category])
        self.client.post(reverse("post_update", args=[novo.pk]), {"title": "Atualizado", "content": "<p>Alterado</p>"})
        novo.refresh_from_db()
        self.assertEqual(novo.title, "Atualizado")
        response = self.client.get(reverse("post_delete", args=[novo.pk]))
        self.assertContains(response, "Remover este artigo?")
        self.assertTrue(Post.objects.filter(pk=novo.pk).exists())
        self.client.post(reverse("post_delete", args=[novo.pk]))
        self.assertFalse(Post.objects.filter(pk=novo.pk).exists())

    def test_comentario_criado_pela_view(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("comment_create", args=[self.post.pk]), {"text": "Mais uma observação"})
        self.assertEqual(response.status_code, 302)
        comentario = Comment.objects.get(text="Mais uma observação")
        self.assertEqual(comentario.author, self.user)
        self.assertEqual(comentario.post, self.post)
        self.assertContains(self.client.get(reverse("post_detail", args=[self.post.pk])), "Mais uma observação")

    def test_ordenacao_comentarios(self):
        Comment.objects.create(post=self.post, author=self.user, text="Comentário mais recente", published_at=timezone.now() + timedelta(minutes=10))
        response = self.client.get(reverse("post_detail", args=[self.post.pk]))
        self.assertEqual(response.context["comments"][0].text, "Comentário mais recente")
