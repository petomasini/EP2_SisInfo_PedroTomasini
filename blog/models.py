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
