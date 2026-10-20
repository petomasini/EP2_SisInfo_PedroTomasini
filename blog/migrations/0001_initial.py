from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200, verbose_name="Título")),
                ("content", models.TextField(verbose_name="Conteúdo HTML")),
                ("published_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="Data de publicação")),
            ],
            options={"ordering": ["-published_at"], "verbose_name": "Post", "verbose_name_plural": "Posts"},
        ),
    ]
