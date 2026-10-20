from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Título do artigo"}),
            "content": forms.Textarea(attrs={"rows": 10, "placeholder": "Use HTML: <p>Texto</p>"}),
        }
