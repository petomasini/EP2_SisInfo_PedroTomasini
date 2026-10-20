from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("blog", "0002_comment")]
    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="Nome")),
                ("description", models.TextField(verbose_name="Descrição")),
            ],
            options={"ordering": ["name"], "verbose_name": "Categoria", "verbose_name_plural": "Categorias"},
        ),
        migrations.AddField(
            model_name="post",
            name="categories",
            field=models.ManyToManyField(blank=True, related_name="posts", to="blog.category", verbose_name="Categorias"),
        ),
    ]
