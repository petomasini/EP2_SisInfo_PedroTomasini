from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "categories"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Título do artigo"}),
            "content": forms.Textarea(attrs={"rows": 10, "placeholder": "Use HTML: <p>Texto</p>"}),
        }


from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {"text": forms.Textarea(attrs={"rows": 4, "placeholder": "Escreva um comentário..."})}
