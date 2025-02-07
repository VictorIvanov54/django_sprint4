from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)


from blog.forms import PostForm, CommentForm, ProfileForm
from blog.models import Post, Category, Comment
from blog.constants import NUMBER_OBJECTS_PER_PAGE
from blog.mixins import OnlyAuthorMixin


User = get_user_model()


class PostListView(ListView):
    """Отображение списка постов (главная страница)."""

    model = Post
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = NUMBER_OBJECTS_PER_PAGE

    def get_queryset(self):
        return self.model.filt.select_annotate().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now()
        )


class PostDetailView(DetailView):
    """Детальное отображение отдельного поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_object(self):
        post = get_object_or_404(self.model, pk=self.kwargs[self.pk_url_kwarg])
        if post.author == self.request.user:
            return post
        return get_object_or_404(
            self.model.objects.select_related(
                'category', 'location', 'author').filter(
                    pk=self.kwargs[self.pk_url_kwarg],
                    is_published=True,
                    category__is_published=True,
                    pub_date__lte=datetime.now()
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Отображение создания нового поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user}
        )


class PostUpdateView(OnlyAuthorMixin, LoginRequiredMixin, UpdateView):
    """Отображение изменения отдельного поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail', args=(self.kwargs[self.pk_url_kwarg],)
        )

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect(
                'blog:post_detail', self.kwargs[self.pk_url_kwarg]
            )
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(OnlyAuthorMixin, LoginRequiredMixin, DeleteView):
    """Отображение удаления отдельного поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        context['form'] = PostForm(instance=instance)
        return context


class CategoryPostsListView(ListView):
    """Отображение постов отдельной категории."""

    model = Post
    template_name = 'blog/category.html'
    slug_url_kwarg = 'category_slug'
    paginate_by = NUMBER_OBJECTS_PER_PAGE
    ordering = '-pub_date'

    def get_queryset(self):
        return self.model.filt.select_annotate().filter(
            category__slug=self.kwargs[self.slug_url_kwarg],
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs[self.slug_url_kwarg],
            is_published=True
        )
        return context


class UserProfileListView(ListView):
    """Отображение страницы конкретного пользователя со списком его постов."""

    model = Post
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    paginate_by = NUMBER_OBJECTS_PER_PAGE
    ordering = '-pub_date'

    def get_queryset(self):
        if self.kwargs[self.slug_url_kwarg] == self.request.user.username:
            return self.model.filt.select_annotate().filter(
                author__username=self.request.user,
            )
        else:
            return self.model.filt.select_annotate().filter(
                is_published=True,
                author__username=self.kwargs[self.slug_url_kwarg],
                category__is_published=True,
                pub_date__lte=datetime.now()
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs[self.slug_url_kwarg],
        )
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Отображение страницы изменения профиля конкретного пользователя."""

    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'
    slug_url_kwarg = 'username'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        """Отправляем письмо, если пользователь изменил профиль."""
        send_mail(
            subject='The user changed the profile',
            message=f'{self.request.user} изменил профиль',
            from_email='User@post.not',
            recipient_list=['admin@post.not'],
            fail_silently=True,
        )
        return reverse(
            'blog:profile', kwargs={'username': self.object.username}
        )


class CommentUpdateView(UserPassesTestMixin, UpdateView):
    """Отображение страницы изменения отдельного комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = get_object_or_404(
            self.model, pk=self.kwargs[self.pk_url_kwarg]
        )
        return comment.author == self.request.user

    def get_success_url(self):
        return reverse(
            'blog:post_detail', args=(self.kwargs['post_id'],)
        )


class CommentDeleteView(UserPassesTestMixin, DeleteView):
    """Отображение страницы удаления отдельного комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        comment = get_object_or_404(
            self.model, pk=self.kwargs[self.pk_url_kwarg]
        )
        return comment.author == self.request.user


@login_required
def add_comment(request, post_id):
    """Добавление комментария к публикации"""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id)
