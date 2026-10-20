from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Post(models.Model):
    title = models.CharField("Título", max_length=200)
    content = models.TextField("Conteúdo HTML")
    published_at = models.DateTimeField("Data de publicação", default=timezone.now)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"pk": self.pk})


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="Post")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_comments",
        verbose_name="Autor",
    )
    text = models.TextField("Texto")
    published_at = models.DateTimeField("Data de postagem", default=timezone.now)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"

    def __str__(self):
        return f"{self.author} em {self.post}"
