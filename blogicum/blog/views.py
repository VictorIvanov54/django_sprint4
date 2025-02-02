from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)


from .forms import PostForm, CommentForm, ProfileForm
from blog.models import Post, Category, Comment

User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    
    def get_queryset(self):
        return self.model.objects.select_related('category', 'location').filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now()
        )
    # ordering = '-pub_date'
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_object(self):
        post = get_object_or_404(self.model, pk=self.kwargs[self.pk_url_kwarg])
        if post.author == self.request.user:
            return post
        return get_object_or_404(        
            self.model.objects.select_related('category', 'location').filter(
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
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:profile')
        
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user})


class PostUpdateView(OnlyAuthorMixin, LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
   
    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', args=(self.kwargs[self.pk_url_kwarg],)
        )
    
    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != self.request.user.pk:
            return reverse_lazy(
                'blog:post_detail', args=(self.kwargs[self.pk_url_kwarg],)
            )
        return super().dispatch(request, *args, **kwargs)
    
    # instance = get_object_or_404(Post, pk=pk)
    # # В форму передаём только объект модели;
    # # передавать в форму параметры запроса не нужно.
    # form = PostForm(instance=instance)
    # context = {'form': form}
    # return redirect('birthday:list')
    # success_url = reverse_lazy('blog:post_detail')
    # # redirect('blog:post_detail', pk=pk)
    # def add_comment(request, pk):
    #     post = get_object_or_404(Post, pk=pk)
    #     # Функция должна обрабатывать только POST-запросы.
    #     form = PostForm(request.POST)

    # def get_object_or_404(self, pk):
    #     form = PostForm(request.POST)
    #     return Post.objects.select_related(
    #         'category', 'location').filter(pk=self.kwargs['pk'])


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    # form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    # context_object_name = 'form.instance'
    success_url = reverse_lazy('blog:index')

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(author=self.request.user)

    # def get_form(self, form_class):
    #     if form_class is None:
    #         form_class = self.get_form_class()
    #     return form_class(**self.get_form_kwargs())

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['form'] = self.get_form(PostForm).filter(pk=self.post.id)
    #     return context
    
    # # def get_object_or_404(self, pk):
    #     # return Post.objects.select_related('category', 'location').filter(
        #     pk=self.kwargs['pk']
        # )
        # instance = get_object_or_404(Post, pk=pk)
    # В форму передаём только объект модели;
    # передавать в форму параметры запроса не нужно.
        # context['form'] = PostForm(instance=instance)
        # return redirect('birthday:list')
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
        
    #     context['form.instance'] = PostForm
    #     return context


class CategoryPostsListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    slug_url_kwarg = 'category_slug'
    # slug_field = 'slug'
    allow_empty = False
    
    def get_queryset(self):
        return self.model.objects.select_related('category', 'location').filter(
            is_published=True,
            category__slug=self.kwargs[self.slug_url_kwarg],
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
    
    paginate_by = 10


class UserProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs[self.slug_url_kwarg])
        if user.username == self.request.user:
            return self.model.objects.select_related('category', 'location').filter(
                author__username=self.request.user,
            )
        else:
            return self.model.objects.select_related('category', 'location').filter(
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
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'
    slug_url_kwarg = 'username'
    
    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.object.username}
        )
    

class CommentUpdateView(UserPassesTestMixin, UpdateView):
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
        return reverse_lazy(
            'blog:post_detail', args=(self.kwargs['post_id'],)
        )


class CommentDeleteView(UserPassesTestMixin, DeleteView):
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
    
    # def get_success_url(self):
    #     return reverse_lazy(
    #         'blog:post_detail', args=(self.kwargs['post_id'],)
    #     )
    

@login_required
def add_comment(request, post_id):
    # Получаем объект поста или выбрасываем 404 ошибку.
    post = get_object_or_404(Post, pk=post_id)
    # Функция должна обрабатывать только POST-запросы.
    form = CommentForm(request.POST)
    if form.is_valid():
        # Создаём объект поста, но не сохраняем его в БД.
        comment = form.save(commit=False)
        # В поле author передаём объект автора поста.
        comment.author = request.user
        # В поле Post передаём объект дня рождения.
        comment.post = post
        # Сохраняем объект в БД.
        comment.save()
    # Перенаправляем пользователя назад, на страницу дня рождения.
    return redirect('blog:post_detail', post_id)

