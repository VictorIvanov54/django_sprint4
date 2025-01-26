from datetime import datetime

from django.shortcuts import get_object_or_404, render

from blog.models import Post, Category
from blog.constants import NUMBER_POSTS_DISPLAYED


def index(request):
    template_name = 'blog/index.html'
    post_list = Post.objects.select_related('category', 'location').filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.now()
    )[:NUMBER_POSTS_DISPLAYED]
    context = {'post_list': post_list}
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = category.posts.filter(
        is_published=True,
        pub_date__lte=datetime.now()
    )
    context = {'post_list': post_list,
               'category': category}
    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.select_related('category', 'location').filter(pk=id),
        pk=id,
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.now()
    )
    context = {'post': post}
    return render(request, template, context)
