from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("blog", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Comment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField(verbose_name="Texto")),
                ("published_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="Data de postagem")),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="blog_comments", to=settings.AUTH_USER_MODEL, verbose_name="Autor")),
                ("post", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="comments", to="blog.post", verbose_name="Post")),
            ],
            options={"ordering": ["-published_at"], "verbose_name": "Comentário", "verbose_name_plural": "Comentários"},
        ),
    ]
