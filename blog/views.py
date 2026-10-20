"""Versão 1: FBV, sem Django Forms e sem validação dos campos."""
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Post


def post_list(request):
    return render(request, "blog/post_list.html", {"posts": Post.objects.all()})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "blog/post_detail.html", {"post": post})


@login_required
def post_create(request):
    if request.method == "POST":
        post = Post.objects.create(
            title=request.POST.get("title", ""),
            content=request.POST.get("content", ""),
        )
        return redirect("post_detail", pk=post.pk)
    return render(request, "blog/post_raw_form.html", {"form_title": "Novo post"})


@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        post.title = request.POST.get("title", "")
        post.content = request.POST.get("content", "")
        post.save()
        return redirect("post_detail", pk=post.pk)
    return render(request, "blog/post_raw_form.html", {"form_title": "Editar post", "post": post})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        post.delete()
        return redirect("post_list")
    return render(request, "blog/post_confirm_delete.html", {"post": post})
