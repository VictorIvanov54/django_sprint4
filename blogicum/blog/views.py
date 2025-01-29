from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.models import Post, Category

User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    # context_object_name = 'page_obj'

    def get_queryset(self):
        return Post.objects.select_related('category', 'location').filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now()
        )
    # ordering = '-pub_date'
    paginate_by = 10


class CategoryPostsListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    # context_object_name = 'page_obj'
    # slug_url_kwarg = 'category_slug'
    # slug_field = 'slug'
    allow_empty = False
    
    def get_queryset(self):
        return Post.objects.select_related('category', 'location').filter(
            is_published=True,
            category__slug=self.kwargs['category_slug'],
            category__is_published=True,
            pub_date__lte=datetime.now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context
    
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    # pk_url_kwarg = 'pk'
    # context_object_name = 'post'

    def get_object_or_404(self):
        return Post.objects.select_related('category', 'location').filter(
            pk=self.kwargs['pk'],
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now()
        )
     

class UserProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
            
    def get_queryset(self):
        return Post.objects.select_related('category', 'location').filter(
            is_published=True,
            author__username=self.kwargs['username'],
            category__is_published=True,
            pub_date__lte=datetime.now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'],
        )
        return context
    
    paginate_by = 10
# =========================================
# from django.views.generic import (
#     CreateView, DeleteView, DetailView, ListView, UpdateView
# )
# from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# from django.urls import reverse_lazy
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect

# from .forms import PostForm, CongratulationForm
# from .models import Post, Congratulation

# from .utils import calculate_Post_countdown


# class OnlyAuthorMixin(UserPassesTestMixin):

#     def test_func(self):
#         object = self.get_object()
#         return object.author == self.request.user


# class PostListView(ListView):
#     model = Post
#     queryset = Post.objects.prefetch_related(
#         'tags'
#     ).select_related('author')
#     ordering = 'id'
#     paginate_by = 10


# class PostCreateView(LoginRequiredMixin, CreateView):
#     model = Post
#     form_class = PostForm

#     def form_valid(self, form):
#         # Присвоить полю author объект пользователя из запроса.
#         form.instance.author = self.request.user
#         # Продолжить валидацию, описанную в форме.
#         return super().form_valid(form)


# class PostUpdateView(OnlyAuthorMixin, UpdateView):
#     model = Post
#     form_class = PostForm


# class PostDeleteView(OnlyAuthorMixin, DeleteView):
#     model = Post
#     success_url = reverse_lazy('Post:list')


# class PostDetailView(DetailView):
#     model = Post

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['Post_countdown'] = calculate_Post_countdown(
#             self.object.Post
#         )
#         # Записываем в переменную form пустой объект формы.
#         context['form'] = CongratulationForm()
#         # Запрашиваем все поздравления для выбранного дня рождения.
#         context['congratulations'] = (
#             # Дополнительно подгружаем авторов комментариев,
#             # чтобы избежать множества запросов к БД.
#             self.object.congratulations.select_related('author')
#         )
#         return context


# @login_required
# def add_comment(request, pk):
#     # Получаем объект дня рождения или выбрасываем 404 ошибку.
#     Post = get_object_or_404(Post, pk=pk)
#     # Функция должна обрабатывать только POST-запросы.
#     form = CongratulationForm(request.POST)
#     if form.is_valid():
#         # Создаём объект поздравления, но не сохраняем его в БД.
#         congratulation = form.save(commit=False)
#         # В поле author передаём объект автора поздравления.
#         congratulation.author = request.user
#         # В поле Post передаём объект дня рождения.
#         congratulation.Post = Post
#         # Сохраняем объект в БД.
#         congratulation.save()
#     # Перенаправляем пользователя назад, на страницу дня рождения.
#     return redirect('Post:detail', pk=pk)
